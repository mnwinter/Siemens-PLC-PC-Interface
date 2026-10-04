# ADR 0001: Native direct PLC runtime

- Status: Accepted
- Date: 2026-07-30

## Context

The browser implementation drove each PLC exchange through a render-timed
JavaScript request, a localhost HTTP route, a Python session controller, and
Snap7. A separate browser-cycle monitor could close an otherwise healthy S7
session after a one-second gap. Recorded commissioning evidence showed
`part_at_pusher` become TRUE while the PLC was healthy, followed roughly
0.35 seconds later by `No live PLC session is connected` before the returned
`pusher_extend` command could actuate the model.

The browser was also a poor ownership boundary. Playback lifecycle, browser
lifecycle, renderer timing, HTTP authorization, and S7 connection state were
coupled across multiple shallow modules.

## Decision

RungProof will ship as one native Python process using Qt Widgets and Qt 3D.
The live data path is:

```text
Plant Runtime
  -> SimulationUpdateLoop
  -> InterfaceRuntime
  -> Snap7Transport
  -> S7-1500
```

The dedicated PLC worker owns that complete path. The UI and renderer read
immutable snapshots from the worker and are never upstream of a PLC cycle.

The implementation reuses the pinned Siemens modules
`ConveyorPusher`, `ConveyorPusherPointBinding`, `SimulationUpdateLoop`,
`InterfaceRuntime`, and `Snap7Transport`. The current Scene 2 vertical slice
adds only the application-level connection and playback ownership needed by
the product.

Connection intent persists until explicit Disconnect or application exit. A
real transport failure enters `RECONNECTING`; it does not silently convert
into an operator disconnect. PLC readiness faults keep the S7 transport open,
force applied plant commands safe, and latch playback stopped. Recovery and
reconnection always require a fresh operator Run.

The native production package contains no browser engine, local HTTP server,
JSON request path, JavaScript runtime, or renderer-driven heartbeat.

## Module depth and seams

The Plant Runtime is a deep module: its small step/reset interface hides fixed
physics, photoeye dwell, pusher stroke, typed point ownership, and reload
behavior.

The PLC transport interface remains a deliberate seam because it isolates
real S7 I/O from deterministic tests. The production implementation is Snap7;
the test adapter provides proof without becoming a user-facing Fake PLC mode.

The Qt renderer is an adapter at the edge. Keeping it downstream improves
locality because plant timing and PLC ownership are not spread across visual
objects.

## Consequences

- A render stall cannot expire a healthy PLC session.
- Stop, Reset, and scene completion cannot disconnect the S7 transport.
- DB14 exchange timing is controlled by one worker at the configured 20 ms
  period.
- A missed exchange slot is skipped; the worker never sends catch-up bursts.
- The UI remains responsive because network I/O never runs on the Qt thread.
- The current package initially supports only the native Scene 2 vertical
  slice; the other scenes and visual assets require incremental porting behind
  the Plant Runtime interface.
- PySide6 and its Qt libraries increase package size and require target-VM GPU
  validation.

## Rejected alternatives

- Embedded Chromium, WebView, Electron, or QtWebEngine: explicitly prohibited
  and retain the rejected browser lifecycle.
- Tkinter Canvas: already available and native, but cannot preserve the
  product's 3D behavior.
- WPF plus Python IPC: requires an unavailable .NET SDK and adds a process and
  serialization seam to the PLC path.
- A monolithic UI/PLC loop: fewer source files but worse module depth,
  testability, safety ownership, and UI responsiveness.
