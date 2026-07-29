SIEMENS PLC-PC INTERFACE - SCENE 2 CONVEYOR PUSHER
==================================================

Purpose
-------
This package runs the second beginner scene: a conveyor, stop photoeye, and
single-solenoid spring-return pusher controlled by PLC logic.

TIA project rule
----------------
Create "Scene 2 - Conveyor Pusher" by using Save As on the completed Scene 1
project. Reuse DB14 inside the new Scene 2 project. Replace the Scene 1
scene-specific tags and logic; do not accumulate both scenes in one PLC
program and do not create DB15 just to preserve the prior scene.

Read SCENE_2_PUSHER.md before changing DB14 or running the live test.

Run order
---------
1. Double-click 1-VALIDATE-SCENE-2.cmd.
2. Require SCENE_VALID: True and PLC_CONNECTION_ATTEMPTED: False.
3. Double-click 2-PREVIEW-SCENE-2.cmd.
4. Require the exact four-field DB14 write scope and no PLC connection.
5. Open the Scene 2 TIA project and its DB14 watch table.
6. Set DB14.DBX10.0 Simulation_Enable to TRUE.
7. Double-click 3-LIVE-SCENE-2.cmd and type RUN.
8. Observe stop, extend, transfer, retract, and ready/running.
9. Stop the viewer and require SAFE_STATE_WRITE: PASS.
10. Set Simulation_Enable to FALSE.

Authorized PC writes
--------------------
  DB14.DBX0.0  Part_At_Pusher
  DB14.DBX0.1  Pusher_Extended
  DB14.DBX0.2  Pusher_Retracted
  DB14.DBD2     PC_Heartbeat

The program does not write physical I/O, PLC commands, Simulation_Enable,
watchdog status, or CPU operating state.

Expected sequence
-----------------
- Conveyor runs with pusher retracted.
- Product reaches Part_At_Pusher and conveyor stops.
- PLC latches Pusher_Extend.
- Pusher extends and transfers the product.
- Pusher_Extended resets the extend command.
- Pusher retracts.
- Pusher_Retracted permits the conveyor to run again.

First failure checks
--------------------
- No conveyor: check Simulation_Comm_OK and Pusher_Retracted.
- No push: check the Pusher_Extend set rung.
- No retract: check the Pusher_Extended reset rung.
- Viewer stays STARTING: check heartbeat echo progression.
- Limits appear inverted: confirm DB14.DBX0.1 extended and DB14.DBX0.2
  retracted, with retracted safe value true.
