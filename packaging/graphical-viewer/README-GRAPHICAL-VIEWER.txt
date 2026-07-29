SIEMENS PLC-PC INTERFACE - FIRST GRAPHICAL VIEWER
=================================================

Purpose
-------
This package runs a graphical conveyor and photoeye simulation driven by the
PLC logic. It is a best-effort visual simulator, not a hard real-time machine
controller.

The configured 20 ms DB14 exchange is independent of the screen redraw. A
delayed display frame does not change scene physics or PLC exchange order.

Target used by the supplied configuration:
  CPU address: 10.70.9.201
  Rack: 0
  Slot: 1

Authorized PC writes:
  DB14.DBX0.0  PC_To_PLC simulated photoeye
  DB14.DBD2     PC_Heartbeat

The program does not write physical I/O, Simulation_Enable, PLC-owned status,
or CPU operating state.

Run order
---------
1. Double-click 1-VALIDATE-GRAPHICAL-VIEWER.cmd.
2. Require SCENE_VALID: True.
3. In TIA Portal, open the DB14 watch table.
4. Set DB14.DBX10.0 Simulation_Enable to TRUE.
5. Double-click 2-LIVE-GRAPHICAL-VIEWER.cmd.
6. Type RUN at the confirmation prompt.
7. Confirm the viewer reaches HEALTHY and matches the TIA watch table.
8. Use the Stop simulator button to close it.
9. Require SAFE_STATE_WRITE: PASS in the terminal.
10. Set Simulation_Enable to FALSE before leaving the test.

Expected visual sequence
------------------------
- Product begins at the conveyor infeed.
- Motor changes to RUN while PLC_To_PC is true.
- Product moves toward the photoeye.
- Photoeye changes from CLEAR to BLOCKED.
- PLC logic drops PLC_To_PC.
- Motor changes to STOP with the product blocking the photoeye.

First failure checks
--------------------
- No window: read the terminal error and confirm the packaged EXE includes
  Tcl/Tk.
- STARTING never becomes HEALTHY: verify PLC_Heartbeat_Echo changes.
- Motor never runs: verify Simulation_Enable, Simulation_Comm_OK, and
  PLC_To_PC in DB14.
- Product never moves: verify PLC_To_PC becomes true.
- Viewer closes with an error: leave Simulation_Enable false and save the
  terminal text for diagnosis.
