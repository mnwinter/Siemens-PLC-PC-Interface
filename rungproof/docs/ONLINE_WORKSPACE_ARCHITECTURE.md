# RungProof Online Workspace Boundary

Status: design boundary; no remote service is enabled by this document.

## Product shape

RungProof remains a native edge client for the plant runtime and PLC session.
An online workspace adds versioned content, assignments, documentation, and
sanitized evidence around that local execution path:

```text
Native RungProof Edge Client
  |-- Workspace Client -- HTTPS --> Hosted Workspace Control Plane
  |                                  |-- identity and roles
  |                                  |-- project and scene versions
  |                                  |-- assignments
  |                                  `-- sanitized evidence metadata
  `-- Plant Runtime -> PLC Session -> Snap7 -> isolated S7-1500
                                      local only
```

## Non-negotiable safety boundary

The hosted workspace must never:

- carry the PLC heartbeat;
- issue Run, Stop, or Reset;
- receive PLC credentials or DB14 write-scope secrets;
- authorize physical PLC writes;
- become the watchdog or safety authority;
- stream raw PLC telemetry by default.

The local PLC Session and PLC watchdog remain authoritative. Online state is
an audit and content state, never a machine-control state.

## Smallest safe vertical slice

1. Sign in to one workspace.
2. List an assigned, versioned Scene 2 package.
3. Download, hash-verify, validate, and stage the package locally.
4. Launch the existing native scene from the last-known-good package.
5. Upload sanitized session metadata only.
6. Keep the last-known-good package available in `Offline Workspace` mode.

The native implementation now includes a deterministic transport seam in
`tools/native_workspace_client.py`. `InMemoryHostedWorkspace` exercises the
same sign-in, assignment, hash/compatibility verification, offline fallback,
and sanitized metadata-upload flow that a future authenticated HTTPS adapter
must implement. It is deliberately a test/development service, not a claim
that a hosted production control plane is deployed.

## Local-first implementation seams

The first code slice can be built without an account or server:

- `WorkspaceClient` protocol;
- deterministic local-fixture adapter;
- package manifest and compatibility schema;
- hash verification and rollback staging;
- sanitized `NativeSessionSnapshot` projection;
- tests proving workspace data cannot alter PLC profile, DB14 scope,
  connection intent, heartbeat, or Plant Runtime inputs.

## Decisions required before deployment

- shared content/evidence only versus remote observation;
- single organization, private deployment, or multi-tenant SaaS;
- identity provider and role model;
- retention, residency, and privacy policy;
- whether assignments warn or block launch;
- whether raw telemetry is permanently prohibited from leaving the workstation;
- update, licensing, and support model.

Remote PLC control is out of scope and should remain permanently prohibited.
