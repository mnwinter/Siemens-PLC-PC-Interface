# Lab 4.9 - Chain-Drive Lift help

Scene ID: `lab-4-09-chain-drive-lift`  
Migrated source: `prototype/scenes/lab-4-09-chain-drive-lift.plcscene`  
Scene contract: `res://scenes/migrated/lab-4-09-chain-drive-lift.scene.json`

## Current installation

A two-strand chain infeed meets the lower bridge at **0.9675 m**. A guided
chain-driven platform raises its staged carton **2.1 m** to the upper bridge
and receiving belt at **3.0675 m**. Two carriage crossmembers support the deck.
Lower and upper limit-switch bodies are mounted on a fixed guide post; the
moving guide shoe contacts their rollers at the endpoints. A floor-mounted
stop stands beyond the upper receiver. The old milling-machine, duplicate
scissor-table, E-stop-as-mechanical-stop and separate pallet/load props are
removed from this scene. Shared catalog packages remain unchanged.

This checkpoint verifies installation and commanded drive motion. **Continuous
carton feeding, discharge, return travel and automatic feedback remain open.**
The carton starts on the lift and follows its carriage; it does not yet travel
from the infeed onto the receiving conveyor. The receiving belt remains static.
The infeed animation shows its upper chain run, not a complete flexible-chain
physics model. Reset restores home; command loss holds the current lift height.

## Expected I/O to operate this scene

These points have no hardware addresses. The three legacy feedback points are
**manual test inputs**, identified by the operator plates. They are not driven
by the installed limit switches or carton position in this checkpoint. For
example, `lift_home=True` can remain manually asserted with the platform raised.
Do not treat these toggles as verified automatic sensing.

| Point | Type | Owner | Initial |
| --- | --- | --- | --- |
| `box_present` | `BOOL` | **PC** | `False` |
| `lift_home` | `BOOL` | **PC** | `False` |
| `destination_clear` | `BOOL` | **PC** | `False` |
| `lift_start` | `BOOL` | **PC** | `False` |
| `chain_run` | `BOOL` | **PLC** | `False` |
| `lift_enable` | `BOOL` | **PLC** | `False` |

`chain_run` drives the infeed chain adapter and its status tower. `lift_enable`
drives the vertical carriage, its chain/sprockets and its status tower. False
commands freeze the drive poses. The scene projects the PLC command image;
it does not manufacture permissives or automatically interlock raw commands.

## Operator actions and bindings

| Action | Type | Point | Equipment/mode |
| --- | --- | --- | --- |
| Toggle box present | toggle | `box_present` | `switch_8` / switch |
| Toggle lift home | toggle | `lift_home` | `switch_9` / switch |
| Toggle destination clear | toggle | `destination_clear` | `switch_10` / switch |
| Start lift installation (momentary) | pulse | `lift_start` | `lift_start_station` / switch |

Legacy toggle action IDs are retained. The new Start action ID is
`start-lift-installation`; its pulse is consumed by an offline controller scan.
Additional output bindings are `chain_run -> conveyor_0 / running` and
`lift_enable -> liftTable_1 / running`; both existing green indicator bindings
are retained. An old two-output program still binds, but may restart immediately
if its logic remains true. The optional reference supplies a fresh-Start seal.

## Expected equipment

| ID | Type | Installed purpose |
| --- | --- | --- |
| `conveyor_0` | conveyor | Two-strand chain infeed |
| `liftTable_1` | liftTable | Guided vertical chain lift (scene opt-in) |
| `box_2` | box | Carton staged on the lift platform |
| `indicator_3` | indicator | Chain run status |
| `training_accessory_4` | sceneInstallation | Lower transfer bridge |
| `training_accessory_5` | sceneInstallation | Upper receiving bridge |
| `training_accessory_6` | sceneInstallation | Mounted limit-switch pair |
| `training_accessory_7` | sceneInstallation | Floor-mounted receiver stop |
| `switch_8` | switch | BOX PRESENT manual input |
| `switch_9` | switch | HOME manual input |
| `switch_10` | switch | DEST CLEAR manual input |
| `indicator_11` | indicator | Lift enable status |
| `receiving_conveyor` | conveyor | Upper receiving belt |
| `lift_start_station` | switch | Momentary START |

The four sceneInstallation objects are composed scene props; they do not claim
an unrelated reusable catalog delivery as their source.

## Run the installation reference

1. In Built-in Simulator mode, select this scene and open
   `programs/examples/chain-lift-installation-reference.rpproj.json` through
   **File -> Open Ladder Agent Project...**.
2. Return to the scene and press bottom **Run**. Both commands remain false.
   Start with a missing manual permissive is rejected.
3. Set all three manual feedback toggles true. Restoring inputs alone does not
   reuse an earlier Start. Press the separate **Start lift installation**.
4. Both green status lamps light, the infeed chain moves, and the supported
   carton/platform rise to the upper carrying height. Travel is four seconds
   in this illustrative installation; no physical drive rating is implied.
5. Bottom **Stop** clears both commands and holds position. **Run** alone cannot
   resume. A fresh Start reasserts commands at the held height. Losing a manual
   permissive clears the seal; recovery also needs a fresh Start.
6. Bottom **Reset** restores the lower platform/carton/chain poses, clears all
   manual points and commands, and stops scans.

The default template remains an exercise. If nothing moves, first check that
the saved reference is loaded, scans are increasing, all three manual inputs
are true, and a fresh Start was pressed. If lamps light without carriage motion,
check the `running` binding and the `ChainLiftMotion` adapter.

## Verification boundary

`--audit-chain-lift-installation` checks the saved reference, actual symbolic
controller scans, command projection, Stop/Run/Reset, deck and carton support,
limit mounting/contact and 211 sampled positions over the full lift stroke.
The clearance screen excludes fixed guide posts, chain links and the limit
assembly's intended contacts. Native camera views provide separate visual evidence. Neither proves
complete chain mechanics, continuous swept-volume clearance, physical safety,
automatic sensing, wiring, a live PLC or complete carton-transfer behavior.
DB14 remains unchanged.
