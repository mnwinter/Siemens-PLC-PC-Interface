# Lab 5.6 - Running-Light Tower help

Scene ID: `lab-5-06-running-light-tower`  
Migrated source: `prototype/scenes/lab-5-06-running-light-tower.plcscene`  
Scene contract: `res://scenes/migrated/lab-5-06-running-light-tower.scene.json`

## Purpose

A maintained ENABLE selector and momentary STEP request drive a PLC-owned red -> amber -> green running-light sequence.

## Expected I/O to operate this scene

All entries are symbolic scene points, not hardware addresses. PC owns raw operator feedback; PLC owns the three color commands.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `tower_enable` | `BOOL` | **PC** | `False` |
| `step_pulse` | `BOOL` | **PC** | `False` |
| `tower_red` | `BOOL` | **PLC** | `False` |
| `tower_amber` | `BOOL` | **PLC** | `False` |
| `tower_green` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Turn ENABLE OFF / RUN` | `toggle` | `tower_enable` |
| `Press STEP (momentary)` | `pulse` | `step_pulse` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `tower_enable` | `switch_0` | `selector` |
| `step_pulse` | `switch_2` | `switch` |
| `tower_red` | `indicator_1` | `indicatorChannel` |
| `tower_amber` | `indicator_1` | `indicatorChannel` |
| `tower_green` | `indicator_1` | `indicatorChannel` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `rotarySwitch` | ENABLE maintained selector OFF / RUN |
| `indicator_1` | `indicator` | PLC three-color running-light tower |
| `switch_2` | `switch` | Momentary sequence Step |

## Machine guide

### Start conditions

- Built-in offline controller with user-authored or explicitly opened reference logic.
- Initial ENABLE OFF, STEP released, phase zero and all lenses dark.

### Normal sequence

- Default exercise editor is empty. Build PLC sequence logic or explicitly open .tools/plant-review-running-light-tower.rpproj.json after --audit-running-tower.
- Run, then turn ENABLE to RUN. The first enabled accepted scan selects red; each fresh STEP edge advances amber, green, red.
- Idle scans never advance. OFF clears lamps and phase on the next accepted scan; re-enable starts red. A simultaneous first-enable STEP is discarded.

### Stop behavior

- Stop clears PLC color commands and discards pending Step, retaining ENABLE and internal phase.
- Run republishes the retained color; its first scan establishes a new Step edge baseline without advancing.
- Application Reset clears requests and phase, returns ENABLE to OFF and leaves stopped scan zero; the next enable selects red.

### Expected observations

- Exactly one PLC color while enabled: red -> amber -> green -> red on separate Step edges. Disabled, held and unsampled repeated clicks cannot accumulate deferred advances.

## Migration and execution boundary

Obsolete `tower_step_active` commanded only green. Update older projects to the three color outputs above. The historical prototype is unchanged.

The seven-rung original reference uses rising-edge detection and PLC DINT phase, with no timer or automatic advance. Its green-to-red wrap is an explicit training choice. One accepted scan samples each pulse and clears it; the next accepted low scan rearms the edge. Unsampled repeated clicks coalesce. The first scan after Stop/Reset establishes the baseline and cannot create a startup Step.

Stop removes symbolic commands; these checks establish neither hardware safety nor live PLC commissioning. Exercise editors stay blank and the authored demo catalog remains five.
