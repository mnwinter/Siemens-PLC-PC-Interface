import { ASSET_BY_TYPE } from "./catalog.js";
import {
  SCENE_FILE_TYPE,
  validateSceneDocument,
} from "../../prototype/src/sceneLoader.js";

/**
 * Pure authoring model for the Scene Editor proof.
 *
 * Prototype question:
 * Can individually placed catalog assets be composed into a working,
 * player-compatible machine without embedding arbitrary JavaScript or PLC
 * addresses in the scene file?
 *
 * The browser editor is only a shell around these transformations. This module
 * does not know about Three.js, DOM elements, files, or network requests.
 */

export const BEHAVIOR_RECIPES = Object.freeze({
  static: {
    id: "static",
    label: "Static layout",
    description: "Assets render but do not exchange commands or feedback.",
    roles: [],
    plcCommands: [],
    pcFeedback: [],
  },
  conveyorPusher: {
    id: "conveyorPusher",
    label: "Conveyor + photoeye + pusher",
    description:
      "Moves one product to a photoeye, actuates a spring-return pusher, and publishes end-position feedback.",
    roles: [
      {
        id: "conveyorId",
        label: "Transport",
        assetType: "conveyor",
        capability: "transport-surface",
        required: true,
      },
      {
        id: "productId",
        label: "Product",
        assetType: "box",
        capability: "movable-material",
        required: true,
      },
      {
        id: "photoeyeId",
        label: "Presence sensor",
        assetType: "photoeye",
        capability: "presence-sensor",
        required: true,
      },
      {
        id: "pusherId",
        label: "Transfer actuator",
        assetType: "pusher",
        capability: "linear-actuator",
        required: true,
      },
      {
        id: "indicatorId",
        label: "Status indication",
        assetType: "indicator",
        capability: "visual-feedback",
        required: false,
      },
    ],
    plcCommands: ["conveyor_running", "pusher_extend"],
    pcFeedback: [
      "part_at_pusher",
      "pusher_extended",
      "pusher_retracted",
    ],
    points: [
      {
        name: "part_at_pusher",
        type: "BOOL",
        owner: "PC",
        initial: false,
        purpose:
          "Simulator photoeye feedback that turns TRUE when a package reaches the pusher.",
      },
      {
        name: "pusher_extended",
        type: "BOOL",
        owner: "PC",
        initial: false,
        purpose: "Simulator extended-limit feedback from the pusher.",
      },
      {
        name: "pusher_retracted",
        type: "BOOL",
        owner: "PC",
        initial: true,
        purpose: "Simulator retracted-limit feedback from the pusher.",
      },
      {
        name: "conveyor_running",
        type: "BOOL",
        owner: "PLC",
        initial: false,
        role: "output",
        purpose: "PLC motor command that runs the conveyor.",
      },
      {
        name: "pusher_extend",
        type: "BOOL",
        owner: "PLC",
        initial: false,
        role: "output",
        purpose: "PLC solenoid command that extends the spring-return pusher.",
      },
      {
        name: "pusher_position",
        type: "REAL",
        owner: "SIM",
        initial: 0,
        unit: "%",
        purpose: "Internal pusher stroke position used by the scene physics.",
      },
      {
        name: "component_state",
        type: "STRING",
        owner: "SIM",
        initial: "stopped_loaded",
        purpose: "Internal readable state of the conveyor, package, and pusher.",
      },
      {
        name: "parts_completed",
        type: "DINT",
        owner: "SIM",
        initial: 0,
        purpose: "Internal count of packages transferred by the pusher.",
      },
    ],
  },
});

function clone(value) {
  return structuredClone(value);
}

function slug(value, fallback = "scene") {
  const normalized = String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return normalized || fallback;
}

export function createEmptyEditorModel() {
  return {
    scene: {
      fileType: SCENE_FILE_TYPE,
      version: 1,
      id: "untitled_scene",
      name: "Untitled scene",
      description: "Created with the separate Scene Editor proof.",
      camera: {
        position: [10.8, 7, 10.8],
        target: [0, 1, 0],
        fov: 43,
      },
      equipment: [],
    },
    behavior: {
      recipeId: "static",
      bindings: {},
    },
    selectedId: null,
  };
}

export function createConveyorPusherStarter() {
  const model = createEmptyEditorModel();
  model.scene.id = "editor_conveyor_pusher";
  model.scene.name = "Editor conveyor pusher proof";
  model.scene.description =
    "Typed asset composition created in the separate Scene Editor proof.";
  model.scene.equipment = [
    createEquipmentDefinition("conveyor", "main_conveyor", [0, 0, 0]),
    createEquipmentDefinition("box", "product_1", [-3.3, 0.99, 0]),
    createEquipmentDefinition("photoeye", "part_photoeye", [0, 0, 0]),
    createEquipmentDefinition("pusher", "transfer_pusher", [0, 0, -2.15]),
    createEquipmentDefinition("indicator", "cell_stacklight", [3.15, 0, -1.75]),
  ];
  model.behavior.recipeId = "conveyorPusher";
  model.behavior.bindings = {
    conveyorId: "main_conveyor",
    productId: "product_1",
    photoeyeId: "part_photoeye",
    pusherId: "transfer_pusher",
    indicatorId: "cell_stacklight",
  };
  model.selectedId = "main_conveyor";
  return model;
}

export function createEquipmentDefinition(type, id, position = [0, 0, 0]) {
  const catalogItem = ASSET_BY_TYPE.get(type);
  if (!catalogItem) {
    throw new Error(`Unknown catalog type "${type}".`);
  }
  return {
    id,
    type,
    label: `${catalogItem.label} ${id.replaceAll("_", " ")}`,
    position: [...position],
    rotation: [0, 0, 0],
    scale: [1, 1, 1],
    config: clone(catalogItem.defaultConfig),
  };
}

function nextEquipmentId(equipment, type) {
  const used = new Set(equipment.map((item) => item.id));
  let suffix = 1;
  while (used.has(`${type}_${suffix}`)) {
    suffix += 1;
  }
  return `${type}_${suffix}`;
}

function nextPlacement(equipment, catalogItem) {
  const column = equipment.length % 4;
  const row = Math.floor(equipment.length / 4);
  const base = catalogItem.defaultPosition ?? [0, 0, 0];
  return [
    base[0] + (column - 1.5) * 2.25,
    base[1],
    base[2] + row * 2.25,
  ];
}

export function autoBindCompatibleRoles(model, recipeId) {
  const recipe = BEHAVIOR_RECIPES[recipeId];
  if (!recipe) {
    throw new Error(`Unknown behavior recipe "${recipeId}".`);
  }
  const bindings = {};
  const claimedIds = new Set();
  for (const role of recipe.roles) {
    const match = model.scene.equipment.find(
      (item) => item.type === role.assetType && !claimedIds.has(item.id),
    );
    if (match) {
      bindings[role.id] = match.id;
      claimedIds.add(match.id);
    }
  }
  return bindings;
}

export function reduceEditorModel(model, action) {
  const next = clone(model);
  switch (action.type) {
    case "add-asset": {
      const catalogItem = ASSET_BY_TYPE.get(action.assetType);
      if (!catalogItem) {
        throw new Error(`Unknown catalog type "${action.assetType}".`);
      }
      const id = nextEquipmentId(next.scene.equipment, action.assetType);
      next.scene.equipment.push(
        createEquipmentDefinition(
          action.assetType,
          id,
          nextPlacement(next.scene.equipment, catalogItem),
        ),
      );
      next.selectedId = id;
      next.behavior.bindings = autoBindCompatibleRoles(
        next,
        next.behavior.recipeId,
      );
      return next;
    }
    case "select":
      next.selectedId = action.equipmentId ?? null;
      return next;
    case "update-equipment": {
      const index = next.scene.equipment.findIndex(
        (item) => item.id === action.equipmentId,
      );
      if (index < 0) {
        return next;
      }
      const previousId = next.scene.equipment[index].id;
      const patch = clone(action.patch);
      if (Object.hasOwn(patch, "id")) {
        const candidateId = String(patch.id ?? "").trim();
        if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(candidateId)) {
          throw new Error(
            "Equipment ID must start with a letter or number and use only letters, numbers, underscores, or hyphens.",
          );
        }
        const duplicate = next.scene.equipment.some(
          (item, itemIndex) =>
            itemIndex !== index && item.id === candidateId,
        );
        if (duplicate) {
          throw new Error(`Equipment ID "${candidateId}" is already in use.`);
        }
        patch.id = candidateId;
      }
      next.scene.equipment[index] = {
        ...next.scene.equipment[index],
        ...patch,
      };
      const currentId = next.scene.equipment[index].id;
      if (currentId !== previousId) {
        for (const [roleId, equipmentId] of Object.entries(
          next.behavior.bindings,
        )) {
          if (equipmentId === previousId) {
            next.behavior.bindings[roleId] = currentId;
          }
        }
        if (next.selectedId === previousId) {
          next.selectedId = currentId;
        }
      }
      return next;
    }
    case "delete-selected": {
      if (!next.selectedId) {
        return next;
      }
      next.scene.equipment = next.scene.equipment.filter(
        (item) => item.id !== next.selectedId,
      );
      for (const [roleId, equipmentId] of Object.entries(
        next.behavior.bindings,
      )) {
        if (equipmentId === next.selectedId) {
          delete next.behavior.bindings[roleId];
        }
      }
      next.selectedId = next.scene.equipment.at(-1)?.id ?? null;
      return next;
    }
    case "set-recipe":
      if (!BEHAVIOR_RECIPES[action.recipeId]) {
        throw new Error(`Unknown behavior recipe "${action.recipeId}".`);
      }
      next.behavior.recipeId = action.recipeId;
      next.behavior.bindings = autoBindCompatibleRoles(next, action.recipeId);
      return next;
    case "bind-role":
      if (action.equipmentId) {
        next.behavior.bindings[action.roleId] = action.equipmentId;
      } else {
        delete next.behavior.bindings[action.roleId];
      }
      return next;
    case "update-scene":
      next.scene = {
        ...next.scene,
        ...clone(action.patch),
      };
      if (Object.hasOwn(action.patch, "name") && !action.keepId) {
        next.scene.id = slug(action.patch.name, "untitled_scene");
      }
      return next;
    default:
      throw new Error(`Unknown editor action "${action.type}".`);
  }
}

export function validateBehaviorComposition(model) {
  const recipe = BEHAVIOR_RECIPES[model.behavior.recipeId];
  if (!recipe) {
    return {
      valid: false,
      errors: [`Unknown behavior recipe "${model.behavior.recipeId}".`],
    };
  }

  const equipmentById = new Map(
    model.scene.equipment.map((item) => [item.id, item]),
  );
  const errors = [];
  const boundIds = new Set();

  for (const role of recipe.roles) {
    const equipmentId = model.behavior.bindings[role.id];
    if (!equipmentId) {
      if (role.required) {
        errors.push(`${role.label} requires one ${role.assetType} asset.`);
      }
      continue;
    }

    const equipment = equipmentById.get(equipmentId);
    if (!equipment) {
      errors.push(`${role.label} references missing asset "${equipmentId}".`);
      continue;
    }
    if (equipment.type !== role.assetType) {
      errors.push(
        `${role.label} requires type ${role.assetType}; "${equipment.id}" is ${equipment.type}.`,
      );
    }
    if (boundIds.has(equipmentId)) {
      errors.push(`Asset "${equipmentId}" is assigned to more than one role.`);
    }
    boundIds.add(equipmentId);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

function buildSimulation(model) {
  const recipe = BEHAVIOR_RECIPES[model.behavior.recipeId];
  if (recipe.id === "static") {
    return { type: "static" };
  }

  if (recipe.id === "conveyorPusher") {
    const bindings = model.behavior.bindings;
    return {
      type: "conveyorPusher",
      points: clone(recipe.points),
      sourceBehavior: "Scene Editor typed conveyor-pusher composition",
      conveyorId: bindings.conveyorId,
      productId: bindings.productId,
      photoeyeId: bindings.photoeyeId,
      pusherId: bindings.pusherId,
      ...(bindings.indicatorId
        ? { indicatorId: bindings.indicatorId }
        : {}),
      lengthM: 1,
      speedMps: 0.5,
      objectLengthM: 0.2,
      photoeyePositionM: 0.5,
      minimumPhotoeyeOnS: 0.1,
      pusherStrokeTimeS: 0.3,
      transferPositionFraction: 0.8,
      repeatLoadSeconds: 2.5,
    };
  }

  throw new Error(`No compiler exists for behavior recipe "${recipe.id}".`);
}

export function compileSceneDocument(model) {
  if (model.scene.equipment.length === 0) {
    throw new Error("Add at least one asset before saving the scene.");
  }
  const composition = validateBehaviorComposition(model);
  if (!composition.valid) {
    throw new Error(composition.errors.join(" "));
  }

  return validateSceneDocument({
    ...clone(model.scene),
    simulation: buildSimulation(model),
  });
}

export function modelFromSceneDocument(sceneDocument) {
  const scene = validateSceneDocument(sceneDocument);
  if (!BEHAVIOR_RECIPES[scene.simulation.type]) {
    throw new Error(
      `This first editor proof can open static and conveyorPusher scenes. ` +
        `"${scene.simulation.type}" must remain in the Scene Player until its typed editor recipe exists.`,
    );
  }
  const recipeId = scene.simulation.type;
  const recipe = BEHAVIOR_RECIPES[recipeId];
  const bindings = {};

  for (const role of recipe.roles) {
    const equipmentId = scene.simulation[role.id];
    if (typeof equipmentId === "string") {
      bindings[role.id] = equipmentId;
    }
  }

  const {
    simulation: _simulation,
    verification: _verification,
    ...authorableScene
  } = scene;
  return {
    scene: authorableScene,
    behavior: {
      recipeId,
      bindings,
    },
    selectedId: scene.equipment[0]?.id ?? null,
  };
}
