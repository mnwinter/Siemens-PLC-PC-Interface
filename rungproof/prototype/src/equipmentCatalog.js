/**
 * Scene Editor prototype catalog.
 *
 * Stable `type` values deliberately match the existing player AssetFactory.
 * The editor owns authoring metadata and starter defaults; the 3D geometry
 * remains owned by the player AssetFactory.
 */

export const ASSET_CATALOG = Object.freeze([
  {
    type: "conveyor",
    label: "Belt conveyor",
    category: "Material handling",
    glyph: "CV",
    capabilities: ["transport-surface", "run-command"],
    defaultConfig: {
      length: 7,
      width: 1.55,
      deckHeight: 0.9,
      beltColor: 0x252c31,
    },
  },
  {
    type: "box",
    label: "Product / carton",
    category: "Material handling",
    glyph: "BX",
    capabilities: ["movable-material", "presence-target"],
    defaultPosition: [0, 1.0, 0],
    defaultConfig: {
      size: [0.85, 0.72, 0.72],
      color: 0xc88a46,
    },
  },
  {
    type: "photoeye",
    label: "Photoeye",
    category: "Sensors",
    glyph: "PE",
    capabilities: ["presence-sensor", "boolean-feedback"],
    defaultConfig: {
      span: 2.08,
      height: 1.1,
      blocked: false,
    },
  },
  {
    type: "pusher",
    label: "Linear pusher",
    category: "Actuators",
    glyph: "PS",
    capabilities: ["linear-actuator", "position-feedback"],
    defaultConfig: {
      stroke: 1.35,
      centerHeight: 1.38,
      initialPosition: 0,
    },
  },
  {
    type: "motor",
    label: "Motor",
    category: "Actuators",
    glyph: "M",
    capabilities: ["run-command", "rotating-equipment"],
    defaultConfig: {
      length: 1.35,
      diameter: 0.72,
      color: 0x176b87,
      running: false,
    },
  },
  {
    type: "pump",
    label: "Centrifugal pump",
    category: "Actuators",
    glyph: "P",
    capabilities: ["run-command", "fluid-source"],
    defaultConfig: {
      color: 0x176b87,
      running: false,
    },
  },
  {
    type: "fan",
    label: "Industrial fan",
    category: "Actuators",
    glyph: "FN",
    capabilities: ["run-command", "rotating-equipment"],
    defaultConfig: {
      diameter: 1.4,
      centerHeight: 1.45,
      bladeCount: 6,
      bladeColor: 0x96a4aa,
      running: false,
    },
  },
  {
    type: "tank",
    label: "Process tank",
    category: "Process",
    glyph: "TK",
    capabilities: ["fluid-storage", "level-state"],
    defaultConfig: {
      height: 4,
      diameter: 2.6,
      initialLevel: 0.42,
      fluidColor: 0x1597d4,
    },
  },
  {
    type: "levelSensor",
    label: "Level sensor",
    category: "Sensors",
    glyph: "LS",
    capabilities: ["level-sensor", "boolean-feedback"],
    defaultConfig: {
      sensorType: "switch",
      threshold: 0.25,
      mode: "low",
      range: [0, 100],
    },
  },
  {
    type: "radarLevelSensor",
    label: "Radar level sensor",
    category: "Sensors",
    glyph: "LT",
    capabilities: ["level-sensor", "analog-feedback"],
    defaultConfig: {
      initialLevel: 0.42,
      mountSpan: 1.6,
      beamRadius: 0.75,
      range: [0, 4],
      engineeringRange: [0, 100],
    },
  },
  {
    type: "switch",
    label: "Pushbutton",
    category: "Controls",
    glyph: "PB",
    capabilities: ["operator-command"],
    defaultConfig: {
      style: "pushbutton",
      color: 0x21a366,
      active: false,
    },
  },
  {
    type: "rotarySwitch",
    label: "Selector switch",
    category: "Controls",
    glyph: "SS",
    capabilities: ["operator-command", "discrete-position"],
    defaultConfig: {
      positionCount: 3,
      initialPosition: 0,
      minimumAngleDeg: -45,
      maximumAngleDeg: 45,
    },
  },
  {
    type: "indicator",
    label: "Stack light",
    category: "Controls",
    glyph: "IL",
    capabilities: ["visual-feedback"],
    defaultConfig: {
      colors: ["red", "amber", "green"],
      active: "amber",
    },
  },
  {
    type: "pipe",
    label: "Process pipe",
    category: "Process",
    glyph: "PI",
    capabilities: ["fluid-path"],
    defaultConfig: {
      length: 3,
      diameter: 0.35,
      axis: "x",
      color: 0x5e6b73,
    },
  },
  {
    type: "valve",
    label: "Valve",
    category: "Process",
    glyph: "V",
    capabilities: ["flow-control", "normalized-position"],
    defaultConfig: {
      initialPosition: 0,
    },
  },
  {
    type: "liftTable",
    label: "Lift table",
    category: "Machines",
    glyph: "LTB",
    capabilities: ["linear-actuator", "normalized-position"],
    defaultConfig: {
      width: 2.4,
      depth: 1.8,
      minimumHeight: 0.45,
      travel: 1.3,
      initialPosition: 0,
    },
  },
  {
    type: "drillPress",
    label: "Drill press",
    category: "Machines",
    glyph: "DR",
    capabilities: ["run-command", "linear-actuator"],
    defaultConfig: {
      travel: 0.8,
      initialPosition: 0,
      running: false,
      color: 0x176b87,
    },
  },
  {
    type: "robotArm",
    label: "Robot arm",
    category: "Machines",
    glyph: "RB",
    capabilities: ["run-command", "normalized-position"],
    defaultConfig: {
      initialPosition: 0,
      running: false,
    },
  },
  {
    type: "rollerShutter",
    label: "Roller shutter",
    category: "Machines",
    glyph: "RS",
    capabilities: ["linear-actuator", "normalized-position"],
    defaultConfig: {
      width: 3,
      height: 3,
      initialPosition: 1,
    },
  },
  {
    type: "rotaryTable",
    label: "Rotary table",
    category: "Machines",
    glyph: "RT",
    capabilities: ["rotary-actuator", "normalized-position"],
    defaultConfig: {
      radius: 1.2,
      angleRangeDeg: 360,
      initialPosition: 0,
    },
  },
  {
    type: "machine",
    label: "Enclosed machine",
    category: "Machines",
    glyph: "MC",
    capabilities: ["run-command", "machine-envelope"],
    defaultConfig: {
      size: [2.5, 2.4, 2],
      color: 0x47606c,
      running: false,
    },
  },
  { type: "palletLoad", label: "Loaded shipping pallet", category: "Material handling", glyph: "PL", capabilities: ["movable-material", "presence-target"], defaultConfig: { caseWidthM: 0.5, caseHeightM: 0.32, caseDepthM: 0.42, layers: 2, color: 0x9c7652 } },
  { type: "containerReceiver", label: "Container receiver", category: "Material handling", glyph: "CR", capabilities: ["container-positioning"], defaultConfig: { size: [2.1, 2.7, 1.7], color: 0x536873, running: false } },
  { type: "toteFiller", label: "Tote filling station", category: "Process", glyph: "TF", capabilities: ["fluid-dispense", "normalized-position"], defaultConfig: { initialPosition: 0 } },
  { type: "toteCapper", label: "Tote capper", category: "Process", glyph: "TC", capabilities: ["container-capping", "run-command"], defaultConfig: { size: [1.8, 2.5, 1.4], color: 0x6f7f88, running: false } },
  { type: "toteLabeler", label: "Tote labeler", category: "Process", glyph: "TL", capabilities: ["container-labeling", "run-command"], defaultConfig: { size: [1.8, 2.5, 1.4], color: 0x176b87, running: false } },
  { type: "toteVision", label: "Tote vision inspection", category: "Sensors", glyph: "TV", capabilities: ["inspection-sensor", "run-command"], defaultConfig: { size: [1.8, 2.5, 1.4], color: 0x536873, running: false } },
  { type: "meteringSkid", label: "Fluid metering skid", category: "Process", glyph: "MS", capabilities: ["fluid-source", "run-command"], defaultConfig: { size: [2, 2.5, 1.3], color: 0x176b87, running: false } },
  { type: "sizeSensorBank", label: "Parcel size sensor bank", category: "Sensors", glyph: "SB", capabilities: ["presence-sensor", "size-classification"], defaultConfig: { span: 2.05, beamHeightsM: [0.95, 1.3, 1.65], blocked: false } },
]);

export const ASSET_BY_TYPE = new Map(
  ASSET_CATALOG.map((asset) => [asset.type, asset]),
);

export const CATALOG_CATEGORIES = Object.freeze(
  [...new Set(ASSET_CATALOG.map((asset) => asset.category))],
);

export const EQUIPMENT_TYPES = new Set(
  ASSET_CATALOG.map((asset) => asset.type),
);

export const MAX_SCENE_EQUIPMENT = 256;
export const MAX_SCENE_COMPLEXITY = 4_000;

const CONFIG_FIELDS = Object.freeze({
  action: { kind: "identifier" },
  active: { kind: "booleanOrString" },
  angleRangeDeg: { kind: "number", min: -3600, max: 3600 },
  axis: { kind: "enum", values: ["x", "y", "z"] },
  beamCenterHeightM: { kind: "number", min: 0.01, max: 100 },
  beamHeightsM: { kind: "vector", min: 0.01, max: 100 },
  beamRadius: { kind: "number", min: 0.01, max: 100 },
  beltColor: { kind: "color" },
  bladeColor: { kind: "color" },
  bladeCount: { kind: "integer", min: 2, max: 24 },
  blocked: { kind: "boolean" },
  centerHeight: { kind: "number", min: 0, max: 100 },
  caseDepthM: { kind: "number", min: 0.01, max: 100 },
  caseHeightM: { kind: "number", min: 0.01, max: 100 },
  caseWidthM: { kind: "number", min: 0.01, max: 100 },
  color: { kind: "color" },
  colors: { kind: "stringArray", minItems: 1, maxItems: 8 },
  deckHeight: { kind: "number", min: 0.01, max: 100 },
  depth: { kind: "number", min: 0.01, max: 100 },
  diameter: { kind: "number", min: 0.01, max: 100 },
  engineeringRange: { kind: "range" },
  fluidColor: { kind: "color" },
  height: { kind: "number", min: 0.01, max: 100 },
  initialLevel: { kind: "number", min: 0, max: 1 },
  initialPosition: { kind: "number", min: 0, max: 16 },
  length: { kind: "number", min: 0.01, max: 100 },
  layers: { kind: "integer", min: 1, max: 20 },
  maximumAngleDeg: { kind: "number", min: -3600, max: 3600 },
  measurement: {
    kind: "enum",
    values: ["level", "distance", "non-contact radar"],
  },
  minimumAngleDeg: { kind: "number", min: -3600, max: 3600 },
  minimumHeight: { kind: "number", min: 0, max: 100 },
  mode: { kind: "enum", values: ["low", "high"] },
  mountSpan: { kind: "number", min: 0.01, max: 100 },
  positionCount: { kind: "integer", min: 2, max: 16 },
  radius: { kind: "number", min: 0.01, max: 100 },
  range: { kind: "range" },
  running: { kind: "boolean" },
  sensorType: { kind: "enum", values: ["switch", "discrete", "analog"] },
  showSupport: { kind: "boolean" },
  size: { kind: "vector", min: 0.01, max: 100 },
  span: { kind: "number", min: 0.01, max: 100 },
  stroke: { kind: "number", min: 0.01, max: 100 },
  style: {
    kind: "enum",
    values: ["pushbutton", "mushroom", "emergency", "selector", "toggle"],
  },
  supportHeight: { kind: "number", min: 0, max: 100 },
  threshold: { kind: "number", min: 0, max: 1 },
  travel: { kind: "number", min: 0.01, max: 100 },
  travelAxis: { kind: "enum", values: ["x", "y", "z"] },
  width: { kind: "number", min: 0.01, max: 100 },
});

const CONFIG_KEYS_BY_TYPE = Object.freeze({
  motor: ["length", "diameter", "color", "running"],
  conveyor: ["length", "width", "deckHeight", "beltColor", "running"],
  box: ["size", "color"],
  photoeye: ["span", "height", "beamCenterHeightM", "blocked"],
  switch: ["style", "color", "active", "action"],
  indicator: ["colors", "active"],
  pump: ["color", "running"],
  fan: [
    "diameter",
    "centerHeight",
    "bladeCount",
    "bladeColor",
    "running",
  ],
  pusher: ["stroke", "centerHeight", "initialPosition", "travelAxis"],
  tank: ["height", "diameter", "initialLevel", "fluidColor"],
  levelSensor: [
    "sensorType",
    "threshold",
    "mode",
    "range",
    "engineeringRange",
    "active",
  ],
  radarLevelSensor: [
    "initialLevel",
    "mountSpan",
    "beamRadius",
    "range",
    "engineeringRange",
    "measurement",
  ],
  pipe: [
    "length",
    "diameter",
    "axis",
    "color",
    "showSupport",
    "supportHeight",
  ],
  rotarySwitch: [
    "positionCount",
    "initialPosition",
    "minimumAngleDeg",
    "maximumAngleDeg",
    "action",
  ],
  liftTable: ["width", "depth", "minimumHeight", "travel", "initialPosition"],
  valve: ["initialPosition"],
  drillPress: ["travel", "initialPosition", "running", "color"],
  robotArm: ["initialPosition", "running"],
  rollerShutter: ["width", "height", "initialPosition"],
  rotaryTable: ["radius", "angleRangeDeg", "initialPosition"],
  machine: ["size", "color", "running"],
  palletLoad: ["caseWidthM", "caseHeightM", "caseDepthM", "layers", "color"],
  containerReceiver: ["size", "color", "running"],
  toteFiller: ["initialPosition"],
  toteCapper: ["size", "color", "running"],
  toteLabeler: ["size", "color", "running"],
  toteVision: ["size", "color", "running"],
  meteringSkid: ["size", "color", "running"],
  sizeSensorBank: ["span", "beamHeightsM", "blocked"],
});

function requireFinite(value, path) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`${path} must be a finite number.`);
  }
  return value;
}

function validateField(value, field, path) {
  if (field.kind === "booleanOrString") {
    if (
      value !== null &&
      typeof value !== "boolean" &&
      (typeof value !== "string" ||
        value.trim() === "" ||
        value.length > 64)
    ) {
      throw new Error(`${path} must be null, a boolean, or a short state name.`);
    }
    return;
  }
  if (field.kind === "boolean") {
    if (typeof value !== "boolean") {
      throw new Error(`${path} must be a boolean.`);
    }
    return;
  }
  if (field.kind === "identifier") {
    if (
      typeof value !== "string" ||
      !/^[A-Za-z][A-Za-z0-9_.:-]{0,127}$/.test(value)
    ) {
      throw new Error(`${path} must be a symbolic action name.`);
    }
    return;
  }
  if (field.kind === "enum") {
    if (!field.values.includes(value)) {
      throw new Error(`${path} must be one of: ${field.values.join(", ")}.`);
    }
    return;
  }
  if (field.kind === "color") {
    if (!Number.isInteger(value) || value < 0 || value > 0xffffff) {
      throw new Error(`${path} must be a 24-bit integer color.`);
    }
    return;
  }
  if (field.kind === "stringArray") {
    if (
      !Array.isArray(value) ||
      value.length < field.minItems ||
      value.length > field.maxItems ||
      value.some(
        (item) =>
          typeof item !== "string" ||
          item.trim() === "" ||
          item.length > 64,
      )
    ) {
      throw new Error(
        `${path} must contain ${field.minItems}-${field.maxItems} short strings.`,
      );
    }
    return;
  }
  if (field.kind === "range") {
    if (
      typeof value === "string" &&
      value.trim() !== "" &&
      value.length <= 64
    ) {
      return;
    }
    if (
      !Array.isArray(value) ||
      value.length !== 2 ||
      value.some((item) => typeof item !== "number" || !Number.isFinite(item)) ||
      value[0] >= value[1] ||
      Math.abs(value[0]) > 1_000_000 ||
      Math.abs(value[1]) > 1_000_000
    ) {
      throw new Error(
        `${path} must be a short range label or increasing two-number range.`,
      );
    }
    return;
  }
  if (field.kind === "vector") {
    if (
      !Array.isArray(value) ||
      value.length !== 3 ||
      value.some(
        (item) =>
          typeof item !== "number" ||
          !Number.isFinite(item) ||
          item < field.min ||
          item > field.max,
      )
    ) {
      throw new Error(
        `${path} must contain three values from ${field.min} to ${field.max}.`,
      );
    }
    return;
  }

  requireFinite(value, path);
  if (
    (field.kind === "integer" && !Number.isInteger(value)) ||
    value < field.min ||
    value > field.max
  ) {
    throw new Error(`${path} must be from ${field.min} to ${field.max}.`);
  }
}

export function validateEquipmentConfig(type, input, path) {
  const config =
    input === undefined
      ? {}
      : input !== null && typeof input === "object" && !Array.isArray(input)
        ? { ...input }
        : null;
  if (config === null) {
    throw new Error(`${path} must be an object.`);
  }

  const allowed = new Set(CONFIG_KEYS_BY_TYPE[type] ?? []);
  for (const [key, value] of Object.entries(config)) {
    if (!allowed.has(key)) {
      throw new Error(`${path}.${key} is not supported for "${type}".`);
    }
    validateField(value, CONFIG_FIELDS[key], `${path}.${key}`);
  }
  if (
    Object.hasOwn(config, "initialPosition") &&
    type !== "rotarySwitch" &&
    config.initialPosition > 1
  ) {
    throw new Error(`${path}.initialPosition must be from 0 to 1 for "${type}".`);
  }
  if (
    type === "rotarySwitch" &&
    Object.hasOwn(config, "initialPosition") &&
    config.initialPosition >= (config.positionCount ?? 3)
  ) {
    throw new Error(
      `${path}.initialPosition must be below the selector positionCount.`,
    );
  }
  return config;
}

function equipmentComplexity(item) {
  if (item.type === "conveyor") {
    return 12 + Math.ceil((item.config.length ?? 7) / 0.55) * 2;
  }
  if (item.type === "fan") {
    return 12 + (item.config.bladeCount ?? 6) * 2;
  }
  if (item.type === "rollerShutter") {
    return 12 + Math.max(8, Math.round((item.config.height ?? 3) / 0.22));
  }
  return 24;
}

export function validateSceneComplexity(equipment) {
  if (equipment.length > MAX_SCENE_EQUIPMENT) {
    throw new Error(
      `scene.equipment cannot exceed ${MAX_SCENE_EQUIPMENT} items.`,
    );
  }
  const complexity = equipment.reduce(
    (total, item) => total + equipmentComplexity(item),
    0,
  );
  if (complexity > MAX_SCENE_COMPLEXITY) {
    throw new Error(
      `Scene geometry complexity ${complexity} exceeds ${MAX_SCENE_COMPLEXITY}.`,
    );
  }
  return complexity;
}
