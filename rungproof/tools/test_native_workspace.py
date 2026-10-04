import unittest

try:
    from native_workspace import (
        DeterministicLocalFixtureAdapter,
        PackageSource,
        PackageCompatibilityError,
        SessionMetadata,
        WorkspacePackageError,
        VersionedAssignedScenePackage,
        content_sha256,
        project_sanitized_session_metadata,
        resolve_assigned_package,
    )
except ModuleNotFoundError:  # Supports repository-level unittest discovery.
    from tools.native_workspace import (
        DeterministicLocalFixtureAdapter,
        PackageSource,
        PackageCompatibilityError,
        SessionMetadata,
        WorkspacePackageError,
        VersionedAssignedScenePackage,
        content_sha256,
        project_sanitized_session_metadata,
        resolve_assigned_package,
    )


class NativeWorkspaceTests(unittest.TestCase):
    CLIENT_VERSION = "0.3.0"

    def make_package(self, *, scene_id: str = "scene-2", version: str = "1.4.0") -> VersionedAssignedScenePackage:
        return VersionedAssignedScenePackage.from_content(
            package_id=f"pkg-{scene_id}-{version}",
            scene_id=scene_id,
            package_version=version,
            compatible_client_versions=(self.CLIENT_VERSION,),
            content={
                "scene": {"title": "Conveyor Pusher", "assets": ["main-conveyor", "pusher"]},
                "assignment": {"id": "lab-02", "role": "operator"},
            },
        )

    def test_valid_package_is_deterministic_and_verified(self) -> None:
        package = self.make_package()
        self.assertEqual(package.content_sha256, content_sha256(package.content))
        self.assertTrue(package.verify_hash())
        package.ensure_compatible(self.CLIENT_VERSION)
        self.assertEqual(package.content["scene"]["title"], "Conveyor Pusher")  # type: ignore[index]

    def test_hash_mismatch_is_rejected(self) -> None:
        package = self.make_package()
        broken = VersionedAssignedScenePackage(
            package_id=package.package_id,
            scene_id=package.scene_id,
            package_version=package.package_version,
            client_schema_version=package.client_schema_version,
            compatible_client_versions=package.compatible_client_versions,
            content=package.content,
            content_sha256="0" * 64,
            assigned_at_utc=package.assigned_at_utc,
        )
        with self.assertRaises(WorkspacePackageError):
            broken.ensure_compatible(self.CLIENT_VERSION)

    def test_incompatible_package_is_rejected_before_use(self) -> None:
        package = VersionedAssignedScenePackage.from_content(
            package_id="pkg-incompatible",
            scene_id="scene-2",
            package_version="1.0.0",
            compatible_client_versions=("0.2.0",),
            content={"scene": {"title": "Old package"}},
        )
        with self.assertRaises(PackageCompatibilityError):
            package.ensure_compatible(self.CLIENT_VERSION)

    def test_offline_uses_verified_last_known_good(self) -> None:
        package = self.make_package()
        adapter = DeterministicLocalFixtureAdapter(
            {"assignment-1": package},
            {"assignment-1": package},
            online=False,
        )
        result = resolve_assigned_package(adapter, "assignment-1", client_version=self.CLIENT_VERSION)
        self.assertEqual(result.source, PackageSource.LAST_KNOWN_GOOD)
        self.assertIs(result.package, package)

    def test_forbidden_workspace_fields_and_unsanitized_metadata_do_not_cross_boundary(self) -> None:
        with self.assertRaises(WorkspacePackageError):
            VersionedAssignedScenePackage.from_content(
                package_id="pkg-forbidden",
                scene_id="scene-2",
                package_version="1.0.0",
                compatible_client_versions=(self.CLIENT_VERSION,),
                content={"scene": {"plc_profile": "secret-profile"}},
            )

        metadata = SessionMetadata(
            session_id="session-1",
            project_id="project-1",
            scene_id="scene-2",
            client_version=self.CLIENT_VERSION,
            started_at_utc="2026-08-07T12:00:00Z",
            package_source=PackageSource.LAST_KNOWN_GOOD,
            connection_state="DISCONNECTED",
            plc_credentials={"password": "never-export"},
            raw_telemetry={"db14": {"raw": "never-export"}, "heartbeat": True},
        )
        sanitized = project_sanitized_session_metadata(metadata)
        self.assertEqual(sanitized.scene_id, "scene-2")
        self.assertFalse(hasattr(sanitized, "plc_credentials"))
        self.assertFalse(hasattr(sanitized, "raw_telemetry"))
        self.assertNotIn("never-export", repr(sanitized))


if __name__ == "__main__":
    unittest.main()
