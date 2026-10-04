# S03 - Conveyor Inspection Cell

## Status and scope

- Native visual approval: **Pending**
- Native behavior/runtime: **Not created**
- Native PLC profile: **Not created**
- Source contract: `prototype/scenes/conveyor-cell.json`
- Player mode: **Visual review only; all PLC and playback commands disabled**

This setup document defines the intended equipment topology, source behavior,
and point ownership for review. It does not authorize use of Scene 2's DB14
profile and it does not claim PLC commissioning.

## Purpose

Prove a basic inspection conveyor sequence in which three cartons circulate on
an end-driven roller conveyor and block an opposed through-beam photoeye one at
a time.

## Equipment and physical topology

| Equipment | Setup requirement |
| --- | --- |
| Main roller conveyor | Discharge/head roller drives the conveyor. Gearmotor and gearbox are mounted on the discharge end roller shaft, not placed loose on the floor. |
| Cartons 1-3 | Three separate cartons sit on the roller bed with 2.6 m nominal spacing. |
| Inspection photoeye | Sender and receiver are mounted outside opposite side channels with the beam crossing the product path. |
| Operator station | Local conveyor station is clear of the moving product path. |
| Stacklight | Cell status stacklight is mounted outside the conveyor envelope. |

The isometric painter order must remain far rail, rollers/products, then near
rail at every supported camera angle. A roller appearing both in front of and
behind the same rail is a rendering failure.

## Source behavior

1. Initial state is stopped, photoeye clear, completed count zero, and three
   cartons at their source positions.
2. When `conveyor_run` is TRUE and the scene runtime is running, cartons move
   in the positive conveyor direction at 1.05 m/s.
3. `photoeye_blocked` is TRUE while any carton overlaps the inspection beam.
4. A carton that exits the discharge end is moved behind the trailing carton
   and `parts_completed` increments.
5. Stopping the conveyor holds carton positions and reports zero actual speed.

## Point contract

| Point | Type | Owner | Initial | Intended use |
| --- | --- | --- | --- | --- |
| `conveyor_run` | BOOL | PLC | FALSE | PLC-owned motor run command. |
| `photoeye_blocked` | BOOL | PC | FALSE | Simulator-owned inspection photoeye feedback to the PLC. |
| `conveyor_speed` | REAL | SIM | 0 m/s | Internal actual conveyor speed. |
| `parts_completed` | DINT | SIM | 0 | Internal count of cartons discharged and recirculated. |

Ownership is strict: the future PLC profile may read PC-owned feedback and
write PLC-owned commands only. SIM points stay internal unless a later profile
explicitly exposes them.

## Initial-state and rate settings

- Conveyor speed: 1.05 m/s
- Product spacing: 2.6 m
- Conveyor command: FALSE
- Photoeye: clear
- Parts completed: 0

## PLC profile and addressing

No native PLC profile or absolute address map exists for S03. Do not copy or
fall back to the Scene 2 DB14 mapping. Connect and Test PLC must remain disabled
while S03 is selected. Addressing will be documented only after a dedicated
profile is created and reviewed.

## Player review procedure

1. Start RungProof and select `S03 - Conveyor Inspection Cell` in the scene
   playlist.
2. Confirm the viewport says `PENDING SCENE APPROVAL`.
3. Orbit from both sides and verify the far rail stays behind every roller and
   the near rail stays in front.
4. Verify the gearmotor is coupled to the discharge roller shaft.
5. Verify both photoeye heads align across the conveyor and do not clip the
   rails or cartons.
6. Confirm Run, Reset, Connect, and Test PLC are disabled.

## Acceptance criteria

- No rail/roller depth inversion or part clipping at supported orbit angles.
- Motor/gearbox/drive roller share a credible shaft centerline.
- Cartons rest on the rollers and remain inside the conveyor channels.
- Photoeye beam crosses the product path between opposed heads.
- The player exposes no S03 PLC operation until a dedicated profile exists.

Likely failure symptoms are an MC Escher rail/roller overlap, a floor-mounted
unconnected motor, a photoeye head inside a rail, or enabled PLC controls.

## Bench PLC assignment and operation guide

Complete `docs/PLC_BENCH_SETUP.md` first. S03 is an independent practice cell;
it does not inherit Scene 2 pusher tags or DB14 process mappings.

Create or map these exact process names:

```text
conveyor_run       BOOL  PLC -> Simulator
photoeye_blocked   BOOL  Simulator -> PLC
```

`conveyor_speed` and `parts_completed` remain internal simulator diagnostics.
With `conveyor_run = TRUE`, cartons travel toward the opposed photoeye;
`photoeye_blocked` becomes TRUE only while a carton crosses the beam. A FALSE
PLC command holds the cartons. The simulator never creates a conveyor command
to complete the expected answer.

Watch `conveyor_run`, `photoeye_blocked`, `conveyor_speed`,
`parts_completed`, and the common watchdog fields. A missing or stuck photoeye
must be reported and must not be silently corrected.
