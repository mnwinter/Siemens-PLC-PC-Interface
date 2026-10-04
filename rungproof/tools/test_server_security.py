"""HTTP integration tests for the local-only server security boundary."""

from __future__ import annotations

from functools import partial
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from tools import serve_player
from tools.plc_live import LivePlcController


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "prototype" / "plc-profiles"


class HttpFakeLiveTransport:
    """Fake S7 endpoint used only through the local HTTP public interface."""

    instances: list["HttpFakeLiveTransport"] = []

    def __init__(self) -> None:
        self._connected = False
        self.writes: list[tuple[str, object]] = []
        self.plc_values: dict[str, object] = {
            "conveyor_running": True,
            "pusher_extend": False,
            "plc_heartbeat_echo": 0,
            "simulation_enable": True,
            "simulation_comm_ok": False,
            "simulation_timeout": True,
        }
        self.__class__.instances.append(self)

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self, _connection: object) -> None:
        self._connected = True

    def read_many(self, tags: tuple[object, ...]) -> dict[str, object]:
        return {tag.name: self.plc_values[tag.name] for tag in tags}

    def write_many(self, values: list[tuple[object, object]]) -> None:
        self.writes.extend((tag.name, value) for tag, value in values)

    def disconnect(self) -> None:
        self._connected = False


class LocalServerSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rungproof-test-")
        HttpFakeLiveTransport.instances.clear()
        self.original_saved = serve_player.SAVED_SCENES_DIR
        serve_player.SAVED_SCENES_DIR = (
            Path(self.temporary.name) / "saved-scenes"
        )
        self.live_controller = LivePlcController(
            PROFILE_DIR,
            transport_factory=HttpFakeLiveTransport,
        )
        handler = partial(
            serve_player.NoCacheHandler,
            directory=str(ROOT),
        )
        self.server = serve_player.LocalPlayerServer(
            ("127.0.0.1", 0),
            handler,
            plc_live_controller=self.live_controller,
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        self.port = self.server.server_address[1]
        self.origin = f"http://127.0.0.1:{self.port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        serve_player.SAVED_SCENES_DIR = self.original_saved
        self.temporary.cleanup()

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        payload = response.read()
        response_headers = {key.lower(): value for key, value in response.getheaders()}
        connection.close()
        return response.status, response_headers, payload

    def session_token(self) -> str:
        status, _, payload = self.request("GET", "/api/session")
        self.assertEqual(status, 200)
        return json.loads(payload)["token"]

    def authorized_headers(self) -> dict[str, str]:
        return {
            "Origin": self.origin,
            "X-RungProof-Token": self.session_token(),
            "Content-Type": "application/json",
        }

    def test_every_mutation_requires_origin_and_capability(self) -> None:
        status, _, _ = self.request(
            "POST",
            "/api/app/heartbeat",
            body=b"{}",
        )
        self.assertEqual(status, 403)

        token = self.session_token()
        status, _, _ = self.request(
            "POST",
            "/api/app/heartbeat",
            headers={
                "Origin": "https://attacker.example",
                "X-RungProof-Token": token,
                "Content-Type": "application/json",
            },
            body=b"{}",
        )
        self.assertEqual(status, 403)

        status, _, payload = self.request(
            "POST",
            "/api/app/heartbeat",
            headers=self.authorized_headers(),
            body=b"{}",
        )
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(payload)["ok"])

    def test_untrusted_host_is_rejected_before_local_api_disclosure(self) -> None:
        for path in ("/api/session", "/api/plc/profiles", "/api/scenes"):
            with self.subTest(path=path):
                status, _, payload = self.request(
                    "GET",
                    path,
                    headers={"Host": "attacker.example"},
                )
                self.assertEqual(status, 421)
                self.assertIn("Host header", json.loads(payload)["error"])

    def test_static_server_exposes_only_application_roots(self) -> None:
        status, headers, _ = self.request("GET", "/prototype/player.html")
        self.assertEqual(status, 200)
        self.assertIn("script-src 'self'", headers["content-security-policy"])
        self.assertEqual(headers["x-content-type-options"], "nosniff")

        for path in (
            "/PROJECT_INFORMATION.md",
            "/prototype/%2e%2e/PROJECT_INFORMATION.md",
            "/prototype/plc-profiles/scene-1-db14-interface.json",
        ):
            with self.subTest(path=path):
                status, _, _ = self.request("GET", path)
                self.assertEqual(status, 404)

    def test_scene_save_uses_full_contract_and_authorization(self) -> None:
        scene_path = ROOT / "prototype" / "scenes" / "scene-1-conveyor-stop.plcscene"
        document = json.loads(scene_path.read_text(encoding="utf-8"))
        document["equipment"][0]["config"]["length"] = 1_000_000
        body = json.dumps(document).encode("utf-8")
        headers = self.authorized_headers()
        headers["Content-Type"] = (
            "application/vnd.plc-visual-simulator.scene+json"
        )
        status, _, payload = self.request(
            "POST",
            "/api/scenes",
            headers=headers,
            body=body,
        )
        self.assertEqual(status, 400)
        self.assertIn("length", json.loads(payload)["error"])
        self.assertEqual(list(serve_player.SAVED_SCENES_DIR.glob("*")), [])

        valid_body = scene_path.read_bytes()
        headers["Content-Length"] = str(len(valid_body))
        status, _, payload = self.request(
            "POST",
            "/api/scenes",
            headers=headers,
            body=valid_body,
        )
        self.assertEqual(status, 200)
        result = json.loads(payload)
        self.assertTrue(
            (serve_player.SAVED_SCENES_DIR / result["fileName"]).is_file()
        )

    def test_guarded_live_plc_http_exchange_requires_exact_scope(self) -> None:
        status, _, payload = self.request("GET", "/api/plc/profiles")
        self.assertEqual(status, 200)
        profiles = json.loads(payload)["profiles"]
        profile = next(
            item
            for item in profiles
            if item["id"] == "scene-2-db14-pusher-interface.json"
        )
        self.assertEqual(len(profile["live"]["writeScope"]), 4)

        headers = self.authorized_headers()
        headers["X-PLC-Live-Mode"] = "guarded-write"
        connect_body = json.dumps(
            {
                "profileId": profile["id"],
                "sceneId": "scene-2-conveyor-pusher",
                "execute": True,
                "authorizedWriteScope": profile["live"]["writeScope"],
            }
        ).encode("utf-8")
        status, _, payload = self.request(
            "POST",
            "/api/plc/live/connect",
            headers=headers,
            body=connect_body,
        )
        self.assertEqual(status, 200)
        connected = json.loads(payload)

        cycle_body = json.dumps(
            {
                "sessionId": connected["sessionId"],
                "sceneId": "scene-2-conveyor-pusher",
                "pcPoints": {
                    "part_at_pusher": False,
                    "pusher_extended": False,
                    "pusher_retracted": True,
                },
            }
        ).encode("utf-8")
        status, _, payload = self.request(
            "POST",
            "/api/plc/live/cycle",
            headers=headers,
            body=cycle_body,
        )
        self.assertEqual(status, 200)
        cycle = json.loads(payload)
        self.assertEqual(cycle["plcPoints"]["conveyor_running"], True)
        self.assertEqual(
            {name for name, _value in HttpFakeLiveTransport.instances[-1].writes},
            {
                "simulated_photoeye",
                "simulated_pusher_extended",
                "simulated_pusher_retracted",
                "pc_heartbeat",
            },
        )

    def test_live_plc_connection_rejects_missing_marker_and_scope_change(
        self,
    ) -> None:
        status, _, payload = self.request("GET", "/api/plc/profiles")
        profile = next(
            item
            for item in json.loads(payload)["profiles"]
            if item["id"] == "scene-2-db14-pusher-interface.json"
        )
        request_body = {
            "profileId": profile["id"],
            "sceneId": "scene-2-conveyor-pusher",
            "execute": True,
            "authorizedWriteScope": profile["live"]["writeScope"],
        }

        status, _, _ = self.request(
            "POST",
            "/api/plc/live/connect",
            headers=self.authorized_headers(),
            body=json.dumps(request_body).encode("utf-8"),
        )
        self.assertEqual(status, 403)
        self.assertEqual(HttpFakeLiveTransport.instances, [])

        request_body["authorizedWriteScope"] = request_body[
            "authorizedWriteScope"
        ][:-1]
        headers = self.authorized_headers()
        headers["X-PLC-Live-Mode"] = "guarded-write"
        status, _, payload = self.request(
            "POST",
            "/api/plc/live/connect",
            headers=headers,
            body=json.dumps(request_body).encode("utf-8"),
        )
        self.assertEqual(status, 409)
        self.assertIn("exactly match", json.loads(payload)["error"])
        self.assertEqual(HttpFakeLiveTransport.instances, [])


if __name__ == "__main__":
    unittest.main()
