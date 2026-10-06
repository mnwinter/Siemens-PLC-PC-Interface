# Lab 4.11 - Barrel Fill Station help

Scene ID: `lab-4-11-barrel-fill-station`  
Scene contract: `res://scenes/migrated/lab-4-11-barrel-fill-station.scene.json`

## Purpose

One supported barrel indexes under a connected nozzle, receives a measured 150 L batch and remains on the outfeed.

Finite prescribed offline model: mechanical indexing at X=0, constant flow of 20 L/s, 150 L target from a 200 L source, and retained outfeed at X=3. The barrel and source use transparent cutaway walls to expose actual liquid volume. Valve position is an immediate command projection; hydraulic head, valve transit, slosh, slip and replenishment are excluded.

## Expected I/O to operate this scene

All points are symbolic; PC owns feedback/inventory, PLC owns commands/authorization. No physical addresses or PLC transport are used.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `barrel_at_fill` | `BOOL` | **PC** | `False` |
| `fill_complete` | `BOOL` | **PC** | `False` |
| `downstream_clear` | `BOOL` | **PC** | `True` |
| `barrel_parked` | `BOOL` | **PC** | `False` |
| `fill_beam_blocked` | `BOOL` | **PC** | `False` |
| `exit_beam_blocked` | `BOOL` | **PC** | `False` |
| `fill_fault` | `BOOL` | **PC** | `False` |
| `batch_start` | `BOOL` | **PC** | `False` |
| `barrel_litres` | `REAL` | **PC** | `0.0` |
| `source_litres` | `REAL` | **PC** | `200.0` |
| `flow_lps` | `REAL` | **PC** | `0.0` |
| `infeed_run` | `BOOL` | **PLC** | `False` |
| `fill_valve_open` | `BOOL` | **PLC** | `False` |
| `cycle_active` | `BOOL` | **PLC** | `False` |
| `cycle_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start / resume barrel batch` | `pulse` | `batch_start` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `infeed_run` | `conveyor_0` | `running` |
| `infeed_run` | `indicator_4` | `indicator` |
| `fill_valve_open` | `indicator_11` | `indicator` |
| `fill_beam_blocked` | `photoeye_3` | `photoeye` |
| `exit_beam_blocked` | `exit_photoeye` | `photoeye` |
| `barrel_litres` | `training_accessory_6` | `numericDisplay` |
| `batch_start` | `switch_8` | `switch` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Indexed barrel conveyor |
| `tank_1` | `tank` | Elevated 200 L source cutaway |
| `valve_2` | `valve` | Connected quarter-turn fill valve |
| `photoeye_3` | `photoeye` | Fill-entry photoeye |
| `exit_photoeye` | `photoeye` | Outfeed occupancy photoeye |
| `indicator_4` | `indicator` | Feed command |
| `training_accessory_5` | `trainingAccessory` | Open-top barrel cutaway |
| `training_accessory_6` | `trainingAccessory` | Connected volumetric meter |
| `training_accessory_7` | `trainingAccessory` | Supported overhead fill nozzle |
| `switch_8` | `switch` | Start / resume barrel batch |
| `indicator_11` | `indicator` | Fill valve command |

## Run the editable reference

1. File -> Open Ladder Agent Project -> `programs/examples/barrel-fill-reference.rpproj.json`.
2. Return to Scene, Run scans, then press Start / resume barrel batch.
3. Barrel stops centered beneath the nozzle. Source volume falls while barrel volume rises; the connected meter displays litres transferred.
4. At 150 L the valve closes. Discharge permission latches while the downstream zone is empty, then allows this barrel to enter and occupy it. The barrel stops retained with 150 L; source retains 50 L; both commands are off.
5. Stop during feed, filling or discharge. Position and inventory hold and flow disappears. Run alone stays held; fresh Start resumes, including after this barrel has entered its owned outfeed zone.
6. Reset restores the empty infeed barrel, 200 L source, zero flow, closed valve and stopped scans. Completed batches cannot restart or recycle without Reset.

Default empty ladder remains an exercise. Run with no loaded program opens the editor and remains stopped.

## Feedback and diagnostics

`barrel_at_fill` observes the mechanical indexed position, while `fill_beam_blocked` separately observes the barrel silhouette across the entry beam. `exit_beam_blocked` observes the outfeed beam. `downstream_clear` is the footprint occupancy of the receiving zone starting at X=2.7 m; it remains false for the retained barrel.

`barrel_litres` plus `source_litres` always equals 200 L. Rendered cylinder volumes follow those same measurements; the stream ends at the current liquid surface. `fill_complete` is the measured 150 L target and `barrel_parked` also requires the final position. Feedback has no manual toggles.

Fill commanded during feed or away from the indexed barrel latches `fill_fault` and holds inventory/position until Reset. Raw PLC commands remain visible for diagnosis. External pause holds poses/inventory without rewriting them. Shared catalog deliveries and DB14 remain unchanged.

This offline sequence and its normal Stop do not prove a physical safety function, real E-stop/watchdog, hydraulic design or live commissioning.
