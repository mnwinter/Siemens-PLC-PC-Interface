RUNGPROOF - NATIVE PLC VISUAL SIMULATOR
=======================================

PILOT BOUNDARY
--------------

The packaged VERSION file identifies the build. Only Scene 2 - Conveyor Pusher
is a supported native live scene. S03-S06 are review-only. RungProof is a
training/isolated-controls-bench tool, not a safety system or production-machine
commissioning authority.

An ordinary package build hides Connect Real PLC and cannot start the persistent
PLC writer. The internal PLC test candidate is deliberately produced with the
explicit -EnableRealPlc build switch. This lets the operator perform the bench
acceptance; it does not itself prove that the TIA/CPU/DB14 configuration passed.

1. Extract the ZIP to a normal writable folder on the Windows VM.
2. Confirm that plc-profiles\scene-2-db14-pusher-interface.json contains the
   intended PLC address, rack, slot, cycle time, and DB14 contract.
3. Run BENCH-PREFLIGHT.ps1. It verifies the package, enabled capability, and
   exact profile without contacting the PLC, then creates bench-evidence\
   BENCH-PREFLIGHT.json and BENCH-RESULT.json.
4. Double-click RungProof.exe.
   For a repeatable visual-approval packet, run CAPTURE-VIEWS.ps1. It creates
   disconnected Views A/B/C and CAPTURE-REPORT.json without connecting to a PLC.
5. Optional: click Test PLC - Read-only to connect, read every configured tag
   twice, write zero PLC values, and disconnect.
6. In the explicitly PLC-enabled internal test build, click Connect Real PLC
   and review the exact write scope.
7. Authorize that connection only when the matching TIA project and standard
   non-optimized DB14 are loaded in the PLC.
8. Wait for REAL PLC CONNECTED - HEALTHY, then click Run.
9. Complete bench-evidence\BENCH-RESULT.json from the TIA watch table and live
   observations, then run VALIDATE-BENCH-RESULT.ps1. It refuses incomplete or
   failed results and produces BENCH-ACCEPTANCE.json only after every required
   item is explicitly recorded as passing.

DELTA QUALIFICATION AFTER THE DISCONNECT-TELEMETRY CORRECTION
-------------------------------------------------------------

If a complete accepted 0.2.0-pilot.1 baseline already exists for this exact
profile and PLC target, preserve that evidence folder unchanged. Qualify the
corrected executable without falsely relabeling the old acceptance:

1. Extract this corrected package into a new folder.
2. Run:

     .\BENCH-PREFLIGHT.ps1 `
       -BaselineEvidenceDirectory "C:\path\to\baseline\bench-evidence"

   This verifies the corrected package and creates BENCH-DELTA-RESULT.json
   bound to both the new preflight and old acceptance hashes.
3. Establish one healthy normal cycle and reconfirm the four-address write
   scope in TIA.
4. Recheck explicit Disconnect, watchdog safe state, network loss,
   unavailable telemetry during loss, automatic reconnect, fresh-Run after
   recovery, and application Close.
5. Fill BENCH-DELTA-RESULT.json and run:

     .\VALIDATE-BENCH-DELTA.ps1 `
       -BaselineEvidenceDirectory "C:\path\to\baseline\bench-evidence"

   A complete passing result produces BENCH-DELTA-ACCEPTANCE.json with the
   full baseline-to-corrected-candidate hash lineage.

This package is a native Qt Windows application. Its default software-rendered
QWidget viewport does not require a Qt 3D native child window, avoiding the
blank/ghosted composition failure seen on the VM. It does not start Edge,
Chrome, Electron, WebView, an HTML engine, a local HTTP server, or a listening
port. Python, npm, a browser, internet access, and a separate Snap7
installation are not required on the target VM.

CURRENT NATIVE SCOPE
--------------------

The native vertical slice currently runs Scene 2 - Conveyor Pusher against the
real PLC. The earlier browser prototype remains in source as a behavior and
scene-contract reference, but it is not the packaged application.

The direct live path is:

  conveyor/pusher model
    -> typed PLC update loop
    -> Snap7 transport
    -> S7-1500

The native renderer only reads immutable runtime snapshots. Rendering,
window-message timing, and frame rate are not in the PLC exchange path.

READ-ONLY TEST OWNERSHIP
------------------------

Test PLC - Read-only owns a separate bounded diagnostic connection:

  connect -> read configured DB14 tags twice -> disconnect

It contains no transport write call. Connect Real PLC is disabled and guarded
at the command boundary while the diagnostic is active, so the persistent live
writer cannot overlap the read-only connection.

CONNECTION OWNERSHIP (OPERATOR-AUTHORIZED PLC TEST BUILD ONLY)
--------------------------------------------------------------

Connect Real PLC creates one persistent operator-authorized session.

- Run starts plant playback.
- Stop stops plant playback but leaves the S7 session and heartbeat active.
- Reset resets plant playback but leaves the S7 session and heartbeat active.
- Disconnect deliberately closes the S7 session.
- Closing RungProof deliberately closes the S7 session.
- A real transport failure moves the session to RECONNECTING while the
  operator's connection intent remains active.
- Closing, disconnected, connecting, and reconnecting states mark PLC
  heartbeat/status and PLC-owned command samples unavailable (`--`); cached
  connected samples are never presented as current telemetry.

Heartbeat or PLC simulation-status faults force conveyor and pusher commands
safe in the plant model and latch playback stopped. After readiness recovers,
press Run again. They do not masquerade as an operator Disconnect.

DB14 CONTRACT
-------------

RungProof writes only:

  DB14.DBX0.0  Part_At_Pusher
  DB14.DBX0.1  Pusher_Extended
  DB14.DBX0.2  Pusher_Retracted
  DB14.DBD2    PC_Heartbeat

RungProof reads:

  DB14.DBX1.0  Conveyor_Run
  DB14.DBX1.1  Pusher_Extend
  DB14.DBD6    PLC_Heartbeat_Echo
  DB14.DBX10.0 Simulation_Enable
  DB14.DBX10.1 Simulation_Comm_OK
  DB14.DBX10.2 Simulation_Timeout

The PLC watchdog is the safety authority. RungProof does not write a
last-second substitute command when the transport closes.

TROUBLESHOOTING
---------------

If the badge remains CONNECTED - NOT READY:

- Simulation_Enable must be TRUE.
- Simulation_Comm_OK must be TRUE.
- Simulation_Timeout must be FALSE.
- PLC_Heartbeat_Echo must continue following PC_Heartbeat.

If part_at_pusher becomes TRUE but the pusher does not move:

- verify DB14.DBX0.0 is TRUE in TIA;
- verify the ladder logic energizes DB14.DBX1.1;
- verify RungProof shows pusher_extend TRUE;
- verify DB14 is standard/non-optimized and matches the documented offsets.

The executable is unsigned, so Windows SmartScreen may require confirmation on
first launch.
