import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sceneDirectory = path.join(projectRoot, "prototype", "scenes");
const catalogPath = path.join(projectRoot, "docs", "TRAINING_SCENE_CATALOG.md");

const COMMON_FOUNDATION_TAGS = Object.freeze([
  "PC_Heartbeat",
  "PLC_Heartbeat_Echo",
  "Simulation_Enable",
  "Simulation_Comm_OK",
  "Simulation_Timeout",
]);

const colors = Object.freeze({
  green: 0x21a366,
  red: 0xe03c31,
  amber: 0xf2a900,
  blue: 0x2e8bd1,
  white: 0xe9f2f5,
  cyan: 0x38bdf8,
  carton: 0xc88a4b,
  dark: 0x273238,
  steel: 0x5e6b73,
  yellow: 0xf2b705,
});

function camera(position = [10, 7, 10], target = [0, 1.2, 0], fov = 43) {
  return { position, target, fov };
}

function pushbutton(id, label, position, action, color = colors.green) {
  return {
    id,
    type: "switch",
    label,
    position,
    config: { style: "pushbutton", action, color },
  };
}

function selector(id, label, position, action, positionCount, initialPosition = 0) {
  return {
    id,
    type: "rotarySwitch",
    label,
    position,
    config: { action, positionCount, initialPosition },
  };
}

function lamp(id, label, position, color = "green", active = null) {
  return {
    id,
    type: "indicator",
    label,
    position,
    config: { colors: [color], active },
  };
}

function stacklight(id, label, position, active = "amber") {
  return {
    id,
    type: "indicator",
    label,
    position,
    config: { colors: ["red", "amber", "green"], active },
  };
}

function conveyor(
  id,
  label,
  position = [0, 0, 0],
  length = 7,
  width = 1.5,
) {
  return {
    id,
    type: "conveyor",
    label,
    position,
    config: {
      length,
      width,
      deckHeight: 0.9,
      beltColor: colors.dark,
      running: false,
    },
  };
}

function product(id, label, position, size = [0.85, 0.72, 0.72], color = colors.carton) {
  return { id, type: "box", label, position, config: { size, color } };
}

function photoeye(id, label, position, blocked = false) {
  return {
    id,
    type: "photoeye",
    label,
    position,
    config: { span: 2.05, height: 0.7, beamCenterHeightM: 1.1, blocked },
  };
}

function machine(id, label, position, size = [2.1, 2.7, 1.7], color = 0x536873) {
  return {
    id,
    type: "machine",
    label,
    position,
    config: { size, color, running: false },
  };
}

function scene(number, slug, name, description, equipment, simulation, verification, catalog) {
  return {
    fileName: `lab-2-${number}-${slug}.plcscene`,
    catalog: {
      exercise: `2.${Number(number)}`,
      name,
      description,
      ...catalog,
    },
    document: {
      fileType: "plc-visual-scene",
      version: 1,
      id: `lab-2-${number}-${slug}`,
      name: `Lab 2.${Number(number)} - ${name}`,
      description,
      camera: catalog.camera ?? camera(),
      equipment,
      simulation,
      training: {
        ...buildTrainingGuide(simulation, { description, ...catalog }),
        machineGuide: buildMachineGuide(simulation, { description, ...catalog }),
      },
      verification,
    },
  };
}

function booleanSimulation(
  points,
  actions,
  rules,
  pointBindings,
  edgeRules = [],
) {
  return {
    type: "booleanPanel",
    points,
    actions,
    rules,
    edgeRules,
    pointBindings,
  };
}

function sequenceSimulation({
  points,
  actions,
  pointBindings,
  sequences,
  defaultSequence,
  safeState = {},
  completionState = {},
  conveyorSpeedMps = 0.75,
}) {
  return {
    type: "sequence",
    points,
    actions,
    pointBindings,
    sequences,
    defaultSequence,
    safeState,
    completionState,
    conveyorSpeedMps,
  };
}

function formatConditionEntries(values = {}) {
  const entries = Object.entries(values);
  return entries.length
    ? entries
        .map(([name, value]) => `${name} = ${JSON.stringify(value)}`)
        .join(", ")
    : "the step is active";
}

function buildReferenceSteps(simulation) {
  if (simulation.type === "booleanPanel") {
    const ruleSteps = (simulation.rules ?? []).map(
      (rule) =>
        `When ${formatConditionEntries(rule.when)}, set ${formatConditionEntries(rule.set)}.`,
    );
    const edgeSteps = (simulation.edgeRules ?? []).map((rule) => {
      const changes = [];
      if (rule.set) {
        changes.push(`set ${formatConditionEntries(rule.set)}`);
      }
      if (Array.isArray(rule.toggle) && rule.toggle.length > 0) {
        changes.push(`toggle ${rule.toggle.join(", ")}`);
      }
      return `On the rising edge of ${rule.rising}, ${changes.join(" and ")}.`;
    });
    return [...edgeSteps, ...ruleSteps];
  }

  if (simulation.type === "sequence") {
    const pointsByName = new Map(
      (simulation.points ?? []).map((point) => [point.name, point]),
    );
    const steps =
      simulation.sequences?.[simulation.defaultSequence] ?? [];
    return steps.map((step) => {
      const commandChanges = Object.fromEntries(
        Object.entries(step.set ?? {}).filter(
          ([name]) => pointsByName.get(name)?.owner === "PLC",
        ),
      );
      const changes = Object.keys(commandChanges).length
        ? formatConditionEntries(commandChanges)
        : "no PLC command changes";
      return `${step.name}: ${changes}.`;
    });
  }

  return [];
}

function buildTrainingGuide(simulation, catalog) {
  const inputNames = catalog.inputs || "the simulator inputs";
  const outputNames = catalog.outputs || "the PLC outputs";
  const sequenceNames =
    simulation.type === "sequence"
      ? (
          simulation.sequences?.[simulation.defaultSequence] ?? []
        ).map((step) => step.name)
      : [];

  return {
    hints: [
      `Define the required result before writing logic: ${catalog.acceptance}`,
      `Treat ${inputNames} as simulator-to-PLC inputs. The PLC should command only ${outputNames}.`,
      simulation.type === "sequence"
        ? `Use a step/state approach and prove the transition order: ${sequenceNames.join(" → ")}.`
        : "List the required input and memory states before assigning any output. Test every state, including the all-false state.",
    ],
    solution: {
      summary:
        "This is one valid functional reference. The same behavior may be implemented in LAD, FBD, or SCL; the rung layout is not prescribed.",
      steps: buildReferenceSteps(simulation),
      acceptance: catalog.acceptance,
    },
  };
}

function buildMachineGuide(simulation, catalog) {
  const inputs = catalog.inputs || "the declared simulator inputs";
  const outputs = catalog.outputs || "the declared PLC outputs";
  const sequence =
    simulation.type === "sequence"
      ? (simulation.sequences?.[simulation.defaultSequence] ?? []).map(
          (step) => step.name,
        )
      : [
          "Observe the initial input state.",
          `Apply ${inputs}.`,
          `Verify the PLC produces only the required ${outputs}.`,
        ];
  return {
    purpose: catalog.description,
    startConditions: [
      "The common PLC/watchdog foundation is healthy.",
      "All required simulator inputs are at their documented initial state.",
      `The PLC is ready to command ${outputs}.`,
    ],
    normalSequence: sequence,
    stopBehavior: [
      "A normal stop removes PLC-owned commands and leaves the equipment in a safe state.",
      "Reset returns the scene to its documented initial condition.",
    ],
    faultBehavior: [
      "A missing, stale, or incorrectly typed input must not be replaced by simulator logic.",
      "A missing PLC command leaves the affected equipment stopped and the test diagnosable.",
    ],
    expectedObservations: [catalog.acceptance],
  };
}

const scenes = [
  scene(
    "01",
    "workstation-call",
    "Workstation Call Lamp",
    "A workstation call button directly controls a blue material-request lamp while the button is held.",
    [
      pushbutton(
        "material_call_button",
        "Material call button",
        [-1.6, 0, 0],
        "toggle-material-call",
        colors.blue,
      ),
      lamp(
        "material_call_lamp",
        "Material request lamp",
        [0.8, 0, 0],
        "blue",
      ),
    ],
    booleanSimulation(
      [
        {
          name: "material_call_pressed",
          type: "BOOL",
          owner: "PC",
          initial: false,
        },
        {
          name: "material_call_on",
          type: "BOOL",
          owner: "PLC",
          initial: false,
          role: "output",
        },
      ],
      [
        {
          id: "toggle-material-call",
          label: "Press / release material call",
          type: "toggle",
          point: "material_call_pressed",
        },
      ],
      [
        {
          when: { material_call_pressed: false },
          set: { material_call_on: false },
        },
        {
          when: { material_call_pressed: true },
          set: { material_call_on: true },
        },
      ],
      [
        {
          point: "material_call_pressed",
          equipmentId: "material_call_button",
          mode: "switch",
        },
        {
          point: "material_call_on",
          equipmentId: "material_call_lamp",
          mode: "indicator",
          activeColor: "blue",
        },
      ],
    ),
    {
      cases: [
        {
          name: "released",
          expect: {
            material_call_pressed: false,
            material_call_on: false,
          },
        },
        {
          name: "pressed",
          actions: ["toggle-material-call"],
          expect: {
            material_call_pressed: true,
            material_call_on: true,
          },
        },
      ],
    },
    {
      sourcePattern: "One normally-open input directly controls one lamp",
      changes:
        "Material-request use case, blue LED load, new symbols, and an original workstation layout.",
      inputs: "material_call_pressed",
      outputs: "material_call_on",
      acceptance:
        "The call lamp follows the button state: off when released and on when pressed.",
    },
  ),
  scene(
    "02",
    "dual-confirmation",
    "Dual Confirmation Lamp",
    "A handoff-ready lamp turns on only after both the operator and quality confirmation buttons are active.",
    [
      pushbutton(
        "operator_confirm_button",
        "Operator confirmation",
        [-1.8, 0, -0.7],
        "toggle-operator-confirm",
        colors.green,
      ),
      pushbutton(
        "quality_confirm_button",
        "Quality confirmation",
        [-1.8, 0, 0.7],
        "toggle-quality-confirm",
        colors.blue,
      ),
      lamp(
        "handoff_ready_lamp",
        "Handoff ready lamp",
        [0.8, 0, 0],
        "green",
      ),
    ],
    booleanSimulation(
      [
        {
          name: "operator_confirmed",
          type: "BOOL",
          owner: "PC",
          initial: false,
        },
        {
          name: "quality_confirmed",
          type: "BOOL",
          owner: "PC",
          initial: false,
        },
        {
          name: "handoff_ready",
          type: "BOOL",
          owner: "PLC",
          initial: false,
          role: "output",
        },
      ],
      [
        {
          id: "toggle-operator-confirm",
          label: "Press / release operator confirm",
          type: "toggle",
          point: "operator_confirmed",
        },
        {
          id: "toggle-quality-confirm",
          label: "Press / release quality confirm",
          type: "toggle",
          point: "quality_confirmed",
        },
      ],
      [
        {
          when: { operator_confirmed: false, quality_confirmed: false },
          set: { handoff_ready: false },
        },
        {
          when: { operator_confirmed: true, quality_confirmed: false },
          set: { handoff_ready: false },
        },
        {
          when: { operator_confirmed: false, quality_confirmed: true },
          set: { handoff_ready: false },
        },
        {
          when: { operator_confirmed: true, quality_confirmed: true },
          set: { handoff_ready: true },
        },
      ],
      [
        {
          point: "operator_confirmed",
          equipmentId: "operator_confirm_button",
          mode: "switch",
        },
        {
          point: "quality_confirmed",
          equipmentId: "quality_confirm_button",
          mode: "switch",
        },
        {
          point: "handoff_ready",
          equipmentId: "handoff_ready_lamp",
          mode: "indicator",
          activeColor: "green",
        },
      ],
    ),
    {
      cases: [
        {
          name: "neither-confirmed",
          expect: {
            operator_confirmed: false,
            quality_confirmed: false,
            handoff_ready: false,
          },
        },
        {
          name: "operator-only",
          actions: ["toggle-operator-confirm"],
          expect: {
            operator_confirmed: true,
            quality_confirmed: false,
            handoff_ready: false,
          },
        },
        {
          name: "quality-only",
          actions: ["toggle-quality-confirm"],
          expect: {
            operator_confirmed: false,
            quality_confirmed: true,
            handoff_ready: false,
          },
        },
        {
          name: "both-confirmed",
          actions: [
            "toggle-operator-confirm",
            "toggle-quality-confirm",
          ],
          expect: {
            operator_confirmed: true,
            quality_confirmed: true,
            handoff_ready: true,
          },
        },
      ],
    },
    {
      sourcePattern: "Two normally-open inputs in series",
      changes:
        "Non-safety handoff-confirmation scenario, separate operator and quality roles, new symbols, and an original panel layout.",
      inputs: "operator_confirmed, quality_confirmed",
      outputs: "handoff_ready",
      acceptance:
        "The ready lamp is on only when both confirmation inputs are active.",
    },
  ),
  scene(
    "03",
    "service-marker-inhibit",
    "Service Marker Inhibit",
    "A normally lit white service marker turns off while its local inhibit button is active.",
    [
      pushbutton(
        "marker_inhibit_button",
        "Marker inhibit button",
        [-1.6, 0, 0],
        "toggle-marker-inhibit",
        colors.red,
      ),
      lamp(
        "service_marker_lamp",
        "Service marker lamp",
        [0.8, 0, 0],
        "white",
      ),
    ],
    booleanSimulation(
      [
        {
          name: "marker_inhibit_pressed",
          type: "BOOL",
          owner: "PC",
          initial: false,
        },
        {
          name: "service_marker_on",
          type: "BOOL",
          owner: "PLC",
          initial: true,
          role: "output",
        },
      ],
      [
        {
          id: "toggle-marker-inhibit",
          label: "Press / release marker inhibit",
          type: "toggle",
          point: "marker_inhibit_pressed",
        },
      ],
      [
        {
          when: { marker_inhibit_pressed: false },
          set: { service_marker_on: true },
        },
        {
          when: { marker_inhibit_pressed: true },
          set: { service_marker_on: false },
        },
      ],
      [
        {
          point: "marker_inhibit_pressed",
          equipmentId: "marker_inhibit_button",
          mode: "switch",
        },
        {
          point: "service_marker_on",
          equipmentId: "service_marker_lamp",
          mode: "indicator",
          activeColor: "white",
        },
      ],
    ),
    {
      cases: [
        {
          name: "released-marker-on",
          expect: {
            marker_inhibit_pressed: false,
            service_marker_on: true,
          },
        },
        {
          name: "pressed-marker-off",
          actions: ["toggle-marker-inhibit"],
          expect: {
            marker_inhibit_pressed: true,
            service_marker_on: false,
          },
        },
      ],
    },
    {
      sourcePattern: "One input inverts a normally-on lamp",
      changes:
        "Service-marker inhibit use case, white LED load, explicit raw input polarity, and an original layout.",
      inputs: "marker_inhibit_pressed",
      outputs: "service_marker_on",
      acceptance:
        "The marker is on with the button released and off while the inhibit input is active.",
    },
  ),
  scene(
    "04",
    "two-station-call",
    "Two-Station Call Beacon",
    "Either of two work areas can request assistance by energizing one shared amber call beacon.",
    [
      pushbutton(
        "north_call_button",
        "North station call",
        [-1.8, 0, -0.7],
        "toggle-north-call",
        colors.amber,
      ),
      pushbutton(
        "south_call_button",
        "South station call",
        [-1.8, 0, 0.7],
        "toggle-south-call",
        colors.amber,
      ),
      lamp(
        "assistance_beacon",
        "Assistance call beacon",
        [0.8, 0, 0],
        "amber",
      ),
    ],
    booleanSimulation(
      [
        {
          name: "north_call_pressed",
          type: "BOOL",
          owner: "PC",
          initial: false,
        },
        {
          name: "south_call_pressed",
          type: "BOOL",
          owner: "PC",
          initial: false,
        },
        {
          name: "assistance_call_on",
          type: "BOOL",
          owner: "PLC",
          initial: false,
          role: "output",
        },
      ],
      [
        {
          id: "toggle-north-call",
          label: "Press / release north call",
          type: "toggle",
          point: "north_call_pressed",
        },
        {
          id: "toggle-south-call",
          label: "Press / release south call",
          type: "toggle",
          point: "south_call_pressed",
        },
      ],
      [
        {
          when: { north_call_pressed: false, south_call_pressed: false },
          set: { assistance_call_on: false },
        },
        {
          when: { north_call_pressed: true, south_call_pressed: false },
          set: { assistance_call_on: true },
        },
        {
          when: { north_call_pressed: false, south_call_pressed: true },
          set: { assistance_call_on: true },
        },
        {
          when: { north_call_pressed: true, south_call_pressed: true },
          set: { assistance_call_on: true },
        },
      ],
      [
        {
          point: "north_call_pressed",
          equipmentId: "north_call_button",
          mode: "switch",
        },
        {
          point: "south_call_pressed",
          equipmentId: "south_call_button",
          mode: "switch",
        },
        {
          point: "assistance_call_on",
          equipmentId: "assistance_beacon",
          mode: "indicator",
          activeColor: "amber",
        },
      ],
    ),
    {
      cases: [
        {
          name: "neither-station",
          expect: {
            north_call_pressed: false,
            south_call_pressed: false,
            assistance_call_on: false,
          },
        },
        {
          name: "north-only",
          actions: ["toggle-north-call"],
          expect: {
            north_call_pressed: true,
            south_call_pressed: false,
            assistance_call_on: true,
          },
        },
        {
          name: "south-only",
          actions: ["toggle-south-call"],
          expect: {
            north_call_pressed: false,
            south_call_pressed: true,
            assistance_call_on: true,
          },
        },
        {
          name: "both-stations",
          actions: ["toggle-north-call", "toggle-south-call"],
          expect: {
            north_call_pressed: true,
            south_call_pressed: true,
            assistance_call_on: true,
          },
        },
      ],
    },
    {
      sourcePattern: "Two normally-open inputs in parallel",
      changes:
        "Two-station assistance-call scenario, shared amber beacon, new symbols, and an original panel layout.",
      inputs: "north_call_pressed, south_call_pressed",
      outputs: "assistance_call_on",
      acceptance:
        "The beacon is off with neither input and on when either or both call inputs are active.",
    },
  ),
  scene(
    "05",
    "bay-light-selector",
    "Bay Light Selector",
    "A two-position maintenance selector controls two independent LED bay lights: isolated in position 0 and both energized in position 1.",
    [
      selector("mode_selector", "Maintenance selector", [-1.8, 0, 0], "next-mode", 2),
      lamp("bay_light_a", "Bay A LED light", [0.4, 0, -0.8], "white"),
      lamp("bay_light_b", "Bay B LED light", [0.4, 0, 0.8], "white"),
    ],
    booleanSimulation(
      [
        { name: "selector_position", type: "DINT", owner: "PC", initial: 0 },
        { name: "bay_a_command", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "bay_b_command", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [{ id: "next-mode", label: "Advance selector", type: "cycle", point: "selector_position", values: [0, 1] }],
      [
        { when: { selector_position: 0 }, set: { bay_a_command: false, bay_b_command: false } },
        { when: { selector_position: 1 }, set: { bay_a_command: true, bay_b_command: true } },
      ],
      [
        { point: "selector_position", equipmentId: "mode_selector", mode: "selector" },
        { point: "bay_a_command", equipmentId: "bay_light_a", mode: "indicator", activeColor: "white" },
        { point: "bay_b_command", equipmentId: "bay_light_b", mode: "indicator", activeColor: "white" },
      ],
    ),
    {
      cases: [
        { name: "isolated", expect: { bay_a_command: false, bay_b_command: false } },
        { name: "energized", actions: ["next-mode"], expect: { bay_a_command: true, bay_b_command: true } },
      ],
    },
    {
      sourcePattern: "Two lamps selected together",
      changes: "Maintenance-bay setting, LED loads, new symbols, and a two-position isolation/energize selector.",
      inputs: "selector_position",
      outputs: "bay_a_command, bay_b_command",
      acceptance: "Position 0 de-energizes both lights; position 1 energizes both.",
    },
  ),
  scene(
    "06",
    "ready-attention",
    "Ready / Attention Button",
    "A spring-return request button transfers indication between a white ready lamp and an amber attention lamp.",
    [
      pushbutton("request_button", "Attention request button", [-1.6, 0, 0], "toggle-request", colors.blue),
      lamp("ready_lamp", "Ready lamp", [0.5, 0, -0.65], "white"),
      lamp("attention_lamp", "Attention lamp", [0.5, 0, 0.65], "amber"),
    ],
    booleanSimulation(
      [
        { name: "request_held", type: "BOOL", owner: "PC", initial: false },
        { name: "ready_light", type: "BOOL", owner: "PLC", initial: true, role: "output" },
        { name: "attention_light", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [{ id: "toggle-request", label: "Press / release request", type: "toggle", point: "request_held" }],
      [
        { when: { request_held: false }, set: { ready_light: true, attention_light: false } },
        { when: { request_held: true }, set: { ready_light: false, attention_light: true } },
      ],
      [
        { point: "request_held", equipmentId: "request_button", mode: "switch" },
        { point: "ready_light", equipmentId: "ready_lamp", mode: "indicator", activeColor: "white" },
        { point: "attention_light", equipmentId: "attention_lamp", mode: "indicator", activeColor: "amber" },
      ],
    ),
    {
      cases: [
        { name: "released", expect: { ready_light: true, attention_light: false } },
        { name: "held", actions: ["toggle-request"], expect: { ready_light: false, attention_light: true } },
      ],
    },
    {
      sourcePattern: "One button selects complementary lamps",
      changes: "Ready/attention annunciation with white and amber LEDs and new signal polarity.",
      inputs: "request_held",
      outputs: "ready_light, attention_light",
      acceptance: "Exactly one indication is on in both released and held states.",
    },
  ),
  scene(
    "07",
    "dual-contact-permissive",
    "Dual-Contact Permissive",
    "A permissive lamp demonstrates how a normally-open reset input and an inverted normally-closed contact can produce the same logical request.",
    [
      pushbutton("reset_button", "NO reset request", [-1.8, 0, -0.7], "toggle-reset", colors.green),
      pushbutton("nc_button", "NC test contact", [-1.8, 0, 0.7], "toggle-nc", colors.red),
      lamp("permit_lamp", "Permit lamp", [0.6, 0, 0], "green"),
    ],
    booleanSimulation(
      [
        { name: "reset_request", type: "BOOL", owner: "PC", initial: false },
        { name: "stop_contact_nc", type: "BOOL", owner: "PC", initial: true },
        { name: "permit_output", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [
        { id: "toggle-reset", label: "Toggle NO reset", type: "toggle", point: "reset_request" },
        { id: "toggle-nc", label: "Toggle NC contact", type: "toggle", point: "stop_contact_nc" },
      ],
      [
        { when: { reset_request: false, stop_contact_nc: true }, set: { permit_output: false } },
        { when: { reset_request: true, stop_contact_nc: true }, set: { permit_output: true } },
        { when: { reset_request: false, stop_contact_nc: false }, set: { permit_output: true } },
        { when: { reset_request: true, stop_contact_nc: false }, set: { permit_output: true } },
      ],
      [
        { point: "reset_request", equipmentId: "reset_button", mode: "switch" },
        { point: "permit_output", equipmentId: "permit_lamp", mode: "indicator", activeColor: "green" },
      ],
    ),
    {
      cases: [
        { name: "normal", expect: { permit_output: false } },
        { name: "no-request", actions: ["toggle-reset"], expect: { permit_output: true } },
        { name: "nc-inverted", actions: ["toggle-nc"], expect: { permit_output: true } },
      ],
    },
    {
      sourcePattern: "NO and NC inputs driving one lamp",
      changes: "Permissive-testing scenario with explicit raw NC contact state and inverted logic.",
      inputs: "reset_request, stop_contact_nc",
      outputs: "permit_output",
      acceptance: "Normal state is off; either logical request turns the permit lamp on.",
    },
  ),
  scene(
    "08",
    "inspection-vote",
    "Inspection Vote Stacklight",
    "Two inspectors enter independent votes. One vote shows the corresponding disposition; simultaneous votes force a red conflict indication.",
    [
      pushbutton("left_vote", "Inspector A vote", [-1.8, 0, -0.8], "toggle-left", colors.green),
      pushbutton("right_vote", "Inspector B vote", [-1.8, 0, 0.8], "toggle-right", colors.amber),
      stacklight("vote_stacklight", "Inspection result stacklight", [0.8, 0, 0], null),
    ],
    booleanSimulation(
      [
        { name: "vote_a", type: "BOOL", owner: "PC", initial: false },
        { name: "vote_b", type: "BOOL", owner: "PC", initial: false },
        { name: "pass_indication", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "hold_indication", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "conflict_indication", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [
        { id: "toggle-left", label: "Toggle inspector A", type: "toggle", point: "vote_a" },
        { id: "toggle-right", label: "Toggle inspector B", type: "toggle", point: "vote_b" },
      ],
      [
        { when: { vote_a: false, vote_b: false }, set: {} },
        { when: { vote_a: true, vote_b: false }, set: { pass_indication: true } },
        { when: { vote_a: false, vote_b: true }, set: { hold_indication: true } },
        { when: { vote_a: true, vote_b: true }, set: { conflict_indication: true } },
      ],
      [
        { point: "vote_a", equipmentId: "left_vote", mode: "switch" },
        { point: "vote_b", equipmentId: "right_vote", mode: "switch" },
        { point: "pass_indication", equipmentId: "vote_stacklight", mode: "indicator", activeColor: "green" },
        { point: "hold_indication", equipmentId: "vote_stacklight", mode: "indicator", activeColor: "amber" },
        { point: "conflict_indication", equipmentId: "vote_stacklight", mode: "indicator", activeColor: "red" },
      ],
    ),
    {
      cases: [
        { name: "vote-a", actions: ["toggle-left"], expect: { pass_indication: true, conflict_indication: false } },
        { name: "vote-b", actions: ["toggle-right"], expect: { hold_indication: true, conflict_indication: false } },
        { name: "conflict", actions: ["toggle-left", "toggle-right"], expect: { conflict_indication: true, pass_indication: false, hold_indication: false } },
      ],
    },
    {
      sourcePattern: "Two buttons and three mutually exclusive lamps",
      changes: "Dual-inspector voting with pass, hold, and conflict meanings.",
      inputs: "vote_a, vote_b",
      outputs: "pass_indication, hold_indication, conflict_indication",
      acceptance: "Single votes select green or amber; simultaneous votes select red only.",
    },
  ),
  scene(
    "09",
    "maintenance-beacon",
    "Maintenance Beacon Selector",
    "A four-position selector chooses off, lockout red, service amber, or released green on a maintenance beacon.",
    [
      selector("beacon_selector", "Maintenance state selector", [-1.8, 0, 0], "next-beacon-state", 4),
      stacklight("maintenance_beacon", "Maintenance beacon", [0.8, 0, 0], null),
    ],
    booleanSimulation(
      [
        { name: "beacon_position", type: "DINT", owner: "PC", initial: 0 },
        { name: "red_beacon", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "amber_beacon", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "green_beacon", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [{ id: "next-beacon-state", label: "Advance beacon selector", type: "cycle", point: "beacon_position", values: [0, 1, 2, 3] }],
      [
        { when: { beacon_position: 0 }, set: {} },
        { when: { beacon_position: 1 }, set: { red_beacon: true } },
        { when: { beacon_position: 2 }, set: { amber_beacon: true } },
        { when: { beacon_position: 3 }, set: { green_beacon: true } },
      ],
      [
        { point: "beacon_position", equipmentId: "beacon_selector", mode: "selector" },
        { point: "red_beacon", equipmentId: "maintenance_beacon", mode: "indicator", activeColor: "red" },
        { point: "amber_beacon", equipmentId: "maintenance_beacon", mode: "indicator", activeColor: "amber" },
        { point: "green_beacon", equipmentId: "maintenance_beacon", mode: "indicator", activeColor: "green" },
      ],
    ),
    {
      cases: [
        { name: "off", expect: { red_beacon: false, amber_beacon: false, green_beacon: false } },
        { name: "lockout", actions: ["next-beacon-state"], expect: { red_beacon: true } },
        { name: "service", actions: ["next-beacon-state", "next-beacon-state"], expect: { amber_beacon: true } },
        { name: "released", actions: ["next-beacon-state", "next-beacon-state", "next-beacon-state"], expect: { green_beacon: true } },
      ],
    },
    {
      sourcePattern: "Four-position selector and three lamps",
      changes: "Maintenance-state beacon with mutually exclusive off/red/amber/green states.",
      inputs: "beacon_position",
      outputs: "red_beacon, amber_beacon, green_beacon",
      acceptance: "Each selector position produces exactly the documented beacon state.",
    },
  ),
  scene(
    "10",
    "dust-collector-seal-in",
    "Dust Collector Seal-In",
    "Separate start and stop controls latch a dust-collector command until an explicit stop request resets it.",
    [
      pushbutton("collector_start", "Collector start", [-2, 0, -0.75], "collector-start", colors.green),
      pushbutton("collector_stop", "Collector stop", [-2, 0, 0.75], "collector-stop", colors.red),
      { id: "collector_motor", type: "fan", label: "Dust collector fan", position: [0.7, 0, 0], config: { diameter: 1.9, centerHeight: 1.6, bladeCount: 6, running: false } },
      lamp("collector_run_lamp", "Collector running lamp", [2.6, 0, 0], "green"),
    ],
    booleanSimulation(
      [
        { name: "collector_start_request", type: "BOOL", owner: "PC", initial: false },
        { name: "collector_stop_request", type: "BOOL", owner: "PC", initial: false },
        { name: "run_latched", type: "BOOL", owner: "PLC", initial: false, role: "memory" },
        { name: "collector_run", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [
        { id: "collector-start", label: "Pulse collector start", type: "pulse", point: "collector_start_request" },
        { id: "collector-stop", label: "Pulse collector stop", type: "pulse", point: "collector_stop_request" },
      ],
      [
        { when: { run_latched: false }, set: { collector_run: false } },
        { when: { run_latched: true }, set: { collector_run: true } },
      ],
      [
        { point: "collector_start_request", equipmentId: "collector_start", mode: "switch" },
        { point: "collector_stop_request", equipmentId: "collector_stop", mode: "switch" },
        { point: "collector_run", equipmentId: "collector_motor", mode: "running" },
        { point: "collector_run", equipmentId: "collector_run_lamp", mode: "indicator", activeColor: "green" },
      ],
      [
        { rising: "collector_start_request", set: { run_latched: true } },
        { rising: "collector_stop_request", set: { run_latched: false } },
      ],
    ),
    {
      cases: [
        { name: "start-latches", actions: ["collector-start"], expect: { collector_run: true, run_latched: true } },
        { name: "stop-resets", actions: ["collector-start", "collector-stop"], expect: { collector_run: false, run_latched: false } },
      ],
    },
    {
      sourcePattern: "Start/stop self-hold",
      changes: "Dust-collection fan, separate latch point, and explicit run indication.",
      inputs: "collector-start, collector-stop",
      outputs: "collector_run",
      acceptance: "Start seals in the run command; stop removes it.",
    },
  ),
  scene(
    "11",
    "inbound-tote-stop",
    "Inbound Tote Stop",
    "A tote advances to a scan photoeye, pauses for identification, then clears the station before the conveyor returns to ready.",
    [
      conveyor("inbound_conveyor", "Inbound tote conveyor", [0, 0, 0], 8),
      product("inbound_tote", "Reusable tote", [-3.2, 0.99, 0], [1.0, 0.78, 0.9], 0x2e8bd1),
      photoeye("scan_photoeye", "Barcode scan photoeye", [0.8, 0, 0]),
      pushbutton("inbound_start", "Start inbound cycle", [-3.1, 0, 2.1], "start-cycle"),
      stacklight("inbound_status", "Inbound status", [3.2, 0, -1.7]),
    ],
    sequenceSimulation({
      points: [
        { name: "conveyor_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "tote_at_scanner", type: "BOOL", owner: "PC", initial: false },
        { name: "scan_complete", type: "BOOL", owner: "PC", initial: false },
        { name: "cell_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-cycle", label: "Start tote cycle", type: "start", sequence: "scan-cycle" },
        { id: "stop-cycle", label: "Stop conveyor safely", type: "stop" },
        { id: "reset-cycle", label: "Reset tote", type: "reset" },
      ],
      pointBindings: [
        { point: "conveyor_run", equipmentId: "inbound_conveyor", mode: "running" },
        { point: "tote_at_scanner", equipmentId: "scan_photoeye", mode: "photoeye" },
        { point: "cell_color", equipmentId: "inbound_status", mode: "indicator" },
      ],
      sequences: {
        "scan-cycle": [
          { name: "feeding", durationS: 2.4, set: { conveyor_run: true, tote_at_scanner: false, scan_complete: false, cycle_complete: false, cell_color: "green" }, motions: [{ type: "translate", equipmentId: "inbound_tote", axis: "x", from: -3.2, to: 0.8 }] },
          { name: "scanning", durationS: 0.8, set: { conveyor_run: false, tote_at_scanner: true, cell_color: "amber" } },
          { name: "clearing", durationS: 1.6, set: { conveyor_run: true, tote_at_scanner: false, scan_complete: true, cell_color: "green" }, motions: [{ type: "translate", equipmentId: "inbound_tote", axis: "x", from: 0.8, to: 4.0 }] },
          { name: "ready", durationS: 0.1, set: { conveyor_run: false, cycle_complete: true, cell_color: "amber" } },
        ],
      },
      defaultSequence: "scan-cycle",
      safeState: { conveyor_run: false, cell_color: "red" },
    }),
    {
      cases: [{ name: "complete-scan", phases: [{ action: "start-cycle", runForS: 5.2 }], expect: { conveyor_run: false, scan_complete: true, cycle_complete: true } }],
    },
    {
      sourcePattern: "Package conveyor stops at a sensor",
      changes: "Reusable tote, barcode dwell, automatic release, 8 m conveyor, and new timing.",
      inputs: "tote_at_scanner, scan_complete",
      outputs: "conveyor_run",
      acceptance: "The tote stops at the scanner, records completion, clears, and leaves the conveyor stopped.",
      camera: camera([10.8, 6.5, 9.8], [0, 0.9, 0]),
    },
  ),
  scene(
    "12",
    "assembly-lift",
    "Ergonomic Assembly Lift",
    "Independent raise and lower commands move a scissor lift between modeled bottom and top limits.",
    [
      { id: "assembly_lift", type: "liftTable", label: "Ergonomic assembly lift", position: [0, 0, 0], config: { width: 3, depth: 1.9, minimumHeight: 0.6, travel: 2.2, initialPosition: 0 } },
      product("lift_fixture", "Assembly fixture", [0, 0.82, 0], [1.4, 0.42, 1.0], 0xf2b705),
      pushbutton("raise_button", "Raise lift", [-2.5, 0, -0.7], "raise-lift"),
      pushbutton("lower_button", "Lower lift", [-2.5, 0, 0.7], "lower-lift", colors.blue),
      lamp("top_limit_lamp", "Top limit", [2.3, 0, -0.55], "green"),
      lamp("bottom_limit_lamp", "Bottom limit", [2.3, 0, 0.55], "amber"),
    ],
    sequenceSimulation({
      points: [
        { name: "lift_up", type: "BOOL", owner: "PLC", initial: false },
        { name: "lift_down", type: "BOOL", owner: "PLC", initial: false },
        { name: "top_limit", type: "BOOL", owner: "PC", initial: false },
        { name: "bottom_limit", type: "BOOL", owner: "PC", initial: true },
        { name: "lift_position", type: "REAL", owner: "SIM", initial: 0, unit: "%" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "raise-lift", label: "Raise to work height", type: "start", sequence: "raise" },
        { id: "lower-lift", label: "Lower to load height", type: "start", sequence: "lower" },
        { id: "stop-lift", label: "Stop lift", type: "stop" },
        { id: "reset-lift", label: "Reset lift", type: "reset" },
      ],
      pointBindings: [
        { point: "top_limit", equipmentId: "top_limit_lamp", mode: "indicator", activeColor: "green" },
        { point: "bottom_limit", equipmentId: "bottom_limit_lamp", mode: "indicator", activeColor: "amber" },
      ],
      sequences: {
        raise: [
          { name: "raising", durationS: 2.0, set: { lift_up: true, lift_down: false, top_limit: false, bottom_limit: false, cycle_complete: false }, motions: [{ type: "position", equipmentId: "assembly_lift", from: 0, to: 1 }, { type: "translate", equipmentId: "lift_fixture", axis: "y", from: 0.82, to: 3.02 }] },
          { name: "at top", durationS: 0.1, set: { lift_up: false, top_limit: true, lift_position: 100, cycle_complete: true } },
        ],
        lower: [
          { name: "lowering", durationS: 2.0, set: { lift_down: true, lift_up: false, top_limit: false, bottom_limit: false, cycle_complete: false }, motions: [{ type: "position", equipmentId: "assembly_lift", from: 1, to: 0 }, { type: "translate", equipmentId: "lift_fixture", axis: "y", from: 3.02, to: 0.82 }] },
          { name: "at bottom", durationS: 0.1, set: { lift_down: false, bottom_limit: true, lift_position: 0, cycle_complete: true } },
        ],
      },
      defaultSequence: "raise",
      safeState: { lift_up: false, lift_down: false },
    }),
    {
      cases: [
        { name: "raise", phases: [{ action: "raise-lift", runForS: 2.3 }], expect: { top_limit: true, lift_up: false, lift_position: 100 } },
        { name: "raise-lower", phases: [{ action: "raise-lift", runForS: 2.3 }, { action: "lower-lift", runForS: 2.3 }], expect: { bottom_limit: true, lift_down: false, lift_position: 0 } },
      ],
    },
    {
      sourcePattern: "Pallet lift with up/down controls and end sensors",
      changes: "Ergonomic assembly table, 2.2 m travel, explicit motion commands, position feedback, and separate verification paths.",
      inputs: "top_limit, bottom_limit",
      outputs: "lift_up, lift_down",
      acceptance: "Raise stops at the top limit; lower stops at the bottom limit; opposed outputs are never on together.",
      camera: camera([8.5, 6.6, 9.2], [0, 1.4, 0]),
    },
  ),
  scene(
    "13",
    "coolant-jug-fill",
    "Coolant Jug Filling Cell",
    "An empty coolant jug indexes under a fill valve, fills to a high probe, and then exits the station.",
    [
      conveyor("fill_conveyor", "Jug indexing conveyor", [0, 0, 0], 8),
      product("coolant_jug", "Coolant jug", [-3.2, 0.99, 0], [0.8, 1.2, 0.75], 0xe9f2f5),
      photoeye("jug_present_sensor", "Jug present sensor", [0, 0, 0]),
      { id: "fill_valve", type: "valve", label: "Coolant fill valve", position: [0, 2.4, 0], config: { initialPosition: 0 } },
      machine("fill_skid", "Metered coolant skid", [0, 0, -2.0], [2.0, 2.5, 1.3], 0x176b87),
      pushbutton("fill_start", "Start fill cycle", [-3.1, 0, 2.1], "start-fill"),
      stacklight("fill_status", "Fill cell status", [3.2, 0, -1.8]),
    ],
    sequenceSimulation({
      points: [
        { name: "conveyor_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "jug_present", type: "BOOL", owner: "PC", initial: false },
        { name: "fill_valve_open", type: "BOOL", owner: "PLC", initial: false },
        { name: "high_level_probe", type: "BOOL", owner: "PC", initial: false },
        { name: "fill_skid_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "fill_percent", type: "REAL", owner: "SIM", initial: 0, unit: "%" },
        { name: "cell_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-fill", label: "Start jug fill", type: "start", sequence: "fill-cycle" },
        { id: "stop-fill", label: "Stop fill cell", type: "stop" },
        { id: "reset-fill", label: "Reset jug", type: "reset" },
      ],
      pointBindings: [
        { point: "conveyor_run", equipmentId: "fill_conveyor", mode: "running" },
        { point: "jug_present", equipmentId: "jug_present_sensor", mode: "photoeye" },
        { point: "fill_valve_open", equipmentId: "fill_valve", mode: "position" },
        { point: "fill_skid_run", equipmentId: "fill_skid", mode: "running" },
        { point: "cell_color", equipmentId: "fill_status", mode: "indicator" },
      ],
      sequences: {
        "fill-cycle": [
          { name: "indexing", durationS: 2.0, set: { conveyor_run: true, jug_present: false, high_level_probe: false, fill_percent: 0, cycle_complete: false, cell_color: "green" }, motions: [{ type: "translate", equipmentId: "coolant_jug", axis: "x", from: -3.2, to: 0 }] },
          { name: "filling", durationS: 2.2, set: { conveyor_run: false, jug_present: true, fill_valve_open: true, fill_skid_run: true, cell_color: "amber" } },
          { name: "level reached", durationS: 0.2, set: { fill_valve_open: false, fill_skid_run: false, high_level_probe: true, fill_percent: 100 } },
          { name: "discharging", durationS: 1.6, set: { conveyor_run: true, jug_present: false, cell_color: "green" }, motions: [{ type: "translate", equipmentId: "coolant_jug", axis: "x", from: 0, to: 3.8 }] },
          { name: "ready", durationS: 0.1, set: { conveyor_run: false, cycle_complete: true, cell_color: "amber" } },
        ],
      },
      defaultSequence: "fill-cycle",
      safeState: { conveyor_run: false, fill_valve_open: false, fill_skid_run: false, cell_color: "red" },
    }),
    {
      cases: [{ name: "fill-complete", phases: [{ action: "start-fill", runForS: 6.5 }], expect: { high_level_probe: true, fill_valve_open: false, conveyor_run: false, fill_percent: 100, cycle_complete: true } }],
    },
    {
      sourcePattern: "Fill moving containers to a level sensor",
      changes: "Coolant jug, metered valve/skid, 100% fill feedback, new distances and timings.",
      inputs: "jug_present, high_level_probe",
      outputs: "conveyor_run, fill_valve_open, fill_skid_run",
      acceptance: "The valve cannot remain open after the high probe; the filled jug exits and the conveyor stops.",
      camera: camera([11, 7, 10.5], [0, 1.2, 0]),
    },
  ),
  scene(
    "14",
    "sump-pump",
    "Sump Dewatering Pump",
    "A simulated sump rises to the high float, starts a dewatering pump, and pumps down until the low float resets the run latch.",
    [
      { id: "sump_tank", type: "tank", label: "Equipment-room sump", position: [0, 0, 0], config: { height: 4.2, diameter: 3.2, initialLevel: 0.22, fluidColor: 0x1597d4 } },
      { id: "sump_pump", type: "pump", label: "Dewatering pump", position: [-4.0, 0, 0], config: { running: false } },
      { id: "low_float", type: "levelSensor", label: "Low float", position: [2.1, 0.9, 0], config: { sensorType: "discrete", threshold: 0.2, mode: "low" } },
      { id: "high_float", type: "levelSensor", label: "High float", position: [2.1, 3.2, 0], config: { sensorType: "discrete", threshold: 0.78, mode: "high" } },
      { id: "discharge_pipe", type: "pipe", label: "Sump discharge", position: [-2.4, 3.4, 0], config: { length: 3.5, diameter: 0.3, axis: "x", showSupport: true } },
      pushbutton("sump_start", "Run level cycle", [-3.2, 0, 2.1], "start-sump"),
      stacklight("sump_status", "Sump status", [3.3, 0, -1.8]),
    ],
    sequenceSimulation({
      points: [
        { name: "sump_level", type: "REAL", owner: "SIM", initial: 22, unit: "%" },
        { name: "high_float_active", type: "BOOL", owner: "PC", initial: false },
        { name: "low_float_active", type: "BOOL", owner: "PC", initial: false },
        { name: "pump_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-sump", label: "Simulate sump cycle", type: "start", sequence: "level-cycle" },
        { id: "stop-sump", label: "Stop pump safely", type: "stop" },
        { id: "reset-sump", label: "Reset sump", type: "reset" },
      ],
      pointBindings: [
        { point: "pump_run", equipmentId: "sump_pump", mode: "running" },
        { point: "high_float_active", equipmentId: "high_float", mode: "levelSensor" },
        { point: "low_float_active", equipmentId: "low_float", mode: "levelSensor" },
        { point: "status_color", equipmentId: "sump_status", mode: "indicator" },
      ],
      sequences: {
        "level-cycle": [
          { name: "level rising", durationS: 2.6, set: { pump_run: false, high_float_active: false, low_float_active: false, sump_level: 78, cycle_complete: false, status_color: "amber" }, motions: [{ type: "tankLevel", equipmentId: "sump_tank", from: 0.22, to: 0.78 }] },
          { name: "pump latched", durationS: 0.2, set: { high_float_active: true, pump_run: true, status_color: "green" } },
          { name: "pumping down", durationS: 2.8, set: { high_float_active: false, sump_level: 18 }, motions: [{ type: "tankLevel", equipmentId: "sump_tank", from: 0.78, to: 0.18 }] },
          { name: "low level stop", durationS: 0.1, set: { low_float_active: true, pump_run: false, cycle_complete: true, status_color: "amber" } },
        ],
      },
      defaultSequence: "level-cycle",
      safeState: { pump_run: false, status_color: "red" },
    }),
    {
      cases: [{ name: "pump-hysteresis", phases: [{ action: "start-sump", runForS: 6.0 }], expect: { pump_run: false, low_float_active: true, high_float_active: false, cycle_complete: true } }],
    },
    {
      sourcePattern: "Pump well with two float switches",
      changes: "Equipment-room sump, 78%/18% thresholds, explicit latch behavior, and visible pump/tank dynamics.",
      inputs: "high_float_active, low_float_active",
      outputs: "pump_run",
      acceptance: "High float starts the pump; it remains on through the deadband and stops only at low float.",
      camera: camera([10.6, 7.8, 10.6], [0, 2.0, 0]),
    },
  ),
  scene(
    "15",
    "fume-extractor",
    "Weld Fume Extractor",
    "A light switch and four-position speed selector independently control an inspection light and a guarded extraction fan.",
    [
      pushbutton("hood_light_switch", "Hood light switch", [-2.4, 0, -0.75], "toggle-light", colors.white),
      selector("fan_speed_selector", "Fan speed selector", [-2.4, 0, 0.75], "next-speed", 4),
      lamp("hood_light", "Inspection light", [0, 0, -1.8], "white"),
      { id: "extractor_fan", type: "fan", label: "Guarded extraction fan", position: [1.0, 0, 0], config: { diameter: 2.4, centerHeight: 1.9, bladeCount: 6, running: false } },
      stacklight("speed_display", "Speed indication", [3.2, 0, -1.2], null),
    ],
    booleanSimulation(
      [
        { name: "hood_light_request", type: "BOOL", owner: "PC", initial: false },
        { name: "hood_light_on", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "fan_selector_position", type: "DINT", owner: "PC", initial: 0 },
        { name: "fan_run", type: "BOOL", owner: "PLC", initial: false, role: "output" },
        { name: "fan_speed_percent", type: "DINT", owner: "PLC", initial: 0, role: "output", unit: "%" },
        { name: "low_speed", type: "BOOL", owner: "SIM", initial: false, role: "output" },
        { name: "medium_speed", type: "BOOL", owner: "SIM", initial: false, role: "output" },
        { name: "high_speed", type: "BOOL", owner: "SIM", initial: false, role: "output" },
      ],
      [
        { id: "toggle-light", label: "Toggle hood light request", type: "toggle", point: "hood_light_request" },
        { id: "next-speed", label: "Advance fan speed", type: "cycle", point: "fan_selector_position", values: [0, 1, 2, 3] },
      ],
      [
        { when: { hood_light_request: false }, set: { hood_light_on: false } },
        { when: { hood_light_request: true }, set: { hood_light_on: true } },
        { when: { fan_selector_position: 0 }, set: { fan_run: false, fan_speed_percent: 0 } },
        { when: { fan_selector_position: 1 }, set: { fan_run: true, fan_speed_percent: 35, low_speed: true } },
        { when: { fan_selector_position: 2 }, set: { fan_run: true, fan_speed_percent: 65, medium_speed: true } },
        { when: { fan_selector_position: 3 }, set: { fan_run: true, fan_speed_percent: 100, high_speed: true } },
      ],
      [
        { point: "hood_light_request", equipmentId: "hood_light_switch", mode: "switch" },
        { point: "hood_light_on", equipmentId: "hood_light", mode: "indicator", activeColor: "white" },
        { point: "fan_selector_position", equipmentId: "fan_speed_selector", mode: "selector" },
        { point: "fan_run", equipmentId: "extractor_fan", mode: "running" },
        { point: "low_speed", equipmentId: "speed_display", mode: "indicator", activeColor: "green" },
        { point: "medium_speed", equipmentId: "speed_display", mode: "indicator", activeColor: "amber" },
        { point: "high_speed", equipmentId: "speed_display", mode: "indicator", activeColor: "red" },
      ],
    ),
    {
      cases: [
        { name: "off", expect: { fan_run: false, fan_speed_percent: 0, hood_light_on: false } },
        { name: "low-with-light", actions: ["toggle-light", "next-speed"], expect: { fan_run: true, fan_speed_percent: 35, hood_light_on: true } },
        { name: "high", actions: ["next-speed", "next-speed", "next-speed"], expect: { fan_run: true, fan_speed_percent: 100, high_speed: true } },
      ],
    },
    {
      sourcePattern: "Hood light and three fan speeds",
      changes: "Weld-fume extractor with 35/65/100% speed commands and separate inspection light.",
      inputs: "hood_light_request, fan_selector_position",
      outputs: "hood_light_on, fan_run, fan_speed_percent",
      acceptance: "Light is independent; selector positions command off/35/65/100% and one speed indication.",
      camera: camera([9.5, 6.8, 10], [0.4, 1.5, 0]),
    },
  ),
  scene(
    "16",
    "safe-drill",
    "Fixture-Safe Drill Station",
    "A guarded drill cycle requires a present workpiece and both hand-request inputs before the spindle can descend.",
    [
      { id: "safe_drill", type: "drillPress", label: "Guarded drill press", position: [0.7, 0, 0], config: { travel: 1.3, initialPosition: 0, running: false } },
      product("drill_workpiece", "Clamped workpiece", [1.0, 1.16, 0], [1.3, 0.2, 0.9], colors.steel),
      pushbutton("left_hand_button", "Left hand request", [-2.2, 0, -0.75], "toggle-left-hand"),
      pushbutton("right_hand_button", "Right hand request", [-2.2, 0, 0.75], "toggle-right-hand"),
      pushbutton("drill_cycle_button", "Initiate guarded cycle", [-1.0, 0, 1.8], "start-drill", colors.blue),
      stacklight("drill_status", "Drill status", [3.2, 0, -1.5]),
    ],
    sequenceSimulation({
      points: [
        { name: "left_hand_request", type: "BOOL", owner: "PC", initial: false },
        { name: "right_hand_request", type: "BOOL", owner: "PC", initial: false },
        { name: "workpiece_present", type: "BOOL", owner: "PC", initial: true },
        { name: "drill_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "drill_at_bottom", type: "BOOL", owner: "PC", initial: false },
        { name: "drill_at_top", type: "BOOL", owner: "PC", initial: true },
        { name: "cycle_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "toggle-left-hand", label: "Toggle left hand request", type: "togglePoint", point: "left_hand_request" },
        { id: "toggle-right-hand", label: "Toggle right hand request", type: "togglePoint", point: "right_hand_request" },
        { id: "start-drill", label: "Start guarded drill cycle", type: "start", sequence: "drill-cycle", requires: { left_hand_request: true, right_hand_request: true, workpiece_present: true }, blockedMessage: "Start blocked - workpiece and both hand requests are required" },
        { id: "stop-drill", label: "Stop and retract", type: "stop" },
        { id: "reset-drill", label: "Reset drill", type: "reset" },
      ],
      pointBindings: [
        { point: "left_hand_request", equipmentId: "left_hand_button", mode: "switch" },
        { point: "right_hand_request", equipmentId: "right_hand_button", mode: "switch" },
        { point: "drill_run", equipmentId: "safe_drill", mode: "running" },
        { point: "cycle_color", equipmentId: "drill_status", mode: "indicator" },
      ],
      sequences: {
        "drill-cycle": [
          { name: "spindle start", durationS: 0.35, set: { drill_run: true, drill_at_top: true, drill_at_bottom: false, cycle_complete: false, cycle_color: "green" } },
          { name: "drilling", durationS: 1.4, set: { drill_at_top: false, cycle_color: "amber" }, motions: [{ type: "position", equipmentId: "safe_drill", from: 0, to: 1 }] },
          { name: "bottom dwell", durationS: 0.35, set: { drill_at_bottom: true } },
          { name: "retracting", durationS: 1.4, set: { drill_at_bottom: false }, motions: [{ type: "position", equipmentId: "safe_drill", from: 1, to: 0 }] },
          { name: "cycle complete", durationS: 0.1, set: { drill_run: false, drill_at_top: true, cycle_complete: true, cycle_color: "amber" } },
        ],
      },
      defaultSequence: "drill-cycle",
      safeState: { drill_run: false, cycle_color: "red" },
    }),
    {
      cases: [
        { name: "blocked-without-hands", phases: [{ action: "start-drill", runForS: 0.5 }], expect: { drill_run: false, cycle_complete: false } },
        { name: "guarded-cycle", phases: [{ action: "toggle-left-hand" }, { action: "toggle-right-hand" }, { action: "start-drill", runForS: 4.0 }], expect: { drill_run: false, drill_at_top: true, cycle_complete: true } },
      ],
    },
    {
      sourcePattern: "Two-hand drilling machine",
      changes: "Guarded fixture, explicit workpiece permissive, blocked-start proof, new travel and timing.",
      inputs: "left_hand_request, right_hand_request, workpiece_present, drill_at_top, drill_at_bottom",
      outputs: "drill_run",
      acceptance: "Start is blocked without both requests; a valid cycle drills, retracts, and stops at top.",
      camera: camera([9.5, 7.2, 10], [0.5, 1.5, 0]),
    },
  ),
  scene(
    "17",
    "pallet-robot",
    "Twin-Container Pallet Cell",
    "A robot transfers two process containers from a staged pallet, then releases the empty pallet to the outbound conveyor.",
    [
      conveyor("robot_pallet_conveyor", "Pallet staging conveyor", [-1.0, 0, 0], 8),
      product("robot_pallet", "Staging pallet", [-2.8, 0.98, 0], [2.2, 0.22, 1.5], 0x8a6b42),
      product("container_a", "Process container A", [-3.15, 1.2, -0.4], [0.62, 1.0, 0.62], colors.white),
      product("container_b", "Process container B", [-2.45, 1.2, 0.4], [0.62, 1.0, 0.62], colors.white),
      { id: "pallet_robot", type: "robotArm", label: "Pallet unloading robot", position: [1.3, 0, -2.2], config: { initialPosition: 0, running: false } },
      machine("process_receiver", "Container process receiver", [3.6, 0, 1.2], [2.1, 2.7, 1.7]),
      photoeye("pallet_ready_sensor", "Pallet ready sensor", [-2.7, 0, 0]),
      pushbutton("robot_cycle_start", "Start robot cycle", [-3.7, 0, 2.2], "start-robot"),
      stacklight("robot_cell_status", "Robot cell status", [4.4, 0, -1.8]),
    ],
    sequenceSimulation({
      points: [
        { name: "pallet_ready", type: "BOOL", owner: "PC", initial: true },
        { name: "robot_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "conveyor_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "placed_count", type: "DINT", owner: "SIM", initial: 0 },
        { name: "cell_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-robot", label: "Start pallet unload", type: "start", sequence: "unload-cycle", requires: { pallet_ready: true } },
        { id: "stop-robot", label: "Stop robot cell", type: "stop" },
        { id: "reset-robot", label: "Reset pallet cell", type: "reset" },
      ],
      pointBindings: [
        { point: "pallet_ready", equipmentId: "pallet_ready_sensor", mode: "photoeye" },
        { point: "robot_run", equipmentId: "pallet_robot", mode: "running" },
        { point: "conveyor_run", equipmentId: "robot_pallet_conveyor", mode: "running" },
        { point: "cell_color", equipmentId: "robot_cell_status", mode: "indicator" },
      ],
      sequences: {
        "unload-cycle": [
          { name: "pick first", durationS: 1.2, set: { robot_run: true, conveyor_run: false, placed_count: 0, cycle_complete: false, cell_color: "amber" }, motions: [{ type: "position", equipmentId: "pallet_robot", from: 0, to: 0.55 }, { type: "translate", equipmentId: "container_a", axis: "x", from: -3.15, to: 1.5 }, { type: "translate", equipmentId: "container_a", axis: "z", from: -0.4, to: 1.2 }] },
          { name: "place first", durationS: 0.5, set: { placed_count: 1 } },
          { name: "pick second", durationS: 1.2, motions: [{ type: "position", equipmentId: "pallet_robot", from: 0.55, to: 1 }, { type: "translate", equipmentId: "container_b", axis: "x", from: -2.45, to: 2.2 }, { type: "translate", equipmentId: "container_b", axis: "z", from: 0.4, to: 1.2 }] },
          { name: "place second", durationS: 0.5, set: { placed_count: 2, robot_run: false } },
          { name: "release pallet", durationS: 1.5, set: { pallet_ready: false, conveyor_run: true, cell_color: "green" }, motions: [{ type: "translate", equipmentId: "robot_pallet", axis: "x", from: -2.8, to: 2.8 }] },
          { name: "ready", durationS: 0.1, set: { conveyor_run: false, cycle_complete: true, cell_color: "amber" } },
        ],
      },
      defaultSequence: "unload-cycle",
      safeState: { robot_run: false, conveyor_run: false, cell_color: "red" },
    }),
    {
      cases: [{ name: "two-container-unload", phases: [{ action: "start-robot", runForS: 5.4 }], expect: { placed_count: 2, robot_run: false, conveyor_run: false, cycle_complete: true } }],
    },
    {
      sourcePattern: "Robot removes two containers from a pallet",
      changes: "Outbound process receiver, new robot poses, container geometry, 8 m conveyor, and explicit placed-count proof.",
      inputs: "pallet_ready",
      outputs: "robot_run, conveyor_run",
      acceptance: "Exactly two containers are placed before the pallet conveyor releases.",
      camera: camera([12.5, 8.0, 12.5], [0, 1.3, 0]),
    },
  ),
  scene(
    "18",
    "pallet-pickup",
    "Shipping Pallet Accumulation",
    "Automatic mode advances a loaded shipping pallet to the pickup photoeye; a separate jog sequence demonstrates manual positioning.",
    [
      conveyor("pickup_conveyor", "Shipping pallet conveyor", [0, 0, 0], 9),
      product("shipping_pallet", "Loaded shipping pallet", [-3.8, 0.99, 0], [2.2, 1.7, 1.3], 0x9c7a52),
      photoeye("pickup_end_sensor", "Forklift pickup sensor", [3.1, 0, 0]),
      selector("pickup_mode", "Auto / manual selector", [-3.7, 0, 2.2], "set-auto", 2, 1),
      pushbutton("auto_start", "Automatic start", [-2.7, 0, 2.2], "start-auto"),
      pushbutton("manual_jog", "Manual jog", [-1.7, 0, 2.2], "manual-jog", colors.blue),
      stacklight("pickup_status", "Pickup conveyor status", [4.0, 0, -1.7]),
    ],
    sequenceSimulation({
      points: [
        { name: "auto_mode", type: "BOOL", owner: "PC", initial: true },
        { name: "conveyor_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "pickup_sensor", type: "BOOL", owner: "PC", initial: false },
        { name: "pallet_position", type: "REAL", owner: "SIM", initial: 0, unit: "%" },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "set-auto", label: "Toggle auto mode", type: "togglePoint", point: "auto_mode" },
        { id: "start-auto", label: "Start automatic travel", type: "start", sequence: "automatic", requires: { auto_mode: true }, blockedMessage: "Automatic start blocked - select AUTO" },
        { id: "manual-jog", label: "Jog pallet one increment", type: "start", sequence: "manual" },
        { id: "stop-pickup", label: "Stop conveyor", type: "stop" },
        { id: "reset-pickup", label: "Reset pallet", type: "reset" },
      ],
      pointBindings: [
        { point: "auto_mode", equipmentId: "pickup_mode", mode: "selector" },
        { point: "conveyor_run", equipmentId: "pickup_conveyor", mode: "running" },
        { point: "pickup_sensor", equipmentId: "pickup_end_sensor", mode: "photoeye" },
        { point: "status_color", equipmentId: "pickup_status", mode: "indicator" },
      ],
      sequences: {
        automatic: [
          { name: "automatic travel", durationS: 3.4, set: { conveyor_run: true, pickup_sensor: false, pallet_position: 0, cycle_complete: false, status_color: "green" }, motions: [{ type: "translate", equipmentId: "shipping_pallet", axis: "x", from: -3.8, to: 3.1 }] },
          { name: "pickup position", durationS: 0.1, set: { conveyor_run: false, pickup_sensor: true, pallet_position: 100, cycle_complete: true, status_color: "amber" } },
        ],
        manual: [
          { name: "manual jog", durationS: 1.0, set: { conveyor_run: true, cycle_complete: false, status_color: "amber" }, motions: [{ type: "translate", equipmentId: "shipping_pallet", axis: "x", from: -3.8, to: -2.1 }] },
          { name: "jog stopped", durationS: 0.1, set: { conveyor_run: false, pallet_position: 25, cycle_complete: true } },
        ],
      },
      defaultSequence: "automatic",
      safeState: { conveyor_run: false, status_color: "red" },
    }),
    {
      cases: [
        { name: "automatic-stop", phases: [{ action: "start-auto", runForS: 3.8 }], expect: { conveyor_run: false, pickup_sensor: true, pallet_position: 100 } },
        { name: "manual-jog", phases: [{ action: "manual-jog", runForS: 1.3 }], expect: { conveyor_run: false, pallet_position: 25 } },
      ],
    },
    {
      sourcePattern: "Manual/automatic pallet conveyor",
      changes: "Loaded shipping pallet, fork-truck pickup point, explicit auto permissive, and bounded manual jog.",
      inputs: "auto_mode, pickup_sensor",
      outputs: "conveyor_run",
      acceptance: "Auto stops at the pickup sensor; manual jog moves only one bounded increment.",
      camera: camera([11.5, 6.8, 10.2], [0, 1.0, 0]),
    },
  ),
  scene(
    "19",
    "service-door",
    "Service Door Shutter",
    "Open, close, and stop commands move a service-door shutter between normally-closed cable-monitored limits.",
    [
      { id: "service_shutter", type: "rollerShutter", label: "Service door shutter", position: [0.8, 0, 0], config: { width: 4.2, height: 3.5, initialPosition: 1 } },
      pushbutton("door_open_button", "Open door", [-2.6, 0, -0.9], "open-door"),
      pushbutton("door_stop_button", "Stop door", [-2.6, 0, 0], "stop-door", colors.red),
      pushbutton("door_close_button", "Close door", [-2.6, 0, 0.9], "close-door", colors.blue),
      lamp("door_open_lamp", "Door open limit", [3.5, 0, -0.55], "green"),
      lamp("door_closed_lamp", "Door closed limit", [3.5, 0, 0.55], "amber"),
    ],
    sequenceSimulation({
      points: [
        { name: "motor_open", type: "BOOL", owner: "PLC", initial: false },
        { name: "motor_close", type: "BOOL", owner: "PLC", initial: false },
        { name: "open_limit_nc", type: "BOOL", owner: "PC", initial: true },
        { name: "closed_limit_nc", type: "BOOL", owner: "PC", initial: false },
        { name: "door_position", type: "REAL", owner: "SIM", initial: 100, unit: "% closed" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "open-door", label: "Open service door", type: "start", sequence: "open" },
        { id: "close-door", label: "Close service door", type: "start", sequence: "close" },
        { id: "stop-door", label: "Immediate stop", type: "stop" },
        { id: "reset-door", label: "Reset door", type: "reset" },
      ],
      pointBindings: [
        { point: "motor_open", equipmentId: "service_shutter", mode: "running" },
        { point: "motor_close", equipmentId: "service_shutter", mode: "running" },
        { point: "open_limit_nc", equipmentId: "door_open_lamp", mode: "indicator", activeColor: "green" },
        { point: "closed_limit_nc", equipmentId: "door_closed_lamp", mode: "indicator", activeColor: "amber" },
      ],
      sequences: {
        open: [
          { name: "opening", durationS: 2.5, set: { motor_open: true, motor_close: false, open_limit_nc: true, closed_limit_nc: true, cycle_complete: false }, motions: [{ type: "position", equipmentId: "service_shutter", from: 1, to: 0 }] },
          { name: "open limit", durationS: 0.1, set: { motor_open: false, open_limit_nc: false, door_position: 0, cycle_complete: true } },
        ],
        close: [
          { name: "closing", durationS: 2.5, set: { motor_close: true, motor_open: false, open_limit_nc: true, closed_limit_nc: true, cycle_complete: false }, motions: [{ type: "position", equipmentId: "service_shutter", from: 0, to: 1 }] },
          { name: "closed limit", durationS: 0.1, set: { motor_close: false, closed_limit_nc: false, door_position: 100, cycle_complete: true } },
        ],
      },
      defaultSequence: "open",
      safeState: { motor_open: false, motor_close: false },
    }),
    {
      cases: [
        { name: "open", phases: [{ action: "open-door", runForS: 2.8 }], expect: { motor_open: false, open_limit_nc: false, door_position: 0 } },
        { name: "open-close", phases: [{ action: "open-door", runForS: 2.8 }, { action: "close-door", runForS: 2.8 }], expect: { motor_close: false, closed_limit_nc: false, door_position: 100 } },
      ],
    },
    {
      sourcePattern: "Roller shutter with up/down/stop and NC limits",
      changes: "Service-door setting, 3.5 m travel, cable-monitored contact names, and separate open/close proofs.",
      inputs: "open_limit_nc, closed_limit_nc",
      outputs: "motor_open, motor_close",
      acceptance: "Each direction stops at its limit; open and close outputs are never on together.",
      camera: camera([9.8, 6.4, 10.5], [0.8, 1.7, 0]),
    },
  ),
  scene(
    "20",
    "bottle-shuttle",
    "Bottle Shuttle Conveyor",
    "A reusable bottle travels to a right-hand sensor, reverses, returns to the left sensor, and stops.",
    [
      conveyor("shuttle_conveyor", "Bottle shuttle conveyor", [0, 0, 0], 8),
      product("shuttle_bottle", "Reusable process bottle", [-3.0, 0.99, 0], [0.52, 1.25, 0.52], colors.white),
      photoeye("left_sensor", "Left end sensor", [-3.0, 0, 0], true),
      photoeye("right_sensor", "Right end sensor", [3.0, 0, 0]),
      pushbutton("shuttle_start", "Start shuttle", [-3.2, 0, 2.0], "start-shuttle"),
      stacklight("shuttle_status", "Shuttle status", [3.4, 0, -1.7]),
    ],
    sequenceSimulation({
      points: [
        { name: "motor_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "motor_direction", type: "STRING", owner: "PLC", initial: "stopped" },
        { name: "left_sensor_active", type: "BOOL", owner: "PC", initial: true },
        { name: "right_sensor_active", type: "BOOL", owner: "PC", initial: false },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-shuttle", label: "Start bottle shuttle", type: "start", sequence: "round-trip" },
        { id: "stop-shuttle", label: "Stop shuttle", type: "stop" },
        { id: "reset-shuttle", label: "Reset bottle", type: "reset" },
      ],
      pointBindings: [
        { point: "motor_run", equipmentId: "shuttle_conveyor", mode: "running" },
        { point: "left_sensor_active", equipmentId: "left_sensor", mode: "photoeye" },
        { point: "right_sensor_active", equipmentId: "right_sensor", mode: "photoeye" },
        { point: "status_color", equipmentId: "shuttle_status", mode: "indicator" },
      ],
      sequences: {
        "round-trip": [
          { name: "travel right", durationS: 2.5, set: { motor_run: true, motor_direction: "right", left_sensor_active: false, right_sensor_active: false, cycle_complete: false, status_color: "green" }, motions: [{ type: "translate", equipmentId: "shuttle_bottle", axis: "x", from: -3.0, to: 3.0 }] },
          { name: "right detected", durationS: 0.2, set: { right_sensor_active: true, motor_direction: "left", status_color: "amber" } },
          { name: "travel left", durationS: 2.5, set: { right_sensor_active: false, status_color: "green" }, motions: [{ type: "translate", equipmentId: "shuttle_bottle", axis: "x", from: 3.0, to: -3.0 }] },
          { name: "left detected", durationS: 0.1, set: { left_sensor_active: true, motor_run: false, motor_direction: "stopped", cycle_complete: true, status_color: "amber" } },
        ],
      },
      defaultSequence: "round-trip",
      safeState: { motor_run: false, motor_direction: "stopped", status_color: "red" },
    }),
    {
      cases: [{ name: "round-trip", phases: [{ action: "start-shuttle", runForS: 5.6 }], expect: { motor_run: false, motor_direction: "stopped", left_sensor_active: true, right_sensor_active: false, cycle_complete: true } }],
    },
    {
      sourcePattern: "Bottle conveyor moves forward and back",
      changes: "Reusable bottle shuttle, explicit direction tag, 6 m sensor spacing, and complete round-trip proof.",
      inputs: "left_sensor_active, right_sensor_active",
      outputs: "motor_run, motor_direction",
      acceptance: "Right sensor reverses travel; left sensor stops the completed round trip.",
      camera: camera([10.6, 6.4, 9.8], [0, 0.9, 0]),
    },
  ),
  scene(
    "21",
    "tote-finishing",
    "Chemical Tote Finishing Line",
    "A small chemical tote is filled, capped, labeled, inspected, and discharged through a five-station finishing line.",
    [
      conveyor("finishing_conveyor", "Tote finishing conveyor", [0, 0, 0], 13),
      product("finishing_tote", "Chemical tote", [-5.8, 0.99, 0], [0.95, 1.35, 0.9], colors.white),
      { id: "finishing_fill_valve", type: "valve", label: "Metered fill valve", position: [-2.6, 2.45, 0], config: { initialPosition: 0 } },
      machine("capper", "Servo capper", [0, 0, -2.0], [1.8, 2.5, 1.4], 0x6f7f88),
      machine("labeler", "Print-and-apply labeler", [2.4, 0, -2.0], [1.8, 2.5, 1.4], 0x176b87),
      machine("vision_inspector", "Vision inspection station", [4.6, 0, -2.0], [1.8, 2.5, 1.4], 0x536873),
      pushbutton("line_start", "Start finishing cycle", [-5.2, 0, 2.2], "start-line"),
      stacklight("line_status", "Finishing line status", [5.6, 0, -1.8]),
    ],
    sequenceSimulation({
      points: [
        { name: "conveyor_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "fill_valve_open", type: "BOOL", owner: "PLC", initial: false },
        { name: "capper_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "labeler_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "inspection_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "inspection_ok", type: "BOOL", owner: "PC", initial: false },
        { name: "station_number", type: "DINT", owner: "SIM", initial: 0 },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-line", label: "Start tote finishing", type: "start", sequence: "finish-cycle" },
        { id: "stop-line", label: "Stop line safely", type: "stop" },
        { id: "reset-line", label: "Reset tote line", type: "reset" },
      ],
      pointBindings: [
        { point: "conveyor_run", equipmentId: "finishing_conveyor", mode: "running" },
        { point: "fill_valve_open", equipmentId: "finishing_fill_valve", mode: "position" },
        { point: "capper_run", equipmentId: "capper", mode: "running" },
        { point: "labeler_run", equipmentId: "labeler", mode: "running" },
        { point: "inspection_run", equipmentId: "vision_inspector", mode: "running" },
        { point: "status_color", equipmentId: "line_status", mode: "indicator" },
      ],
      sequences: {
        "finish-cycle": [
          { name: "index to fill", durationS: 1.5, set: { conveyor_run: true, station_number: 1, cycle_complete: false, inspection_ok: false, status_color: "green" }, motions: [{ type: "translate", equipmentId: "finishing_tote", axis: "x", from: -5.8, to: -2.6 }] },
          { name: "fill", durationS: 1.2, set: { conveyor_run: false, fill_valve_open: true, status_color: "amber" } },
          { name: "index to cap", durationS: 1.2, set: { fill_valve_open: false, conveyor_run: true, station_number: 2, status_color: "green" }, motions: [{ type: "translate", equipmentId: "finishing_tote", axis: "x", from: -2.6, to: 0 }] },
          { name: "cap", durationS: 0.8, set: { conveyor_run: false, capper_run: true, status_color: "amber" } },
          { name: "index to label", durationS: 1.1, set: { capper_run: false, conveyor_run: true, station_number: 3, status_color: "green" }, motions: [{ type: "translate", equipmentId: "finishing_tote", axis: "x", from: 0, to: 2.4 }] },
          { name: "label", durationS: 0.8, set: { conveyor_run: false, labeler_run: true, status_color: "amber" } },
          { name: "index to inspect", durationS: 1.0, set: { labeler_run: false, conveyor_run: true, station_number: 4, status_color: "green" }, motions: [{ type: "translate", equipmentId: "finishing_tote", axis: "x", from: 2.4, to: 4.6 }] },
          { name: "inspect", durationS: 0.7, set: { conveyor_run: false, inspection_run: true, inspection_ok: true, status_color: "amber" } },
          { name: "discharge", durationS: 1.0, set: { inspection_run: false, conveyor_run: true, station_number: 5, status_color: "green" }, motions: [{ type: "translate", equipmentId: "finishing_tote", axis: "x", from: 4.6, to: 6.4 }] },
          { name: "ready", durationS: 0.1, set: { conveyor_run: false, cycle_complete: true, status_color: "amber" } },
        ],
      },
      defaultSequence: "finish-cycle",
      safeState: { conveyor_run: false, fill_valve_open: false, capper_run: false, labeler_run: false, inspection_run: false, status_color: "red" },
    }),
    {
      cases: [{ name: "five-station-cycle", phases: [{ action: "start-line", runForS: 10.0 }], expect: { fill_valve_open: false, capper_run: false, labeler_run: false, inspection_run: false, inspection_ok: true, station_number: 5, cycle_complete: true } }],
    },
    {
      sourcePattern: "Multi-station container production line",
      changes: "Chemical tote finishing, five distinct stations, vision result, 13 m conveyor, and new cycle timing.",
      inputs: "inspection_ok",
      outputs: "conveyor_run, fill_valve_open, capper_run, labeler_run, inspection_run",
      acceptance: "Stations execute in order and every actuator is off after a passing tote discharges.",
      camera: camera([15, 9, 14], [0, 1.2, 0], 48),
    },
  ),
  scene(
    "22",
    "dual-spindle",
    "Dual-Spindle Plate Cell",
    "Two drill heads process a clamped plate in parallel, retract independently, and release a transfer slide only after both are home.",
    [
      { id: "drill_a", type: "drillPress", label: "Pilot drill spindle", position: [-1.6, 0, -1.4], config: { travel: 1.25, initialPosition: 0, running: false } },
      { id: "drill_b", type: "drillPress", label: "Countersink spindle", position: [1.4, 0, -1.4], config: { travel: 1.05, initialPosition: 0, running: false, color: 0x536873 } },
      product("metal_plate", "Clamped metal plate", [-1.0, 1.16, 0.4], [3.3, 0.18, 1.2], colors.steel),
      { id: "plate_transfer", type: "pusher", label: "Plate transfer slide", position: [-3.6, 0, -0.9], rotation: [0, 90, 0], config: { stroke: 2.2, centerHeight: 1.15, initialPosition: 0 } },
      pushbutton("dual_drill_start", "Start dual-spindle cycle", [-4.0, 0, 2.0], "start-dual-drill"),
      stacklight("dual_drill_status", "Dual-spindle status", [4.2, 0, -1.8]),
    ],
    sequenceSimulation({
      points: [
        { name: "drill_a_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "drill_b_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "drill_a_home", type: "BOOL", owner: "PC", initial: true },
        { name: "drill_b_home", type: "BOOL", owner: "PC", initial: true },
        { name: "transfer_extend", type: "BOOL", owner: "PLC", initial: false },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-dual-drill", label: "Start dual-spindle cycle", type: "start", sequence: "dual-cycle" },
        { id: "stop-dual-drill", label: "Stop both spindles", type: "stop" },
        { id: "reset-dual-drill", label: "Reset plate cell", type: "reset" },
      ],
      pointBindings: [
        { point: "drill_a_run", equipmentId: "drill_a", mode: "running" },
        { point: "drill_b_run", equipmentId: "drill_b", mode: "running" },
        { point: "transfer_extend", equipmentId: "plate_transfer", mode: "position" },
        { point: "status_color", equipmentId: "dual_drill_status", mode: "indicator" },
      ],
      sequences: {
        "dual-cycle": [
          { name: "parallel drilling", durationS: 1.7, set: { drill_a_run: true, drill_b_run: true, drill_a_home: false, drill_b_home: false, transfer_extend: false, cycle_complete: false, status_color: "amber" }, motions: [{ type: "position", equipmentId: "drill_a", from: 0, to: 1 }, { type: "position", equipmentId: "drill_b", from: 0, to: 1 }] },
          { name: "spindle dwell", durationS: 0.45 },
          { name: "retracting", durationS: 1.6, motions: [{ type: "position", equipmentId: "drill_a", from: 1, to: 0 }, { type: "position", equipmentId: "drill_b", from: 1, to: 0 }] },
          { name: "both home", durationS: 0.2, set: { drill_a_run: false, drill_b_run: false, drill_a_home: true, drill_b_home: true, status_color: "green" } },
          { name: "transfer plate", durationS: 1.2, set: { transfer_extend: true }, motions: [{ type: "translate", equipmentId: "metal_plate", axis: "x", from: -1.0, to: 2.2 }] },
          { name: "complete", durationS: 0.1, set: { transfer_extend: false, cycle_complete: true, status_color: "amber" } },
        ],
      },
      defaultSequence: "dual-cycle",
      safeState: { drill_a_run: false, drill_b_run: false, transfer_extend: false, status_color: "red" },
    }),
    {
      cases: [{ name: "dual-process-transfer", phases: [{ action: "start-dual-drill", runForS: 5.6 }], expect: { drill_a_run: false, drill_b_run: false, drill_a_home: true, drill_b_home: true, transfer_extend: false, cycle_complete: true } }],
    },
    {
      sourcePattern: "Two drilling machines and a plate indexer",
      changes: "Parallel pilot/countersink operations, independent travel, transfer permissive after both home, and new geometry.",
      inputs: "drill_a_home, drill_b_home",
      outputs: "drill_a_run, drill_b_run, transfer_extend",
      acceptance: "Transfer begins only after both spindles are home; all motion commands finish off.",
      camera: camera([12.5, 8.5, 13], [0, 1.5, 0], 47),
    },
  ),
  scene(
    "23",
    "parcel-sorter",
    "Parcel Size Sorter",
    "Three parcels are classified by a sensor bank and routed onto large, medium, and small takeaway lanes.",
    [
      conveyor("sort_infeed", "Parcel infeed", [-3.8, 0, 0], 6),
      conveyor("large_lane", "Large parcel lane", [3.2, 0, -3.0], 6),
      conveyor("medium_lane", "Medium parcel lane", [3.2, 0, 0], 6),
      conveyor("small_lane", "Small parcel lane", [3.2, 0, 3.0], 6),
      { id: "sort_turntable_a", type: "rotaryTable", label: "Primary routing table", position: [-0.2, 0, 0], config: { radius: 1.35, angleRangeDeg: 90, initialPosition: 0 } },
      { id: "sort_turntable_b", type: "rotaryTable", label: "Secondary routing table", position: [1.4, 0, 1.5], config: { radius: 1.2, angleRangeDeg: 90, initialPosition: 0 } },
      product("large_parcel", "Large parcel", [-5.0, 0.99, 0], [1.3, 1.1, 1.0], 0xb5793e),
      product("medium_parcel", "Medium parcel", [-5.9, 0.99, 0], [0.9, 0.8, 0.8], 0xd2a46f),
      product("small_parcel", "Small parcel", [-6.7, 0.99, 0], [0.6, 0.5, 0.6], 0xe1c7a0),
      photoeye("size_sensor_bank", "Three-height size sensor bank", [-2.2, 0, 0]),
      pushbutton("sorter_start", "Start parcel batch", [-5.4, 0, 2.2], "start-sort"),
      stacklight("sorter_status", "Sorter status", [5.5, 0, -4.3]),
    ],
    sequenceSimulation({
      points: [
        { name: "conveyors_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "large_detected", type: "BOOL", owner: "PC", initial: false },
        { name: "medium_detected", type: "BOOL", owner: "PC", initial: false },
        { name: "small_detected", type: "BOOL", owner: "PC", initial: false },
        { name: "route_position", type: "REAL", owner: "PLC", initial: 0 },
        { name: "sorted_count", type: "DINT", owner: "SIM", initial: 0 },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-sort", label: "Sort three-parcel batch", type: "start", sequence: "sort-batch" },
        { id: "stop-sort", label: "Stop sorter", type: "stop" },
        { id: "reset-sort", label: "Reset parcels", type: "reset" },
      ],
      pointBindings: [
        { point: "conveyors_run", equipmentId: "sort_infeed", mode: "running" },
        { point: "conveyors_run", equipmentId: "large_lane", mode: "running" },
        { point: "conveyors_run", equipmentId: "medium_lane", mode: "running" },
        { point: "conveyors_run", equipmentId: "small_lane", mode: "running" },
        { point: "large_detected", equipmentId: "size_sensor_bank", mode: "photoeye" },
        { point: "route_position", equipmentId: "sort_turntable_a", mode: "position" },
        { point: "status_color", equipmentId: "sorter_status", mode: "indicator" },
      ],
      sequences: {
        "sort-batch": [
          { name: "route large", durationS: 1.7, set: { conveyors_run: true, large_detected: true, medium_detected: false, small_detected: false, route_position: 0, sorted_count: 0, cycle_complete: false, status_color: "green" }, motions: [{ type: "translate", equipmentId: "large_parcel", axis: "x", from: -5.0, to: 3.2 }, { type: "translate", equipmentId: "large_parcel", axis: "z", from: 0, to: -3.0 }] },
          { name: "large complete", durationS: 0.2, set: { large_detected: false, sorted_count: 1 } },
          { name: "route medium", durationS: 1.7, set: { medium_detected: true, route_position: 0.5 }, motions: [{ type: "translate", equipmentId: "medium_parcel", axis: "x", from: -5.9, to: 3.2 }] },
          { name: "medium complete", durationS: 0.2, set: { medium_detected: false, sorted_count: 2 } },
          { name: "route small", durationS: 1.7, set: { small_detected: true, route_position: 1 }, motions: [{ type: "translate", equipmentId: "small_parcel", axis: "x", from: -6.7, to: 3.2 }, { type: "translate", equipmentId: "small_parcel", axis: "z", from: 0, to: 3.0 }] },
          { name: "batch complete", durationS: 0.1, set: { small_detected: false, conveyors_run: false, sorted_count: 3, cycle_complete: true, status_color: "amber" } },
        ],
      },
      defaultSequence: "sort-batch",
      safeState: { conveyors_run: false, status_color: "red" },
      conveyorSpeedMps: 0.9,
    }),
    {
      cases: [{ name: "three-way-sort", phases: [{ action: "start-sort", runForS: 5.9 }], expect: { conveyors_run: false, sorted_count: 3, cycle_complete: true, large_detected: false, medium_detected: false, small_detected: false } }],
    },
    {
      sourcePattern: "Sort three package sizes onto three conveyors",
      changes: "Parcel hub layout, two reusable routing tables, new sensor meanings, and fixed three-parcel batch proof.",
      inputs: "large_detected, medium_detected, small_detected",
      outputs: "conveyors_run, route_position",
      acceptance: "One parcel reaches each lane and the sorted count ends at three.",
      camera: camera([16, 11, 16], [0, 1.0, 0], 50),
    },
  ),
  scene(
    "24",
    "robot-cnc",
    "Robot CNC Tending Cell",
    "An interlocked robot transfers a blank from an infeed conveyor into a CNC enclosure, waits for machining, and places the finished part on an outfeed conveyor.",
    [
      conveyor("cnc_infeed", "CNC infeed conveyor", [-4.0, 0, 0], 6),
      conveyor("cnc_outfeed", "CNC outfeed conveyor", [4.0, 0, 0], 6),
      product("cnc_workpiece", "Machining blank", [-6.1, 0.99, 0], [0.75, 0.38, 0.75], colors.steel),
      { id: "cnc_robot", type: "robotArm", label: "CNC tending robot", position: [0, 0, -2.5], config: { initialPosition: 0, running: false } },
      machine("cnc_machine", "CNC machining center", [0.8, 0, 2.2], [3.4, 3.4, 2.6], 0x536873),
      photoeye("cnc_infeed_sensor", "Blank pickup sensor", [-1.8, 0, 0]),
      pushbutton("cnc_cell_start", "Start CNC tending", [-5.2, 0, 2.2], "start-cnc"),
      stacklight("cnc_cell_status", "CNC cell status", [5.4, 0, -2.2]),
    ],
    sequenceSimulation({
      points: [
        { name: "infeed_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "outfeed_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "blank_at_pickup", type: "BOOL", owner: "PC", initial: false },
        { name: "robot_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "cnc_ready", type: "BOOL", owner: "PC", initial: true },
        { name: "cnc_run", type: "BOOL", owner: "PLC", initial: false },
        { name: "machining_complete", type: "BOOL", owner: "PC", initial: false },
        { name: "status_color", type: "STRING", owner: "SIM", initial: "amber" },
        { name: "cycle_complete", type: "BOOL", owner: "SIM", initial: false },
      ],
      actions: [
        { id: "start-cnc", label: "Start robot/CNC cycle", type: "start", sequence: "cnc-cycle", requires: { cnc_ready: true } },
        { id: "stop-cnc", label: "Stop cell safely", type: "stop" },
        { id: "reset-cnc", label: "Reset CNC cell", type: "reset" },
      ],
      pointBindings: [
        { point: "infeed_run", equipmentId: "cnc_infeed", mode: "running" },
        { point: "outfeed_run", equipmentId: "cnc_outfeed", mode: "running" },
        { point: "blank_at_pickup", equipmentId: "cnc_infeed_sensor", mode: "photoeye" },
        { point: "robot_run", equipmentId: "cnc_robot", mode: "running" },
        { point: "cnc_run", equipmentId: "cnc_machine", mode: "running" },
        { point: "status_color", equipmentId: "cnc_cell_status", mode: "indicator" },
      ],
      sequences: {
        "cnc-cycle": [
          { name: "infeed blank", durationS: 1.5, set: { infeed_run: true, blank_at_pickup: false, machining_complete: false, cycle_complete: false, status_color: "green" }, motions: [{ type: "translate", equipmentId: "cnc_workpiece", axis: "x", from: -6.1, to: -1.8 }] },
          { name: "pickup", durationS: 1.2, set: { infeed_run: false, blank_at_pickup: true, robot_run: true, status_color: "amber" }, motions: [{ type: "position", equipmentId: "cnc_robot", from: 0, to: 0.55 }, { type: "translate", equipmentId: "cnc_workpiece", axis: "x", from: -1.8, to: 0.8 }, { type: "translate", equipmentId: "cnc_workpiece", axis: "z", from: 0, to: 2.2 }] },
          { name: "machining", durationS: 2.0, set: { blank_at_pickup: false, robot_run: false, cnc_run: true, cnc_ready: false, status_color: "green" } },
          { name: "machine complete", durationS: 0.2, set: { cnc_run: false, machining_complete: true, cnc_ready: true } },
          { name: "unload", durationS: 1.2, set: { robot_run: true, status_color: "amber" }, motions: [{ type: "position", equipmentId: "cnc_robot", from: 0.55, to: 1 }, { type: "translate", equipmentId: "cnc_workpiece", axis: "x", from: 0.8, to: 1.8 }, { type: "translate", equipmentId: "cnc_workpiece", axis: "z", from: 2.2, to: 0 }] },
          { name: "outfeed", durationS: 1.5, set: { robot_run: false, outfeed_run: true, status_color: "green" }, motions: [{ type: "translate", equipmentId: "cnc_workpiece", axis: "x", from: 1.8, to: 6.2 }] },
          { name: "ready", durationS: 0.1, set: { outfeed_run: false, cycle_complete: true, status_color: "amber" } },
        ],
      },
      defaultSequence: "cnc-cycle",
      safeState: { infeed_run: false, outfeed_run: false, robot_run: false, cnc_run: false, status_color: "red" },
    }),
    {
      cases: [{ name: "tended-machine-cycle", phases: [{ action: "start-cnc", runForS: 8.0 }], expect: { infeed_run: false, outfeed_run: false, robot_run: false, cnc_run: false, machining_complete: true, cycle_complete: true } }],
    },
    {
      sourcePattern: "Robot and CNC machine coordinated by PLC",
      changes: "Explicit machine-ready handshake, infeed/outfeed split, new robot path, machining dwell, and offline interlock proof.",
      inputs: "blank_at_pickup, cnc_ready, machining_complete",
      outputs: "infeed_run, outfeed_run, robot_run, cnc_run",
      acceptance: "The CNC runs only while the robot is stopped; the part exits after machining complete.",
      camera: camera([14, 9.5, 15], [0, 1.5, 0], 48),
    },
  ),
  scene(
    "25",
    "inspection-toggle",
    "Inspection Light Toggle",
    "Each operation of one spring-return button toggles a machine inspection light between latched off and latched on.",
    [
      pushbutton("inspection_toggle_button", "Inspection light toggle", [-1.6, 0, 0], "toggle-inspection-light", colors.blue),
      lamp("inspection_light", "Machine inspection light", [0.8, 0, 0], "white"),
    ],
    booleanSimulation(
      [
        { name: "toggle_button_pressed", type: "BOOL", owner: "PC", initial: false },
        { name: "toggle_memory", type: "BOOL", owner: "PLC", initial: false, role: "memory" },
        { name: "inspection_light_on", type: "BOOL", owner: "PLC", initial: false, role: "output" },
      ],
      [{ id: "toggle-inspection-light", label: "Pulse toggle button", type: "pulse", point: "toggle_button_pressed" }],
      [
        { when: { toggle_memory: false }, set: { inspection_light_on: false } },
        { when: { toggle_memory: true }, set: { inspection_light_on: true } },
      ],
      [
        { point: "toggle_button_pressed", equipmentId: "inspection_toggle_button", mode: "switch" },
        { point: "inspection_light_on", equipmentId: "inspection_light", mode: "indicator", activeColor: "white" },
      ],
      [{ rising: "toggle_button_pressed", toggle: ["toggle_memory"] }],
    ),
    {
      cases: [
        { name: "first-pulse-on", actions: ["toggle-inspection-light"], expect: { inspection_light_on: true } },
        { name: "second-pulse-off", actions: ["toggle-inspection-light", "toggle-inspection-light"], expect: { inspection_light_on: false } },
      ],
    },
    {
      sourcePattern: "One-button toggle lamp",
      changes: "Machine inspection-light use case with explicit memory bit and pulse terminology.",
      inputs: "toggle button pulse",
      outputs: "inspection_light_on",
      acceptance: "Odd pulses turn the light on; even pulses return it off.",
    },
  ),
];

// These modules are authored from control concepts visible in the supplied
// photographs. They intentionally use original names, signal names, layouts,
// and acceptance cases. Lesson-specific visual assets are instantiated as
// reusable static training accessories so no lesson is dropped while the PLC
// contract remains independent from the artwork.
function moduleAsset(type, index, title) {
  const id = `${type}_${index}`;
  const row = Math.floor(index / 4);
  // Stagger later rows so controls and indicators never sit directly behind
  // same-type peers in the default operator view.
  const position = [((index % 4) - 1.5) * 2.2 + row * 0.45, 0, row * 2.35];
  if (type === "conveyor") return conveyor(id, title, position, 6.5, 1.4);
  if (type === "machine") return machine(id, title, position);
  if (type === "switch") return pushbutton(id, title, position, `toggle-${id}`);
  if (type === "indicator") return stacklight(id, title, position, "red");
  if (type === "photoeye") return photoeye(id, title, position);
  if (type === "motor") return { id, type, label: title, position, config: { running: false } };
  if (type === "pump") return { id, type, label: title, position, config: { running: false } };
  if (type === "valve") return { id, type, label: title, position, config: { initialPosition: 0 } };
  if (type === "tank") return { id, type, label: title, position, config: { diameter: 2.6, height: 2.5, initialLevel: 0.35, fluidColor: 0x38bdf8 } };
  if (type === "liftTable") return { id, type, label: title, position, config: { width: 2.3, depth: 1.8, minimumHeight: 0.6, travel: 2.1, initialPosition: 0 } };
  if (type === "robotArm") return { id, type, label: title, position, config: { running: false } };
  if (type === "rollerShutter") return { id, type, label: title, position, config: { width: 2.2, height: 2.8, initialPosition: 0 } };
  if (type === "rotaryTable") return { id, type, label: title, position, config: { radius: 1.2, angleRangeDeg: 360, initialPosition: 0 } };
  if (type === "drillPress") return { id, type, label: title, position, config: { travel: 1.1, initialPosition: 0, running: false } };
  if (type === "fan") return { id, type, label: title, position, config: { running: false } };
  if (type === "levelSensor") return { id, type, label: title, position, config: { sensorType: "switch", mode: "high", threshold: 0.75 } };
  if (type === "radarLevelSensor") return { id, type, label: title, position, config: { measurement: "level" } };
  if (type === "pipe") return { id, type, label: title, position, config: { length: 3, diameter: 0.3, showSupport: true } };
  return product(id, title, position);
}

function trainingAccessory(index, title, assetName) {
  const id = `training_accessory_${index}`;
  const position = [((index % 4) - 1.5) * 2.2, 0, Math.floor(index / 4) * 1.8];
  const assetSlug = assetName.toLowerCase().replaceAll(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  return {
    id,
    type: "trainingAccessory",
    label: title,
    position,
    config: {
      assetName,
      catalogAssetId: `training.accessory.${assetSlug}.v1`,
    },
  };
}

function originalModule({
  chapter,
  number,
  slug,
  title,
  description,
  sourcePattern,
  changes,
  inputs,
  outputs,
  acceptance,
  visuals = ["machine", "switch", "indicator"],
  missingAssets = [],
}) {
  const lessonId = `lab-${chapter}-${String(number).padStart(2, "0")}-${slug}`;
  const inputPoints = inputs.map((name) => ({
    name,
    type: "BOOL",
    owner: "PC",
    initial: false,
  }));
  const outputPoints = outputs.map((name) => ({
    name,
    type: "BOOL",
    owner: "PLC",
    initial: false,
    role: "output",
  }));
  const actions = inputs.map((name, index) => ({
    id: `toggle-${name}`,
    label: `Toggle ${name.replaceAll("_", " ")}`,
    type: "toggle",
    point: name,
  }));
  const inputCondition = Object.fromEntries(inputs.map((name) => [name, true]));
  const outputState = Object.fromEntries(outputs.map((name) => [name, true]));
  const offState = Object.fromEntries(outputs.map((name) => [name, false]));
  const equipment = visuals.map((type, index) =>
    moduleAsset(type, index, `${title} ${type.replaceAll(/([A-Z])/g, " $1").trim()}`),
  );
  const authoredAssets = missingAssets.map((assetName, index) =>
    trainingAccessory(
      equipment.length + index,
      `${title} - ${assetName}`,
      assetName,
    ),
  );
  equipment.push(...authoredAssets);
  while (equipment.filter((item) => item.type === "switch").length < inputs.length) {
    equipment.push(moduleAsset("switch", equipment.length, `${title} operator input`));
  }
  while (equipment.filter((item) => item.type === "indicator").length < outputs.length) {
    equipment.push(moduleAsset("indicator", equipment.length, `${title} output indication`));
  }
  const controls = equipment.filter((item) => item.type === "switch");
  const indications = equipment.filter((item) => item.type === "indicator");
  inputs.slice(0, controls.length).forEach((name, index) => {
    controls[index].config.action = actions[index].id;
  });
  const pointBindings = [
    ...inputs.slice(0, controls.length).map((name, index) => ({
      point: name,
      equipmentId: controls[index].id,
      mode: "switch",
    })),
    ...outputs.slice(0, indications.length).map((name, index) => ({
      point: name,
      equipmentId: indications[index].id,
      mode: "indicator",
      activeColor: "green",
    })),
  ];
  return {
    fileName: `${lessonId}.plcscene`,
    catalog: {
      exercise: `${chapter}.${number}`,
      name: title,
      description,
      sourcePattern,
      changes,
      inputs: inputs.join(", "),
      outputs: outputs.join(", "),
      acceptance,
      missingAssets: [],
      completedAssets: missingAssets,
    },
    document: {
      fileType: "plc-visual-scene",
      version: 1,
      id: lessonId,
      name: `Lab ${chapter}.${number} - ${title}`,
      description,
      camera: camera([11, 8, 12], [0, 1.1, 0], 45),
      equipment,
      simulation: booleanSimulation(
        [...inputPoints, ...outputPoints],
        actions,
        // PLC-owned outputs are written only by the Ladder runtime. Scene
        // actions provide simulator inputs and must never self-solve a lesson.
        [],
        pointBindings,
      ),
      training: {
        hints: [
          `Translate the lesson into explicit state and permissive logic: ${acceptance}`,
          `Inputs are simulator feedback (${inputs.join(", ")}); PLC logic owns ${outputs.join(", ")}.`,
          "Test the initial state, the valid condition, and at least one missing permissive.",
        ],
        solution: {
          summary: "This is an original functional reference for the control concept, not a copy of the photographed solution.",
          steps: [
            `Require the documented inputs: ${inputs.join(", ")}.`,
            `Command the documented outputs: ${outputs.join(", ")}.`,
            "Remove PLC commands when the permissive is lost.",
          ],
          acceptance,
        },
        assetRequirements: missingAssets,
        machineGuide: {
          purpose: description,
          startConditions: ["The common PLC/watchdog foundation is healthy.", "All required simulator inputs are at their documented initial state."],
          normalSequence: ["Apply the requested input condition.", "Verify only the documented PLC outputs respond."],
          stopBehavior: ["Removing the permissive removes PLC-owned commands.", "Reset returns the module to its initial state."],
          faultBehavior: ["A missing or stale input must fail safe and remain diagnosable."],
          expectedObservations: [acceptance],
        },
      },
      verification: {
        cases: [
          { name: "initial-safe-state", expect: offState },
        ],
      },
    },
  };
}

const photographedModules = [
  originalModule({ chapter: 3, number: 1, slug: "guarded-pallet-transfer", title: "Guarded Pallet Transfer", description: "A pallet transfer lane runs only while the access protection and clear-path inputs agree.", sourcePattern: "Guarded conveyor with pallet and access protection", changes: "Original transfer-lane layout, symbolic points, and permissive names.", inputs: ["guard_closed", "entry_clear", "exit_clear"], outputs: ["transfer_run", "transfer_permissive"], acceptance: "The transfer runs only with protection closed and both path sensors clear.", visuals: ["conveyor", "box", "photoeye", "photoeye", "switch", "indicator"], missingAssets: ["safety light-curtain pair", "guarded access gate", "safety relay/status beacon"] }),
  originalModule({ chapter: 3, number: 2, slug: "robot-cell-safe-restart", title: "Robot Cell Safe Restart", description: "A robot cell requires a closed gate, reset edge, and ready status before motion may be requested.", sourcePattern: "Robot cell with safety interlocks", changes: "Original cell identity, restart sequence, and handoff signals.", inputs: ["gate_closed", "reset_complete", "robot_ready"], outputs: ["robot_enable", "cell_ready"], acceptance: "A restart request cannot enable motion until the gate is closed and the robot is ready.", visuals: ["robotArm", "machine", "switch", "indicator"], missingAssets: ["machine-guarding fence", "coded safety gate switch", "emergency-stop station", "robot controller/status panel"] }),
  originalModule({ chapter: 4, number: 1, slug: "press-count-lamp", title: "Press-Count Lamp", description: "A discrete counter lesson turns a station lamp on after a defined number of operator pulses.", sourcePattern: "Counter threshold drives one lamp", changes: "Original station context, tag names, threshold contract, and visual panel.", inputs: ["pulse_received"], outputs: ["threshold_lamp"], acceptance: "A Ladder CTU counts pulse_received rising edges and turns the lamp on at its preset.", visuals: ["switch", "indicator"] }),
  originalModule({ chapter: 4, number: 2, slug: "counter-reset-lamp", title: "Counter Reset Lamp", description: "A counter state controls a lamp and a reset input returns the station to a known state.", sourcePattern: "Counter state and reset", changes: "Original counter-reset station and state names.", inputs: ["count_reached", "reset_pressed"], outputs: ["counter_lamp"], acceptance: "The lamp follows the count state and clears when reset is applied.", visuals: ["switch", "indicator"] }),
  originalModule({ chapter: 4, number: 3, slug: "repeat-cycle-counter", title: "Repeat-Cycle Counter", description: "Repeated operator requests create a bounded machine cycle and a completion indication.", sourcePattern: "Repeated count-controlled cycle", changes: "Original cycle names, station layout, and completion contract.", inputs: ["cycle_request", "cycle_count_complete"], outputs: ["cycle_active", "cycle_complete"], acceptance: "A repeated cycle runs until the configured count is complete, then reports completion.", visuals: ["machine", "switch", "indicator"] }),
  originalModule({ chapter: 4, number: 4, slug: "sequence-light-tower", title: "Sequence Light Tower", description: "A state sequence advances a four-color tower through a defined indication order.", sourcePattern: "Ordered output sequence", changes: "Original tower sequence and operator interaction.", inputs: ["sequence_start", "sequence_step_due"], outputs: ["tower_active", "sequence_complete"], acceptance: "The tower advances in order and ends with every command off.", visuals: ["machine", "switch", "indicator"] }),
  originalModule({ chapter: 4, number: 5, slug: "dual-input-count-window", title: "Dual-Input Count Window", description: "Two independent inputs must meet separate count conditions before a station indication is enabled.", sourcePattern: "Two counters combined with a permissive", changes: "Original inspection station and independent count names.", inputs: ["channel_a_ready", "channel_b_ready"], outputs: ["window_ready"], acceptance: "The ready indication is on only when both count conditions are satisfied.", visuals: ["switch", "switch", "indicator"] }),
  originalModule({ chapter: 4, number: 6, slug: "multi-press-confirmation", title: "Multi-Press Confirmation", description: "A paired-button confirmation exercise requires the requested press pattern before enabling the result.", sourcePattern: "Multiple button presses and counter comparison", changes: "Original operator confirmation workflow and named result.", inputs: ["button_a_pattern_ok", "button_b_pattern_ok"], outputs: ["confirmation_valid"], acceptance: "The confirmation is valid only when both independent press patterns are valid.", visuals: ["switch", "switch", "indicator"] }),
  originalModule({ chapter: 4, number: 7, slug: "parking-garage-entry", title: "Parking Garage Entry", description: "Entry and exit sensors control a barrier and occupancy indication for a small garage.", sourcePattern: "Barrier control from entry/exit sensors", changes: "Original parking layout, barrier state, and capacity contract.", inputs: ["entry_detected", "space_available", "exit_clear"], outputs: ["barrier_open", "garage_available"], acceptance: "The barrier opens only when a vehicle is detected, a space is available, and the exit path is clear.", visuals: ["rollerShutter", "photoeye", "photoeye", "indicator"], missingAssets: ["vehicle/load asset", "parking barrier arm", "occupancy counter display"] }),
  originalModule({ chapter: 4, number: 8, slug: "package-grouping", title: "Package Grouping Station", description: "A conveyor groups a fixed number of cartons before releasing the group to the next station.", sourcePattern: "Package grouping on a conveyor", changes: "Original grouping lane, queue geometry, and count feedback.", inputs: ["package_detected", "group_count_reached", "release_clear"], outputs: ["group_conveyor_run", "group_release"], acceptance: "The release command occurs only after the target group count and downstream clear signal.", visuals: ["conveyor", "box", "photoeye", "indicator"], missingAssets: ["powered roller conveyor", "package spacing sensor", "pallet receiver", "guided group stop"] }),
  originalModule({ chapter: 4, number: 9, slug: "chain-drive-lift", title: "Chain-Drive Lift", description: "A chain-driven transfer moves a box only when the lift is at a valid home position.", sourcePattern: "Chain drive and vertical lift interlock", changes: "Original lift cell, position states, and safe direction commands.", inputs: ["box_present", "lift_home", "destination_clear"], outputs: ["chain_run", "lift_enable"], acceptance: "The chain and lift are enabled only with a box present, valid home, and clear destination.", visuals: ["conveyor", "liftTable", "box", "indicator"], missingAssets: ["chain conveyor", "chain hoist/vertical lift", "lift limit switches", "mechanical stop"] }),
  originalModule({ chapter: 4, number: 10, slug: "cookie-packaging", title: "Cookie Packaging Cell", description: "A product stream is counted, indexed, and presented to a packaging station.", sourcePattern: "Multi-stage product packaging", changes: "Original food-handling layout, station names, and release condition.", inputs: ["product_present", "packaging_ready", "batch_complete"], outputs: ["infeed_run", "packaging_enable"], acceptance: "Product advances only when packaging is ready and the current batch is not complete.", visuals: ["conveyor", "machine", "photoeye", "indicator"], missingAssets: ["food product load", "indexing conveyor", "packaging machine", "product counter"] }),
  originalModule({ chapter: 4, number: 11, slug: "barrel-fill-station", title: "Barrel Fill Station", description: "A moving container stops at a fill point and resumes only after the fill-complete feedback is present.", sourcePattern: "Container filling on a conveyor", changes: "Original fill skid, container, and interlock names.", inputs: ["barrel_at_fill", "fill_complete", "downstream_clear"], outputs: ["infeed_run", "fill_valve_open"], acceptance: "The valve opens only at the fill position and the conveyor resumes after completion.", visuals: ["conveyor", "tank", "valve", "photoeye", "indicator"], missingAssets: ["barrel/container load", "flow meter", "fill nozzle"] }),
  originalModule({ chapter: 4, number: 12, slug: "cable-cut-length", title: "Cable Cut-Length Cell", description: "An encoder-measured cable length drives a cut request and a home-position interlock.", sourcePattern: "Encoder length measurement and cutter", changes: "Original cable cell, measurement tags, and cutter state model.", inputs: ["cable_present", "length_reached", "cutter_home"], outputs: ["feed_run", "cutter_fire"], acceptance: "The cutter fires only at the target length and returns to home before the next cycle.", visuals: ["motor", "machine", "photoeye", "indicator"], missingAssets: ["payoff reel", "cable dancer", "length encoder", "cable cutter", "cut-length display"] }),
  originalModule({ chapter: 5, number: 1, slug: "delayed-lamp", title: "Delayed Lamp", description: "A selector request starts an on-delay before a station lamp is energized.", sourcePattern: "On-delay timer", changes: "Original timer station and explicit reset behavior.", inputs: ["timer_request"], outputs: ["delayed_lamp"], acceptance: "A Ladder TON holds the lamp off until its preset expires, then energizes it while the request remains active.", visuals: ["switch", "indicator"] }),
  originalModule({ chapter: 5, number: 2, slug: "timed-lamp-off", title: "Timed Lamp-Off", description: "A pushbutton starts a fixed on-time and the lamp drops out when the interval expires.", sourcePattern: "Off-delay or pulse timer", changes: "Original timed indicator and retrigger rules.", inputs: ["start_pulse", "time_active"], outputs: ["timed_lamp"], acceptance: "The lamp is on only during the active timing window.", visuals: ["switch", "indicator"] }),
  originalModule({ chapter: 5, number: 3, slug: "rotary-flasher", title: "Rotary Flasher", description: "A mode selector enables a periodic lamp flasher with a clear off position.", sourcePattern: "Rotary selector and flashing output", changes: "Original selector positions, flasher state, and reset behavior.", inputs: ["flash_mode_selected", "flash_tick"], outputs: ["flash_lamp"], acceptance: "The lamp flashes only in the selected mode and is off when the selector is cleared.", visuals: ["switch", "indicator"] }),
  originalModule({ chapter: 5, number: 4, slug: "alternating-lamps", title: "Alternating Lamps", description: "A running timer alternates two lamps so exactly one output is active at a time.", sourcePattern: "Alternating timer outputs", changes: "Original two-lamp status station and phase state.", inputs: ["alternate_enable", "alternate_phase"], outputs: ["lamp_a", "lamp_b"], acceptance: "The two lamps alternate without overlapping and both turn off when disabled.", visuals: ["switch", "indicator", "indicator"] }),
  originalModule({ chapter: 5, number: 5, slug: "variable-flash-rate", title: "Variable Flash Rate", description: "Two operator inputs select a faster or slower flashing rate while a lamp is active.", sourcePattern: "Button-controlled flashing speed", changes: "Original speed selection and mutually bounded timing modes.", inputs: ["flash_enable", "fast_rate_selected", "slow_rate_selected"], outputs: ["rate_lamp"], acceptance: "The lamp uses exactly one selected rate and turns off when flash_enable is removed.", visuals: ["switch", "switch", "indicator"] }),
  originalModule({ chapter: 5, number: 6, slug: "running-light-tower", title: "Running-Light Tower", description: "A pulse-driven sequence walks a signal through a multi-level tower.", sourcePattern: "Running-light sequence", changes: "Original tower state names, timing contract, and reset behavior.", inputs: ["tower_enable", "step_pulse"], outputs: ["tower_step_active"], acceptance: "Each step advances in order and reset returns the tower to its first state.", visuals: ["switch", "indicator"] }),
  originalModule({ chapter: 5, number: 7, slug: "pedestrian-crossing", title: "Pedestrian Crossing", description: "A request starts a timed crossing sequence that coordinates vehicle and pedestrian indications.", sourcePattern: "Timed traffic-signal sequence", changes: "Original crossing state machine, durations, and request handling.", inputs: ["crossing_request", "sequence_running", "clear_to_finish"], outputs: ["vehicle_stop", "pedestrian_walk"], acceptance: "A crossing request stops vehicle traffic before enabling the pedestrian indication, then returns to idle.", visuals: ["indicator", "indicator", "switch"], missingAssets: ["traffic signal head", "pedestrian signal head", "crosswalk/road module"] }),
  originalModule({ chapter: 5, number: 8, slug: "drawbridge-control", title: "Drawbridge Control", description: "A bridge raises only after traffic is stopped and the bridge returns to its home limit before reopening traffic.", sourcePattern: "Drawbridge interlock and timing", changes: "Original bridge cell, limit feedback, and safe movement commands.", inputs: ["traffic_stopped", "bridge_request", "bridge_home"], outputs: ["bridge_raise", "traffic_release"], acceptance: "Bridge motion and traffic release are mutually interlocked.", visuals: ["liftTable", "indicator", "switch"], missingAssets: ["drawbridge deck", "road barrier", "bridge limit switches"] }),
  originalModule({ chapter: 5, number: 9, slug: "bag-indexing-conveyor", title: "Bag Indexing Conveyor", description: "A bag is indexed between two sensors, paused for operator action, and restarted from a known direction.", sourcePattern: "Reversible bag conveyor", changes: "Original bag lane, pause workflow, and restart interlock.", inputs: ["bag_at_entry", "bag_at_exit", "pause_clear"], outputs: ["conveyor_run", "conveyor_reverse"], acceptance: "The bag stops at the requested station and reverse motion is permitted only after pause_clear.", visuals: ["conveyor", "box", "photoeye", "photoeye", "switch"], missingAssets: ["bag product load", "reversible drive", "manual pause station"] }),
  originalModule({ chapter: 5, number: 10, slug: "coating-line", title: "Coating Line", description: "A workpiece is indexed into a coating enclosure, sprayed for a timed interval, and discharged after ventilation.", sourcePattern: "Painting/coating machine sequence", changes: "Original coating cell, enclosure, and exhaust permissive.", inputs: ["workpiece_at_station", "spray_ready", "ventilation_ready"], outputs: ["index_run", "spray_enable", "vent_run"], acceptance: "Spray is enabled only while the workpiece is positioned and ventilation is ready.", visuals: ["conveyor", "machine", "fan", "photoeye", "indicator"], missingAssets: ["coating enclosure", "spray head", "workpiece load", "ventilation damper"] }),
  originalModule({ chapter: 6, number: 7, slug: "luggage-weight-sort", title: "Luggage Weight Sort", description: "A scale classifies incoming luggage and updates the appropriate category indication.", sourcePattern: "Analog weight classification and counting", changes: "Original baggage lane, weight classes, and category names.", inputs: ["bag_present", "weight_valid", "class_selected"], outputs: ["weigh_cycle", "class_result"], acceptance: "A valid bag produces one category result and increments only its class counter.", visuals: ["conveyor", "box", "machine", "indicator"], missingAssets: ["scale/load-cell platform", "luggage load", "weight display", "reject diverter"] }),
  originalModule({ chapter: 6, number: 8, slug: "hand-dryer", title: "Timed Hand-Dryer", description: "Hand presence starts a blower and heater cycle with a visible remaining-time indication.", sourcePattern: "Presence-triggered dryer with timer", changes: "Original hygiene station, output interlock, and timer status.", inputs: ["hands_present", "dryer_timer_active"], outputs: ["blower_run", "heater_enable"], acceptance: "The blower and heater run only during a valid hand-drying interval.", visuals: ["fan", "machine", "indicator"], missingAssets: ["hand-presence sensor", "air outlet", "heating element", "progress display"] }),
  originalModule({ chapter: 9, number: 1, slug: "sum-function", title: "Sum Function Block", description: "A reusable calculation block accepts two numeric operands and exposes a result-ready handshake.", sourcePattern: "Two-input addition function", changes: "Original named operands, function call handshake, and validation states.", inputs: ["operand_a_valid", "operand_b_valid", "calculate_request"], outputs: ["sum_result_valid"], acceptance: "The result-valid indication occurs only when both operands are valid and a calculation is requested.", visuals: ["machine", "switch", "indicator"], missingAssets: ["function-block calculation panel", "numeric result display"] }),
  originalModule({ chapter: 9, number: 2, slug: "product-function", title: "Product Function Block", description: "A reusable calculation block multiplies two numeric operands after both inputs pass validation.", sourcePattern: "Two-input multiplication function", changes: "Original operands, function identity, and result handshake.", inputs: ["factor_a_valid", "factor_b_valid", "calculate_request"], outputs: ["product_result_valid"], acceptance: "The product result becomes valid only after both factors and the request are valid.", visuals: ["machine", "switch", "indicator"], missingAssets: ["function-block calculation panel", "numeric result display"] }),
  originalModule({ chapter: 9, number: 3, slug: "sum-and-counter-function", title: "Sum and Counter Function", description: "A function calculates a result and increments an internal event count when the call completes.", sourcePattern: "Function block with internal counter", changes: "Original call-complete handshake and event counter contract.", inputs: ["inputs_valid", "calculate_request", "call_complete"], outputs: ["result_valid", "event_counted"], acceptance: "Each completed call produces one valid result and one counter event.", visuals: ["machine", "switch", "indicator"] }),
  originalModule({ chapter: 9, number: 4, slug: "function-selector", title: "Function Selector", description: "A selector chooses between two calculation paths and reports the selected result.", sourcePattern: "Function block calling other functions", changes: "Original selector values, call routing, and result-valid contract.", inputs: ["operand_set_valid", "function_select_valid", "calculate_request"], outputs: ["selected_result_valid"], acceptance: "Only the selected calculation path may assert selected_result_valid.", visuals: ["switch", "machine", "indicator"], missingAssets: ["function-block panel", "numeric selector/display"] }),
  originalModule({ chapter: 9, number: 10, slug: "box-volume", title: "Box Volume Calculation", description: "Three measured dimensions are accepted before a box-volume result is released to the next step.", sourcePattern: "Volume calculation from three analog measurements", changes: "Original dimensional inputs, units, and result-ready handshake.", inputs: ["length_valid", "width_valid", "height_valid"], outputs: ["volume_result_valid"], acceptance: "Volume result-valid is asserted only when all three dimensions are valid.", visuals: ["box", "machine", "indicator"], missingAssets: ["dimension sensors", "numeric measurement display"] }),
  originalModule({ chapter: 9, number: 11, slug: "pallet-counting", title: "Pallet Count Function", description: "A reusable block counts pallets by type and publishes the current pallet-count result.", sourcePattern: "Counting pallets by type", changes: "Original pallet taxonomy, count event, and result handshake.", inputs: ["pallet_detected", "pallet_type_valid", "count_request"], outputs: ["pallet_count_valid"], acceptance: "Each valid pallet event contributes to the selected count and produces a valid count result.", visuals: ["conveyor", "box", "machine", "indicator"], missingAssets: ["pallet load", "pallet-type sensor", "count display"] }),
  originalModule({ chapter: 9, number: 12, slug: "ev-charging-manager", title: "EV Charging Manager", description: "A shared controller allocates charging permission and accumulates energy pulse events for occupied bays.", sourcePattern: "Multi-bay charging station and energy meter", changes: "Original bay allocation, authorization, and pulse-count contract.", inputs: ["bay_occupied", "customer_authorized", "charger_ready"], outputs: ["charge_enable", "energy_session_active"], acceptance: "Charging is enabled only for an occupied, authorized, ready bay.", visuals: ["machine", "switch", "indicator"], missingAssets: ["EV/charger bay", "connector latch", "energy meter", "pulse-output meter", "authorization reader"] }),
  originalModule({ chapter: 11, number: 6, slug: "wastewater-collection", title: "Wastewater Collection", description: "Collection vessels inhibit intake when full and transfer wastewater only when the treatment path is ready.", sourcePattern: "Multiple collection tanks and shared outlet", changes: "Original collection cell, level policy, and treatment permissive.", inputs: ["source_level_high", "treatment_ready", "outlet_clear"], outputs: ["transfer_pump_run", "outlet_valve_open"], acceptance: "The pump and outlet valve run only when a source requires service and treatment is ready.", visuals: ["tank", "tank", "tank", "pump", "valve", "indicator"], missingAssets: ["collection tank bank", "level transmitters", "pipe manifold", "alarm beacon"] }),
  originalModule({ chapter: 11, number: 7, slug: "multi-conveyor-pallet-route", title: "Multi-Conveyor Pallet Route", description: "Several conveyor zones start only from a clear leading edge and stop together from a common stop request.", sourcePattern: "Multiple modular conveyor belts", changes: "Original zone layout, handoff signals, and energy-save stop behavior.", inputs: ["zone_1_clear", "zone_2_clear", "zone_3_clear"], outputs: ["zone_1_run", "zone_2_run", "zone_3_run"], acceptance: "A blocked zone removes the affected run command while preserving a diagnosable handoff state.", visuals: ["conveyor", "conveyor", "conveyor", "photoeye", "photoeye", "photoeye"], missingAssets: ["pallet roller conveyor zone", "zone handoff sensor", "common stop station"] }),
  originalModule({ chapter: 11, number: 11, slug: "service-elevator", title: "Service Elevator", description: "A lift travels between two landings only with door, position, and direction interlocks satisfied.", sourcePattern: "Elevator control with floor requests", changes: "Original lift cell, landing handshakes, and door permissive.", inputs: ["call_valid", "doors_closed", "landing_clear"], outputs: ["lift_up_cmd", "lift_down_cmd"], acceptance: "The elevator receives one direction command only when the doors are closed and the landing is clear.", visuals: ["liftTable", "rollerShutter", "switch", "indicator"], missingAssets: ["elevator car/shaft", "floor call station", "landing door", "floor-position sensor"] }),
  originalModule({ chapter: 11, number: 12, slug: "mobile-traffic-lights", title: "Mobile Traffic Lights", description: "Two synchronized mobile signal heads coordinate a safe alternating vehicle-flow state.", sourcePattern: "Portable traffic-light synchronization", changes: "Original paired signal state machine and synchronization handshake.", inputs: ["controller_ready", "road_a_clear", "road_b_clear"], outputs: ["road_a_green", "road_b_green"], acceptance: "Only one road receives a green command at a time, and both roads stop on a fault.", visuals: ["indicator", "indicator", "switch"], missingAssets: ["mobile traffic signal head", "roadway module", "signal synchronization link"] }),
  originalModule({ chapter: 11, number: 13, slug: "xy-palletizing", title: "XY Palletizing Cell", description: "A gantry places cartons at indexed pallet positions and reports a full-layer condition.", sourcePattern: "XY robot palletizing", changes: "Original pallet pattern, transfer handshake, and position contract.", inputs: ["carton_at_pick", "gantry_home", "pallet_position_valid"], outputs: ["vacuum_pick", "gantry_cycle", "layer_complete"], acceptance: "A carton is picked only at home and placed only at a valid pallet position.", visuals: ["robotArm", "conveyor", "box", "indicator"], missingAssets: ["XY gantry", "vacuum gripper", "pallet magazine", "carton load", "coordinate sensors"] }),
  originalModule({ chapter: 11, number: 19, slug: "powder-batch-mixer", title: "Powder Batch Mixer", description: "Ingredient hoppers dose a mixer, a load signal confirms the batch, and discharge occurs through a controlled valve.", sourcePattern: "Powder batch mixing process", changes: "Original hopper arrangement, recipe handshake, and batch-complete contract.", inputs: ["recipe_valid", "dose_complete", "mixer_ready"], outputs: ["dose_run", "mixer_run", "discharge_valve_open"], acceptance: "Dosing precedes mixing, and discharge is permitted only after a complete batch.", visuals: ["tank", "tank", "tank", "motor", "valve", "indicator"], missingAssets: ["bulk powder hopper", "slide-gate feeder", "load cell", "recipe selector", "powder discharge chute"] }),
  originalModule({ chapter: 10, number: 1, slug: "drive-alarm-code-string", title: "Drive Alarm-Code String", description: "A drive alarm string is received, searched for a selected code, and converted into a PLC alarm result.", sourcePattern: "Frequency-converter alarm string parsing", changes: "Original drive diagnostic panel, alarm-code contract, and search result.", inputs: ["drive_alarm_string_valid", "alarm_code_found", "alarm_reset"], outputs: ["drive_alarm_active", "alarm_match_valid"], acceptance: "The alarm result is active only for a valid drive message containing the selected code.", visuals: ["motor", "machine", "indicator"], missingAssets: ["VFD diagnostic panel", "fieldbus alarm-string display", "drive status indicator"] }),
  originalModule({ chapter: 10, number: 2, slug: "chicken-label-print", title: "Chicken Label Print", description: "A weighed product receives a formatted label after the weight and printer-ready signals are valid.", sourcePattern: "Label formatting from measured product data", changes: "Original food-packaging station, text-field contract, and print handshake.", inputs: ["product_weighed", "printer_ready", "label_data_valid"], outputs: ["print_request", "label_applied"], acceptance: "A label request is issued only when the product data and printer are ready.", visuals: ["conveyor", "machine", "box", "indicator"], missingAssets: ["food product load", "checkweigher", "label printer", "formatted label display"] }),
  originalModule({ chapter: 10, number: 3, slug: "vision-package-sorter", title: "Vision Package Sorter", description: "A vision result routes packages to one of four destination lanes using a conveyor and actuator handshake.", sourcePattern: "Vision-camera package sorting", changes: "Original package classes, lane layout, and result-valid state.", inputs: ["package_present", "vision_result_valid", "destination_clear"], outputs: ["sort_conveyor_run", "diverter_enable"], acceptance: "Sorting is enabled only for a present package with a valid vision result and clear destination.", visuals: ["conveyor", "box", "photoeye", "rotaryTable", "indicator"], missingAssets: ["industrial vision camera", "package-class result display", "four-lane diverter", "destination conveyor bank"] }),
  originalModule({ chapter: 10, number: 4, slug: "motor-enum-state", title: "Motor Operating-State Enum", description: "A motor state machine exposes one named operating state at a time and rejects conflicting commands.", sourcePattern: "ENUM for motor operating state", changes: "Original motor state names, state transition inputs, and safe fallback.", inputs: ["start_request", "stop_request", "fault_active"], outputs: ["motor_running", "state_valid"], acceptance: "A fault or stop request dominates start and leaves the motor in a safe stopped state.", visuals: ["motor", "switch", "indicator"] }),
  originalModule({ chapter: 10, number: 5, slug: "motor-struct-data", title: "Motor STRUCT Data", description: "A structured motor record combines command, power, temperature, and alarm fields for one motor.", sourcePattern: "STRUCT for motor data", changes: "Original structured record fields, validation handshake, and diagnostic indication.", inputs: ["motor_record_valid", "temperature_valid", "alarm_clear"], outputs: ["motor_enable", "record_ready"], acceptance: "The motor record is accepted only when its required fields are valid and alarms are clear.", visuals: ["motor", "machine", "indicator"], missingAssets: ["motor diagnostic faceplate", "temperature display", "structured-data monitor"] }),
  originalModule({ chapter: 10, number: 6, slug: "ten-motor-array-startup", title: "Ten-Motor Array Startup", description: "An array-based startup sequence starts ten motors with a staggered delay and stops the group on alarm.", sourcePattern: "ARRAY and FOR loop motor startup", changes: "Original ten-motor lineup, staggered timing, and group alarm behavior.", inputs: ["group_start_request", "all_motors_ready", "group_alarm_clear"], outputs: ["motor_array_run", "startup_sequence_active"], acceptance: "The array starts in order with a delay between motors and stops safely on a group alarm.", visuals: ["motor", "motor", "motor", "motor", "motor", "indicator"], missingAssets: ["ten-motor lineup asset", "group motor status panel", "staggered-start sequence display"] }),
];

scenes.push(
  ...photographedModules.sort((a, b) => {
    const [aChapter, aNumber] = a.catalog.exercise.split(".").map(Number);
    const [bChapter, bNumber] = b.catalog.exercise.split(".").map(Number);
    return aChapter - bChapter || aNumber - bNumber;
  }),
);

let previousScene = null;
for (const [sceneIndex, item] of scenes.entries()) {
  const currentPoints = new Map(
    (item.document.simulation.points ?? []).map((point) => [point.name, point]),
  );
  const previousPoints = new Map(
    (previousScene?.document.simulation.points ?? []).map((point) => [
      point.name,
      point,
    ]),
  );
  const retainedTags = [
    ...COMMON_FOUNDATION_TAGS,
    ...[...previousPoints.keys()].filter((name) => currentPoints.has(name)),
  ].filter((name, index, values) => values.indexOf(name) === index);
  const addedTags = [...currentPoints.keys()].filter(
    (name) => !previousPoints.has(name),
  );
  const changedTags = [...currentPoints.keys()]
    .filter((name) => previousPoints.has(name))
    .filter((name) => {
      const before = previousPoints.get(name);
      const after = currentPoints.get(name);
      return before.type !== after.type || before.owner !== after.owner;
    })
    .map((name) => ({
      name,
      reason: "This lab reuses the symbolic name with a changed contract; review before implementation.",
    }));
  item.document.training.sequenceNumber = sceneIndex + 1;
  item.document.training.inheritsFrom =
    previousScene?.document.id ?? "common-plc-watchdog-foundation";
  item.document.training.foundation = "common-plc-watchdog-foundation";
  item.document.training.retainedTags = retainedTags;
  item.document.training.addedTags = addedTags;
  item.document.training.changedTags = changedTags;
  item.document.training.previousAcceptance = previousScene
    ? [previousScene.document.id]
    : [];
  previousScene = item;
}

function catalogMarkdown(items) {
  const rows = items
    .map(
      ({ catalog, fileName }) =>
        `| ${catalog.exercise} | ${catalog.name} | ${catalog.sourcePattern} | ${catalog.changes} | \`${catalog.inputs}\` | \`${catalog.outputs}\` | ${catalog.acceptance} | \`${fileName}\` |`,
    )
    .join("\n");
  const assetRows = [...new Map(
    items.flatMap(({ catalog }) =>
      (catalog.completedAssets ?? []).map((asset) => [asset, catalog.name]),
    ),
  )].map(([asset, sceneName]) => `| ${asset} | ${sceneName} | Reusable static training accessory included in the scene with a stable visual contract. |`).join("\n");
  return `# Original PLC training scene catalog

## Scope and source boundary

The photographed exercises were used only to identify control concepts, I/O
relationships, and machine-sequence categories. The scenes below use original
names, layouts, dimensions, timings, equipment combinations, symbolic points,
descriptions, and acceptance cases. They do not reproduce the book diagrams,
wording, wiring illustrations, or proposed solutions.

All scenes remain offline. Point ownership describes the proposed PLC/PC
direction in the mock runtime; it does not authorize a PLC connection or write.

## Cumulative project foundation

Lab 2.1 establishes the common PLC/watchdog foundation documented in
\`docs/PLC_BENCH_SETUP.md\`. Each subsequent lab retains that foundation and
records its lineage, retained tags, added tags, and changed tags in the scene
document. The scene runtime remains a deterministic exercise contract; actual
TIA ladder blocks remain on the bench PLC until exported and reviewed.

## Scene inventory

| Ref. | Original simulator scene | Control concept retained | Material changes | Inputs / feedback | Outputs / commands | Acceptance proof | Scene file |
|---|---|---|---|---|---|---|---|
${rows}

## Completed authored assets

These lesson-specific assets are implemented as reusable static training
accessories. PLC behavior remains defined by the scene's symbolic simulation
points; the accessory is visual and does not invent live I/O behavior.

| Authored asset | First training module | Implementation |
|---|---|---|
${assetRows || "| None | None | None |"}

## Reusable assets added

- \`rotarySwitch\`: configurable 2- to N-position selector.
- \`liftTable\`: animated scissor lift with normalized travel.
- \`valve\`: animated valve stem, handwheel, and flow lamp.
- \`drillPress\`: animated drill head and spindle.
- \`robotArm\`: reusable articulated robot with normalized pose.
- \`rollerShutter\`: animated slatted service door with drive.
- \`rotaryTable\`: indexed routing table.
- \`machine\`: reusable enclosed process-machine cabinet with run indication.

## Verification contract

Every generated scene contains machine-readable \`verification.cases\`.
\`tools/verify_training_scenes.mjs\` loads the same scene files through the
production validator, builds every 3D asset through the shared factory, runs
the declared actions and simulated time, and asserts the expected final tags.
Browser acceptance remains a separate rendering and interaction gate.

## In-player learning guides

Every generated training scene also contains three progressive hints and one
explicit reference solution. The player derives **Configuration** directly
from \`simulation.points\`; simulator-only values and PLC memory bits are
excluded from the external tag list. This keeps the tag contract separate from
the hints and answer while preventing tag-name or data-type drift.
`;
}

await mkdir(sceneDirectory, { recursive: true });
for (const item of scenes) {
  // Lab 2 is the established baseline and may contain reviewed manual edits;
  // the generator owns the new photographed-module tranche only.
  if (item.document.id.startsWith("lab-2-")) {
    continue;
  }
  await writeFile(
    path.join(sceneDirectory, item.fileName),
    `${JSON.stringify(item.document, null, 2)}\n`,
    "utf8",
  );
}
await writeFile(catalogPath, catalogMarkdown(scenes), "utf8");
console.log(`WROTE_SCENES: ${scenes.length}`);
console.log(`CATALOG: ${catalogPath}`);
