# RungProof brand system

## Working identity

**Name:** RungProof  
**Descriptor:** PLC Visual Simulator  
**Tagline:** Build the logic. Prove the machine.

**Positioning:** An offline-first 3D plant simulator for learning and testing
PLC ladder logic against deterministic machine behavior.

RungProof is a working product name selected after a preliminary web collision
scan. That scan is not trademark, corporate-name, domain, or legal clearance.
Do not spend materially on signage, domains, or registration until a formal
clearance search is complete.

## Name rationale

- **Rung** immediately anchors the product in ladder logic.
- **Proof** promises evidence and testing rather than vague visualization.
- The name is short enough for an executable, app title, icon, and spoken use.
- It supports a product family without losing the core meaning:
  RungProof Player, RungProof Scene Editor, and RungProof Lab.

## Logo

The selected production direction is the **ladder-baseline wordmark**:

- a bold `RungProof` wordmark with `Proof` in proof green;
- a restrained ladder baseline beneath the wordmark;
- cyan contact bars for the logic path;
- proof green reserved for the verified/proven segment.

Production assets:

- `rungproof-next/assets/brand/rungproof-mark.svg`
- `rungproof-next/assets/brand/rungproof-lockup.svg`
- `rungproof-next/assets/brand/rungproof-icon.svg`

The earlier cube/checkmark artwork remains in the prototype history as a
superseded exploration and is no longer the selected RungProof Next identity.

The AI-designed concept sheet is retained at:

- `docs/brand/logo-concepts/rungproof-logo-concept-sheet-v2-green.png`

The concept sheet is exploratory raster artwork. The SVG mark is the canonical
production source because its ladder contact, geometry, colors, and scaling are
deterministic.

Additional green-check explorations:

- `docs/brand/logo-concepts/rungproof-concept-rp-monogram-v1.png`
- `docs/brand/logo-concepts/rungproof-concept-ladder-check-v1.png`
- `docs/brand/logo-concepts/rungproof-concept-plant-cell-v1.png`

These three sheets are candidate directions, not production assets. The current
canonical SVG remains in place until one direction is explicitly selected and
redrawn as deterministic vector artwork.

## Color tokens

| Token | Hex | Use |
|---|---|---|
| Proof Navy | `#071A2A` | Wordmark, cube, primary dark identity |
| Logic Cyan | `#28A9E2` | Ladder contact, links, focused controls |
| Proof Green | `#16A34A` | Logo check mark; deliberate TRUE/good meaning |
| Warning Amber | `#FFB000` | Warnings and attention states only |
| Plant White | `#F7FAFB` | Icon tile and light surfaces |
| Steel | `#4B6674` | Secondary copy and technical metadata |
| Safe Green | `#3DD6A5` | Runtime-safe/active status only |
| Fault Red | `#EF6A61` | Faults and destructive actions only |

Green and red remain operational state colors rather than general decoration.
The logo check is the one intentional identity exception: its green explicitly
means verified, good, and ladder-logic TRUE. Amber remains reserved for warning
or attention states.

## Typography

- UI and wordmark fallback: `Segoe UI Variable`, `Segoe UI`, system UI.
- Technical values: a system monospace font.
- Use sentence case for product copy.
- Use uppercase only for short state labels such as `DISCONNECTED`,
  `FAKE PLC`, `SYSTEM STOP`, and `READ-ONLY`.

## Voice

RungProof is direct, technical, and evidence-led.

Use:

- “Controller disconnected — scene outputs safe.”
- “Readback passed with warnings.”
- “Connect Real PLC — review and confirm the exact DB scope.”
- “The PLC watchdog state still requires live verification.”

Avoid:

- marketing claims such as “guaranteed safe”;
- calling Fake PLC a real PLC;
- describing a read-only diagnostic as live binding;
- calling a training scene a digital twin without measured model fidelity.

## Product terminology

| Preferred | Avoid |
|---|---|
| RungProof | PLC Scene Player as the product name |
| PLC Visual Simulator | generic “viewer” |
| Offline Fake PLC | virtual real PLC |
| Read-only PLC Check | Test PLC as a scene-control claim |
| Connect Real PLC | connect live, when the guarded runtime is actually present |
| plant scene | animation |
| command / feedback point | arbitrary tag |
| system stop / operator stop / interlock stop | paused |

## UI rules

- The current controller source must always be visible.
- A PLC write capability must never be implied when none exists.
- Real PLC connection must show and confirm the exact write scope before the
  final Connect action is enabled.
- Disconnection may claim the scene outputs are safe; it must not claim
  physical PLC outputs are proven safe without live watchdog evidence.
- Use one product header for brand, menus, and controller state.
- Operational state colors take priority over brand decoration.
- Configuration, Hint, and Solution remain separate disclosure levels.
- Faults and alarms must say they are simulated and local.
- Loading a scene resets Fake PLC and clears forces.

## Brand decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-07-30 | Adopt RungProof as working name | Ladder-logic specificity plus test/proof positioning |
| 2026-07-30 | Keep “PLC Visual Simulator” as descriptor | Preserves high-value PLC, visual, and simulator keywords |
| 2026-07-30 | Use “Build the logic. Prove the machine.” | Connects ladder programming to observable plant evidence |
| 2026-07-30 | Canonicalize the vector mark | Correct ladder symbol and deterministic release assets |
| 2026-10-02 | Select direction 10, ladder-baseline wordmark | Stronger wordmark ownership, better small-size behavior, and a direct PLC-language cue; keep Proof green for verified meaning |
| 2026-07-30 | Reserve green/red for operating state | Controls meaning is more important than decorative branding |
| 2026-07-30 | Separate Read-only PLC Check from Connect Real PLC | Prevents a diagnostic from being mistaken for live scene control |
| 2026-07-30 | Say “scene outputs safe” when disconnected | Avoids claiming unobserved physical PLC output state |
| 2026-07-30 | Consolidate the web menus into one product header | Removes duplicate product chrome while retaining native window controls |
| 2026-07-30 | Change the proof check from amber to green | Aligns verification with ladder-logic TRUE/good meaning and leaves amber for warnings |
| 2026-07-30 | Explore RP monogram, ladder-check, and plant-cell alternatives | Provides distinct directions without replacing the canonical vector before selection |

## Brand steward remit

The RungProof Brand Steward workspace agent should maintain this decision log,
review UI and documentation for naming and controls-language consistency, flag
unsubstantiated claims, track missing release assets, and keep legal-clearance
work visibly separate from creative naming.
