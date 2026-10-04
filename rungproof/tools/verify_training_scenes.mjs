import { readdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { AssetFactory } from "../prototype/src/assetFactory.js";
import {
  BUILTIN_SCENES,
  validateSceneDocument,
} from "../prototype/src/sceneLoader.js";
import {
  CONTROL_SOURCES,
  createSimulation,
} from "../prototype/src/simulations.js";
import {
  getSceneConfiguration,
  getSceneHints,
  getSceneSolution,
} from "../prototype/src/sceneGuides.js";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sceneDirectory = path.join(projectRoot, "prototype", "scenes");
const expectedSceneCount = 70;
const requiredReusableTypes = new Set([
  "rotarySwitch",
  "liftTable",
  "valve",
  "drillPress",
  "robotArm",
  "rollerShutter",
  "rotaryTable",
  "machine",
]);
const forbiddenSceneKeys = new Set([
  "ip",
  "ipAddress",
  "rack",
  "slot",
  "dbOffset",
  "plcAddress",
  "physicalAddress",
  "writeAuthorization",
]);
const commonFoundationTags = new Set([
  "PC_Heartbeat",
  "PLC_Heartbeat_Echo",
  "Simulation_Enable",
  "Simulation_Comm_OK",
  "Simulation_Timeout",
]);

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertSafeKeys(value, source, pathParts = []) {
  if (Array.isArray(value)) {
    value.forEach((item, index) =>
      assertSafeKeys(item, source, [...pathParts, String(index)]),
    );
    return;
  }
  if (value === null || typeof value !== "object") {
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    assert(
      !forbiddenSceneKeys.has(key),
      `${source}: forbidden scene key ${[...pathParts, key].join(".")}`,
    );
    assertSafeKeys(child, source, [...pathParts, key]);
  }
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

function runFor(simulation, seconds) {
  const stepSeconds = 0.05;
  const steps = Math.ceil(seconds / stepSeconds);
  for (let index = 0; index < steps; index += 1) {
    simulation.update(stepSeconds);
  }
}

function tagsByName(simulation) {
  const result = new Map();
  for (const tag of simulation.getTags()) {
    assert(!result.has(tag.name), `Duplicate runtime tag "${tag.name}".`);
    if (typeof tag.value === "number") {
      assert(Number.isFinite(tag.value), `Tag "${tag.name}" is not finite.`);
    }
    result.set(tag.name, tag.value);
  }
  return result;
}

function assertExpectedTags(sceneId, caseName, simulation, expected) {
  const actual = tagsByName(simulation);
  for (const [name, expectedValue] of Object.entries(expected ?? {})) {
    assert(actual.has(name), `${sceneId}/${caseName}: missing tag "${name}".`);
    const actualValue = actual.get(name);
    const equal =
      typeof expectedValue === "number" && typeof actualValue === "number"
        ? Math.abs(actualValue - expectedValue) <= 1e-6
        : actualValue === expectedValue;
    assert(
      equal,
      `${sceneId}/${caseName}: expected ${name}=${JSON.stringify(expectedValue)}, received ${JSON.stringify(actualValue)}.`,
    );
  }
}

function assertTrainingProgression(scene, previousScene) {
  const training = scene.training;
  assert(training?.machineGuide, `${scene.id}: machine guide is required.`);
  for (const field of [
    "startConditions",
    "normalSequence",
    "stopBehavior",
    "faultBehavior",
    "expectedObservations",
  ]) {
    assert(
      Array.isArray(training.machineGuide[field]) &&
        training.machineGuide[field].length > 0 &&
        training.machineGuide[field].every((item) => item.trim().length > 0),
      `${scene.id}: machineGuide.${field} is incomplete.`,
    );
  }
  assert(
    Number.isInteger(training.sequenceNumber) && training.sequenceNumber >= 1,
    `${scene.id}: sequence number is missing.`,
  );
  assert(
    training.foundation === "common-plc-watchdog-foundation",
    `${scene.id}: common foundation is missing.`,
  );
  for (const tag of commonFoundationTags) {
    assert(
      training.retainedTags.includes(tag),
      `${scene.id}: common tag ${tag} is not retained.`,
    );
  }
  if (previousScene) {
    assert(
      training.inheritsFrom === previousScene.id,
      `${scene.id}: does not inherit ${previousScene.id}.`,
    );
    assert(
      training.previousAcceptance.includes(previousScene.id),
      `${scene.id}: previous acceptance is not retained.`,
    );
  } else {
    assert(
      training.inheritsFrom === "common-plc-watchdog-foundation",
      `${scene.id}: first lab must inherit the common foundation.`,
    );
  }
}

async function verifyScene(fileName, observedTypes, previousScene) {
  const raw = JSON.parse(await readFile(path.join(sceneDirectory, fileName), "utf8"));
  assertSafeKeys(raw, fileName);
  const scene = validateSceneDocument(raw);
  assertTrainingProgression(scene, previousScene);
  assert(scene.fileType === "plc-visual-scene", `${fileName}: wrong file type.`);
  assert(scene.id.startsWith("lab-"), `${fileName}: unexpected scene id.`);
  assert(
    Array.isArray(scene.verification?.cases) && scene.verification.cases.length > 0,
    `${fileName}: verification cases are required.`,
  );
  const configuration = getSceneConfiguration(scene);
  const expectedExternalPoints = (scene.simulation.points ?? []).filter(
    (point) =>
      ["PC", "PLC"].includes(point.owner) && point.role !== "memory",
  );
  assert(
    configuration.requiredTags.length === expectedExternalPoints.length,
    `${fileName}: configuration tag count does not match the scene contract.`,
  );
  assert(
    new Set(configuration.requiredTags.map((tag) => tag.name)).size ===
      configuration.requiredTags.length,
    `${fileName}: configuration contains duplicate tags.`,
  );
  for (const point of expectedExternalPoints) {
    const configured = configuration.requiredTags.find(
      (tag) => tag.name === point.name,
    );
    assert(configured, `${fileName}: configuration is missing ${point.name}.`);
    assert(
      configured.type === point.type &&
        configured.owner === point.owner &&
        configured.initial === point.initial,
      `${fileName}: configuration drift detected for ${point.name}.`,
    );
    assert(
      typeof configured.purpose === "string" && configured.purpose.length > 0,
      `${fileName}: configuration purpose is missing for ${point.name}.`,
    );
  }
  const hints = getSceneHints(scene);
  assert(
    hints.length >= 3 && hints.every((hint) => hint.trim().length > 0),
    `${fileName}: at least three progressive hints are required.`,
  );
  const solution = getSceneSolution(scene);
  assert(
    solution &&
      solution.summary.trim().length > 0 &&
      solution.steps.length > 0 &&
      solution.steps.every((step) => step.trim().length > 0),
    `${fileName}: a complete reference solution is required.`,
  );
  for (const equipment of scene.equipment) {
    observedTypes.add(equipment.type);
  }
  const pointOwners = new Map(
    (scene.simulation.points ?? []).map((point) => [point.name, point.owner]),
  );
  for (const action of scene.simulation.actions ?? []) {
    if (!action.point) {
      continue;
    }
    assert(
      pointOwners.get(action.point) !== "PLC",
      `${scene.id}: operator action "${action.id}" directly writes PLC-owned point "${action.point}".`,
    );
  }

  let passedCases = 0;
  for (const testCase of scene.verification.cases) {
    const { simulation, registry } = buildRuntime(scene);
    assert(
      simulation.getControlSource() === CONTROL_SOURCES.DISCONNECTED,
      `${scene.id}: runtime must default to a disconnected controller.`,
    );
    simulation.setControlSource(CONTROL_SOURCES.FAKE_PLC);
    assert(
      registry.size === scene.equipment.length,
      `${scene.id}: registry count does not match equipment count.`,
    );

    for (const actionId of testCase.actions ?? []) {
      simulation.handleAction(actionId);
    }
    for (const phase of testCase.phases ?? []) {
      if (phase.action) {
        simulation.handleAction(phase.action);
      }
      if (phase.runForS) {
        runFor(simulation, phase.runForS);
      }
    }
    assertExpectedTags(scene.id, testCase.name, simulation, testCase.expect);
    passedCases += 1;
  }

  return {
    id: scene.id,
    equipmentCount: scene.equipment.length,
    caseCount: passedCases,
    configurationTagCount: configuration.requiredTags.length,
  };
}

const sceneFiles = (await readdir(sceneDirectory))
  .filter((name) => /^lab-\d+-\d{2}-.+\.plcscene$/i.test(name))
  .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
assert(
  sceneFiles.length === expectedSceneCount,
  `Expected ${expectedSceneCount} training scenes; found ${sceneFiles.length}.`,
);

const observedTypes = new Set();
const results = [];
let previousScene = null;
for (const fileName of sceneFiles) {
  const raw = JSON.parse(await readFile(path.join(sceneDirectory, fileName), "utf8"));
  const result = await verifyScene(fileName, observedTypes, previousScene);
  previousScene = raw;
  results.push(result);
  console.log(
    `SCENE_PASS ${result.id}: ${result.equipmentCount} assets, ${result.caseCount} cases`,
  );
}

for (const requiredType of requiredReusableTypes) {
  assert(
    observedTypes.has(requiredType),
    `Reusable asset type "${requiredType}" is not exercised by any training scene.`,
  );
}

const totalCases = results.reduce((sum, result) => sum + result.caseCount, 0);

const descriptorIds = new Set();
let librarySceneCount = 0;
for (const descriptor of BUILTIN_SCENES) {
  assert(
    !descriptorIds.has(descriptor.id),
    `Duplicate built-in scene descriptor "${descriptor.id}".`,
  );
  descriptorIds.add(descriptor.id);
  const localPath = path.join(
    projectRoot,
    "prototype",
    descriptor.url.replace(/^\.\//, ""),
  );
  const raw = JSON.parse(await readFile(localPath, "utf8"));
  const validated = validateSceneDocument(raw);
  assert(
    validated.id === descriptor.id,
    `Descriptor "${descriptor.id}" loads scene "${validated.id}".`,
  );
  const { registry } = buildRuntime(validated);
  assert(
    registry.size === validated.equipment.length,
    `${descriptor.id}: built-in registry count mismatch.`,
  );
  librarySceneCount += 1;
}

console.log(`TRAINING_SCENES_VALID: ${results.length}`);
console.log(`TRAINING_CASES_PASS: ${totalCases}`);
console.log(`SCENE_GUIDES_VALID: ${results.length}`);
console.log(`REUSABLE_TYPES_COVERED: ${requiredReusableTypes.size}`);
console.log(`LIBRARY_SCENES_VALID: ${librarySceneCount}`);
console.log("PLC_CONNECTION_ATTEMPTED: FALSE");
