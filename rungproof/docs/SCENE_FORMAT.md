# Scene JSON format — prototype version 1

The preferred portable extension is `.plcscene`. It is UTF-8 JSON and uses:

```json
{
  "fileType": "plc-visual-scene",
  "version": 1
}
```

Legacy `.json` files remain loadable during this prototype.

## Design rule

A scene describes equipment and process behavior. It does **not** contain PLC
IP addresses, DB offsets, `%I`/`%Q` addresses, rack/slot settings, or write
authorization.

PLC bindings belong in a separate validated interface file and must be handled
by the guarded transport/runtime. A scene may optionally name one read-only
test profile with `plcTestProfile`, but that value is only a local JSON filename
reference. Paths and embedded connection parameters are rejected.

## Top-level shape

```json
{
  "version": 1,
  "id": "example-scene",
  "plcTestProfile": "scene-1-db14-interface.json",
  "name": "Example Scene",
  "description": "What the operator should observe.",
  "camera": {
    "position": [9, 7, 9],
    "target": [0, 1, 0],
    "fov": 45
  },
  "equipment": [],
  "simulation": {
    "type": "static"
  }
}
```

Required fields:

| Field | Meaning |
|---|---|
| `version` | Must be `1` for this prototype |
| `id` | Stable non-empty scene identifier |
| `name` | Operator-visible scene name |
| `equipment` | Non-empty list of equipment definitions |

Optional `plcTestProfile` rules:

- it must be one local `.json` filename, such as
  `scene-1-db14-interface.json`;
- it may not contain a directory path or traversal such as `../`;
- Test PLC automatically loads only that exact validated profile;
- no profile reference means the read-only test is unavailable for that scene;
- connection settings and DB tag addresses remain in the external profile.

Supported `simulation.type` values:

- `conveyor`
- `conveyorStop`
- `conveyorPusher`
- `tank`
- `gallery`
- `booleanPanel`
- `sequence`
- `static`

## Simulation point contract

Every non-`static` simulation must declare every runtime-visible point in
`simulation.points`. The player rejects missing, duplicate, mistyped, or
invalid point declarations before constructing the runtime.

```json
{
  "simulation": {
    "type": "conveyorStop",
    "points": [
      {
        "name": "conveyor_running",
        "type": "BOOL",
        "owner": "PLC",
        "initial": false,
        "role": "output",
        "purpose": "PLC motor command that runs the conveyor."
      },
      {
        "name": "simulated_photoeye",
        "type": "BOOL",
        "owner": "PC",
        "initial": false,
        "purpose": "Simulator photoeye feedback read by the PLC."
      },
      {
        "name": "object_position",
        "type": "REAL",
        "owner": "SIM",
        "initial": 0,
        "unit": "m"
      }
    ]
  }
}
```

Point rules:

- `name` is unique, case-sensitive, and is the exact symbolic interface name.
- `type` is `BOOL`, `DINT`, `REAL`, or `STRING`.
- `owner: "PLC"` means a PLC-produced command consumed by the simulator.
- `owner: "PC"` means simulator-produced feedback read by the PLC.
- `owner: "SIM"` is internal diagnostics and is not an external PLC tag.
- `initial` is required and must match the declared data type.
- `unit`, `role`, and `purpose` are optional descriptive metadata.
- PLC points with `role: "memory"` and all `SIM` points are shown as internal,
  not as external Configuration rows.

Custom runtimes provide only current values. Tag name, type, owner, and unit are
projected from this declaration so runtime metadata cannot silently disagree
with the Configuration popup.

## Equipment definition

```json
{
  "id": "tank_1",
  "type": "tank",
  "label": "Process tank T-101",
  "position": [0, 0, 0],
  "rotation": [0, 0, 0],
  "scale": [1, 1, 1],
  "config": {
    "height": 5,
    "diameter": 3,
    "initialLevel": 0.42
  }
}
```

- `position` is `[x, y, z]` in scene meters.
- `rotation` is degrees around `[x, y, z]`.
- `scale` is a dimensionless multiplier.
- `config` is asset-type-specific.
- Equipment IDs must be unique inside a scene.

Supported equipment types:

| Type | Important configuration |
|---|---|
| `motor` | `length`, `diameter`, `color`, `running` |
| `conveyor` | `length`, `width`, `deckHeight`, `beltColor` |
| `box` | `size: [x,y,z]`, `color` |
| `photoeye` | `span`, `height`, `blocked` |
| `switch` | `style: pushbutton/emergency`, `active`, `action` |
| `indicator` | `colors`, `active` |
| `pump` | `color`, `running` |
| `fan` | `diameter`, `centerHeight`, `bladeCount`, `bladeColor`, `running` |
| `pusher` | `stroke`, `centerHeight`, `initialPosition` |
| `tank` | `height`, `diameter`, `initialLevel`, `fluidColor` |
| `levelSensor` | `sensorType`, `threshold`, `mode`, `range` |
| `radarLevelSensor` | `initialLevel`, `mountSpan`, `beamRadius`, `range`, `engineeringRange` |
| `pipe` | `length`, `diameter`, `axis`, `color` |
| `rotarySwitch` | `positionCount`, `initialPosition`, `minimumAngleDeg`, `maximumAngleDeg`, `action` |
| `liftTable` | `width`, `depth`, `minimumHeight`, `travel`, `initialPosition` |
| `valve` | `initialPosition` |
| `drillPress` | `travel`, `initialPosition`, `running`, `color` |
| `robotArm` | `initialPosition`, `running` |
| `rollerShutter` | `width`, `height`, `initialPosition` |
| `rotaryTable` | `radius`, `angleRangeDeg`, `initialPosition` |
| `machine` | `size`, `color`, `running` |

Switch `action` values used by the built-in scenes:

| Action | Behavior |
|---|---|
| `conveyor_run` | Toggle the conveyor scene run state |
| `toggle-pump` | Toggle the tank inlet-pump command |
| `toggle-drain` | Toggle the tank drain-valve command |
| `toggle-gallery` | Start or stop the gallery's animated equipment |
| `stop-all` | Latch/reset the gallery emergency stop |

The visible button cap and its faceplate are both hit targets. Clicking the
pedestal outside the faceplate only selects the equipment for inspection.

Colors are Three.js hexadecimal color values represented as JSON numbers.

## Conveyor simulation

```json
{
  "type": "conveyor",
  "conveyorId": "main_conveyor",
  "photoeyeId": "inspection_photoeye",
  "indicatorId": "cell_stacklight",
  "productIds": ["carton_1", "carton_2"],
  "speedMps": 1.05,
  "spacingM": 2.6
}
```

All referenced IDs must exist and match the expected equipment type.

## Prior Scene 1 simulation

`conveyorStop` uses one conveyor, one product, one photoeye, and one indicator.
Its established physical fields are `lengthM`, `speedMps`, `objectLengthM`,
`photoeyePositionM`, and `minimumPhotoeyeOnS`.

## Prior Scene 2 simulation

`conveyorPusher` adds `pusherId`, `pusherStrokeTimeS`,
`transferPositionFraction`, and `repeatLoadSeconds`. The offline player mirrors
the established ladder sequence: set extend at part/retracted, reset at the
extended limit, and run only while retracted, clear, and not extending.

## Tank simulation

```json
{
  "type": "tank",
  "tankId": "process_tank",
  "pumpId": "inlet_pump",
  "lowSensorId": "low_level_switch",
  "highSensorId": "high_level_switch",
  "transmitterId": "level_transmitter",
  "indicatorId": "tank_stacklight",
  "initialLevel": 0.42,
  "inletRatePerSecond": 0.07,
  "outletRatePerSecond": 0.045,
  "lowThreshold": 0.2,
  "highThreshold": 0.8
}
```

The prototype uses ideal normalized level:

```text
level_percent = level_fraction * 100
transmitter_mA = 4 + (16 * level_fraction)
```

This is a visualization proof. A production point binding must separately
define raw analog counts, engineering units, clamping/fault policy, ownership,
and safe behavior.

`lowSensorId`, `highSensorId`, and `transmitterId` are optional so a scene can
represent discrete-only, analog-only, radar-only, or combined instrumentation.
When `transmitterId` references a `radarLevelSensor`, the player also projects:

```text
radar_level_percent = level_fraction * 100
radar_distance_m = modeled_horn_elevation - modeled_fluid_surface_elevation
radar_mA = 4 + (16 * level_fraction)
radar_echo_ok = true
```

The echo flag is fixed true in this proof. It must not be treated as a real
instrument diagnostic.

## Boolean-panel training simulation

`booleanPanel` describes small selector, pushbutton, latch, lamp, fan, and
annunciator exercises without embedding executable expressions. It contains:

- typed symbolic `points` with explicit owner and initial value;
- validated input `actions` limited to `toggle`, `set`, `pulse`, and `cycle`;
- exact-match `rules`; every matching rule is applied in declaration order;
- optional rising-edge `edgeRules` for reference-controller latch/toggle memory;
- `pointBindings` that project point state onto reusable switches, selectors,
  indicators, running equipment, or normalized-position assets.

In Godot Next, numeric binding mode `speedPercent` scales an equipment motion
controller's authored rotational speed by a clamped 0..100%. Pair it with a
separate BOOL `running` binding; a speed value never starts stopped equipment.
Assets without this optional binding retain their nominal animation speed.
Godot Next also supports BOOL `indicatorChannel` bindings with an explicit
`activeColor` (red, amber, green, blue or white). This mode changes only lenses
named for that color, preserving the other channels. Provide a binding for
each installed tier so its false state is projected too. Multiple true outputs
remain visibly lit together; the renderer does not enforce sequence exclusivity.
Use the existing `indicator` mode for an exclusive status-color selector.
The standalone boolean-panel reference preview's Stop suppresses reference
rules and returns outputs to their declared initial values while retaining PC
inputs. Run resumes rule evaluation; Reset restores the scene. A selected
virtual/external controller continues to own its output image and playback gate.
These are symbolic animation/reference contracts, not physical drive commands.

Operator actions may not target a PLC-owned point. Fake PLC rules may write
only declared non-PC points. `pulse` holds a PC-owned BOOL input true for at
least 150 ms so a future live adapter can sample it; a second operation
generates a new release/rising edge. Scene files cannot call JavaScript or
address PLC memory.

The runtime control source defaults to `disconnected`. In that state,
PLC-owned values are forced to type-appropriate safe values even when their
reference-controller initial value is nonzero or true. `fake-plc` must be
explicitly enabled before rules, edge rules, or reference sequences produce
PLC outputs. The reserved `live-plc` state has no working player adapter yet.

## Declarative sequence training simulation

`sequence` contains named, timed step lists for offline machine-cycle
visualization. Each step can:

- assign declared symbolic points;
- move an equipment instance along one transform axis;
- rotate an equipment instance;
- command a normalized actuator position;
- animate a tank level or equipment visibility.

Actions are limited to starting a named sequence, stopping, resetting, or
changing a declared point. A start action may declare required point values.
`safeState` removes motion commands when the player is stopped.

Reaching the final step of a non-repeating sequence is a normal program
completion and enters `SYSTEM STOP`. A step can request the same behavior
before the final step:

```json
{
  "name": "fault detected",
  "durationS": 0.1,
  "systemStop": true,
  "stopMessage": "System stop — guard input opened",
  "stopState": {
    "guard_fault": true
  }
}
```

- `systemStop: true` ends the active sequence at that step.
- `stopMessage` is the operator-facing reason.
- `safeState` is applied first so PLC-owned motion outputs turn off.
- `stopState` is then applied for non-motion state that must remain visible,
  such as a detected fault or limit condition.

The player **Loop scene** option is runtime state, not scene logic. It performs
Reset then Start only after `SYSTEM STOP`, and the new Start must pass the same
controller and process permissives as a manual Start. It does not restart
`OPERATOR STOP` or `INTERLOCK STOP`.

## Declarative scene alarm rules

Every loaded scene has a Faults & Alarms popup even when it declares no custom
rules. The runtime automatically reports unplanned system stops, blocked Start
requests, and interlock stops. A scene may additionally map a symbolic point to
an alarm condition:

```json
{
  "alarmRules": [
    {
      "id": "MOTOR_OVERLOAD",
      "severity": "fault",
      "point": "motor_overload",
      "operator": "isTrue",
      "message": "Motor overload relay is tripped",
      "check": "Check the overload relay and motor current."
    },
    {
      "id": "LEVEL_HIGH",
      "severity": "warning",
      "point": "level_percent",
      "operator": "gte",
      "value": 90,
      "message": "Tank level is above 90 percent",
      "check": "Check the inlet command and high-level device."
    }
  ]
}
```

Supported severities are `warning`, `alarm`, and `fault`. Supported operators
are `isTrue`, `isFalse`, `eq`, `neq`, `gt`, `gte`, `lt`, and `lte`. Numeric
comparison operators require a finite numeric `value`.

Alarm acknowledgement and history are player-runtime state. Acknowledgement
does not clear the underlying scene condition and cannot write to or
acknowledge a real PLC.

This is a deterministic visualization model, not safety-rated logic, a
real-time controller, or permission to operate equipment.

## Embedded acceptance cases

Training scenes may include a top-level `verification.cases` list. These cases
are ignored by the player and consumed by
`tools/verify_training_scenes.mjs`. Each case starts from a fresh runtime,
explicitly enables Fake PLC, applies declared actions and simulated time, and
compares the resulting symbolic tags with exact expected values. The separate
`tools/test_control_ownership.mjs` suite leaves Fake PLC disabled and verifies
that all lab PLC-owned points remain safe under every operator action.

## Reusable catalog direction

### Chain lift scene plant (Godot migrated scene)

`lab-4-09-chain-drive-lift` uses the following scene-local equipment config
selectors. These create installation geometry without registering substitute
catalog assets or modifying shared deliveries:

| Equipment type | `config.installation` | Result |
| --- | --- | --- |
| `conveyor` | `chainLiftFeed` | Delivered two-strand chain conveyor with demonstration pallet removed and a commanded upper-run animation |
| `liftTable` | `guidedChainLift` | Guided vertical chain lift with a 2.1 m stroke in 4 s |
| `sceneInstallation` | `chainLiftFeedBridge` | Fixed lower transfer plate and supports |
| `sceneInstallation` | `chainLiftOutfeedBridge` | Fixed upper receiving plate and supports |
| `sceneInstallation` | `chainLiftLimits` | Two guide-mounted endpoint switches |
| `sceneInstallation` | `chainLiftStop` | Floor-mounted upper receiving end stop |

An unknown `sceneInstallation` selector fails composition. The opt-in simulation
entry `chainLiftPlant: { "model": "single-carton-guided-lift-v1" }` selects the
scene-local single-carton plant. Unknown plant models fail initialization.
It requires this scene's fixed equipment IDs (`liftTable_1`, `box_2`,
`conveyor_0`, `receiving_conveyor`) and authored installation dimensions. Moving
or resizing them requires corresponding model and audit changes; this is not
a generic scene-builder actuator or collision-physics implementation.

The plant alone integrates horizontal travel, lift height, carrying attachment
and discharge. Independent carriage, chain and belt callbacks are disabled.
PLC-owned BOOLs `chain_run`, `lift_enable` and `lift_lower` request horizontal,
up and down travel. The same actual displacement projects onto carton pose,
lift chains, carriage belt and receiving belt. Position and footprint feedback
is PC-owned: `box_present`, `lift_home`, `destination_clear`,
`carton_on_infeed`, `carton_on_lift`, `lift_upper`, `carton_at_receiver`,
`receiver_occupied`, `receiver_beam_blocked`, `transfer_fault`. Entry photoeye
feedback clears after the carton passes; receiver zone occupancy remains true
for the parked carton. The runtime validates these types and
owners. The momentary `lift_start` remains PC-owned; `cycle_active` and
`cycle_complete` are PLC-owned outputs of the selected ladder program.

Opposing directions, simultaneous horizontal/vertical drive, a straddling
carton during lift motion or transfer across an absent endpoint latch a plant
diagnostic and hold position until global Reset. The raw PLC command image is
preserved for diagnosis. No falling-load, slip, inertia or flexible-chain
physics is modeled. Reset restores the original infeed carton, home lift,
feedback, fault state and exact drive phases. External paused playback freezes
the plant without rewriting PLC commands. Offline Stop removes controller
authorization; the supplied reference requires a fresh Start to resume any leg.

`--visual-scene-review` exposes Hold offline plant clock and Step 2.0 s for
this scene's offline operator view. A step executes 100 actual 20 ms controller
scans through the ordinary input/ladder/output/plant path. Camera changes do
not advance a held plant. Editor, source and scene transitions release the
hold. This control is excluded in external PLC mode and is not a general
simulation-clock facility. DB14 and catalog asset deliveries are unchanged.

### Cookie packaging scene plant (Godot migrated scene)

`lab-4-10-cookie-packaging` opts in with
`cookiePackagingPlant: { "model": "six-cookie-index-seal-v1" }`.
Unknown models fail initialization. Scene-local config selectors are
`machine` / `cookieSealer`, `trainingAccessory` / `cookieTray` and
`trainingAccessory` / `cookieCounter`; shared deliveries remain unchanged.
Fixed IDs are `conveyor_0`, `machine_1`, `cookie_0` through `cookie_5`,
`photoeye_2`, `cookie_counter` and `package_counter`. Authored dimensions and
positions must match the model; installation edits need corresponding model
and audit changes. This is not a generic scene-builder actuator.

One plant integrates belt displacement and head travel; independent belt
physics is disabled. Validated PC-owned BOOL feedback is `product_present`,
`packaging_ready`, `packaging_busy`, `batch_complete`, `count_beam_blocked`
and `packaging_fault`; PC-owned INTs are `cookie_count` and `wrapped_count`.
Validated PLC-owned BOOL commands are `infeed_run` and `packaging_enable`.
`batch_start` is a PC pulse; `cycle_active` and `cycle_complete` belong to
selected ladder. Counts arise from biscuit leading-edge crossings and complete
jaw cycles. Visible packages project from that same plant state. Mechanical
indexing at the next unwrapped tray is assumed; all six remain at completion.

Feed during sealing/busy latches a diagnostic and holds until Reset, preserving
raw PLC commands. External pause preserves commands and poses. Offline Stop
clears reference authorization; Run alone holds; fresh Start resumes. Reset
restores initial trays/head, counts, fault and belt phases.
`--audit-cookie-packaging` verifies the reference and installation. Offline
review Hold/Step executes 100 actual 20 ms scans per 2 s step. Heat, film
mechanics, slip, replenishment and collision dynamics are excluded. Bounds and
snapshots are not physical process acceptance.

Scene equipment instances already reference stable type IDs and type-specific
configuration. A future scene builder should use the same definitions as its
equipment palette and emit this same versioned JSON. The builder must validate
IDs, transforms, configuration, and symbolic behavior references before the
player accepts the file.

## Loading a scene

Use the scene library selector or click **Load**. Validation occurs before the
current 3D equipment is replaced. If validation fails, the player displays the
error and does not attempt any PLC operation.

## Barrel filling plant opt-in

Scene 52 declares `barrelFillPlant: { "model": "single-barrel-metered-fill-v1" }`.
It owns a fixed single-barrel route: X=-2.8 to indexed X=0 to retained X=3,
belt top Y=0.9, inner barrel radius 0.28 m and 200 L source. A prescribed
20 L/s transfers a 150 L batch. This is an offline exercise with mechanical
indexing, not a hydraulic solver. No replenishment or recycling occurs.

The model requires PC-owned BOOL `barrel_at_fill`, `fill_complete`,
`downstream_clear`, `barrel_parked`, `fill_beam_blocked`, `exit_beam_blocked`,
`fill_fault`; PC-owned REAL `barrel_litres`, `source_litres`, `flow_lps`; and
PLC-owned BOOL `infeed_run`, `fill_valve_open`. Feedback follows the rendered
plant. Commands are not rewritten by the plant. Fill away from the station
or with feed active latches a diagnostic fault without changing inventory.

Scene-local selectors are `barrelSupply` (tank), `barrelValve` (valve), and
`barrelLoad`, `barrelMeter`, `barrelNozzle` (training accessory). Fixed runtime
IDs are `conveyor_0`, `tank_1`, `valve_2`, `training_accessory_5`,
`training_accessory_6` and `training_accessory_7`; geometry, IDs and constants
must change together. Shared delivered assets are unaffected. All belt/load/
liquid/stream projections use one clock. Stop preserves plant state and
requires a fresh Start after Run. The reference retains discharge intent
across Stop so the same barrel may finish parking through its occupied exit
sensor; feed is still gated by active cycle authorization. Reset clears intent
and restores the initial inventory.

## Numeric display formatting

A `numericDisplay` binding may specify `format`: `G` (default, preserving
existing displays), `F0`, `F1`, `F2`, or `F3`. Other values are rejected.
Formatting uses invariant culture and changes displayed text only, not point
values or calculations. Scene 52 binds `barrel_litres` with `format: "F1"`
so fractional readings fit the meter. Decimal display precision does not
establish physical measurement accuracy.
