# Pilot support runbook

## Information to collect first

- RungProof version from **Help > About RungProof** or packaged `VERSION`.
- Windows edition/build, VM platform/version, display resolution, and renderer.
- Exact scene and whether the controller state was disconnected, read-only
  diagnostic, or authorized real PLC.
- The visible connection/readiness status and the first failed step.
- Sanitized screenshots and logs. Remove PLC IPs if the support recipient is not
  authorized to receive controls-network information.

Never request passwords, production data, safety-program exports, or unrelated
plant/customer files.

## First checks by symptom

| Symptom | First check | Expected evidence |
|---|---|---|
| Application will not open | Confirm ZIP was extracted and `VERSION`, `RungProof.exe`, Qt DLLs, profiles, and licenses remain together | Missing-file error or complete one-folder package |
| Blank/ghosted viewport | Confirm default software renderer and declared VM/display | Self-test reports `software-qwidget` and no native child window |
| Run unavailable | Check selected scene and controller/readiness state | Only Scene 2 supports native live actions; other scenes fail closed |
| Read-only check fails | Verify exact profile, network reachability, rack/slot, DB existence and type | Actionable connection/address result; zero writes |
| Connected - not ready | Check enable, communication-good, timeout, and heartbeat echo in TIA | All readiness conditions healthy before Run |
| Pusher does not move | Follow command/feedback chain in `README-VM.txt` | Part feedback reaches PLC, ladder commands extend, command returns to RungProof |
| Playback stopped after fault | Confirm the fresh-Run requirement | Recovery never resumes motion automatically |
| Close appears delayed | Wait for bounded PLC worker shutdown; do not kill power to an active bench as a normal close method | Window remains visible in closing state, then no residual process |

## Severity

- **S0 safety/security:** unintended PLC write, scope mismatch, automatic
  connection, misleading safe-state claim, credential/data exposure, or an
  active writer after Close. Stop pilot use and preserve evidence.
- **S1 blocker:** cannot install/start or complete the supported Scene 2 task.
- **S2 degraded:** supported workflow works with a repeatable workaround.
- **S3 minor:** cosmetic/documentation issue with no state or safety ambiguity.

## Release and rollback ownership

The product owner approves the release and rollback artifact. Development owns
reproduction, fix, and regression evidence. The controls-bench owner approves
TIA/CPU configuration and live test conditions. Legal/compliance approval is
separate from engineering acceptance.
