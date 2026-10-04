import { readdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { AssetFactory } from "../prototype/src/assetFactory.js";
import { validateSceneDocument } from "../prototype/src/sceneLoader.js";
import { createSimulation } from "../prototype/src/simulations.js";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function loadScene(fileName) {
  const raw = JSON.parse(
    await readFile(
      path.join(projectRoot, "prototype", "scenes", fileName),
      "utf8",
    ),
  );
  return validateSceneDocument(raw);
}

function buildRuntime(scene) {
  const factory = new AssetFactory();
  const registry = new Map();
  for (const definition of scene.equipment) {
    const group = factory.create(definition);
    registry.set(definition.id, {
      definition,
      group,
      dynamic: group.userData.dynamic ?? null,
    });
  }
  return { registry, simulation: createSimulation(scene, registry) };
}

function valuesByName(simulation) {
  return new Map(simulation.getTags().map((tag) => [tag.name, tag.value]));
}

function assertPoint(simulation, name, expected, context) {
  const values = valuesByName(simulation);
  assert(values.has(name), `${context}: point "${name}" is missing.`);
  assert(
    values.get(name) === expected,
    `${context}: expected ${name}=${JSON.stringify(expected)}, received ${JSON.stringify(values.get(name))}.`,
  );
}

function safeValueForType(type) {
  if (type === "BOOL") {
    return false;
  }
  if (["DINT", "REAL"].includes(type)) {
    return 0;
  }
  return "";
}

const lightScene = await loadScene("lab-2-05-bay-light-selector.plcscene");
const { simulation: lightSimulation, registry: lightRegistry } =
  buildRuntime(lightScene);

assert(
  lightSimulation.getControlSource() === "disconnected",
  "Training scenes must default to a disconnected controller.",
);

lightSimulation.handleAction("next-mode");
assertPoint(
  lightSimulation,
  "selector_position",
  1,
  "Disconnected selector operation",
);
assertPoint(
  lightSimulation,
  "bay_a_command",
  false,
  "Disconnected controller must not synthesize output A",
);
assertPoint(
  lightSimulation,
  "bay_b_command",
  false,
  "Disconnected controller must not synthesize output B",
);
assert(
  lightRegistry.get("bay_light_a").dynamic.active === null,
  "Disconnected output A must leave its lamp off.",
);
assert(
  lightRegistry.get("bay_light_b").dynamic.active === null,
  "Disconnected output B must leave its lamp off.",
);

lightSimulation.setControlSource("fake-plc");
assertPoint(
  lightSimulation,
  "bay_a_command",
  true,
  "Fake PLC reference logic output A",
);
assertPoint(
  lightSimulation,
  "bay_b_command",
  true,
  "Fake PLC reference logic output B",
);

lightSimulation.setControllerPoint("bay_a_command", true);
lightSimulation.setControllerPoint("bay_b_command", false);
assertPoint(
  lightSimulation,
  "bay_a_command",
  true,
  "Forced incorrect Fake PLC output A",
);
assertPoint(
  lightSimulation,
  "bay_b_command",
  false,
  "Forced incorrect Fake PLC output B",
);
assert(
  lightRegistry.get("bay_light_a").dynamic.active === "white",
  "A forced-true output must illuminate lamp A.",
);
assert(
  lightRegistry.get("bay_light_b").dynamic.active === null,
  "A forced-false output must leave lamp B off.",
);

lightSimulation.setControlSource("disconnected");
assertPoint(
  lightSimulation,
  "bay_a_command",
  false,
  "Disconnect must fail output A safe",
);
assertPoint(
  lightSimulation,
  "bay_b_command",
  false,
  "Disconnect must fail output B safe",
);

const readyScene = await loadScene("lab-2-06-ready-attention.plcscene");
const { simulation: readySimulation } = buildRuntime(readyScene);
assertPoint(
  readySimulation,
  "ready_light",
  false,
  "Disconnected PLC output must ignore a true reference initial value",
);
readySimulation.handleAction("toggle-request");
assertPoint(
  readySimulation,
  "request_held",
  true,
  "Disconnected PC request input",
);
assertPoint(
  readySimulation,
  "ready_light",
  false,
  "Disconnected ready output",
);
assertPoint(
  readySimulation,
  "attention_light",
  false,
  "Disconnected attention output",
);
readySimulation.setControlSource("fake-plc");
assertPoint(
  readySimulation,
  "ready_light",
  false,
  "Fake PLC complementary ready output",
);
assertPoint(
  readySimulation,
  "attention_light",
  true,
  "Fake PLC complementary attention output",
);

const liftScene = await loadScene("lab-2-12-assembly-lift.plcscene");
const { simulation: liftSimulation } = buildRuntime(liftScene);
liftSimulation.handleAction("raise-lift");
assert(
  liftSimulation.getStatus().running === false,
  "A sequence must not start with its controller disconnected.",
);
assertPoint(
  liftSimulation,
  "lift_up",
  false,
  "Disconnected lift-up output",
);
liftSimulation.setControlSource("fake-plc");
liftSimulation.handleAction("raise-lift");
assert(
  liftSimulation.getStatus().running === true,
  "The explicit Fake PLC must be able to run the reference sequence.",
);

const labFiles = (await readdir(
  path.join(projectRoot, "prototype", "scenes"),
))
  .filter((name) => /^lab-\d+-\d{2}-.+\.plcscene$/i.test(name))
  .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
for (const fileName of labFiles) {
  const scene = await loadScene(fileName);
  const { simulation } = buildRuntime(scene);
  for (const action of simulation.getActions()) {
    simulation.handleAction(action.id);
    simulation.update(0.2);
  }
  assert(
    simulation.getStatus().running === false,
    `${scene.id}: disconnected operator inputs must not start scene playback.`,
  );
  for (const tag of simulation.getTags().filter((point) => point.owner === "PLC")) {
    const expected = safeValueForType(tag.type);
    assert(
      tag.value === expected,
      `${scene.id}: disconnected PLC point ${tag.name} must remain ${JSON.stringify(expected)}, received ${JSON.stringify(tag.value)}.`,
    );
  }
}

console.log("CONTROL_SOURCE_DEFAULT: disconnected");
console.log("DISCONNECTED_INPUT_ACCEPTED: PASS");
console.log("DISCONNECTED_PLC_OUTPUTS_SAFE: PASS");
console.log("FAKE_PLC_REFERENCE_LOGIC: PASS");
console.log("FAKE_PLC_WRONG_OUTPUT_RESPONSE: PASS");
console.log("TRUE_REFERENCE_OUTPUT_FAILS_SAFE: PASS");
console.log("SEQUENCE_CONTROLLER_GATE: PASS");
console.log(`ALL_LABS_DISCONNECTED_SAFE: ${labFiles.length}`);
