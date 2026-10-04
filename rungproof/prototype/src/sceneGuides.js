/**
 * Pure helpers for scene-specific training guides.
 *
 * The configuration contract is always derived from simulation.points so the
 * displayed tag names and types cannot drift from the scene runtime.
 */

const EXTERNAL_POINT_OWNERS = new Set(["PC", "PLC"]);

function pointBindingsFor(scene, pointName) {
  return (scene.simulation?.pointBindings ?? []).filter(
    (binding) => binding.point === pointName,
  );
}

function equipmentLabelsFor(scene, bindings) {
  const equipmentById = new Map(
    (scene.equipment ?? []).map((equipment) => [
      equipment.id,
      equipment.label ?? equipment.id,
    ]),
  );
  return [
    ...new Set(
      bindings
        .map((binding) => equipmentById.get(binding.equipmentId))
        .filter(Boolean),
    ),
  ];
}

function actionLabelsFor(scene, pointName) {
  return [
    ...new Set(
      (scene.simulation?.actions ?? [])
        .filter((action) => action.point === pointName)
        .map((action) => action.label ?? action.id)
        .filter(Boolean),
    ),
  ];
}

function purposeFor(scene, point) {
  if (typeof point.purpose === "string" && point.purpose.trim()) {
    return point.purpose.trim();
  }

  const bindings = pointBindingsFor(scene, point.name);
  const equipmentLabels = equipmentLabelsFor(scene, bindings);
  const actionLabels = actionLabelsFor(scene, point.name);

  if (point.owner === "PC") {
    if (actionLabels.length > 0) {
      return `Simulator/operator input from ${actionLabels.join(", ")}.`;
    }
    if (equipmentLabels.length > 0) {
      return `Simulator feedback from ${equipmentLabels.join(", ")}.`;
    }
    return "Simulator-generated input or process feedback read by the PLC.";
  }

  if (equipmentLabels.length > 0) {
    return `PLC command consumed by ${equipmentLabels.join(", ")}.`;
  }
  return "PLC command consumed by the scene runtime.";
}

export function formatGuideValue(value) {
  if (typeof value === "boolean") {
    return value ? "TRUE" : "FALSE";
  }
  if (typeof value === "string") {
    return `"${value}"`;
  }
  return String(value);
}

export function getSceneConfiguration(scene) {
  const points = Array.isArray(scene?.simulation?.points)
    ? scene.simulation.points
    : [];

  const requiredTags = points
    .filter(
      (point) =>
        EXTERNAL_POINT_OWNERS.has(point.owner) && point.role !== "memory",
    )
    .map((point) => ({
      name: point.name,
      type: point.type,
      owner: point.owner,
      direction:
        point.owner === "PC"
          ? "Simulator → PLC input"
          : "PLC → Simulator output",
      initial: point.initial,
      purpose: purposeFor(scene, point),
    }));

  const internalPoints = points
    .filter(
      (point) =>
        point.owner === "SIM" ||
        (point.owner === "PLC" && point.role === "memory"),
    )
    .map((point) => point.name);

  return {
    requiredTags,
    internalPoints,
  };
}

export function getSceneHints(scene) {
  return Array.isArray(scene?.training?.hints)
    ? scene.training.hints
    : [];
}

export function getSceneSolution(scene) {
  const solution = scene?.training?.solution;
  if (!solution || typeof solution !== "object") {
    return null;
  }
  return solution;
}

export function getSceneMachineGuide(scene) {
  const guide = scene?.training?.machineGuide ?? scene?.machineGuide;
  if (!guide || typeof guide !== "object") {
    return null;
  }
  return guide;
}

export function getSceneProgression(scene) {
  const training = scene?.training;
  if (!training || typeof training !== "object") {
    return null;
  }
  return {
    sequenceNumber: training.sequenceNumber ?? null,
    inheritsFrom: training.inheritsFrom ?? null,
    foundation: training.foundation ?? null,
    retainedTags: Array.isArray(training.retainedTags)
      ? training.retainedTags
      : [],
    addedTags: Array.isArray(training.addedTags) ? training.addedTags : [],
    changedTags: Array.isArray(training.changedTags)
      ? training.changedTags
      : [],
    previousAcceptance: Array.isArray(training.previousAcceptance)
      ? training.previousAcceptance
      : [],
  };
}
