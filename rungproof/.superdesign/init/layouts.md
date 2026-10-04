# Native application layout

The only shipped layout is `RungProofWindow._build_ui` plus
`RungProofWindow.set_view_mode` in `tools/rungproof_native.py`. The design
call must use those source ranges directly because the implementation is a
single native QWidget composition rather than separate frontend components.

```text
QMainWindow
`-- QWidget#appRoot
    |-- QFrame#header
    |   |-- QFrame#brandTile (RP and green check)
    |   |-- product title and descriptor
    |   |-- QMenuBar#applicationMenu
    |   |-- QLabel#viewBadge
    |   `-- QLabel#connectionBadge
    |-- QFrame#workspace
    |   |-- left rail: scene and runtime panels
    |   |-- QFrame#viewportFrame: scene bar, native renderer, status
    |   |-- right rail: PLC health and equipment panels
    |   `-- live simulation points panel
    `-- QFrame#transportHud
        |-- Run, Step, Reset
        |-- now-playing state
        `-- time, exchange P99, controller meters
```

View A is the operator console, View B is viewport-first with edge cards, and
View C is the engineering split. All three reparent the same panels, viewport,
session, actions, and snapshot stream. The product header and transport HUD
remain singular and persistent.

Authoritative source:

- `tools/rungproof_native.py:976` (`_build_ui`)
- `tools/rungproof_native.py:1642` (`set_view_mode`)

