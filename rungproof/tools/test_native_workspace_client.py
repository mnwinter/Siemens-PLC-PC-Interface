import unittest

try:
    from .native_workspace import (
        PackageCompatibilityError,
        PackageSource,
        SanitizedSessionMetadata,
        VersionedAssignedScenePackage,
    )
    from .native_workspace_client import (
        InMemoryHostedWorkspace,
        NativeWorkspaceClient,
        WorkspaceAuthenticationError,
        WorkspaceBoundaryError,
    )
except ImportError:
    from native_workspace import (
        PackageCompatibilityError,
        PackageSource,
        SanitizedSessionMetadata,
        VersionedAssignedScenePackage,
    )
    from native_workspace_client import (
        InMemoryHostedWorkspace,
        NativeWorkspaceClient,
        WorkspaceAuthenticationError,
        WorkspaceBoundaryError,
    )


class NativeWorkspaceClientTests(unittest.TestCase):
    def setUp(self) -> None:
        package = VersionedAssignedScenePackage.from_content(
            package_id="pkg-scene-2-v3",
            scene_id="scene-2",
            package_version="3.0.0",
            compatible_client_versions=("0.2.0-pilot.2",),
            content={"scene": "scene-2", "equipment": ["conveyor", "pusher"]},
        )
        self.service = InMemoryHostedWorkspace({"assignment-2": package})
        self.client = NativeWorkspaceClient(self.service, client_version="0.2.0-pilot.2")

    def test_sign_in_issues_only_an_opaque_workspace_token(self) -> None:
        identity = self.client.sign_in("operator@example.test", "workspace-secret")
        self.assertEqual(identity.subject, "operator@example.test")
        token_values = self.service.issued_token_values
        self.assertEqual(len(token_values), 1)
        value = token_values[0]
        self.assertTrue(value.startswith("fws_"))
        self.assertNotIn("workspace-secret", value)

    def test_operations_require_sign_in(self) -> None:
        with self.assertRaises(WorkspaceAuthenticationError):
            self.client.list_assigned_packages()

    def test_lists_assignments_and_syncs_verified_package(self) -> None:
        self.client.sign_in("operator", "secret")
        assignments = self.client.list_assigned_packages()
        self.assertEqual([item.assignment_id for item in assignments], ["assignment-2"])
        result = self.client.sync("assignment-2")
        self.assertEqual(result.source, PackageSource.ASSIGNED)
        self.assertTrue(result.package.verify_hash())

    def test_transport_outage_uses_last_known_good(self) -> None:
        self.client.sign_in("operator", "secret")
        first = self.client.sync("assignment-2")
        self.assertEqual(first.source, PackageSource.ASSIGNED)
        self.service.available = False
        fallback = self.client.sync("assignment-2")
        self.assertEqual(fallback.source, PackageSource.LAST_KNOWN_GOOD)
        self.assertEqual(fallback.package.package_id, first.package.package_id)

    def test_incompatible_assignment_is_rejected_before_cache_use(self) -> None:
        self.client.sign_in("operator", "secret")
        incompatible = VersionedAssignedScenePackage.from_content(
            package_id="pkg-incompatible",
            scene_id="scene-2",
            package_version="4.0.0",
            compatible_client_versions=("0.9.0",),
            content={"scene": "scene-2"},
        )
        self.service.replace_assignment("assignment-2", incompatible)
        with self.assertRaises(PackageCompatibilityError):
            self.client.sync("assignment-2")
        self.service.available = False
        fallback = self.client.sync("assignment-2")
        self.assertEqual(fallback.source, PackageSource.UNAVAILABLE)

    def test_uploads_only_sanitized_session_metadata(self) -> None:
        self.client.sign_in("operator", "secret")
        metadata = SanitizedSessionMetadata(
            session_id="session-1",
            project_id="project-1",
            scene_id="scene-2",
            client_version="0.2.0-pilot.2",
            started_at_utc="2026-08-08T00:00:00Z",
            package_source=PackageSource.ASSIGNED,
            connection_state="DISCONNECTED",
        )
        self.client.upload_session_metadata(metadata)
        self.assertEqual(len(self.service.uploads), 1)
        self.assertNotIn("plc_credentials", self.service.uploads[0])
        with self.assertRaises(WorkspaceBoundaryError):
            self.client.upload_session_metadata(object())  # type: ignore[arg-type]

    def test_transport_rejects_plc_and_control_fields(self) -> None:
        self.client.sign_in("operator", "secret")
        # Deliberately exercise the transport boundary with a valid fake token.
        issued_token, _ = self.service.sign_in("boundary", "secret")
        base = {
            "session_id": "s",
            "project_id": "p",
            "scene_id": "scene-2",
            "client_version": "0.2.0-pilot.2",
            "started_at_utc": "2026-08-08T00:00:00Z",
            "package_source": "assigned",
            "connection_state": "DISCONNECTED",
        }
        for forbidden_field in ("PLCProfile", "DB14", "write_scope", "heartbeat", "control_command"):
            with self.subTest(forbidden_field=forbidden_field), self.assertRaises(WorkspaceBoundaryError):
                payload = dict(base)
                payload[forbidden_field] = {"value": "rejected"}
                self.service.upload_session_metadata(issued_token, payload)


if __name__ == "__main__":
    unittest.main()
