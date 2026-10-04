import { symbolicName } from "./safeMarkup.js";

const EQUIPMENT_REFERENCES = Object.freeze({
  conveyor: {
    conveyorId: ["conveyor"],
    photoeyeId: ["photoeye"],
    indicatorId: ["indicator"],
    productIds: ["box"],
  },
  conveyorStop: {
    conveyorId: ["conveyor"],
    photoeyeId: ["photoeye"],
    productId: ["box"],
    indicatorId: ["indicator"],
  },
  conveyorPusher: {
    conveyorId: ["conveyor"],
    photoeyeId: ["photoeye"],
    productId: ["box"],
    pusherId: ["pusher"],
    indicatorId: ["indicator"],
  },
  tank: {
    tankId: ["tank"],
    pumpId: ["pump"],
    lowSensorId: ["levelSensor"],
    highSensorId: ["levelSensor"],
    transmitterId: ["levelSensor", "radarLevelSensor"],
    indicatorId: ["indicator"],
  },
});

const OPTIONAL_EQUIPMENT_REFERENCES = new Set([
  "lowSensorId",
  "highSensorId",
  "transmitterId",
]);

const ACTION_TYPES = new Set([
  "toggle",
  "set",
  "pulse",
  "cycle",
  "start",
  "run",
  "stop",
  "reset",
  "togglePoint",
]);

const BINDING_MODES = new Set([
  "switch",
  "indicator",
  "selector",
  "running",
  "photoeye",
  "position",
  "levelSensor",
]);

function requirePlainObject(value, path) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${path} must be an object.`);
  }
  return value;
}

function requireShortString(value, path) {
  if (
    typeof value !== "string" ||
    value.trim() === "" ||
    value.length > 2_048
  ) {
    throw new Error(`${path} must be a non-empty short string.`);
  }
  return value.trim();
}

function validatePointValue(point, value, path) {
  if (!point) {
    throw new Error(`${path} references an unknown point.`);
  }
  if (point.type === "BOOL" && typeof value !== "boolean") {
    throw new Error(`${path} must be a boolean for ${point.name}.`);
  }
  if (point.type === "DINT" && !Number.isInteger(value)) {
    throw new Error(`${path} must be an integer for ${point.name}.`);
  }
  if (
    point.type === "REAL" &&
    (typeof value !== "number" || !Number.isFinite(value))
  ) {
    throw new Error(`${path} must be a finite number for ${point.name}.`);
  }
  if (point.type === "STRING" && typeof value !== "string") {
    throw new Error(`${path} must be a string for ${point.name}.`);
  }
}

function validatePointMap(value, points, path) {
  const candidate = requirePlainObject(value ?? {}, path);
  for (const [name, pointValue] of Object.entries(candidate)) {
    symbolicName(name, `${path} key`);
    validatePointValue(points.get(name), pointValue, `${path}.${name}`);
  }
}

function validateEquipmentReference(
  equipment,
  id,
  expectedTypes,
  path,
  optional = false,
) {
  if (id === undefined && optional) {
    return;
  }
  const reference = symbolicName(
    requireShortString(id, path),
    path,
  );
  const definition = equipment.get(reference);
  if (!definition) {
    throw new Error(`${path} references missing equipment "${reference}".`);
  }
  if (!expectedTypes.includes(definition.type)) {
    throw new Error(
      `${path} must reference ${expectedTypes.join(" or ")}, not "${definition.type}".`,
    );
  }
}

function validateActions(actions, points, sequences, path) {
  if (actions === undefined) {
    return;
  }
  if (!Array.isArray(actions) || actions.length > 128) {
    throw new Error(`${path} must be an array with at most 128 actions.`);
  }
  const ids = new Set();
  actions.forEach((action, index) => {
    const actionPath = `${path}[${index}]`;
    requirePlainObject(action, actionPath);
    const id = symbolicName(
      requireShortString(action.id, `${actionPath}.id`),
      `${actionPath}.id`,
    );
    if (ids.has(id)) {
      throw new Error(`Duplicate simulation action "${id}".`);
    }
    ids.add(id);
    requireShortString(action.label, `${actionPath}.label`);
    if (!ACTION_TYPES.has(action.type)) {
      throw new Error(`${actionPath}.type "${action.type}" is unsupported.`);
    }
    if (action.point !== undefined) {
      const pointName = symbolicName(action.point, `${actionPath}.point`);
      const point = points.get(pointName);
      if (!point) {
        throw new Error(`${actionPath}.point references unknown point "${pointName}".`);
      }
      if (Object.hasOwn(action, "value")) {
        validatePointValue(point, action.value, `${actionPath}.value`);
      }
      if (action.values !== undefined) {
        if (!Array.isArray(action.values) || action.values.length === 0) {
          throw new Error(`${actionPath}.values must be a non-empty array.`);
        }
        action.values.forEach((value, valueIndex) =>
          validatePointValue(
            point,
            value,
            `${actionPath}.values[${valueIndex}]`,
          ),
        );
      }
    }
    if (
      action.sequence !== undefined &&
      !Object.hasOwn(sequences, action.sequence)
    ) {
      throw new Error(
        `${actionPath}.sequence references unknown sequence "${action.sequence}".`,
      );
    }
    if (action.requires !== undefined) {
      validatePointMap(action.requires, points, `${actionPath}.requires`);
    }
    if (
      action.durationS !== undefined &&
      (typeof action.durationS !== "number" ||
        !Number.isFinite(action.durationS) ||
        action.durationS < 0.01 ||
        action.durationS > 60)
    ) {
      throw new Error(`${actionPath}.durationS must be from 0.01 to 60.`);
    }
  });
}

function validateBindings(bindings, points, equipment, path) {
  if (bindings === undefined) {
    return;
  }
  if (!Array.isArray(bindings) || bindings.length > 256) {
    throw new Error(`${path} must be an array with at most 256 bindings.`);
  }
  bindings.forEach((binding, index) => {
    const bindingPath = `${path}[${index}]`;
    requirePlainObject(binding, bindingPath);
    const point = symbolicName(binding.point, `${bindingPath}.point`);
    if (!points.has(point)) {
      throw new Error(`${bindingPath}.point references unknown point "${point}".`);
    }
    const equipmentId = symbolicName(
      binding.equipmentId,
      `${bindingPath}.equipmentId`,
    );
    if (!equipment.has(equipmentId)) {
      throw new Error(
        `${bindingPath}.equipmentId references missing equipment "${equipmentId}".`,
      );
    }
    if (!BINDING_MODES.has(binding.mode)) {
      throw new Error(`${bindingPath}.mode "${binding.mode}" is unsupported.`);
    }
  });
}

function validateBooleanRules(simulation, points) {
  for (const [index, rule] of (simulation.rules ?? []).entries()) {
    const path = `scene.simulation.rules[${index}]`;
    requirePlainObject(rule, path);
    validatePointMap(rule.when, points, `${path}.when`);
    validatePointMap(rule.set, points, `${path}.set`);
  }
  for (const [index, rule] of (simulation.edgeRules ?? []).entries()) {
    const path = `scene.simulation.edgeRules[${index}]`;
    requirePlainObject(rule, path);
    const rising = symbolicName(rule.rising, `${path}.rising`);
    const point = points.get(rising);
    if (!point || point.type !== "BOOL") {
      throw new Error(`${path}.rising must reference a BOOL point.`);
    }
    validatePointMap(rule.set ?? {}, points, `${path}.set`);
    if (rule.toggle !== undefined) {
      if (!Array.isArray(rule.toggle)) {
        throw new Error(`${path}.toggle must be an array.`);
      }
      for (const [toggleIndex, name] of rule.toggle.entries()) {
        const pointName = symbolicName(name, `${path}.toggle[${toggleIndex}]`);
        if (points.get(pointName)?.type !== "BOOL") {
          throw new Error(`${path}.toggle must reference BOOL points.`);
        }
      }
    }
  }
}

function validateSequences(simulation, points, equipment) {
  const sequences = requirePlainObject(
    simulation.sequences ?? {},
    "scene.simulation.sequences",
  );
  const entries = Object.entries(sequences);
  if (entries.length === 0 || entries.length > 64) {
    throw new Error("scene.simulation.sequences must contain 1-64 sequences.");
  }
  for (const [sequenceName, states] of entries) {
    symbolicName(sequenceName, "scene.simulation.sequences key");
    if (!Array.isArray(states) || states.length === 0 || states.length > 128) {
      throw new Error(`Sequence "${sequenceName}" must contain 1-128 states.`);
    }
    states.forEach((state, stateIndex) => {
      const path =
        `scene.simulation.sequences.${sequenceName}[${stateIndex}]`;
      requirePlainObject(state, path);
      requireShortString(state.name, `${path}.name`);
      if (
        typeof state.durationS !== "number" ||
        !Number.isFinite(state.durationS) ||
        state.durationS < 0 ||
        state.durationS > 3_600
      ) {
        throw new Error(`${path}.durationS must be from 0 to 3600.`);
      }
      validatePointMap(state.set ?? {}, points, `${path}.set`);
      for (const [motionIndex, motion] of (state.motions ?? []).entries()) {
        const motionPath = `${path}.motions[${motionIndex}]`;
        requirePlainObject(motion, motionPath);
        const equipmentId = symbolicName(
          motion.equipmentId,
          `${motionPath}.equipmentId`,
        );
        if (!equipment.has(equipmentId)) {
          throw new Error(
            `${motionPath}.equipmentId references missing equipment "${equipmentId}".`,
          );
        }
        if (!["translate", "position", "tankLevel"].includes(motion.type)) {
          throw new Error(`${motionPath}.type "${motion.type}" is unsupported.`);
        }
        if (
          motion.type === "translate" &&
          !["x", "y", "z"].includes(motion.axis)
        ) {
          throw new Error(`${motionPath}.axis must be x, y, or z.`);
        }
        for (const property of ["from", "to"]) {
          if (
            typeof motion[property] !== "number" ||
            !Number.isFinite(motion[property]) ||
            Math.abs(motion[property]) > 10_000
          ) {
            throw new Error(`${motionPath}.${property} must be finite and bounded.`);
          }
        }
      }
    });
  }
  if (
    simulation.defaultSequence !== undefined &&
    !Object.hasOwn(sequences, simulation.defaultSequence)
  ) {
    throw new Error("scene.simulation.defaultSequence is not defined.");
  }
  validatePointMap(simulation.safeState ?? {}, points, "scene.simulation.safeState");
  validatePointMap(
    simulation.completionState ?? {},
    points,
    "scene.simulation.completionState",
  );
  return sequences;
}

export function validateSceneSemantics(scene) {
  const equipment = new Map(scene.equipment.map((item) => [item.id, item]));
  const points = new Map(
    (scene.simulation.points ?? []).map((point) => [point.name, point]),
  );
  const referenceContract = EQUIPMENT_REFERENCES[scene.simulation.type] ?? {};
  for (const [property, expectedTypes] of Object.entries(referenceContract)) {
    const value = scene.simulation[property];
    if (property === "productIds") {
      if (!Array.isArray(value) || value.length === 0 || value.length > 128) {
        throw new Error(`scene.simulation.${property} must be a non-empty array.`);
      }
      value.forEach((id, index) =>
        validateEquipmentReference(
          equipment,
          id,
          expectedTypes,
          `scene.simulation.${property}[${index}]`,
        ),
      );
      continue;
    }
    validateEquipmentReference(
      equipment,
      value,
      expectedTypes,
      `scene.simulation.${property}`,
      OPTIONAL_EQUIPMENT_REFERENCES.has(property),
    );
  }

  const sequences =
    scene.simulation.type === "sequence"
      ? validateSequences(scene.simulation, points, equipment)
      : {};
  validateActions(
    scene.simulation.actions,
    points,
    sequences,
    "scene.simulation.actions",
  );
  validateBindings(
    scene.simulation.pointBindings,
    points,
    equipment,
    "scene.simulation.pointBindings",
  );
  if (scene.simulation.type === "booleanPanel") {
    validateBooleanRules(scene.simulation, points);
  }
  for (const [index, alarm] of scene.alarmRules.entries()) {
    const point = points.get(alarm.point);
    if (!point) {
      throw new Error(
        `scene.alarmRules[${index}].point references unknown point "${alarm.point}".`,
      );
    }
    if (Object.hasOwn(alarm, "value")) {
      validatePointValue(
        point,
        alarm.value,
        `scene.alarmRules[${index}].value`,
      );
    }
  }
  return scene;
}
