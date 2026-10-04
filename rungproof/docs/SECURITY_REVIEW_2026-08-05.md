# RungProof security review - 2026-08-05

Status: manual partitioned source review complete; formal Codex Security backend
run blocked by a Windows inventory-path normalization defect.

## Scope and method

Three independent reviews covered the native/PLC path (49 of 49 scoped files),
browser/server path (21 of 21 files, 12,921 lines), and editor/data/vendor path
(77 of 79 files fully reviewed). The remaining two files are minified upstream
Three.js bundles; their pinned versions and license/provenance were reviewed,
but their minified implementation was not semantically audited line by line.

The formal scan was started against Git revision
`9968dc3e3ec2d024068f82889943632a6b5ce5fc`. Its threat model completed, but
finding preparation regenerated Windows paths such as `.\.gitignore` and then
rejected those same paths as unsafe. This is a scanner/tooling failure, not a
successful formal scan. No formal completion claim is made.

## Validated findings and disposition

| Severity | Finding | Resolution |
|---|---|---|
| High | A partial `pcPoints` cycle could preserve prior PC-owned values while heartbeat traffic continued | Require the exact declared PC-owned point set; disconnect and fail closed on missing or extra values |
| High | Any changing PLC heartbeat value could be accepted instead of an exact acknowledgement of the prior PC heartbeat | Require the PLC echo to equal the expected previously written heartbeat; unrelated changes no longer establish health |
| High | Build dependencies were version-pinned but not artifact-hashed, and a reusable build environment could retain unexpected distributions | Add SHA-256 hashes, `pip --require-hashes`, a clean build environment, and an exact installed-distribution audit |
| High | Browser scene import accepted unbounded local or fetched scene text | Reject over 2 MiB before local read where size is available and enforce the byte limit after decoding/fetch |
| High | A non-positive repeat-load interval could create a non-terminating browser simulation loop | Validate 0.05-3600 seconds at the schema/loader boundary and retain a defensive runtime guard |
| Medium | The development localhost server did not validate `Host`, permitting DNS-rebinding-style access to development content | Permit only the exact loopback host and selected port; reject other hosts with HTTP 421 |
| High | The pilot documentation required hiding live PLC writes before bench acceptance, but the package did not enforce that state | Add a fail-closed package capability manifest; the default artifact hides and command-guards Connect Real PLC, and an enabled build requires an explicit acceptance-record hash |

## Rejected candidate paths

Manual trace review found no supported-path evidence of automatic PLC
connection, writes outside the declared PC-owned DB14 points, overlap between
the read-only diagnostic and persistent writer, browser/server inclusion in the
native package, path traversal from the development server, state-changing HTTP
requests, executable scene content, XSS through the reviewed rendering seams,
or secrets committed in the reviewed product files.

## Remaining security gates

- Run the formal repository scan when its Windows path handling is corrected.
- Retain a dated dependency-vulnerability report with the release evidence.
- Verify the default packaged self-test reports `realPlcWritesEnabled: false`.
- For any PLC-write-enabled artifact, retain the approved bench record whose
  SHA-256 appears in `PILOT-CAPABILITIES.json`.
- Establish a private vulnerability-reporting address and response targets.
- Recheck dependencies and rerun affected tests for every release candidate.

This review is source and package engineering evidence. It is not PLC bench
commissioning, legal approval, or proof about unobserved physical machine I/O.
