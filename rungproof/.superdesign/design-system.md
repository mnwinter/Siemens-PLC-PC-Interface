# RungProof native design system

## Product context

RungProof is a native Windows PLC visual simulator for controls engineers and
students testing ladder logic against deterministic plant behavior and a real
Siemens S7-1500. It is dense, technical, and safety explicit. The application
must look like an engineering tool rather than a consumer dashboard.

## Visual direction

- Preserve the current dark blue-slate industrial identity and compact data
  density.
- Use subtle solid shade differences to identify functional regions; never use
  gradients, neon washes, high-gloss surfaces, or large saturated panels.
- Header: near-black blue slate.
- Left control/scene family: slightly teal-blue.
- Center viewport shell: deepest neutral blue; do not recolor the 3D scene.
- Right health/equipment family: neutral slate distinct from controls.
- Live-points/data family: dark cyan-slate with alternating table rows.
- Bottom transport: darkest operational band.
- Workspace gutters: deepest background tone.

## Semantic color contract

- `#16A34A` brand proof check and explicit good state.
- `#3DD6A5` TRUE/ready/run state.
- `#5FC5EC` actionable controls and keyboard focus.
- `#F2B94B` warning/disconnected state.
- `#EF6A61` fault/error only.
- Never encode PLC state by color alone; retain explicit text labels.

## Typography and spacing

- Segoe UI Variable or Segoe UI for interface text.
- Cascadia Mono or Consolas for addresses, timing, tag values, badges, and
  controller state.
- Dense 3-18 px spacing; 2-6 px corner radii; one-pixel separators.
- Avoid oversized headings and unnecessary card padding.

## Navigation and layout rules

- Maintain one product header and one bottom transport HUD.
- Preserve Views A, B, and C; they share one session and one viewport.
- Scene navigation belongs only in the `Scene` menu. `Scene Editor` is a
  direct menu action; production scenes and training labs remain grouped
  submenus. No main-page scene selector.
- `PLC > Test PLC - Read-only` is menu-only.
- Unsupported scenes may be listed but must be disabled until both a native
  plant runtime and exact PLC profile are approved. Never fall back to the
  active Scene 2 DB14 profile.

## Motion

Only the native machine simulation animates. UI shade changes are static.
Avoid decorative motion.
