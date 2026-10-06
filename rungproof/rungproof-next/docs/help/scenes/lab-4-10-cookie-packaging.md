# Lab 4.10 - Cookie Packaging Cell help

Scene ID: `lab-4-10-cookie-packaging`  
Scene contract: `res://scenes/migrated/lab-4-10-cookie-packaging.scene.json`

## Purpose

Six supported cookie trays are optically counted, indexed and sealed; completed packages remain on the outfeed.

This is a finite, prescribed offline six-tray exercise. Its single belt indexes one unwrapped tray at a time at X=0.3 m, seals it in 2 s, then advances the batch. There is no replenishment, deletion, film/heat/slip or collision dynamics. Shared catalog deliveries remain unchanged.

## Expected I/O to operate this scene

All points are symbolic. PC owns position, optical and completion feedback; PLC owns commands and sequence authorization. No PLC transport or physical addresses are used.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `product_present` | `BOOL` | **PC** | `False` |
| `packaging_ready` | `BOOL` | **PC** | `True` |
| `batch_complete` | `BOOL` | **PC** | `False` |
| `packaging_busy` | `BOOL` | **PC** | `False` |
| `count_beam_blocked` | `BOOL` | **PC** | `False` |
| `packaging_fault` | `BOOL` | **PC** | `False` |
| `batch_start` | `BOOL` | **PC** | `False` |
| `cookie_count` | `INT` | **PC** | `0` |
| `wrapped_count` | `INT` | **PC** | `0` |
| `infeed_run` | `BOOL` | **PLC** | `False` |
| `packaging_enable` | `BOOL` | **PLC** | `False` |
| `cycle_active` | `BOOL` | **PLC** | `False` |
| `cycle_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start / resume cookie batch` | `pulse` | `batch_start` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `infeed_run` | `conveyor_0` | `running` |
| `infeed_run` | `indicator_3` | `indicator` |
| `packaging_enable` | `indicator_11` | `indicator` |
| `count_beam_blocked` | `photoeye_2` | `photoeye` |
| `batch_start` | `switch_8` | `switch` |
| `cookie_count` | `cookie_counter` | `numericDisplay` |
| `wrapped_count` | `package_counter` | `numericDisplay` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Six-cookie indexing conveyor |
| `machine_1` | `machine` | Cookie tray sealing station |
| `photoeye_2` | `photoeye` | Physical cookie count photoeye |
| `cookie_0` | `trainingAccessory` | Cookie tray 1 |
| `cookie_1` | `trainingAccessory` | Cookie tray 2 |
| `cookie_2` | `trainingAccessory` | Cookie tray 3 |
| `cookie_3` | `trainingAccessory` | Cookie tray 4 |
| `cookie_4` | `trainingAccessory` | Cookie tray 5 |
| `cookie_5` | `trainingAccessory` | Cookie tray 6 |
| `cookie_counter` | `trainingAccessory` | COOKIES physical feedback display |
| `package_counter` | `trainingAccessory` | SEALED physical feedback display |
| `switch_8` | `switch` | Start / resume cookie batch |
| `indicator_3` | `indicator` | Feed command |
| `indicator_11` | `indicator` | Sealer command |

## Run the editable reference

1. File -> Open Ladder Agent Project -> `programs/examples/cookie-packaging-reference.rpproj.json`.
2. Return to Scene, then Run. Scans advance while the batch remains held.
3. Press Start / resume cookie batch. Expect six distinct optical counts and six sealing cycles; both displays finish at 6.
4. Stop during feed or partial jaw travel. All trays and the head hold. Run alone stays held; fresh Start resumes.
5. At completion the head is home, feed and sealing commands are off, and six wrapped cookies remain visible. Start cannot recycle a completed batch.
6. Reset restores six unwrapped trays, both counts zero, head home and stopped playback.

The default empty ladder is an exercise and remains empty until edited or a project is opened. Run with no loaded controller opens the editor and remains stopped.

## Diagnostics and model boundary

`cookie_count` increments once per actual biscuit leading-edge crossing of the beam at X=0, Y=0.935 m. `wrapped_count` increments once per completed head stroke, and controls the visible wrap. Neither is preloaded or controlled by manual feedback toggles.

`product_present` reports an unwrapped tray indexed at the station. `packaging_busy` retains partial head travel. `packaging_ready` means idle head and no fault. Feed while sealing/busy latches `packaging_fault` and holds until Reset; PLC command values remain visible for diagnosis. An empty station cannot manufacture a package.

Offline Stop is a playback/control action, not a proven real-machine safety function. External paused playback holds geometry without overwriting command values. No live PLC, heat-sealing quality, food-process compliance or commissioning acceptance is claimed.

`--visual-scene-review` enables held 2 s steps using 100 actual 20 ms offline scans for multi-angle inspection. It is excluded in external mode.
