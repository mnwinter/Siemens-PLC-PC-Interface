# Lab 4.12 - Cable Cut-Length Cell help

Scene ID: `lab-4-12-cable-cut-length`  
Scene contract: `res://scenes/migrated/lab-4-12-cable-cut-length.scene.json`

## Purpose

One prethreaded cable feeds a measured 3 m length onto a receiving surface, cuts it and returns the blade home. The cut piece remains supported until Reset.

## Expected I/O to operate this scene

These are symbolic offline points, not hardware addresses. PC owns observed feedback and PLC owns commands and authorization. No physical PLC transport is used.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `cable_present` | `BOOL` | **PC** | `True` |
| `length_reached` | `BOOL` | **PC** | `False` |
| `cutter_home` | `BOOL` | **PC** | `True` |
| `cut_done` | `BOOL` | **PC** | `False` |
| `cut_complete` | `BOOL` | **PC** | `False` |
| `cut_fault` | `BOOL` | **PC** | `False` |
| `measured_length_m` | `REAL` | **PC** | `0.0` |
| `stock_remaining_m` | `REAL` | **PC** | `10.0` |
| `feed_speed_mps` | `REAL` | **PC** | `0.0` |
| `cutter_position` | `REAL` | **PC** | `0.0` |
| `batch_start` | `BOOL` | **PC** | `False` |
| `feed_run` | `BOOL` | **PLC** | `False` |
| `cutter_fire` | `BOOL` | **PLC** | `False` |
| `cycle_active` | `BOOL` | **PLC** | `False` |
| `cycle_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start / resume cable cut` | `pulse` | `batch_start` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `batch_start` | `switch_9` | `switch` |
| `feed_run` | `indicator_3` | `indicator` |
| `cutter_fire` | `indicator_12` | `indicator` |
| `measured_length_m` | `training_accessory_8` | `numericDisplay` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `training_accessory_4` | `trainingAccessory` | Constant-radius payoff reel |
| `training_accessory_5` | `trainingAccessory` | Passive cable guide rolls |
| `training_accessory_6` | `trainingAccessory` | Length encoder rolls |
| `machine_1` | `machine` | Powered feed rolls |
| `training_accessory_7` | `trainingAccessory` | Slotted-anvil guillotine cutter |
| `cable_receiver` | `trainingAccessory` | Supported receiving surface |
| `cable_strand` | `trainingAccessory` | Prethreaded cable and retained cut piece |
| `training_accessory_8` | `trainingAccessory` | Cable Cut-Length Cell - cut-length display |
| `switch_9` | `switch` | Start or resume one cable cut |
| `indicator_3` | `indicator` | Feed command |
| `indicator_12` | `indicator` | Cutter command |

## Running the reference

Open `programs/examples/cable-cut-reference.rpproj.json` through **File -> Open Ladder Agent Project**. Return to Scene, press Run, then Start / resume cable cut. Run alone stays at zero measured length.

Expect the readout to rise to **3.00 m**, feed to stop, the knife to lower through its anvil slot, and the knife to return home. The received piece is shifted 60 mm to reveal separation and stays supported on the anvil and receiving table. Available stock finishes at 7 m. Another Start does not recycle it.

Stop preserves length and knife pose; Run requires a fresh Start. Reset restores the initial prethreaded cable, 10 m available stock, zero measurement, home knife and stopped playback.

If it does not move, first verify the saved reference is loaded, Run is active and Start was pressed. For cut_fault, inspect simultaneous feed/cut, feed with knife away from home, or cut before length_reached. Reset clears the latched diagnostic.

## Stop and safety boundary

This finite offline model prescribes no-slip feed and constant-radius reel/roller motion. The guide rollers are passive. Available stock excludes the cable already threaded to the knife. Reel layering, dancer tension control, sag, elasticity, cutting force, collection and collision physics are excluded. A normal Stop clears commands and freezes motion; this is not a physical safety circuit or commissioning proof.

## Machine guide

### Start conditions

- One cable is prethreaded at the cutting plane; available stock is 10 m, excluding the already threaded route.
- Load the editable offline reference; no physical PLC is connected.

### Normal sequence

- Press Run, then Start.
- Encoder/reel rotations follow actual feed length at prescribed constant radii.
- At 3 m, feed stops; knife travels down then returns home. A 60 mm separation reveals the cut.

### Expected observations

- LENGTH m finishes at 3.00. stock_remaining_m finishes at 7.0.
- The piece stays supported on the receiver. No automatic recycling occurs.
- Prescribed no-slip feed and constant-radius reel/rollers; no tension, layering, cutting force, elasticity or collision solver.
