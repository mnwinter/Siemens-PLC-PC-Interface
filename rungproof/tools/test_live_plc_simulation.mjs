import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { AssetFactory } from "../prototype/src/assetFactory.js";
import { validateSceneDocument } from "../prototype/src/sceneLoader.js";
import {
  CONTROL_SOURCES,
  createSimulation,
} from "../prototype/src/simulations.js";

const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const raw = JSON.parse(
  await readFile(
    path.join(
      projectRoot,
      "prototype",
      "scenes",
      "scene-2-conveyor-pusher.plcscene",
    ),
    "utf8",
  ),
);
const scene = validateSceneDocument(raw);
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
const simulation = createSimulation(scene, registry);
simulation.setControlSource(CONTROL_SOURCES.LIVE_PLC);
assert(simulation.setRunning(true), "Live PLC scene should accept Run.");

assert(
  simulation.setControllerPoint("conveyor_running", false),
  "Scene 2 must accept the configured live PLC conveyor command.",
);
assert(
  simulation.setControllerPoint("pusher_extend", true),
  "Scene 2 must accept the configured live PLC pusher command.",
);
simulation.update(0.1);

const values = new Map(
  simulation.getTags().map((tag) => [tag.name, tag.value]),
);
assert(
  values.get("conveyor_running") === false,
  "The internal reference controller must not overwrite a live conveyor command.",
);
assert(
  values.get("pusher_extend") === true,
  "The internal reference controller must not overwrite a live pusher command.",
);
assert(
  values.get("pusher_position") > 0,
  "The live pusher command must move the simulated actuator.",
);
assert(
  simulation.setControllerPoint("part_at_pusher", true) === false,
  "Live PLC output application must reject PC-owned feedback points.",
);
assert(
  simulation.canHandleAction("scene-toggle") === false,
  "Scene 2's local 3D run/stop toggle must be disabled during live PLC control.",
);
simulation.holdControllerSafe();
const heldSceneTwoValues = new Map(
  simulation.getTags().map((tag) => [tag.name, tag.value]),
);
assert(
  heldSceneTwoValues.get("conveyor_running") === false &&
    heldSceneTwoValues.get("pusher_extend") === false,
  "Scene 2 must clear both live PLC commands when readiness is lost.",
);
const liveSceneTwoRunning = simulation.running;
const liveSceneTwoConveyor = heldSceneTwoValues.get("conveyor_running");
simulation.handleAction("scene-toggle");
const valuesAfterRejectedAction = new Map(
  simulation.getTags().map((tag) => [tag.name, tag.value]),
);
assert(
  simulation.running === liveSceneTwoRunning &&
    valuesAfterRejectedAction.get("conveyor_running") === liveSceneTwoConveyor,
  "A direct Scene 2 local action must not bypass live PLC ownership.",
);

console.log("LIVE_SCENE_2_PLC_OUTPUTS: PASS");
console.log("LIVE_SCENE_2_PC_OWNERSHIP: PASS");

const sceneOneRaw = JSON.parse(
  await readFile(
    path.join(
      projectRoot,
      "prototype",
      "scenes",
      "scene-1-conveyor-stop.plcscene",
    ),
    "utf8",
  ),
);
const sceneOne = validateSceneDocument(sceneOneRaw);
const sceneOneRegistry = new Map();
for (const definition of sceneOne.equipment) {
  const group = factory.create(definition);
  sceneOneRegistry.set(definition.id, {
    definition,
    group,
    dynamic: group.userData.dynamic ?? null,
  });
}
const sceneOneSimulation = createSimulation(sceneOne, sceneOneRegistry);
sceneOneSimulation.setControlSource(CONTROL_SOURCES.LIVE_PLC);
assert(sceneOneSimulation.setRunning(true), "Live Scene 1 should accept Run.");
assert(
  sceneOneSimulation.setControllerPoint("conveyor_running", false),
  "Scene 1 must accept its configured live conveyor command.",
);
sceneOneSimulation.update(0.1);
const sceneOneValues = new Map(
  sceneOneSimulation.getTags().map((tag) => [tag.name, tag.value]),
);
assert(
  sceneOneValues.get("conveyor_running") === false,
  "Scene 1 reference logic must not overwrite a live conveyor command.",
);
assert(
  sceneOneSimulation.canHandleAction("scene-toggle") === false,
  "Scene 1's local 3D run/stop toggle must be disabled during live PLC control.",
);
sceneOneSimulation.holdControllerSafe();
const heldSceneOneValues = new Map(
  sceneOneSimulation.getTags().map((tag) => [tag.name, tag.value]),
);
assert(
  heldSceneOneValues.get("conveyor_running") === false,
  "Scene 1 must clear its live conveyor command when readiness is lost.",
);
const liveSceneOneRunning = sceneOneSimulation.running;
sceneOneSimulation.handleAction("scene-toggle");
assert(
  sceneOneSimulation.running === liveSceneOneRunning,
  "A direct Scene 1 local action must not stop a live scene without disconnecting.",
);

console.log("LIVE_SCENE_1_PLC_OUTPUTS: PASS");
console.log("PLC_CONNECTION_ATTEMPTED: FALSE");
