/**
 * Scene loading and validation for the throwaway 3D player prototype.
 *
 * This is deliberately independent of PLC addressing. A future production
 * adapter can bind point names to the existing guarded DB14 transport without
 * allowing a scene file to write arbitrary PLC memory.
 */

import {
  EQUIPMENT_TYPES,
  MAX_SCENE_EQUIPMENT,
  validateEquipmentConfig,
  validateSceneComplexity,
} from "./equipmentCatalog.js";
import { symbolicName } from "./safeMarkup.js";
import { validateSceneSemantics } from "./sceneSemantics.js";

export const SCENE_FILE_TYPE = "plc-visual-scene";
export const SCENE_FILE_EXTENSION = ".plcscene";
export const SCENE_FILE_MIME =
  "application/vnd.plc-visual-simulator.scene+json";

export const BUILTIN_SCENES = Object.freeze([
  {
    id: "lab-2-01-workstation-call",
    label: "Lab 2.01 - Workstation call lamp",
    url: "./scenes/lab-2-01-workstation-call.plcscene",
  },
  {
    id: "lab-2-02-dual-confirmation",
    label: "Lab 2.02 - Dual confirmation lamp",
    url: "./scenes/lab-2-02-dual-confirmation.plcscene",
  },
  {
    id: "lab-2-03-service-marker-inhibit",
    label: "Lab 2.03 - Service marker inhibit",
    url: "./scenes/lab-2-03-service-marker-inhibit.plcscene",
  },
  {
    id: "lab-2-04-two-station-call",
    label: "Lab 2.04 - Two-station call beacon",
    url: "./scenes/lab-2-04-two-station-call.plcscene",
  },
  {
    id: "lab-2-05-bay-light-selector",
    label: "Lab 2.05 - Bay light selector",
    url: "./scenes/lab-2-05-bay-light-selector.plcscene",
  },
  {
    id: "lab-2-06-ready-attention",
    label: "Lab 2.06 - Ready / attention button",
    url: "./scenes/lab-2-06-ready-attention.plcscene",
  },
  {
    id: "lab-2-07-dual-contact-permissive",
    label: "Lab 2.07 - Dual-contact permissive",
    url: "./scenes/lab-2-07-dual-contact-permissive.plcscene",
  },
  {
    id: "lab-2-08-inspection-vote",
    label: "Lab 2.08 - Inspection vote stacklight",
    url: "./scenes/lab-2-08-inspection-vote.plcscene",
  },
  {
    id: "lab-2-09-maintenance-beacon",
    label: "Lab 2.09 - Maintenance beacon selector",
    url: "./scenes/lab-2-09-maintenance-beacon.plcscene",
  },
  {
    id: "lab-2-10-dust-collector-seal-in",
    label: "Lab 2.10 - Dust collector seal-in",
    url: "./scenes/lab-2-10-dust-collector-seal-in.plcscene",
  },
  {
    id: "lab-2-11-inbound-tote-stop",
    label: "Lab 2.11 - Inbound tote stop",
    url: "./scenes/lab-2-11-inbound-tote-stop.plcscene",
  },
  {
    id: "lab-2-12-assembly-lift",
    label: "Lab 2.12 - Ergonomic assembly lift",
    url: "./scenes/lab-2-12-assembly-lift.plcscene",
  },
  {
    id: "lab-2-13-coolant-jug-fill",
    label: "Lab 2.13 - Coolant jug filling cell",
    url: "./scenes/lab-2-13-coolant-jug-fill.plcscene",
  },
  {
    id: "lab-2-14-sump-pump",
    label: "Lab 2.14 - Sump dewatering pump",
    url: "./scenes/lab-2-14-sump-pump.plcscene",
  },
  {
    id: "lab-2-15-fume-extractor",
    label: "Lab 2.15 - Weld fume extractor",
    url: "./scenes/lab-2-15-fume-extractor.plcscene",
  },
  {
    id: "lab-2-16-safe-drill",
    label: "Lab 2.16 - Fixture-safe drill station",
    url: "./scenes/lab-2-16-safe-drill.plcscene",
  },
  {
    id: "lab-2-17-pallet-robot",
    label: "Lab 2.17 - Twin-container pallet cell",
    url: "./scenes/lab-2-17-pallet-robot.plcscene",
  },
  {
    id: "lab-2-18-pallet-pickup",
    label: "Lab 2.18 - Shipping pallet accumulation",
    url: "./scenes/lab-2-18-pallet-pickup.plcscene",
  },
  {
    id: "lab-2-19-service-door",
    label: "Lab 2.19 - Service door shutter",
    url: "./scenes/lab-2-19-service-door.plcscene",
  },
  {
    id: "lab-2-20-bottle-shuttle",
    label: "Lab 2.20 - Bottle shuttle conveyor",
    url: "./scenes/lab-2-20-bottle-shuttle.plcscene",
  },
  {
    id: "lab-2-21-tote-finishing",
    label: "Lab 2.21 - Chemical tote finishing line",
    url: "./scenes/lab-2-21-tote-finishing.plcscene",
  },
  {
    id: "lab-2-22-dual-spindle",
    label: "Lab 2.22 - Dual-spindle plate cell",
    url: "./scenes/lab-2-22-dual-spindle.plcscene",
  },
  {
    id: "lab-2-23-parcel-sorter",
    label: "Lab 2.23 - Parcel size sorter",
    url: "./scenes/lab-2-23-parcel-sorter.plcscene",
  },
  {
    id: "lab-2-24-robot-cnc",
    label: "Lab 2.24 - Robot CNC tending cell",
    url: "./scenes/lab-2-24-robot-cnc.plcscene",
  },
  {
    id: "lab-2-25-inspection-toggle",
    label: "Lab 2.25 - Inspection light toggle",
    url: "./scenes/lab-2-25-inspection-toggle.plcscene",
  },
  {
    id: "scene-1-conveyor-stop",
    label: "Scene 1 — Conveyor stop",
    url: "./scenes/scene-1-conveyor-stop.plcscene",
  },
  {
    id: "scene-2-conveyor-pusher",
    label: "Scene 2 — Conveyor pusher",
    url: "./scenes/scene-2-conveyor-pusher.plcscene",
  },
  {
    id: "conveyor-cell",
    label: "Conveyor inspection cell",
    url: "./scenes/conveyor-cell.json",
  },
  {
    id: "tank-level",
    label: "Tank level / 4–20 mA",
    url: "./scenes/tank-level.json",
  },
  {
    id: "tank-high-low",
    label: "Water tank — high/low switches",
    url: "./scenes/tank-high-low.json",
  },
  {
    id: "tank-radar",
    label: "Water tank — radar level",
    url: "./scenes/tank-radar.json",
  },
  {
    id: "equipment-gallery",
    label: "Reusable equipment gallery",
    url: "./scenes/equipment-gallery.json",
  },
]);

const SIMULATION_TYPES = new Set([
  "conveyor",
  "conveyorStop",
  "conveyorPusher",
  "tank",
  "gallery",
  "booleanPanel",
  "sequence",
  "static",
]);
const POINT_TYPES = new Set(["BOOL", "DINT", "REAL", "STRING"]);
const POINT_OWNERS = new Set(["PC", "PLC", "SIM"]);

const ALARM_SEVERITIES = new Set(["warning", "alarm", "fault"]);
const ALARM_OPERATORS = new Set([
  "isTrue",
  "isFalse",
  "eq",
  "neq",
  "gt",
  "gte",
  "lt",
  "lte",
]);

function requireObject(value, path) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${path} must be an object.`);
  }
  return value;
}

function requireString(value, path) {
  if (
    typeof value !== "string" ||
    value.trim() === "" ||
    value.length > 2_048
  ) {
    throw new Error(`${path} must be a non-empty string up to 2048 characters.`);
  }
  return value;
}

function finiteNumber(value, path) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`${path} must be a finite number.`);
  }
  return value;
}

function validatePointValue(value, type, path) {
  if (type === "BOOL" && typeof value !== "boolean") {
    throw new Error(`${path} must be a boolean for a BOOL point.`);
  }
  if (type === "DINT" && !Number.isInteger(value)) {
    throw new Error(`${path} must be an integer for a DINT point.`);
  }
  if (type === "REAL" && (typeof value !== "number" || !Number.isFinite(value))) {
    throw new Error(`${path} must be a finite number for a REAL point.`);
  }
  if (type === "STRING" && typeof value !== "string") {
    throw new Error(`${path} must be a string for a STRING point.`);
  }
  return value;
}

function validateSimulationPoints(points, simulationType) {
  if (simulationType === "static" && points === undefined) {
    return undefined;
  }
  if (!Array.isArray(points) || points.length === 0) {
    throw new Error(
      `scene.simulation.points must declare every runtime point for "${simulationType}".`,
    );
  }

  const names = new Set();
  return points.map((sourcePoint, index) => {
    const path = `scene.simulation.points[${index}]`;
    const point = requireObject(sourcePoint, path);
    const name = symbolicName(
      requireString(point.name, `${path}.name`),
      `${path}.name`,
    );
    if (names.has(name)) {
      throw new Error(`Duplicate simulation point "${name}".`);
    }
    names.add(name);

    const type = requireString(point.type, `${path}.type`);
    if (!POINT_TYPES.has(type)) {
      throw new Error(
        `${path}.type "${type}" is not supported. Allowed: ${[
          ...POINT_TYPES,
        ].join(", ")}.`,
      );
    }
    const owner = requireString(point.owner, `${path}.owner`);
    if (!POINT_OWNERS.has(owner)) {
      throw new Error(
        `${path}.owner "${owner}" is not supported. Allowed: ${[
          ...POINT_OWNERS,
        ].join(", ")}.`,
      );
    }
    if (!Object.hasOwn(point, "initial")) {
      throw new Error(`${path}.initial is required.`);
    }
    const initial = validatePointValue(point.initial, type, `${path}.initial`);
    if (Object.hasOwn(point, "safe")) {
      validatePointValue(point.safe, type, `${path}.safe`);
    }
    if (point.unit !== undefined) {
      requireString(point.unit, `${path}.unit`);
    }
    if (point.role !== undefined) {
      requireString(point.role, `${path}.role`);
    }
    if (point.purpose !== undefined) {
      requireString(point.purpose, `${path}.purpose`);
    }
    if (point.hidden !== undefined && typeof point.hidden !== "boolean") {
      throw new Error(`${path}.hidden must be a boolean when provided.`);
    }

    return {
      ...point,
      name,
      type,
      owner,
      initial,
      ...(typeof point.unit === "string" ? { unit: point.unit.trim() } : {}),
      ...(typeof point.role === "string" ? { role: point.role.trim() } : {}),
      ...(typeof point.purpose === "string"
        ? { purpose: point.purpose.trim() }
        : {}),
      ...(typeof point.hidden === "boolean" ? { hidden: point.hidden } : {}),
    };
  });
}

function validatePlcTestProfile(value) {
  if (value === undefined) {
    return undefined;
  }
  const profileId = requireString(value, "scene.plcTestProfile").trim();
  if (!/^[a-z0-9][a-z0-9._-]*\.json$/i.test(profileId)) {
    throw new Error(
      "scene.plcTestProfile must be one local JSON file name.",
    );
  }
  return profileId;
}

function vector(
  value,
  path,
  fallback,
  { min = -10_000, max = 10_000 } = {},
) {
  if (value === undefined) {
    return [...fallback];
  }
  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    value.some(
      (item) =>
        typeof item !== "number" ||
        !Number.isFinite(item) ||
        item < min ||
        item > max,
    )
  ) {
    throw new Error(
      `${path} must contain three finite numbers from ${min} to ${max}.`,
    );
  }
  return [...value];
}

function validateEquipment(item, index) {
  const path = `equipment[${index}]`;
  requireObject(item, path);
  const id = symbolicName(
    requireString(item.id, `${path}.id`),
    `${path}.id`,
  );
  const type = requireString(item.type, `${path}.type`);
  if (!EQUIPMENT_TYPES.has(type)) {
    throw new Error(
      `${path}.type "${type}" is not supported. Allowed: ${[
        ...EQUIPMENT_TYPES,
      ].join(", ")}.`,
    );
  }

  return {
    ...item,
    id,
    type,
    label:
      typeof item.label === "string" && item.label.trim()
        ? item.label.trim()
        : id,
    position: vector(item.position, `${path}.position`, [0, 0, 0]),
    rotation: vector(item.rotation, `${path}.rotation`, [0, 0, 0]),
    scale: vector(
      item.scale,
      `${path}.scale`,
      [1, 1, 1],
      { min: 0.001, max: 100 },
    ),
    config: validateEquipmentConfig(item.type, item.config, `${path}.config`),
  };
}

function validateTrainingGuide(value) {
  if (value === undefined) {
    return undefined;
  }

  const guide = requireObject(value, "scene.training");
  if (!Array.isArray(guide.hints) || guide.hints.length === 0) {
    throw new Error("scene.training.hints must contain at least one hint.");
  }
  const hints = guide.hints.map((hint, index) =>
    requireString(hint, `scene.training.hints[${index}]`),
  );

  const solution = requireObject(
    guide.solution,
    "scene.training.solution",
  );
  const summary = requireString(
    solution.summary,
    "scene.training.solution.summary",
  );
  if (!Array.isArray(solution.steps) || solution.steps.length === 0) {
    throw new Error(
      "scene.training.solution.steps must contain at least one reference step.",
    );
  }
  const steps = solution.steps.map((step, index) =>
    requireString(step, `scene.training.solution.steps[${index}]`),
  );

  const machineGuide = requireObject(
    guide.machineGuide ?? {
      purpose: "",
      startConditions: [],
      normalSequence: [],
      stopBehavior: [],
      faultBehavior: [],
      expectedObservations: [],
    },
    "scene.training.machineGuide",
  );
  const guideArray = (name) => {
    if (!Array.isArray(machineGuide[name])) {
      throw new Error(`scene.training.machineGuide.${name} must be an array.`);
    }
    return machineGuide[name].map((item, index) =>
      requireString(item, `scene.training.machineGuide.${name}[${index}]`),
    );
  };
  const machinePurpose = requireString(
    machineGuide.purpose,
    "scene.training.machineGuide.purpose",
  );

  const sequenceNumber = guide.sequenceNumber;
  if (
    sequenceNumber !== undefined &&
    (!Number.isInteger(sequenceNumber) || sequenceNumber < 1 || sequenceNumber > 999)
  ) {
    throw new Error("scene.training.sequenceNumber must be a positive integer.");
  }
  const inheritedFrom = guide.inheritsFrom;
  if (inheritedFrom !== undefined) {
    symbolicName(inheritedFrom, "scene.training.inheritsFrom");
  }
  const foundation = guide.foundation;
  if (foundation !== undefined) {
    symbolicName(foundation, "scene.training.foundation");
  }
  const tagList = (name) => {
    if (!Array.isArray(guide[name])) {
      throw new Error(`scene.training.${name} must be an array.`);
    }
    return guide[name].map((item, index) =>
      symbolicName(item, `scene.training.${name}[${index}]`),
    );
  };
  const retainedTags = guide.retainedTags === undefined ? [] : tagList("retainedTags");
  const addedTags = guide.addedTags === undefined ? [] : tagList("addedTags");
  const changedTags = guide.changedTags === undefined ? [] : guide.changedTags.map((item, index) => {
    const changed = requireObject(item, `scene.training.changedTags[${index}]`);
    return {
      name: symbolicName(changed.name, `scene.training.changedTags[${index}].name`),
      reason: requireString(changed.reason, `scene.training.changedTags[${index}].reason`),
    };
  });
  const previousAcceptance = guide.previousAcceptance === undefined
    ? []
    : guide.previousAcceptance.map((item, index) =>
        symbolicName(item, `scene.training.previousAcceptance[${index}]`),
      );

  return {
    hints,
    solution: {
      summary,
      steps,
        acceptance:
        typeof solution.acceptance === "string"
          ? solution.acceptance
          : "",
    },
    ...(sequenceNumber !== undefined ? { sequenceNumber } : {}),
    ...(inheritedFrom !== undefined ? { inheritsFrom: inheritedFrom } : {}),
    ...(foundation !== undefined ? { foundation } : {}),
    retainedTags,
    addedTags,
    changedTags,
    previousAcceptance,
    machineGuide: {
      purpose: machinePurpose,
      startConditions: guideArray("startConditions"),
      normalSequence: guideArray("normalSequence"),
      stopBehavior: guideArray("stopBehavior"),
      faultBehavior: guideArray("faultBehavior"),
      expectedObservations: guideArray("expectedObservations"),
    },
  };
}

function validateAlarmRules(value) {
  if (value === undefined) {
    return [];
  }
  if (!Array.isArray(value)) {
    throw new Error("scene.alarmRules must be an array.");
  }

  const ids = new Set();
  return value.map((candidate, index) => {
    const path = `scene.alarmRules[${index}]`;
    const rule = requireObject(candidate, path);
    const id = symbolicName(
      requireString(rule.id, `${path}.id`),
      `${path}.id`,
    );
    if (ids.has(id)) {
      throw new Error(`Duplicate alarm rule id "${id}".`);
    }
    ids.add(id);

    const severity = requireString(rule.severity, `${path}.severity`);
    if (!ALARM_SEVERITIES.has(severity)) {
      throw new Error(
        `${path}.severity must be warning, alarm, or fault.`,
      );
    }
    const operator = requireString(rule.operator, `${path}.operator`);
    if (!ALARM_OPERATORS.has(operator)) {
      throw new Error(
        `${path}.operator "${operator}" is not supported.`,
      );
    }
    if (
      !["isTrue", "isFalse"].includes(operator) &&
      rule.value === undefined
    ) {
      throw new Error(`${path}.value is required for operator "${operator}".`);
    }
    if (
      ["gt", "gte", "lt", "lte"].includes(operator) &&
      (typeof rule.value !== "number" || !Number.isFinite(rule.value))
    ) {
      throw new Error(
        `${path}.value must be a finite number for operator "${operator}".`,
      );
    }

    return {
      id,
      severity,
      point: symbolicName(
        requireString(rule.point, `${path}.point`),
        `${path}.point`,
      ),
      operator,
      ...(rule.value === undefined ? {} : { value: rule.value }),
      message: requireString(rule.message, `${path}.message`),
      check:
        typeof rule.check === "string" && rule.check.trim()
          ? rule.check.trim()
          : "Inspect the active scene point and related logic.",
    };
  });
}

export const MAX_SCENE_FILE_BYTES = 2 * 1024 * 1024;

function rejectOversizedScene(size, source) {
  if (!Number.isFinite(size) || size < 0) {
    throw new Error(`${source} has an invalid size.`);
  }
  if (size > MAX_SCENE_FILE_BYTES) {
    throw new Error(
      `${source} exceeds the ${MAX_SCENE_FILE_BYTES}-byte scene limit.`,
    );
  }
}

function validateSceneTextSize(text, source) {
  rejectOversizedScene(new TextEncoder().encode(text).byteLength, source);
  return text;
}

export function validateSceneDocument(input) {
  const source =
    typeof input === "string" ? JSON.parse(input) : structuredClone(input);
  requireObject(source, "scene");

  if (source.version !== 1) {
    throw new Error(`scene.version must be 1; received ${source.version}.`);
  }
  if (
    source.fileType !== undefined &&
    source.fileType !== SCENE_FILE_TYPE
  ) {
    throw new Error(
      `scene.fileType must be "${SCENE_FILE_TYPE}" when provided.`,
    );
  }

  const id = symbolicName(
    requireString(source.id, "scene.id"),
    "scene.id",
  );
  const name = requireString(source.name, "scene.name");
  if (!Array.isArray(source.equipment) || source.equipment.length === 0) {
    throw new Error("scene.equipment must contain at least one item.");
  }
  if (source.equipment.length > MAX_SCENE_EQUIPMENT) {
    throw new Error(
      `scene.equipment cannot exceed ${MAX_SCENE_EQUIPMENT} items.`,
    );
  }

  const equipment = source.equipment.map(validateEquipment);
  validateSceneComplexity(equipment);
  const ids = new Set();
  for (const item of equipment) {
    if (ids.has(item.id)) {
      throw new Error(`Duplicate equipment id "${item.id}".`);
    }
    ids.add(item.id);
  }

  const simulation =
    source.simulation === undefined
      ? { type: "static" }
      : { ...requireObject(source.simulation, "scene.simulation") };
  const simulationType = requireString(
    simulation.type ?? "static",
    "scene.simulation.type",
  );
  if (!SIMULATION_TYPES.has(simulationType)) {
    throw new Error(
      `scene.simulation.type "${simulationType}" is not supported.`,
    );
  }
  const simulationPoints = validateSimulationPoints(
    simulation.points,
    simulationType,
  );
  let repeatLoadSeconds;
  if (simulation.repeatLoadSeconds !== undefined) {
    repeatLoadSeconds = finiteNumber(
      simulation.repeatLoadSeconds,
      "scene.simulation.repeatLoadSeconds",
    );
    if (repeatLoadSeconds < 0.05 || repeatLoadSeconds > 3_600) {
      throw new Error(
        "scene.simulation.repeatLoadSeconds must be from 0.05 to 3600 seconds.",
      );
    }
  }

  const camera =
    source.camera === undefined
      ? {}
      : requireObject(source.camera, "scene.camera");
  const training = validateTrainingGuide(source.training);
  const alarmRules = validateAlarmRules(source.alarmRules);
  const plcTestProfile = validatePlcTestProfile(source.plcTestProfile);

  const normalized = {
    ...source,
    fileType: SCENE_FILE_TYPE,
    id,
    name,
    description:
      typeof source.description === "string" ? source.description : "",
    equipment,
    simulation: {
      ...simulation,
      type: simulationType,
      ...(simulationPoints ? { points: simulationPoints } : {}),
      ...(repeatLoadSeconds === undefined ? {} : { repeatLoadSeconds }),
    },
    alarmRules,
    ...(plcTestProfile ? { plcTestProfile } : {}),
    ...(training ? { training } : {}),
    camera: {
      position: vector(camera.position, "scene.camera.position", [9, 7, 9]),
      target: vector(camera.target, "scene.camera.target", [0, 1, 0]),
      fov:
        camera.fov === undefined
          ? 45
          : Math.min(85, Math.max(20, finiteNumber(camera.fov, "camera.fov"))),
    },
  };
  return validateSceneSemantics(normalized);
}

export async function loadSceneFromUrl(url, { signal } = {}) {
  const response = await fetch(url, { cache: "no-store", signal });
  if (!response.ok) {
    throw new Error(`Could not load ${url}: HTTP ${response.status}.`);
  }
  const declaredSize = response.headers.get("content-length");
  if (declaredSize !== null) {
    rejectOversizedScene(Number(declaredSize), `Scene ${url}`);
  }
  const text = await response.text();
  return validateSceneDocument(validateSceneTextSize(text, `Scene ${url}`));
}

export function loadSceneFromFile(file) {
  const lowerName = file.name.toLowerCase();
  if (
    !lowerName.endsWith(SCENE_FILE_EXTENSION) &&
    !lowerName.endsWith(".json")
  ) {
    return Promise.reject(
      new Error(
        `Scene files must use ${SCENE_FILE_EXTENSION}; legacy .json files are also accepted.`,
      ),
    );
  }
  try {
    rejectOversizedScene(file.size, `Scene file ${file.name}`);
  } catch (error) {
    return Promise.reject(error);
  }
  return file
    .text()
    .then((text) =>
      validateSceneDocument(
        validateSceneTextSize(text, `Scene file ${file.name}`),
      ),
    );
}

export function serializeSceneDocument(scene) {
  const validated = validateSceneDocument(scene);
  return `${JSON.stringify(validated, null, 2)}\n`;
}

export function sceneDownloadName(scene) {
  const id = String(scene?.id ?? "untitled-scene")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${id || "untitled-scene"}${SCENE_FILE_EXTENSION}`;
}
