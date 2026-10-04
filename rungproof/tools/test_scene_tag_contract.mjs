import { readFile, readdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { AssetFactory } from "../prototype/src/assetFactory.js";
import {
  BUILTIN_SCENES,
  validateSceneDocument,
} from "../prototype/src/sceneLoader.js";
import { getSceneConfiguration } from "../prototype/src/sceneGuides.js";
import { createSimulation } from "../prototype/src/simulations.js";
import {
  compileSceneDocument,
  createConveyorPusherStarter,
} from "../scene-editor-prototype/src/editorModel.js";

const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);

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

function contractShape(point) {
  return {
    name: point.name,
    type: point.type,
    owner: point.owner,
    unit: point.unit ?? null,
  };
}

function sameContract(left, right) {
  return (
    left.name === right.name &&
    left.type === right.type &&
    left.owner === right.owner &&
    (left.unit ?? null) === (right.unit ?? null)
  );
}

function sameExternalContract(left, right) {
  return (
    left.name === right.name &&
    left.type === right.type &&
    left.owner === right.owner
  );
}

const failures = [];
let externalTagCount = 0;
let declaredPointCount = 0;

for (const descriptor of BUILTIN_SCENES) {
  const scenePath = path.join(
    projectRoot,
    "prototype",
    descriptor.url.replace(/^\.\//, ""),
  );
  const scene = validateSceneDocument(
    JSON.parse(await readFile(scenePath, "utf8")),
  );
  const runtime = buildRuntime(scene);
  const runtimeTags = runtime.getTags();
  const declaredPoints = (scene.simulation.points ?? []).filter(
    (point) => !point.hidden,
  );
  const declaredByName = new Map(
    declaredPoints.map((point) => [point.name, point]),
  );
  const runtimeByName = new Map(runtimeTags.map((tag) => [tag.name, tag]));

  declaredPointCount += declaredPoints.length;

  for (const tag of runtimeTags) {
    const declared = declaredByName.get(tag.name);
    if (!declared) {
      failures.push(
        `${scene.id}: runtime tag "${tag.name}" is not declared in simulation.points`,
      );
      continue;
    }
    if (!sameContract(contractShape(tag), contractShape(declared))) {
      failures.push(
        `${scene.id}: runtime/declaration mismatch for "${tag.name}": ` +
          `${JSON.stringify(contractShape(tag))} != ${JSON.stringify(contractShape(declared))}`,
      );
    }
  }

  for (const point of declaredPoints) {
    if (!runtimeByName.has(point.name)) {
      failures.push(
        `${scene.id}: declared point "${point.name}" is missing from runtime tags`,
      );
    }
  }

  const expectedExternal = declaredPoints
    .filter(
      (point) =>
        ["PC", "PLC"].includes(point.owner) && point.role !== "memory",
    )
    .map(contractShape)
    .sort((left, right) => left.name.localeCompare(right.name));
  const configurationExternal = getSceneConfiguration(scene).requiredTags
    .map(contractShape)
    .sort((left, right) => left.name.localeCompare(right.name));
  externalTagCount += expectedExternal.length;

  if (
    expectedExternal.length !== configurationExternal.length ||
    expectedExternal.some(
      (point, index) =>
        !sameExternalContract(point, configurationExternal[index]),
    )
  ) {
    failures.push(
      `${scene.id}: Configuration popup does not match the declared external tag contract`,
    );
  }

  for (const configured of getSceneConfiguration(scene).requiredTags) {
    const declared = declaredByName.get(configured.name);
    if (
      !declared ||
      configured.initial !== declared.initial ||
      typeof configured.purpose !== "string" ||
      configured.purpose.trim() === ""
    ) {
      failures.push(
        `${scene.id}: Configuration popup has incomplete setup data for "${configured.name}"`,
      );
    }
  }
}

const authoredScene = compileSceneDocument(createConveyorPusherStarter());
if (
  !Array.isArray(authoredScene.simulation.points) ||
  authoredScene.simulation.points.length === 0
) {
  failures.push(
    "Scene Editor: conveyor-pusher exports no declared simulation.points contract",
  );
} else {
  const authoredRuntime = buildRuntime(authoredScene);
  const authoredTags = authoredRuntime.getTags();
  const authoredNames = new Set(
    authoredScene.simulation.points.map((point) => point.name),
  );
  for (const tag of authoredTags) {
    if (!authoredNames.has(tag.name)) {
      failures.push(
        `Scene Editor: runtime tag "${tag.name}" is absent from the exported contract`,
      );
    }
  }
}

const savedSceneDirectory = path.join(
  projectRoot,
  "prototype",
  "saved-scenes",
);
// Saved scenes are user-generated and absent from a fresh checkout. Preserve
// failures other than ENOENT; a permission/I/O error must not look like no work.
let savedSceneFiles;
try { savedSceneFiles = await readdir(savedSceneDirectory); }
catch (error) { if (error.code !== "ENOENT") throw error; savedSceneFiles = []; }
for (const fileName of savedSceneFiles.filter((name) =>
  name.endsWith(".plcscene"),
)) {
  const savedScene = validateSceneDocument(
    JSON.parse(
      await readFile(path.join(savedSceneDirectory, fileName), "utf8"),
    ),
  );
  const savedRuntime = buildRuntime(savedScene);
  const savedTags = savedRuntime.getTags();
  const savedPoints = savedScene.simulation.points ?? [];
  const savedNames = new Set(savedPoints.map((point) => point.name));
  for (const tag of savedTags) {
    if (!savedNames.has(tag.name)) {
      failures.push(
        `${fileName}: saved-scene runtime tag "${tag.name}" is undeclared`,
      );
    }
  }
}

const invalidPointScene = structuredClone(authoredScene);
invalidPointScene.simulation.points = [
  {
    name: "duplicate_point",
    type: "BOOL",
    owner: "PC",
    initial: false,
  },
  {
    name: "duplicate_point",
    type: "BOOL",
    owner: "PLC",
    initial: false,
  },
];
let duplicatePointRejected = false;
try {
  validateSceneDocument(invalidPointScene);
} catch (error) {
  duplicatePointRejected = /Duplicate simulation point/.test(error.message);
}
if (!duplicatePointRejected) {
  failures.push(
    "Scene validation: duplicate simulation point names were not rejected",
  );
}

if (failures.length > 0) {
  console.error(failures.join("\n"));
  throw new Error(
    `SCENE_TAG_CONTRACT_FAILED: ${failures.length} mismatch${
      failures.length === 1 ? "" : "es"
    }`,
  );
}

console.log(`SCENE_TAG_CONTRACTS_VALID: ${BUILTIN_SCENES.length}`);
console.log(`DECLARED_RUNTIME_POINTS: ${declaredPointCount}`);
console.log(`EXTERNAL_INTERFACE_TAGS: ${externalTagCount}`);
console.log("PLC_CONNECTION_ATTEMPTED: FALSE");
