"""Serve RungProof and launch its dedicated desktop app window.

The local HTTP server supplies the bundled player assets and saved-scene API.
The desktop shell uses an installed Chromium engine in application mode, with
no tabs or address bar. The PLC setup test is read-only. A separate explicit
guarded session can exchange only the configured DB tags for a live scene.
"""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from typing import Any
from urllib.parse import quote, unquote, urlparse
import webbrowser

try:
    from .plc_diagnostics import (
        PlcDiagnosticError,
        list_plc_profiles,
        run_read_only_plc_test,
    )
    from .plc_live import LivePlcController, LivePlcError
    from .scene_contract import SceneContractError, validate_scene_document
except ImportError:
    from plc_diagnostics import (
        PlcDiagnosticError,
        list_plc_profiles,
        run_read_only_plc_test,
    )
    from plc_live import LivePlcController, LivePlcError
    from scene_contract import SceneContractError, validate_scene_document


FROZEN = bool(getattr(sys, "frozen", False))
RESOURCE_ROOT = (
    Path(getattr(sys, "_MEIPASS")).resolve()
    if FROZEN
    else Path(__file__).resolve().parents[1]
)
APPLICATION_DIR = (
    Path(sys.executable).resolve().parent
    if FROZEN
    else RESOURCE_ROOT / "prototype"
)
SAVED_SCENES_DIR = APPLICATION_DIR / "saved-scenes"
PLC_PROFILES_DIR = APPLICATION_DIR / "plc-profiles"
SCENE_SCHEMA_PATH = RESOURCE_ROOT / "prototype" / "scene.schema.json"
SCENE_FILE_TYPE = "plc-visual-scene"
SCENE_FILE_MIME = "application/vnd.plc-visual-simulator.scene+json"
MAX_SCENE_BYTES = 2 * 1024 * 1024
APP_HEARTBEAT_TIMEOUT_SECONDS = 12.0
APP_STARTUP_TIMEOUT_SECONDS = 30.0


def _safe_print(message: str) -> None:
    """Print when a console exists; PyInstaller's windowed mode has none."""

    if sys.stdout is not None:
        print(message, flush=True)


def _show_error(message: str) -> None:
    """Show startup failures even when the packaged EXE has no console."""

    if FROZEN and os.name == "nt":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                None,
                message,
                "RungProof",
                0x00000010,
            )
            return
        except (AttributeError, OSError):
            pass
    if sys.stderr is not None:
        print(message, file=sys.stderr, flush=True)


def _candidate_browser_paths() -> list[tuple[str, Path]]:
    """Return installed browsers that support Chromium application mode."""

    candidates: list[tuple[str, Path]] = []
    environment_roots = {
        name: Path(value)
        for name in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA")
        if (value := os.environ.get(name))
    }
    browser_locations = (
        (
            "Microsoft Edge",
            "PROGRAMFILES(X86)",
            Path("Microsoft/Edge/Application/msedge.exe"),
        ),
        (
            "Microsoft Edge",
            "PROGRAMFILES",
            Path("Microsoft/Edge/Application/msedge.exe"),
        ),
        (
            "Microsoft Edge",
            "LOCALAPPDATA",
            Path("Microsoft/Edge/Application/msedge.exe"),
        ),
        (
            "Google Chrome",
            "PROGRAMFILES",
            Path("Google/Chrome/Application/chrome.exe"),
        ),
        (
            "Google Chrome",
            "PROGRAMFILES(X86)",
            Path("Google/Chrome/Application/chrome.exe"),
        ),
        (
            "Google Chrome",
            "LOCALAPPDATA",
            Path("Google/Chrome/Application/chrome.exe"),
        ),
    )
    for name, root_name, relative_path in browser_locations:
        root = environment_roots.get(root_name)
        if root is not None:
            candidates.append((name, root / relative_path))
    for name, command in (
        ("Microsoft Edge", "msedge"),
        ("Google Chrome", "chrome"),
    ):
        resolved = shutil.which(command)
        if resolved:
            candidates.append((name, Path(resolved)))
    return candidates


def _find_app_browser() -> tuple[str, Path] | None:
    seen: set[str] = set()
    for name, path in _candidate_browser_paths():
        key = str(path).casefold()
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            return name, path.resolve()
    return None


def _app_profile_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else APPLICATION_DIR
    return base / "RungProof" / "Browser Profile"


def _launch_app_window(url: str) -> tuple[str, subprocess.Popen[bytes]] | None:
    browser = _find_app_browser()
    if browser is None:
        return None

    browser_name, executable = browser
    profile_dir = _app_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(executable),
        f"--app={url}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1440,900",
        "--no-first-run",
        "--disable-default-apps",
        "--disable-background-mode",
    ]
    if browser_name == "Microsoft Edge":
        command.append("--disable-features=msEdgeFirstRunExperience")
    creation_flags = 0x08000000 if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )
    return browser_name, process


class LocalPlayerServer(ThreadingHTTPServer):
    """HTTP server with optional application-window lifetime tracking."""

    daemon_threads = True

    def __init__(
        self,
        *args: object,
        plc_live_controller: LivePlcController | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.app_window_mode = False
        self.app_process: subprocess.Popen[bytes] | None = None
        self.app_heartbeat_seen = False
        self.app_last_heartbeat = time.monotonic()
        self.app_monitor_stop = threading.Event()
        self.plc_test_lock = threading.Lock()
        self.app_token = secrets.token_urlsafe(32)
        self.plc_live = plc_live_controller or LivePlcController(
            PLC_PROFILES_DIR
        )
        self.plc_live_monitor_stop = threading.Event()
        self.plc_live_monitor = threading.Thread(
            target=self._monitor_plc_live,
            daemon=True,
        )
        self.plc_live_monitor.start()

    def _monitor_plc_live(self) -> None:
        while not self.plc_live_monitor_stop.wait(0.1):
            if self.plc_live.expire_stale():
                _safe_print(
                    "LIVE PLC: browser cycle timeout; guarded session closed."
                )

    def server_close(self) -> None:
        self.plc_live_monitor_stop.set()
        self.plc_live.close()
        if (
            self.plc_live_monitor.is_alive()
            and self.plc_live_monitor is not threading.current_thread()
        ):
            self.plc_live_monitor.join(timeout=1)
        super().server_close()

    def note_app_heartbeat(self) -> None:
        self.app_heartbeat_seen = True
        self.app_last_heartbeat = time.monotonic()

    def stop_from_app(self) -> None:
        def stop() -> None:
            self.plc_live.close()
            process = self.app_process
            if process is not None and process.poll() is None:
                process.terminate()
            self.shutdown()

        threading.Thread(target=stop, daemon=True).start()


def _monitor_app_window(server: LocalPlayerServer) -> None:
    """Stop the hidden server after its dedicated window is closed."""

    started = time.monotonic()
    while not server.app_monitor_stop.wait(0.75):
        now = time.monotonic()
        process = server.app_process
        process_exited = process is not None and process.poll() is not None
        heartbeat_stale = (
            server.app_heartbeat_seen
            and now - server.app_last_heartbeat > APP_HEARTBEAT_TIMEOUT_SECONDS
        )
        if server.app_heartbeat_seen and (process_exited or heartbeat_stale):
            _safe_print("Application window closed; stopping local server.")
            server.shutdown()
            return
        if (
            not server.app_heartbeat_seen
            and now - started > APP_STARTUP_TIMEOUT_SECONDS
        ):
            _show_error(
                "RungProof opened a browser engine, but the application "
                "window did not finish loading."
            )
            if process is not None and process.poll() is None:
                process.terminate()
            server.shutdown()
            return


class NoCacheHandler(SimpleHTTPRequestHandler):
    """Static files plus a local-only saved-scene library."""

    def _send_json(self, status: int, payload: object) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _saved_scene_descriptors(self) -> list[dict[str, str]]:
        SAVED_SCENES_DIR.mkdir(parents=True, exist_ok=True)
        descriptors: list[dict[str, str]] = []
        for path in sorted(SAVED_SCENES_DIR.glob("*.plcscene")):
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
                validate_scene_document(document, SCENE_SCHEMA_PATH)
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                SceneContractError,
            ):
                continue
            if not isinstance(document, dict):
                continue
            name = document.get("name")
            if not isinstance(name, str) or not name.strip():
                name = path.stem
            descriptors.append(
                {
                    "id": f"saved:{path.name}",
                    "label": f"Saved — {name.strip()}",
                    "url": f"/api/scenes/{quote(path.name, safe='')}",
                    "fileName": path.name,
                }
            )
        return descriptors

    def _request_host_is_allowed(self) -> bool:
        """Reject DNS-rebinding hostnames before exposing localhost data."""

        server = self.server
        if not isinstance(server, LocalPlayerServer):
            return False
        port = server.server_address[1]
        supplied_host = self.headers.get("Host", "").strip().lower()
        return supplied_host in {
            f"127.0.0.1:{port}",
            f"localhost:{port}",
        }

    def _reject_untrusted_host(self) -> bool:
        if self._request_host_is_allowed():
            return False
        self._send_json(
            421,
            {"error": "The local RungProof server rejected the Host header."},
        )
        return True

    def _mutation_request_is_authorized(self) -> bool:
        """Require both a same-origin browser request and app capability."""

        server = self.server
        if not isinstance(server, LocalPlayerServer):
            return False
        port = server.server_address[1]
        allowed_origins = {
            f"http://127.0.0.1:{port}",
            f"http://localhost:{port}",
        }
        supplied_token = self.headers.get("X-RungProof-Token", "")
        return (
            self.headers.get("Origin") in allowed_origins
            and secrets.compare_digest(supplied_token, server.app_token)
        )

    def _plc_test_request_is_authorized(self) -> bool:
        """Keep the PLC route's explicit read-only operator intent marker."""

        return (
            self._mutation_request_is_authorized()
            and self.headers.get("X-PLC-Test-Mode") == "read-only"
        )

    def _plc_live_request_is_authorized(self) -> bool:
        """Require an explicit marker for the configured guarded write path."""

        return (
            self._mutation_request_is_authorized()
            and self.headers.get("X-PLC-Live-Mode") == "guarded-write"
        )

    def _read_json_request(
        self,
        label: str,
        *,
        maximum_bytes: int = 64 * 1024,
    ) -> dict[str, Any] | None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length."})
            return None
        if not 1 <= content_length <= maximum_bytes:
            self._send_json(
                413,
                {
                    "error": (
                        f"{label} request must be 1 byte to "
                        f"{maximum_bytes // 1024} KiB."
                    )
                },
            )
            return None
        try:
            payload = json.loads(
                self.rfile.read(content_length).decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send_json(
                400,
                {"error": f"Invalid {label} request JSON: {exc}"},
            )
            return None
        if not isinstance(payload, dict):
            self._send_json(
                400,
                {"error": f"{label} request must be an object."},
            )
            return None
        return payload

    def _static_path_is_allowed(self, request_path: str) -> bool:
        decoded = unquote(request_path)
        if "\\" in decoded:
            return False
        segments = decoded.split("/")
        if any(segment in {".", ".."} for segment in segments):
            return False
        normalized = "/" + decoded.lstrip("/")
        blocked_prefixes = (
            "/prototype/plc-profiles/",
            "/prototype/saved-scenes/",
        )
        if any(normalized.startswith(prefix) for prefix in blocked_prefixes):
            return False
        allowed_prefixes = ["/prototype/", "/vendor/"]
        if not FROZEN:
            allowed_prefixes.append("/scene-editor-prototype/")
        return any(normalized.startswith(prefix) for prefix in allowed_prefixes)

    def do_GET(self) -> None:
        if self._reject_untrusted_host():
            return
        request_path = urlparse(self.path).path
        if request_path == "/api/session":
            server = self.server
            if not isinstance(server, LocalPlayerServer):
                self._send_json(500, {"error": "Local server is unavailable."})
                return
            self._send_json(200, {"token": server.app_token})
            return
        if request_path == "/api/plc/profiles":
            server = self.server
            if not isinstance(server, LocalPlayerServer):
                self._send_json(500, {"error": "Local server is unavailable."})
                return
            profiles = list_plc_profiles(PLC_PROFILES_DIR)
            for profile in profiles:
                try:
                    profile["live"] = server.plc_live.describe_profile(
                        profile["id"]
                    )
                except LivePlcError as exc:
                    profile["live"] = {
                        "available": False,
                        "error": str(exc),
                    }
            self._send_json(
                200,
                {
                    "profiles": profiles,
                    "readOnly": True,
                    "writePathPresent": True,
                    "liveWritePath": "guarded",
                },
            )
            return
        if request_path == "/api/scenes":
            self._send_json(
                200,
                {
                    "fileType": SCENE_FILE_TYPE,
                    "extension": ".plcscene",
                    "scenes": self._saved_scene_descriptors(),
                },
            )
            return
        if request_path.startswith("/api/scenes/"):
            file_name = unquote(request_path.removeprefix("/api/scenes/"))
            if (
                Path(file_name).name != file_name
                or not file_name.lower().endswith(".plcscene")
            ):
                self._send_json(404, {"error": "Saved scene was not found."})
                return
            scene_path = SAVED_SCENES_DIR / file_name
            try:
                encoded = scene_path.read_bytes()
                document = json.loads(encoded.decode("utf-8"))
                validate_scene_document(document, SCENE_SCHEMA_PATH)
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                SceneContractError,
            ):
                self._send_json(404, {"error": "Saved scene was not found."})
                return
            self.send_response(200)
            self.send_header("Content-Type", f"{SCENE_FILE_MIME}; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        if not self._static_path_is_allowed(request_path):
            self._send_json(404, {"error": "Resource was not found."})
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self._reject_untrusted_host():
            return
        request_path = urlparse(self.path).path
        if not self._static_path_is_allowed(request_path):
            self.send_error(404, "Resource was not found.")
            return
        super().do_HEAD()

    def do_POST(self) -> None:
        if self._reject_untrusted_host():
            return
        request_path = urlparse(self.path).path
        if not self._mutation_request_is_authorized():
            self._send_json(
                403,
                {
                    "error": (
                        "Local changes require an authorized same-origin "
                        "RungProof application session."
                    )
                },
            )
            return
        if request_path == "/api/app/heartbeat":
            server = self.server
            if isinstance(server, LocalPlayerServer) and server.app_window_mode:
                server.note_app_heartbeat()
            self._send_json(200, {"ok": True})
            return
        if request_path == "/api/app/exit":
            server = self.server
            if not (
                isinstance(server, LocalPlayerServer)
                and server.app_window_mode
            ):
                self._send_json(
                    409,
                    {"error": "The player is not running in app-window mode."},
                )
                return
            self._send_json(200, {"ok": True})
            server.stop_from_app()
            return
        if request_path == "/api/plc/test":
            if not self._plc_test_request_is_authorized():
                self._send_json(
                    403,
                    {
                        "error": (
                            "PLC tests require an explicit same-origin "
                            "read-only request."
                        )
                    },
                )
                return
            server = self.server
            if not isinstance(server, LocalPlayerServer):
                self._send_json(500, {"error": "Local player server is unavailable."})
                return
            if not server.plc_test_lock.acquire(blocking=False):
                self._send_json(409, {"error": "A PLC test is already running."})
                return
            try:
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    self._send_json(400, {"error": "Invalid Content-Length."})
                    return
                if not 1 <= content_length <= 16 * 1024:
                    self._send_json(
                        413,
                        {"error": "PLC test request must be 1 byte to 16 KiB."},
                    )
                    return
                try:
                    payload = json.loads(
                        self.rfile.read(content_length).decode("utf-8")
                    )
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    self._send_json(
                        400,
                        {"error": f"Invalid PLC test request JSON: {exc}"},
                    )
                    return
                if not isinstance(payload, dict):
                    self._send_json(
                        400,
                        {"error": "PLC test request must be an object."},
                    )
                    return
                profile_id = payload.get("profileId")
                if not isinstance(profile_id, str):
                    self._send_json(400, {"error": "profileId is required."})
                    return
                try:
                    result = run_read_only_plc_test(
                        PLC_PROFILES_DIR,
                        profile_id,
                    )
                except (OSError, ValueError, PlcDiagnosticError) as exc:
                    self._send_json(400, {"error": str(exc)})
                    return
                self._send_json(200, result)
            finally:
                server.plc_test_lock.release()
            return
        if request_path.startswith("/api/plc/live/"):
            if not self._plc_live_request_is_authorized():
                self._send_json(
                    403,
                    {
                        "error": (
                            "Live PLC exchange requires explicit same-origin "
                            "guarded-write authorization."
                        )
                    },
                )
                return
            server = self.server
            if not isinstance(server, LocalPlayerServer):
                self._send_json(500, {"error": "Local player server is unavailable."})
                return
            payload = self._read_json_request("live PLC")
            if payload is None:
                return
            try:
                if request_path == "/api/plc/live/connect":
                    result = server.plc_live.connect(
                        profile_id=payload.get("profileId"),
                        scene_id=payload.get("sceneId"),
                        execute=payload.get("execute"),
                        authorized_write_scope=payload.get(
                            "authorizedWriteScope"
                        ),
                    )
                elif request_path == "/api/plc/live/cycle":
                    result = server.plc_live.cycle(
                        session_id=payload.get("sessionId"),
                        scene_id=payload.get("sceneId"),
                        pc_points=payload.get("pcPoints"),
                    )
                elif request_path == "/api/plc/live/disconnect":
                    session_id = payload.get("sessionId")
                    if session_id is not None and not isinstance(
                        session_id,
                        str,
                    ):
                        raise LivePlcError(
                            "sessionId must be a string when supplied."
                        )
                    result = server.plc_live.disconnect(
                        session_id=session_id,
                    )
                else:
                    self._send_json(
                        404,
                        {"error": "Unknown live PLC endpoint."},
                    )
                    return
            except (LivePlcError, OSError, ValueError) as exc:
                self._send_json(409, {"error": str(exc)})
                return
            self._send_json(200, result)
            return
        if request_path != "/api/scenes":
            self._send_json(404, {"error": "Unknown local API endpoint."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length."})
            return
        if not 1 <= content_length <= MAX_SCENE_BYTES:
            self._send_json(
                413,
                {"error": "Scene file must be between 1 byte and 2 MiB."},
            )
            return

        try:
            raw = self.rfile.read(content_length).decode("utf-8")
            document = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": f"Invalid scene JSON: {exc}"})
            return

        try:
            validate_scene_document(document, SCENE_SCHEMA_PATH)
        except SceneContractError as exc:
            self._send_json(400, {"error": str(exc)})
            return

        assert isinstance(document, dict)
        document["fileType"] = SCENE_FILE_TYPE
        scene_id = document.get("id")
        assert isinstance(scene_id, str)

        safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", scene_id).strip("-")
        if not safe_stem:
            self._send_json(400, {"error": "Scene id cannot form a file name."})
            return

        SAVED_SCENES_DIR.mkdir(parents=True, exist_ok=True)
        destination = SAVED_SCENES_DIR / f"{safe_stem}.plcscene"
        temporary = destination.with_suffix(".plcscene.tmp")
        overwritten = destination.exists()
        encoded = f"{json.dumps(document, indent=2, ensure_ascii=False)}\n"
        try:
            temporary.write_text(encoded, encoding="utf-8")
            temporary.replace(destination)
        except OSError as exc:
            self._send_json(500, {"error": f"Could not save scene: {exc}"})
            return

        self._send_json(
            200,
            {
                "id": f"saved:{destination.name}",
                "fileName": destination.name,
                "url": f"/api/scenes/{quote(destination.name, safe='')}",
                "overwritten": overwritten,
            },
        )

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header(
            "Content-Security-Policy",
            (
                "default-src 'self'; script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; connect-src 'self'; "
                "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
            ),
        )
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), usb=()",
        )
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        # Keep the terminal useful: report requests, but prefix them clearly.
        _safe_print(f"HTTP: {format % args}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run RungProof, the local PLC visual simulator.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=(
            "Local HTTP port. Source runs default to 4173; the packaged EXE "
            "selects a free port. Use 0 to always select a free port."
        ),
    )
    launch_group = parser.add_mutually_exclusive_group()
    launch_group.add_argument(
        "--no-browser",
        action="store_true",
        help="Start only the server; do not open a player window.",
    )
    launch_group.add_argument(
        "--browser",
        action="store_true",
        help="Open a normal default-browser tab instead of an app window.",
    )
    parser.add_argument(
        "--variant",
        choices=("A", "B", "C", "a", "b", "c"),
        default="A",
        help="Initial prototype layout (default: A).",
    )
    parser.add_argument(
        "--editor",
        action="store_true",
        help=(
            "Open the separate Scene Editor proof instead of the packaged "
            "Scene Player."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.editor and FROZEN:
        _show_error(
            "The separate Scene Editor proof is not bundled in the current "
            "RungProof EXE. Run it from the source workspace."
        )
        return 2

    handler = partial(NoCacheHandler, directory=str(RESOURCE_ROOT))
    requested_port = args.port if args.port is not None else (0 if FROZEN else 4173)

    try:
        server = LocalPlayerServer(("127.0.0.1", requested_port), handler)
    except OSError as exc:
        message = (
            f"Could not start local player server on port {requested_port}: "
            f"{exc}\n"
            "Try: py -3 tools\\serve_player.py --port 0",
        )
        _show_error(message)
        return 1

    actual_port = server.server_address[1]
    use_app_window = not args.no_browser and not args.browser
    if args.editor:
        url = (
            f"http://127.0.0.1:{actual_port}/"
            "scene-editor-prototype/editor.html"
        )
        application_name = "RUNGPROOF SCENE EDITOR PROOF"
        url_label = "EDITOR URL"
    else:
        url = (
            f"http://127.0.0.1:{actual_port}/prototype/player.html"
            f"?variant={args.variant.upper()}"
        )
        application_name = "RUNGPROOF — PLC VISUAL SIMULATOR"
        url_label = "PLAYER URL"
    query_separator = "&" if "?" in url else "?"
    application_url = (
        f"{url}{query_separator}appWindow=1" if use_app_window else url
    )
    _safe_print(application_name)
    _safe_print("PLC TEST: READ-ONLY ON EXPLICIT REQUEST")
    _safe_print("PLC LIVE: GUARDED WRITE SCOPE ON EXPLICIT AUTHORIZATION")
    _safe_print(f"RESOURCE ROOT: {RESOURCE_ROOT}")
    _safe_print(f"SAVED SCENES: {SAVED_SCENES_DIR}")
    _safe_print(f"PLC PROFILES: {PLC_PROFILES_DIR}")
    _safe_print(f"{url_label}: {application_url}")

    if use_app_window:
        launched = _launch_app_window(application_url)
        if launched is None:
            _safe_print(
                "No Edge or Chrome installation was found for app-window "
                "mode; opening the default browser instead."
            )
            webbrowser.open(url)
        else:
            browser_name, process = launched
            server.app_window_mode = True
            server.app_process = process
            _safe_print(f"APP WINDOW ENGINE: {browser_name}")
            threading.Thread(
                target=_monitor_app_window,
                args=(server,),
                daemon=True,
            ).start()
    elif args.browser:
        webbrowser.open(url)

    if args.no_browser or args.browser:
        _safe_print("Press Ctrl+C to stop the local server.")

    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        _safe_print("Stopping local player server.")
    finally:
        server.app_monitor_stop.set()
        process = server.app_process
        if process is not None and process.poll() is None:
            process.terminate()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
