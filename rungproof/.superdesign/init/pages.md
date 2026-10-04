# Window dependency tree

## Main RungProof window

Entry: `tools/rungproof_native.py`

Dependencies:

- `tools/rungproof_native.py`
  - `tools/native_runtime.py`
    - vendored `siemens_plc_pc_interface` runtime and Snap7 transport
  - `tools/native_software_viewport.py`
    - renderer-neutral primitive geometry and QPainter viewport
  - `tools/plc_diagnostics.py`
    - isolated read-only PLC test
  - `prototype/scenes/*`
    - 7 production/reference scenes
    - 25 training labs
  - `packaging/vm/RungProof.ico`

Visual source ranges:

- Header/actions/layout: `tools/rungproof_native.py:758:1293`
- Theme/QSS: `tools/rungproof_native.py:1294:1617`
- A/B/C layout reassignment: `tools/rungproof_native.py:1618:1810`
- Native renderer: `tools/native_software_viewport.py`

PLC runtime logic is deliberately not part of the visual design payload.

