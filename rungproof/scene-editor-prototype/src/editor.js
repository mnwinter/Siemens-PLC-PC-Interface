import * as THREE from "../../vendor/three/three.module.min.js";
import { OrbitControls } from "../../vendor/three/addons/controls/OrbitControls.js";
import { AssetFactory } from "../../prototype/src/assetFactory.js";
import {
  SCENE_FILE_MIME,
  loadSceneFromFile,
  sceneDownloadName,
  serializeSceneDocument,
} from "../../prototype/src/sceneLoader.js";
import { escapeHtml } from "../../prototype/src/safeMarkup.js";
import { postLocal } from "../../prototype/src/localApi.js";
import {
  ASSET_BY_TYPE,
  ASSET_CATALOG,
  CATALOG_CATEGORIES,
  validateEquipmentConfig,
} from "./catalog.js";
import {
  BEHAVIOR_RECIPES,
  compileSceneDocument,
  createConveyorPusherStarter,
  createEmptyEditorModel,
  modelFromSceneDocument,
  reduceEditorModel,
  validateBehaviorComposition,
} from "./editorModel.js";

const factory = new AssetFactory();
const viewport = document.querySelector("#viewport");
const messageElement = document.querySelector("#message");
const APP_WINDOW_MODE =
  new URLSearchParams(window.location.search).get("appWindow") === "1";

let model = createConveyorPusherStarter();
let undoStack = [];
let redoStack = [];
let selectionBox = null;
let catalogFilter = "";

const threeScene = new THREE.Scene();
threeScene.background = new THREE.Color(0x071017);
threeScene.fog = new THREE.Fog(0x071017, 24, 52);

const camera = new THREE.PerspectiveCamera(43, 1, 0.05, 200);
camera.position.fromArray(model.scene.camera.position);

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.6));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
viewport.append(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.fromArray(model.scene.camera.target);
controls.minDistance = 2.5;
controls.maxDistance = 45;
controls.maxPolarAngle = Math.PI * 0.49;
controls.update();

threeScene.add(new THREE.HemisphereLight(0xaed8ef, 0x27333a, 1.65));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.25);
keyLight.position.set(8, 14, 7);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.left = -18;
keyLight.shadow.camera.right = 18;
keyLight.shadow.camera.top = 18;
keyLight.shadow.camera.bottom = -18;
threeScene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0x62b9e8, 0.65);
fillLight.position.set(-9, 6, -8);
threeScene.add(fillLight);

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(48, 48),
  new THREE.MeshStandardMaterial({
    color: 0x172229,
    roughness: 0.92,
    metalness: 0.05,
  }),
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
threeScene.add(floor);

const grid = new THREE.GridHelper(48, 48, 0x35657a, 0x253945);
grid.position.y = 0.004;
threeScene.add(grid);

const assetRoot = new THREE.Group();
assetRoot.name = "Authored equipment";
threeScene.add(assetRoot);

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function clone(value) {
  return structuredClone(value);
}

function showMessage(message, tone = "normal") {
  messageElement.textContent = message;
  messageElement.className = tone === "normal" ? "" : tone;
}

function runSafely(operation) {
  try {
    operation();
  } catch (error) {
    console.error(error);
    showMessage(error instanceof Error ? error.message : String(error), "error");
  }
}

function commit(nextModel, message, { resetCamera = false } = {}) {
  undoStack.push(clone(model));
  if (undoStack.length > 75) {
    undoStack.shift();
  }
  redoStack = [];
  model = nextModel;
  if (resetCamera) {
    camera.position.fromArray(model.scene.camera.position);
    controls.target.fromArray(model.scene.camera.target);
    controls.update();
  }
  renderEditor();
  showMessage(message);
}

function dispatch(action, message) {
  runSafely(() => commit(reduceEditorModel(model, action), message));
}

function undo() {
  if (undoStack.length === 0) {
    return;
  }
  redoStack.push(clone(model));
  model = undoStack.pop();
  renderEditor();
  showMessage("Undid the last editor change.");
}

function redo() {
  if (redoStack.length === 0) {
    return;
  }
  undoStack.push(clone(model));
  model = redoStack.pop();
  renderEditor();
  showMessage("Redid the editor change.");
}

function disposeObject(object) {
  object.traverse((child) => {
    child.geometry?.dispose?.();
    if (Array.isArray(child.material)) {
      child.material.forEach((item) => item.dispose?.());
    } else {
      child.material?.dispose?.();
    }
  });
}

function rebuildViewport() {
  if (selectionBox) {
    threeScene.remove(selectionBox);
    selectionBox.dispose();
    selectionBox = null;
  }

  while (assetRoot.children.length > 0) {
    const child = assetRoot.children[0];
    assetRoot.remove(child);
    disposeObject(child);
  }

  for (const definition of model.scene.equipment) {
    const group = factory.create(definition);
    assetRoot.add(group);
    if (definition.id === model.selectedId) {
      selectionBox = new THREE.BoxHelper(group, 0x38bdf8);
      selectionBox.material.depthTest = false;
      selectionBox.renderOrder = 20;
      threeScene.add(selectionBox);
    }
  }
}

function renderLibrary() {
  const filter = catalogFilter.trim().toLowerCase();
  const visible = ASSET_CATALOG.filter((asset) => {
    const haystack = `${asset.label} ${asset.type} ${asset.category} ${asset.capabilities.join(" ")}`.toLowerCase();
    return haystack.includes(filter);
  });

  document.querySelector("#asset-count").textContent =
    `${visible.length}/${ASSET_CATALOG.length}`;
  document.querySelector("#asset-library").innerHTML = CATALOG_CATEGORIES.map(
    (category) => {
      const categoryAssets = visible.filter(
        (asset) => asset.category === category,
      );
      if (categoryAssets.length === 0) {
        return "";
      }
      return `
        <section class="catalog-group">
          <h2>${escapeHtml(category)}</h2>
          ${categoryAssets
            .map(
              (asset) => `
                <button
                  class="asset-card"
                  type="button"
                  data-add-type="${escapeHtml(asset.type)}"
                  title="Add ${escapeHtml(asset.label)}"
                >
                  <span class="glyph">${escapeHtml(asset.glyph)}</span>
                  <span>${escapeHtml(asset.label)}</span>
                  <span class="add-mark">+</span>
                </button>
              `,
            )
            .join("")}
        </section>
      `;
    },
  ).join("");
}

function renderSceneMetadata() {
  document.querySelector("#scene-name-heading").textContent = model.scene.name;
  document.querySelector("#scene-name").value = model.scene.name;
  document.querySelector("#scene-id").value = model.scene.id;
  document.querySelector("#scene-description").value =
    model.scene.description ?? "";
  document.querySelector("#scene-asset-count").textContent =
    `${model.scene.equipment.length} asset${model.scene.equipment.length === 1 ? "" : "s"}`;
}

function renderSceneTree() {
  const tree = document.querySelector("#scene-tree");
  if (model.scene.equipment.length === 0) {
    tree.innerHTML =
      '<div class="empty-state">Pick a part from the asset library.</div>';
    return;
  }
  tree.innerHTML = model.scene.equipment
    .map((item) => {
      const catalogItem = ASSET_BY_TYPE.get(item.type);
      return `
        <button
          class="scene-tree-button ${item.id === model.selectedId ? "is-selected" : ""}"
          type="button"
          data-select-id="${escapeHtml(item.id)}"
        >
          <span class="mini-glyph">${escapeHtml(catalogItem?.glyph ?? "?")}</span>
          <span>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${escapeHtml(item.id)} · ${escapeHtml(item.type)}</small>
          </span>
        </button>
      `;
    })
    .join("");
}

function selectedEquipment() {
  return model.scene.equipment.find((item) => item.id === model.selectedId);
}

function renderInspector() {
  const selected = selectedEquipment();
  const empty = document.querySelector("#empty-inspector");
  const inspector = document.querySelector("#equipment-inspector");
  const typeBadge = document.querySelector("#selected-type");
  document.querySelector("#delete-button").disabled = !selected;

  if (!selected) {
    empty.hidden = false;
    inspector.hidden = true;
    typeBadge.textContent = "NONE";
    document.querySelector("#selection-status").textContent =
      "No asset selected";
    return;
  }

  const catalogItem = ASSET_BY_TYPE.get(selected.type);
  empty.hidden = true;
  inspector.hidden = false;
  typeBadge.textContent = selected.type.toUpperCase();
  document.querySelector("#selection-status").textContent =
    `${selected.label} · ${selected.id}`;
  document.querySelector("#equipment-label").value = selected.label;
  document.querySelector("#equipment-id").value = selected.id;

  ["x", "y", "z"].forEach((axis, index) => {
    document.querySelector(`#position-${axis}`).value =
      String(selected.position[index]);
    document.querySelector(`#rotation-${axis}`).value =
      String(selected.rotation[index]);
  });
  document.querySelector("#equipment-config").value = JSON.stringify(
    selected.config,
    null,
    2,
  );
  document.querySelector("#capability-list").innerHTML = (
    catalogItem?.capabilities ?? []
  )
    .map((capability) => `<span>${escapeHtml(capability)}</span>`)
    .join("");
}

function roleOptions(role) {
  const compatible = model.scene.equipment.filter(
    (item) => item.type === role.assetType,
  );
  return [
    `<option value="">${role.required ? "Select required asset…" : "None"}</option>`,
    ...compatible.map(
      (item) => `
        <option
          value="${escapeHtml(item.id)}"
          ${model.behavior.bindings[role.id] === item.id ? "selected" : ""}
        >
          ${escapeHtml(item.label)} (${escapeHtml(item.id)})
        </option>
      `,
    ),
  ].join("");
}

function renderBehavior() {
  const recipe = BEHAVIOR_RECIPES[model.behavior.recipeId];
  document.querySelector("#behavior-recipe").innerHTML = Object.values(
    BEHAVIOR_RECIPES,
  )
    .map(
      (item) => `
        <option
          value="${escapeHtml(item.id)}"
          ${item.id === recipe.id ? "selected" : ""}
        >${escapeHtml(item.label)}</option>
      `,
    )
    .join("");
  document.querySelector("#behavior-description").textContent =
    recipe.description;

  const rolesElement = document.querySelector("#behavior-roles");
  rolesElement.innerHTML =
    recipe.roles.length === 0
      ? ""
      : recipe.roles
          .map(
            (role) => `
              <div class="role-row">
                <label>
                  ${escapeHtml(role.label)}
                  <small>${escapeHtml(role.capability)}</small>
                </label>
                <select data-role-id="${escapeHtml(role.id)}">
                  ${roleOptions(role)}
                </select>
              </div>
            `,
          )
          .join("");

  const contract = document.querySelector("#point-contract");
  contract.innerHTML =
    recipe.plcCommands.length === 0 && recipe.pcFeedback.length === 0
      ? ""
      : `
          <section class="point-group">
            <header><span>PLC → plant commands</span><span>PLC OWNED</span></header>
            <ul>${recipe.plcCommands.map((point) => `<li>${escapeHtml(point)}</li>`).join("")}</ul>
          </section>
          <section class="point-group">
            <header><span>Plant → PLC feedback</span><span>PC OWNED</span></header>
            <ul>${recipe.pcFeedback.map((point) => `<li>${escapeHtml(point)}</li>`).join("")}</ul>
          </section>
        `;

  const result = validateBehaviorComposition(model);
  const diagnostics = document.querySelector("#behavior-diagnostics");
  const status = document.querySelector("#composition-status");
  diagnostics.className = `diagnostics ${result.valid ? "valid" : "invalid"}`;
  status.className = `status-chip ${result.valid ? "valid" : "invalid"}`;
  if (result.valid) {
    diagnostics.textContent =
      recipe.id === "static"
        ? "Valid static scene. No command or feedback contract is active."
        : "Valid typed composition. This scene can compile to the current player format.";
    status.textContent =
      recipe.id === "static" ? "STATIC LAYOUT" : "COMPOSITION VALID";
  } else {
    diagnostics.innerHTML = `
      <strong>Composition is incomplete.</strong>
      <ul>${result.errors.map((error) => `<li>${escapeHtml(error)}</li>`).join("")}</ul>
    `;
    status.textContent = "COMPOSITION INCOMPLETE";
  }
}

function renderHistory() {
  document.querySelector("#undo-button").disabled = undoStack.length === 0;
  document.querySelector("#redo-button").disabled = redoStack.length === 0;
}

function renderEditor() {
  renderSceneMetadata();
  renderSceneTree();
  renderInspector();
  renderBehavior();
  renderHistory();
  rebuildViewport();
}

function updateSelectedVector(field, axisIndex, value) {
  const selected = selectedEquipment();
  if (!selected) {
    return;
  }
  const number = Number(value);
  if (!Number.isFinite(number)) {
    throw new Error("Transform values must be finite numbers.");
  }
  const vector = [...selected[field]];
  vector[axisIndex] = number;
  commit(
    reduceEditorModel(model, {
      type: "update-equipment",
      equipmentId: selected.id,
      patch: { [field]: vector },
    }),
    `Updated ${selected.id} ${field}.`,
  );
}

function compileCurrentScene() {
  return compileSceneDocument(model);
}

async function saveToPlayerLibrary() {
  const scene = compileCurrentScene();
  const response = await postLocal("/api/scenes", {
    contentType: SCENE_FILE_MIME,
    body: serializeSceneDocument(scene),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error ?? `Save failed with HTTP ${response.status}.`);
  }
  showMessage(
    `${payload.overwritten ? "Updated" : "Saved"} ${payload.fileName} in the Scene Player library.`,
    "success",
  );
}

function downloadCurrentScene() {
  const scene = compileCurrentScene();
  const blob = new Blob([serializeSceneDocument(scene)], {
    type: `${SCENE_FILE_MIME};charset=utf-8`,
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = sceneDownloadName(scene);
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
  showMessage(`Downloaded ${sceneDownloadName(scene)}.`, "success");
}

function installModel(nextModel, message) {
  undoStack = [];
  redoStack = [];
  model = nextModel;
  camera.position.fromArray(model.scene.camera.position);
  controls.target.fromArray(model.scene.camera.target);
  controls.update();
  renderEditor();
  showMessage(message, "success");
}

document.querySelector("#asset-library").addEventListener("click", (event) => {
  const button = event.target.closest("[data-add-type]");
  if (!button) {
    return;
  }
  dispatch(
    { type: "add-asset", assetType: button.dataset.addType },
    `Added ${ASSET_BY_TYPE.get(button.dataset.addType)?.label ?? button.dataset.addType}.`,
  );
});

document.querySelector("#library-filter").addEventListener("input", (event) => {
  catalogFilter = event.target.value;
  renderLibrary();
});

document.querySelector("#scene-tree").addEventListener("click", (event) => {
  const button = event.target.closest("[data-select-id]");
  if (!button) {
    return;
  }
  model = reduceEditorModel(model, {
    type: "select",
    equipmentId: button.dataset.selectId,
  });
  renderEditor();
});

document.querySelector("#behavior-roles").addEventListener("change", (event) => {
  const select = event.target.closest("[data-role-id]");
  if (!select) {
    return;
  }
  dispatch(
    {
      type: "bind-role",
      roleId: select.dataset.roleId,
      equipmentId: select.value,
    },
    `Updated ${select.dataset.roleId} behavior binding.`,
  );
});

document.querySelector("#behavior-recipe").addEventListener("change", (event) => {
  dispatch(
    { type: "set-recipe", recipeId: event.target.value },
    `Selected ${BEHAVIOR_RECIPES[event.target.value].label}.`,
  );
});

document.querySelector("#scene-name").addEventListener("change", (event) => {
  dispatch(
    {
      type: "update-scene",
      patch: { name: event.target.value.trim() || "Untitled scene" },
      keepId: true,
    },
    "Updated scene name.",
  );
});

document.querySelector("#scene-id").addEventListener("change", (event) => {
  const candidate = event.target.value.trim();
  runSafely(() => {
    if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(candidate)) {
      throw new Error(
        "Scene ID must start with a letter or number and use only letters, numbers, underscores, or hyphens.",
      );
    }
    commit(
      reduceEditorModel(model, {
        type: "update-scene",
        patch: { id: candidate },
        keepId: true,
      }),
      "Updated scene ID.",
    );
  });
});

document
  .querySelector("#scene-description")
  .addEventListener("change", (event) => {
    dispatch(
      {
        type: "update-scene",
        patch: { description: event.target.value },
        keepId: true,
      },
      "Updated scene description.",
    );
  });

document.querySelector("#equipment-label").addEventListener("change", (event) => {
  const selected = selectedEquipment();
  if (!selected) {
    return;
  }
  dispatch(
    {
      type: "update-equipment",
      equipmentId: selected.id,
      patch: { label: event.target.value.trim() || selected.id },
    },
    `Updated ${selected.id} label.`,
  );
});

document.querySelector("#equipment-id").addEventListener("change", (event) => {
  const selected = selectedEquipment();
  if (!selected) {
    return;
  }
  dispatch(
    {
      type: "update-equipment",
      equipmentId: selected.id,
      patch: { id: event.target.value },
    },
    `Renamed ${selected.id}.`,
  );
});

["position", "rotation"].forEach((field) => {
  ["x", "y", "z"].forEach((axis, index) => {
    document.querySelector(`#${field}-${axis}`).addEventListener(
      "change",
      (event) => runSafely(() => updateSelectedVector(field, index, event.target.value)),
    );
  });
});

document
  .querySelector("#equipment-config")
  .addEventListener("change", (event) => {
    const selected = selectedEquipment();
    if (!selected) {
      return;
    }
    runSafely(() => {
      const config = validateEquipmentConfig(
        selected.type,
        JSON.parse(event.target.value),
        `${selected.id}.config`,
      );
      commit(
        reduceEditorModel(model, {
          type: "update-equipment",
          equipmentId: selected.id,
          patch: { config },
        }),
        `Updated ${selected.id} configuration.`,
      );
    });
  });

document.querySelector("#delete-button").addEventListener("click", () => {
  const selected = selectedEquipment();
  if (!selected) {
    return;
  }
  dispatch({ type: "delete-selected" }, `Deleted ${selected.id}.`);
});

document.querySelector("#undo-button").addEventListener("click", undo);
document.querySelector("#redo-button").addEventListener("click", redo);

document.querySelector("#new-button").addEventListener("click", () => {
  installModel(createEmptyEditorModel(), "Created a new empty scene.");
});

document.querySelector("#starter-button").addEventListener("click", () => {
  installModel(
    createConveyorPusherStarter(),
    "Loaded the typed conveyor-pusher starter assembly.",
  );
});

document.querySelector("#open-button").addEventListener("click", () => {
  document.querySelector("#scene-file-input").click();
});

document.querySelector("#scene-file-input").addEventListener("change", (event) => {
  const [file] = event.target.files;
  if (!file) {
    return;
  }
  loadSceneFromFile(file)
    .then((scene) => {
      installModel(
        modelFromSceneDocument(scene),
        `Opened ${file.name} in the editor.`,
      );
    })
    .catch((error) => {
      console.error(error);
      showMessage(error.message, "error");
    })
    .finally(() => {
      event.target.value = "";
    });
});

document
  .querySelector("#save-library-button")
  .addEventListener("click", () => {
    saveToPlayerLibrary().catch((error) => {
      console.error(error);
      showMessage(error.message, "error");
    });
  });

document.querySelector("#download-button").addEventListener("click", () => {
  runSafely(downloadCurrentScene);
});

renderer.domElement.addEventListener("click", (event) => {
  const bounds = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
  pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const [hit] = raycaster.intersectObjects(assetRoot.children, true);
  const pickRoot = hit?.object?.userData?.pickRoot;
  const equipmentId = pickRoot?.userData?.equipmentId ?? null;
  model = reduceEditorModel(model, {
    type: "select",
    equipmentId,
  });
  renderEditor();
});

document.addEventListener("keydown", (event) => {
  if (event.ctrlKey && event.key.toLowerCase() === "z") {
    event.preventDefault();
    undo();
    return;
  }
  if (event.ctrlKey && event.key.toLowerCase() === "y") {
    event.preventDefault();
    redo();
    return;
  }
  if (event.ctrlKey && event.key.toLowerCase() === "s") {
    event.preventDefault();
    saveToPlayerLibrary().catch((error) => showMessage(error.message, "error"));
    return;
  }
  if (event.ctrlKey && event.key.toLowerCase() === "o") {
    event.preventDefault();
    document.querySelector("#scene-file-input").click();
    return;
  }
  if (
    event.key === "Delete" &&
    !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)
  ) {
    document.querySelector("#delete-button").click();
  }
});

const resizeObserver = new ResizeObserver(() => {
  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  if (width <= 0 || height <= 0) {
    return;
  }
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
});
resizeObserver.observe(viewport);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  selectionBox?.update();
  renderer.render(threeScene, camera);
}

renderLibrary();
renderEditor();
animate();
showMessage(
  "Working conveyor-pusher starter loaded. Add parts or change typed behavior roles.",
);

if (APP_WINDOW_MODE) {
  const sendHeartbeat = () => {
    void postLocal("/api/app/heartbeat").catch(() => {});
  };
  sendHeartbeat();
  window.setInterval(sendHeartbeat, 3000);
}

window.__PLC_SCENE_EDITOR__ = {
  getModel: () => clone(model),
  compile: () => compileCurrentScene(),
  loadStarter: () =>
    installModel(
      createConveyorPusherStarter(),
      "Loaded the conveyor-pusher starter through the test API.",
    ),
};
