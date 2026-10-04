import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { AssetFactory } from "../prototype/src/assetFactory.js";
import { validateSceneDocument } from "../prototype/src/sceneLoader.js";
import {
  CONTROL_SOURCES,
  STOP_REASONS,
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
  return createSimulation(scene, registry);
}

function runFor(simulation, seconds) {
  const stepSeconds = 0.05;
  const steps = Math.ceil(seconds / stepSeconds);
  for (let index = 0; index < steps; index += 1) {
    simulation.update(stepSeconds);
  }
}

function tagValue(simulation, name) {
  const tag = simulation.getTags().find((candidate) => candidate.name === name);
  assert(tag, `Missing runtime tag "${name}".`);
  return tag.value;
}

const sceneOne = buildRuntime(
  await loadScene("scene-1-conveyor-stop.plcscene"),
);
sceneOne.setControlSource(CONTROL_SOURCES.FAKE_PLC);
assert(sceneOne.setRunning(true), "Scene 1 should accept a clear start.");
runFor(sceneOne, 1.2);

assert(
  sceneOne.getStatus().stopReason === STOP_REASONS.SYSTEM,
  "Scene 1 must enter a system stop when the package blocks the photoeye.",
);
assert(
  sceneOne.getStatus().running === false,
  "Scene 1 must stop its runtime at the programmed photoeye stop.",
);
assert(
  tagValue(sceneOne, "simulated_photoeye") === true,
  "Scene 1 stop photoeye must remain blocked after the system stop.",
);
assert(
  tagValue(sceneOne, "conveyor_running") === false,
  "Scene 1 conveyor output must be off after the system stop.",
);

const heldPosition = tagValue(sceneOne, "object_position");
assert(
  sceneOne.setRunning(true) === false,
  "Scene 1 must reject Start while the stop photoeye remains blocked.",
);
assert(
  sceneOne.getStatus().stopReason === STOP_REASONS.START_BLOCKED,
  "Rejected Scene 1 Start must be visible as START BLOCKED.",
);
runFor(sceneOne, 0.5);
assert(
  Math.abs(tagValue(sceneOne, "object_position") - heldPosition) <= 1e-9,
  "A rejected Start must not move the blocked package.",
);

sceneOne.setLoopEnabled(true);
assert(
  sceneOne.getStatus().loopPending === false,
  "Enabling Loop after a rejected Start must not bypass the active permissive.",
);
sceneOne.reset();
assert(
  sceneOne.setRunning(true),
  "Scene 1 should start after Reset clears the simulated stop condition.",
);
runFor(sceneOne, 1.2);
assert(
  sceneOne.getStatus().loopPending,
  "Loop must schedule a reset after a normal Scene 1 system stop.",
);
runFor(sceneOne, 0.8);
assert(
  sceneOne.getStatus().running,
  "Loop must reset and restart Scene 1 after the configured delay.",
);
assert(
  sceneOne.getStatus().loopCount === 1,
  "Scene 1 must record one completed automatic loop restart.",
);
assert(
  tagValue(sceneOne, "simulated_photoeye") === false,
  "The loop reset must clear the simulated photoeye before restart.",
);

sceneOne.setRunning(
  false,
  STOP_REASONS.OPERATOR,
  "Operator stop test",
);
runFor(sceneOne, 1.0);
assert(
  sceneOne.getStatus().running === false &&
    sceneOne.getStatus().stopReason === STOP_REASONS.OPERATOR,
  "Operator Stop must remain latched even when Loop is enabled.",
);
assert(
  sceneOne.getStatus().loopCount === 1,
  "Operator Stop must not increment or restart the loop.",
);

const explicitStopDocument = await loadScene(
  "lab-2-11-inbound-tote-stop.plcscene",
);
const explicitStopSequence =
  explicitStopDocument.simulation.sequences[
    explicitStopDocument.simulation.defaultSequence
  ];
explicitStopSequence[0].durationS = 0.2;
explicitStopSequence[0].systemStop = true;
explicitStopSequence[0].stopMessage =
  "System stop — explicit sequence stop test";
const explicitStopRuntime = buildRuntime(explicitStopDocument);
explicitStopRuntime.setControlSource(CONTROL_SOURCES.FAKE_PLC);
assert(
  explicitStopRuntime.setRunning(true),
  "The explicit-stop sequence should accept its initial Start.",
);
runFor(explicitStopRuntime, 0.25);
assert(
  explicitStopRuntime.getStatus().stopReason === STOP_REASONS.SYSTEM &&
    explicitStopRuntime.getStatus().running === false,
  "An explicit systemStop sequence step must stop the scene runtime.",
);
assert(
  tagValue(explicitStopRuntime, "conveyor_run") === false,
  "An explicit systemStop step must apply the declared safe output state.",
);

const sequenceScene = buildRuntime(
  await loadScene("lab-2-11-inbound-tote-stop.plcscene"),
);
sequenceScene.setControlSource(CONTROL_SOURCES.FAKE_PLC);
sequenceScene.setLoopEnabled(true);
assert(
  sequenceScene.setRunning(true),
  "A clear default sequence should accept the global Run command.",
);
runFor(sequenceScene, 5.2);
assert(
  sequenceScene.getStatus().loopPending,
  "A completed sequence must enter LOOP RESET when Loop is enabled.",
);
runFor(sequenceScene, 0.8);
assert(
  sequenceScene.getStatus().running &&
    sequenceScene.getStatus().loopCount === 1,
  "A completed sequence must reset and restart exactly once.",
);
sequenceScene.setRunning(
  false,
  STOP_REASONS.OPERATOR,
  "Operator stop test",
);
runFor(sequenceScene, 1.0);
assert(
  sequenceScene.getStatus().running === false &&
    sequenceScene.getStatus().loopPending === false,
  "Operator Stop must hold a sequence stopped with Loop enabled.",
);

const guardedDrill = buildRuntime(
  await loadScene("lab-2-16-safe-drill.plcscene"),
);
guardedDrill.setControlSource(CONTROL_SOURCES.FAKE_PLC);
assert(
  guardedDrill.setRunning(true) === false,
  "Global Run must not bypass the guarded drill start permissives.",
);
assert(
  guardedDrill.getStatus().stopReason === STOP_REASONS.START_BLOCKED,
  "The guarded drill must expose a blocked global start.",
);
guardedDrill.handleAction("toggle-left-hand");
guardedDrill.handleAction("toggle-right-hand");
assert(
  guardedDrill.setRunning(true),
  "The guarded drill should start after all declared permissives are true.",
);

console.log("SCENE_1_SYSTEM_STOP: PASS");
console.log("SCENE_1_BLOCKED_RESTART: PASS");
console.log("SCENE_1_LOOP_RESET_RESTART: PASS");
console.log("OPERATOR_STOP_LOOP_INHIBIT: PASS");
console.log("EXPLICIT_SEQUENCE_SYSTEM_STOP: PASS");
console.log("SEQUENCE_COMPLETION_LOOP: PASS");
console.log("GLOBAL_RUN_PERMISSIVES: PASS");
console.log("PLC_CONNECTION_ATTEMPTED: FALSE");
