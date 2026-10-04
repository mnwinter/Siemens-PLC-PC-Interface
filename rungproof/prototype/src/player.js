import * as THREE from "../../vendor/three/three.module.min.js";
import { OrbitControls } from "../../vendor/three/addons/controls/OrbitControls.js";
import { AssetFactory } from "./assetFactory.js";
import {
  BUILTIN_SCENES,
  SCENE_FILE_EXTENSION,
  SCENE_FILE_MIME,
  loadSceneFromFile,
  loadSceneFromUrl,
  serializeSceneDocument,
} from "./sceneLoader.js";
import {
  CONTROL_SOURCES,
  STOP_REASONS,
  createSimulation,
} from "./simulations.js";
import { SceneAlarmManager } from "./alarmManager.js";
import {
  formatGuideValue,
  getSceneConfiguration,
  getSceneHints,
  getSceneMachineGuide,
  getSceneProgression,
  getSceneSolution,
} from "./sceneGuides.js";
import { resolveScenePlcProfile } from "./plcProfiles.js";
import { escapeHtml } from "./safeMarkup.js";
import { SceneLoadCoordinator } from "./sceneLoadCoordinator.js";
import { stageSceneSession } from "./sceneSession.js";
import { postLocal, postLocalJson } from "./localApi.js";
import {
  LivePlcBinding,
  getLivePlcReadiness,
} from "./livePlcBinding.js";

const VARIANTS = Object.freeze([
  { id: "A", name: "Operator console" },
  { id: "B", name: "Immersive floor" },
  { id: "C", name: "Engineering split" },
]);

const APP_WINDOW_MODE =
  new URLSearchParams(window.location.search).get("appWindow") === "1";

async function postLocalPayload(path, payload, options = {}) {
  const response = await postLocalJson(path, payload, options);
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error ?? `Request failed: HTTP ${response.status}.`);
  }
  return result;
}

function currentVariant() {
  const requested = new URLSearchParams(window.location.search)
    .get("variant")
    ?.toUpperCase();
  return VARIANTS.some((variant) => variant.id === requested) ? requested : "A";
}

function requestedSceneId() {
  return new URLSearchParams(window.location.search).get("scene");
}

function brandMarkup(variantId) {
  return `
    <div class="brand-lockup">
      <img class="brand-logo" src="./assets/brand/rungproof-mark.svg" alt="" />
      <span>
        <strong>RungProof</strong>
        <small>PLC Visual Simulator</small>
      </span>
    </div>
    ${applicationMenuMarkup(variantId)}
    <span id="control-source-badge" class="safety-badge">
      <i></i><span>CONTROLLER DISCONNECTED — SCENE OUTPUTS SAFE</span>
    </span>
  `;
}

function applicationMenuMarkup(variantId) {
  const viewItems = VARIANTS.map(
    (variant) => `
      <button
        type="button"
        class="menu-item ${variant.id === variantId ? "is-selected" : ""}"
        data-view-variant="${variant.id}"
      >
        <span class="menu-check">${variant.id === variantId ? "&#10003;" : ""}</span>
        <span>${variant.id} — ${variant.name}</span>
        <kbd>Alt+${VARIANTS.indexOf(variant) + 1}</kbd>
      </button>
    `,
  ).join("");

  return `
    <nav class="application-menu" aria-label="Application menu">
      <div class="menu-cluster">
        <details class="app-menu">
          <summary>File</summary>
          <div class="menu-popover">
            <button type="button" class="menu-item" data-player-command="open-scene">
              <span class="menu-check"></span><span>Open scene…</span><kbd>Ctrl+O</kbd>
            </button>
            <button type="button" class="menu-item" data-player-command="save-scene">
              <span class="menu-check"></span><span>Save scene</span><kbd>Ctrl+S</kbd>
            </button>
            <div class="menu-divider"></div>
            <button type="button" class="menu-item" data-player-command="exit-player">
              <span class="menu-check"></span><span>Exit player</span><kbd>Alt+F4</kbd>
            </button>
          </div>
        </details>
        <details class="app-menu">
          <summary>View</summary>
          <div class="menu-popover">
            <div class="menu-label">Workspace layout</div>
            ${viewItems}
            <div class="menu-divider"></div>
            <button id="menu-alarms" type="button" class="menu-item" data-player-command="show-alarms">
              <span class="menu-check alarm-menu-count">0</span><span>Faults &amp; alarms&hellip;</span><kbd>F8</kbd>
            </button>
            <button type="button" class="menu-item" data-player-command="fullscreen">
              <span class="menu-check"></span><span>Toggle fullscreen</span><kbd>F11</kbd>
            </button>
          </div>
        </details>
        <details class="app-menu">
          <summary>Playback</summary>
          <div class="menu-popover">
            <button type="button" class="menu-item" data-player-command="run">
              <span class="menu-check"></span><span>Run</span><kbd>Space</kbd>
            </button>
            <button type="button" class="menu-item" data-player-command="stop">
              <span class="menu-check"></span><span>Stop</span>
            </button>
            <button type="button" class="menu-item" data-player-command="reset">
              <span class="menu-check"></span><span>Reset</span>
            </button>
            <div class="menu-divider"></div>
            <button id="menu-loop-scene" type="button" class="menu-item" data-player-command="toggle-loop">
              <span class="menu-check"></span><span>Loop scene</span>
            </button>
          </div>
        </details>
        <details class="app-menu">
          <summary>PLC</summary>
          <div class="menu-popover">
            <div class="menu-label">Real controller</div>
            <button id="menu-live-plc" type="button" class="menu-item" data-player-command="toggle-live-plc">
              <span class="menu-check"></span><span>Connect Real PLC&hellip;</span>
            </button>
            <div class="menu-divider"></div>
            <div class="menu-label">Offline simulation</div>
            <button id="menu-fake-plc" type="button" class="menu-item" data-player-command="toggle-fake-plc">
              <span class="menu-check"></span><span>Enable Fake PLC</span>
            </button>
            <button type="button" class="menu-item" data-player-command="clear-fake-forces">
              <span class="menu-check"></span><span>Clear Fake PLC forces</span>
            </button>
            <div class="menu-divider"></div>
            <div class="menu-label">Read-only diagnostics</div>
            <button type="button" class="menu-item" data-player-command="test-plc">
              <span class="menu-check"></span><span>Read-only PLC check…</span>
            </button>
          </div>
        </details>
        <details class="app-menu">
          <summary>Help</summary>
          <div class="menu-popover menu-popover-right">
            <div class="menu-label">Current scene</div>
            <button type="button" class="menu-item" data-player-command="show-configuration">
              <span class="menu-check"></span><span>Configuration</span>
            </button>
            <button type="button" class="menu-item" data-player-command="show-hint">
              <span class="menu-check"></span><span>Hint</span>
            </button>
            <button type="button" class="menu-item" data-player-command="show-solution">
              <span class="menu-check"></span><span>Solution</span>
            </button>
            <div class="menu-divider"></div>
            <button type="button" class="menu-item" data-player-command="show-controls">
              <span class="menu-check"></span><span>Player controls</span>
            </button>
            <button type="button" class="menu-item" data-player-command="show-about">
              <span class="menu-check"></span><span>About RungProof</span>
            </button>
          </div>
        </details>
      </div>
    </nav>
  `;
}

function mediaHudMarkup() {
  return `
    <footer class="media-hud" aria-label="Scene playback HUD">
      <div class="hud-controls" role="group" aria-label="Scene transport">
        <button id="hud-run-button" class="hud-primary" type="button" data-player-command="run" aria-label="Run scene" title="Run scene">&#9654;</button>
        <button id="hud-stop-button" type="button" data-player-command="stop" aria-label="Stop scene" title="Stop scene">&#9632;</button>
        <button type="button" data-player-command="reset" aria-label="Reset scene" title="Reset scene">&#8634;</button>
      </div>
      <div class="hud-now-playing">
        <div class="hud-scene-line">
          <span><small>NOW PLAYING</small><strong id="hud-scene">Loading scene…</strong></span>
          <span id="hud-state" class="hud-state">READY</span>
        </div>
        <div id="hud-live-track" class="hud-live-track">
          <i></i>
          <span>LIVE SIMULATION — NO FIXED DURATION OR SEEK</span>
        </div>
      </div>
      <div class="hud-meters">
        <span><small>TIME</small><strong id="hud-time">0.0 s</strong></span>
        <span><small>RENDER</small><strong id="hud-fps">— fps</strong></span>
        <span id="hud-controller-source" class="hud-offline"><i></i><strong>DISCONNECTED</strong><small>SCENE OUTPUTS SAFE</small></span>
      </div>
    </footer>
  `;
}

function appDialogMarkup() {
  return `
    <dialog id="app-dialog" class="app-dialog">
      <div class="app-dialog-header">
        <strong id="app-dialog-title">RungProof</strong>
        <button type="button" data-dialog-close aria-label="Close dialog">&times;</button>
      </div>
      <div id="app-dialog-content" class="app-dialog-content"></div>
      <div class="app-dialog-actions">
        <button class="button" type="button" data-dialog-close>Close</button>
      </div>
    </dialog>
  `;
}

function sceneMarkup() {
  return `
    <section class="panel-block scene-block">
      <div class="section-heading">
        <span>Scene</span>
        <span id="load-count" class="micro-badge">0 loads</span>
      </div>
      <label class="field-label" for="scene-select">Scene library</label>
      <div class="scene-picker-row">
        <select id="scene-select" aria-label="Scene library"></select>
        <button id="load-scene-button" class="button button-secondary" type="button">
          Load
        </button>
        <button id="save-scene-button" class="button button-secondary" type="button">
          Save
        </button>
        <input
          id="scene-file"
          type="file"
          accept="${SCENE_FILE_EXTENSION},${SCENE_FILE_MIME},.json,application/json"
          hidden
        />
      </div>
      <small class="scene-file-note">PLC Scene file: *${SCENE_FILE_EXTENSION}</small>
      <h1 id="scene-title">Loading player…</h1>
      <p id="scene-description" class="scene-description"></p>
      <div id="scene-guide-actions" class="scene-guide-actions" role="group" aria-label="Scene learning guides">
        <button class="button button-secondary" type="button" data-player-command="show-configuration">Configuration</button>
        <button class="button button-secondary" type="button" data-player-command="show-hint">Hint</button>
        <button class="button button-secondary" type="button" data-player-command="show-solution">Solution</button>
      </div>
    </section>
  `;
}

function transportMarkup() {
  return `
    <section class="panel-block transport-block">
      <div class="section-heading"><span>Player controls</span></div>
      <div class="transport-controls" role="group" aria-label="Player controls">
        <button id="run-button" class="button button-run" type="button">
          <span class="play-icon">▶</span> Run
        </button>
        <button id="stop-button" class="button" type="button">
          <span>■</span> Stop
        </button>
        <button id="reset-button" class="button" type="button">
          <span>↺</span> Reset
        </button>
        <button id="plc-live-button" class="button button-plc-live" type="button">
          Connect Real PLC
        </button>
        <button id="fake-plc-button" class="button button-fake-plc" type="button">
          Offline Fake PLC: OFF
        </button>
        <button id="plc-test-button" class="button button-plc-test" type="button">
          <span>✓</span> Read-only PLC Check
        </button>
        <button id="alarm-button" class="button button-alarms" type="button">
          <span>⚠</span> Faults &amp; alarms
          <strong id="alarm-button-count" class="alarm-count">0</strong>
        </button>
        <label class="loop-scene-control" for="loop-scene-checkbox">
          <input id="loop-scene-checkbox" type="checkbox" />
          <span>
            <strong>Loop scene</strong>
            <small>Auto-reset after a normal system stop</small>
          </span>
        </label>
      </div>
      <div id="action-controls" class="action-controls"></div>
    </section>
  `;
}

function statusMarkup() {
  return `
    <section class="panel-block status-block">
      <div class="section-heading"><span>Runtime</span></div>
      <div id="status-chips" class="status-grid">
        <div><small>PLAYER</small><strong id="status-player">READY</strong></div>
        <div><small>SCENE</small><strong id="status-scene">—</strong></div>
        <div><small>TIME</small><strong id="status-time">0.0 s</strong></div>
        <div><small>RENDER</small><strong id="status-fps">— fps</strong></div>
      </div>
    </section>
  `;
}

function tagsMarkup() {
  return `
    <section class="panel-block tags-block">
      <div class="section-heading">
        <span>Live simulation points</span>
        <div class="tag-view-controls">
          <label for="tag-order-select">Order</label>
          <select id="tag-order-select" aria-label="Live point ordering">
            <option value="plc-io">PLC inputs / PLC outputs</option>
            <option value="sim-io">Simulation inputs / outputs</option>
            <option value="owner">Owner: PLC / PC + SIM</option>
            <option value="type">Type: BOOL / numeric + diagnostics</option>
            <option value="name">Name: A–Z</option>
          </select>
          <span id="io-source-badge" class="micro-badge">PLC DISCONNECTED</span>
        </div>
      </div>
      <div class="tag-table-grid">
        <div class="table-scroll">
          <div id="tag-column-left" class="tag-column-heading">PLC inputs</div>
          <table class="tag-table">
            <thead><tr><th>Point</th><th>Type</th><th>Value</th><th>Owner</th></tr></thead>
            <tbody id="tag-table-body-left"></tbody>
          </table>
        </div>
        <div class="table-scroll">
          <div id="tag-column-right" class="tag-column-heading">PLC outputs</div>
          <table class="tag-table">
            <thead><tr><th>Point</th><th>Type</th><th>Value</th><th>Owner</th></tr></thead>
            <tbody id="tag-table-body-right"></tbody>
          </table>
      </div>
    </section>
  `;
}

function inspectorMarkup() {
  return `
    <section class="panel-block inspector-block">
      <div class="section-heading"><span>Equipment inspector</span></div>
      <div id="inspector-content" class="inspector-content">
        <div class="empty-state">
          <span class="selection-cube">◇</span>
          <p>Click equipment in the 3D scene to inspect it.</p>
        </div>
      </div>
    </section>
  `;
}

function viewportMarkup() {
  return `
    <section class="viewport-panel" aria-label="3D scene viewport">
      <div id="scene-mount" class="scene-mount"></div>
      <div class="viewport-overlay viewport-top-left">
        <span id="scene-kind">SCENE PLAYER</span>
      </div>
      <div class="viewport-overlay viewport-help">
        Drag to orbit · Wheel to zoom · Click equipment to inspect · Click 3D controls to operate
      </div>
      <div id="interaction-feedback" class="interaction-feedback" role="status"></div>
      <div id="loading-overlay" class="loading-overlay">
        <span class="spinner"></span>
        <strong>Loading scene…</strong>
      </div>
      <div id="error-overlay" class="error-overlay" hidden></div>
    </section>
  `;
}

function renderVariantA(variantId) {
  return `
    <header class="app-header">${brandMarkup(variantId)}</header>
    <main class="operator-console">
      <aside class="control-rail">
        ${sceneMarkup()}
        ${transportMarkup()}
        ${statusMarkup()}
      </aside>
      ${viewportMarkup()}
      <aside class="inspection-rail">${inspectorMarkup()}</aside>
      <div class="tag-strip">${tagsMarkup()}</div>
    </main>
  `;
}

function renderVariantB(variantId) {
  return `
    <main class="immersive-floor">
      ${viewportMarkup()}
      <header class="immersive-header">${brandMarkup(variantId)}</header>
      <div class="immersive-scene-card">${sceneMarkup()}</div>
      <div class="immersive-status-card">${statusMarkup()}</div>
      <div class="immersive-inspector">${inspectorMarkup()}</div>
      <div class="immersive-tag-drawer">${tagsMarkup()}</div>
      <div class="immersive-transport">${transportMarkup()}</div>
    </main>
  `;
}

function renderVariantC(variantId) {
  return `
    <header class="engineering-header">${brandMarkup(variantId)}</header>
    <main class="engineering-split">
      <aside class="engineering-sidebar">
        ${sceneMarkup()}
        ${transportMarkup()}
        ${tagsMarkup()}
      </aside>
      ${viewportMarkup()}
      <aside class="engineering-inspector">
        ${statusMarkup()}
        ${inspectorMarkup()}
      </aside>
    </main>
  `;
}

function renderShell(variantId) {
  const app = document.querySelector("#app");
  document.body.dataset.variant = variantId;
  const workspace =
    variantId === "B"
      ? renderVariantB(variantId)
      : variantId === "C"
        ? renderVariantC(variantId)
        : renderVariantA(variantId);
  app.innerHTML = `
    <div class="application-workspace">${workspace}</div>
    ${mediaHudMarkup()}
    ${appDialogMarkup()}
  `;
}

function formatTagValue(tag) {
  if (tag.type === "BOOL") {
    return tag.value ? "TRUE" : "FALSE";
  }
  if (typeof tag.value === "number") {
    const decimals = tag.type === "DINT" ? 0 : 2;
    return `${tag.value.toFixed(decimals)}${tag.unit ? ` ${tag.unit}` : ""}`;
  }
  return String(tag.value);
}

function disposeObject(root) {
  root.traverse((child) => {
    if (!child.isMesh) {
      return;
    }
    child.geometry?.dispose();
    const materials = Array.isArray(child.material)
      ? child.material
      : [child.material];
    for (const item of materials) {
      item?.dispose();
    }
  });
}

class Player {
  constructor() {
    this.mount = document.querySelector("#scene-mount");
    this.factory = new AssetFactory();
    this.sceneLoads = new SceneLoadCoordinator();
    this.registry = new Map();
    this.sceneDocument = null;
    this.simulation = null;
    this.controlSource = CONTROL_SOURCES.DISCONNECTED;
    this.loopEnabled = false;
    this.tagOrder = "plc-io";
    this.availableBuiltinScenes = [...BUILTIN_SCENES];
    this.sceneDescriptors = [...this.availableBuiltinScenes];
    this.assetRoot = new THREE.Group();
    this.assetRoot.name = "Loaded scene assets";
    this.loadCount = 0;
    this.selected = null;
    this.selectionBox = null;
    this.frameCount = 0;
    this.fps = 0;
    this.fpsAccumulator = 0;
    this.uiAccumulator = 0;
    this.lastTimestamp = performance.now();
    this.pointerStart = null;
    this.initialSceneId = requestedSceneId();
    this.plcProfiles = [];
    this.livePlcStatus = null;
    this.liveCycleAccumulatorMs = 0;
    this.livePlc = new LivePlcBinding({
      postJson: postLocalPayload,
      applyPlcPoint: (name, value) =>
        this.controlSource === CONTROL_SOURCES.LIVE_PLC &&
        (this.simulation?.setControllerPoint(name, value) ?? false),
      holdControllerSafe: () => {
        if (this.controlSource === CONTROL_SOURCES.LIVE_PLC) {
          this.simulation?.holdControllerSafe();
        }
      },
      onStatus: (status) => {
        this.livePlcStatus = status;
        this._refreshUi();
      },
    });
    this.hintLevels = new Map();
    this.alarmManager = null;
    this.renderedAlarmRevision = -1;

    this._createRenderer();
    this._wireUi();
    this._populateScenes();
    void this._refreshAvailableBuiltins()
      .then(() => this._refreshSavedScenes())
      .then(() => {
        if (
          this.initialSceneId &&
          !this.availableBuiltinScenes.some(
            (scene) => scene.id === this.initialSceneId,
          )
        ) {
          const requested = this.sceneDescriptors.find(
            (scene) => scene.id === this.initialSceneId,
          );
          if (requested) {
            void this.loadBuiltIn(requested);
          }
        }
      });
    this._animate = this._animate.bind(this);
    requestAnimationFrame(this._animate);
    const initialScene =
      BUILTIN_SCENES.find((scene) => scene.id === this.initialSceneId) ??
      BUILTIN_SCENES.find((scene) => scene.id === "scene-1-conveyor-stop") ??
      BUILTIN_SCENES[0];
    void this.loadBuiltIn(initialScene);
  }

  _createRenderer() {
    this.threeScene = new THREE.Scene();
    this.threeScene.background = new THREE.Color(0x081116);
    this.threeScene.fog = new THREE.Fog(0x081116, 22, 58);
    this.threeScene.add(this.assetRoot);

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.05, 200);
    this.camera.position.set(9, 7, 9);

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.04;
    this.mount.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.07;
    // Match physical CAD navigation: dragging right/up rotates the view
    // right/up instead of producing the reversed trackball response.
    this.controls.rotateSpeed = -1;
    this.controls.minDistance = 2.5;
    this.controls.maxDistance = 45;
    this.controls.maxPolarAngle = Math.PI * 0.49;
    this.controls.target.set(0, 1, 0);

    const hemisphere = new THREE.HemisphereLight(0xb8d8e8, 0x1b2528, 1.7);
    this.threeScene.add(hemisphere);

    const keyLight = new THREE.DirectionalLight(0xffffff, 3.2);
    keyLight.position.set(8, 14, 7);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.set(2048, 2048);
    keyLight.shadow.camera.near = 1;
    keyLight.shadow.camera.far = 45;
    keyLight.shadow.camera.left = -14;
    keyLight.shadow.camera.right = 14;
    keyLight.shadow.camera.top = 14;
    keyLight.shadow.camera.bottom = -14;
    this.threeScene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x5bb8e8, 1.15);
    fillLight.position.set(-9, 7, -8);
    this.threeScene.add(fillLight);

    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(80, 80),
      new THREE.MeshStandardMaterial({
        color: 0x111d22,
        roughness: 0.95,
        metalness: 0.05,
      }),
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    this.threeScene.add(floor);

    const grid = new THREE.GridHelper(80, 80, 0x34505b, 0x1b3038);
    grid.position.y = 0.004;
    grid.material.transparent = true;
    grid.material.opacity = 0.48;
    this.threeScene.add(grid);

    this.resizeObserver = new ResizeObserver(() => this._resize());
    this.resizeObserver.observe(this.mount);
    this._resize();

    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.interactionFeedbackTimer = null;
    this.renderer.domElement.addEventListener("pointerdown", (event) => {
      this.pointerStart = { x: event.clientX, y: event.clientY };
    });
    this.renderer.domElement.addEventListener("pointerup", (event) => {
      if (!this.pointerStart) {
        return;
      }
      const movement = Math.hypot(
        event.clientX - this.pointerStart.x,
        event.clientY - this.pointerStart.y,
      );
      this.pointerStart = null;
      if (movement < 5) {
        this._selectAt(event);
      }
    });
    this.renderer.domElement.addEventListener("pointermove", (event) => {
      if (event.buttons !== 0) {
        this.renderer.domElement.style.cursor = "grabbing";
        return;
      }
      const hit = this._raycastAt(event.clientX, event.clientY);
      this.renderer.domElement.style.cursor = hit?.object?.userData
        ?.interactiveAction
        ? "pointer"
        : "grab";
    });
    this.renderer.domElement.addEventListener("pointerleave", () => {
      this.renderer.domElement.style.cursor = "grab";
    });
  }

  _wireUi() {
    document.querySelector("#run-button").addEventListener("click", () => {
      this._executeCommand("run");
    });
    document.querySelector("#stop-button").addEventListener("click", () => {
      this._executeCommand("stop");
    });
    document.querySelector("#reset-button").addEventListener("click", () => {
      this._executeCommand("reset");
    });
    document
      .querySelector("#loop-scene-checkbox")
      .addEventListener("change", (event) => {
        this._setLoopEnabled(event.target.checked);
      });
    document.querySelector("#fake-plc-button").addEventListener("click", () => {
      this._executeCommand("toggle-fake-plc");
    });
    document.querySelector("#plc-live-button").addEventListener("click", () => {
      this._executeCommand("toggle-live-plc");
    });
    document.querySelector("#plc-test-button").addEventListener("click", () => {
      this._executeCommand("test-plc");
    });
    document.querySelector("#alarm-button").addEventListener("click", () => {
      this._executeCommand("show-alarms");
    });
    document.querySelector("#scene-select").addEventListener("change", (event) => {
      const selected = this.sceneDescriptors.find(
        (scene) => scene.id === event.target.value,
      );
      if (selected) {
        this.loadBuiltIn(selected);
      }
    });
    document
      .querySelector("#load-scene-button")
      .addEventListener("click", () =>
        document.querySelector("#scene-file").click(),
      );
    document
      .querySelector("#save-scene-button")
      .addEventListener("click", () => void this._saveScene());
    document
      .querySelector("#scene-guide-actions")
      .addEventListener("click", (event) => {
        const commandButton = event.target.closest("[data-player-command]");
        if (commandButton) {
          this._executeCommand(commandButton.dataset.playerCommand);
        }
      });
    document.querySelector("#scene-file").addEventListener("change", async (event) => {
      const [file] = event.target.files;
      if (!file) {
        return;
      }
      if (
        this.livePlc.connected ||
        this.controlSource === CONTROL_SOURCES.LIVE_PLC
      ) {
        await this._disconnectLivePlc(
          "Scene changed — real PLC session disconnected",
        );
      }
      const request = this.sceneLoads.begin();
      await this._withLoading(async () => {
        const scene = await loadSceneFromFile(file);
        if (request.isCurrent()) {
          this._installScene(scene, `File: ${file.name}`);
          this._selectCustomScene(file.name);
        }
      }, request);
      event.target.value = "";
    });
    document
      .querySelector("#action-controls")
      .addEventListener("click", (event) => {
        const button = event.target.closest("[data-simulation-action]");
        if (!button) {
          return;
        }
        if (!this.simulation?.canHandleAction(button.dataset.simulationAction)) {
          this._showInteractionFeedback(
            "Controller disconnected — enable Fake PLC or connect the live runtime",
          );
          return;
        }
        const message = this.simulation?.handleAction(
          button.dataset.simulationAction,
        );
        if (message) {
          this._showInteractionFeedback(message);
        }
        this._refreshUi();
      });
    document
      .querySelector(".tags-block")
      .addEventListener("click", (event) => {
        const button = event.target.closest("[data-fake-plc-point]");
        if (button) {
          this._forceFakePlcPoint(button.dataset.fakePlcPoint);
        }
      });
    document
      .querySelector("#tag-order-select")
      .addEventListener("change", (event) => {
        this.tagOrder = event.target.value;
        this._refreshUi();
      });

    document.querySelector(".application-menu").addEventListener("click", (event) => {
      const variantButton = event.target.closest("[data-view-variant]");
      const commandButton = event.target.closest("[data-player-command]");
      if (variantButton) {
        this._selectVariant(variantButton.dataset.viewVariant);
      } else if (commandButton) {
        this._executeCommand(commandButton.dataset.playerCommand);
      }
      if (variantButton || commandButton) {
        this._closeMenus();
      }
    });
    document.querySelector(".media-hud").addEventListener("click", (event) => {
      const commandButton = event.target.closest("[data-player-command]");
      if (commandButton) {
        this._executeCommand(commandButton.dataset.playerCommand);
      }
    });
    document.querySelector("#app-dialog").addEventListener("click", (event) => {
      if (event.target.closest("[data-dialog-close]")) {
        document.querySelector("#app-dialog").close();
        return;
      }
      if (event.target.closest("[data-plc-test-run]")) {
        void this._runPlcTest();
        return;
      }
      if (event.target.closest("[data-live-plc-connect]")) {
        void this._connectLivePlc();
        return;
      }
      if (event.target.closest("[data-reveal-next-hint]")) {
        this._revealNextHint();
        return;
      }
      if (event.target.closest("[data-reveal-solution]")) {
        this._openSolutionGuide(true);
        return;
      }
      if (event.target.closest("[data-alarm-acknowledge]")) {
        this.alarmManager?.acknowledgeActive();
        this._renderOpenAlarmDialog();
        this._refreshUi();
        return;
      }
      if (event.target.closest("[data-alarm-clear-history]")) {
        this.alarmManager?.clearHistory();
        this._renderOpenAlarmDialog();
        this._refreshUi();
      }
    });
    document.querySelector("#app-dialog").addEventListener("change", (event) => {
      if (event.target.id !== "live-plc-confirm") {
        return;
      }
      const connectButton = document.querySelector("[data-live-plc-connect]");
      if (connectButton) {
        connectButton.disabled = !event.target.checked;
      }
    });
    document.querySelectorAll(".app-menu").forEach((menu) => {
      menu.addEventListener("toggle", () => {
        if (menu.open) {
          document.querySelectorAll(".app-menu").forEach((other) => {
            if (other !== menu) {
              other.open = false;
            }
          });
        }
      });
    });
    document.addEventListener("pointerdown", (event) => {
      if (!event.target.closest(".app-menu")) {
        this._closeMenus();
      }
    });
    window.addEventListener("keydown", (event) => {
      const target = event.target;
      if (
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLSelectElement ||
        target?.isContentEditable
      ) {
        return;
      }
      if (event.ctrlKey && event.key.toLowerCase() === "o") {
        event.preventDefault();
        this._executeCommand("open-scene");
        return;
      }
      if (event.ctrlKey && event.key.toLowerCase() === "s") {
        event.preventDefault();
        this._executeCommand("save-scene");
        return;
      }
      if (event.altKey && ["1", "2", "3"].includes(event.key)) {
        event.preventDefault();
        this._selectVariant(VARIANTS[Number(event.key) - 1].id);
        return;
      }
      if (event.key === "F11") {
        event.preventDefault();
        this._executeCommand("fullscreen");
        return;
      }
      if (event.key === "F8") {
        event.preventDefault();
        this._executeCommand("show-alarms");
        return;
      }
      if (event.code === "Space") {
        event.preventDefault();
        this._executeCommand(this.simulation?.running ? "stop" : "run");
      }
    });
    window.addEventListener("pagehide", () => {
      void this.livePlc.disconnect({ keepalive: true }).catch(() => {});
    });
  }

  _executeCommand(command) {
    if (command === "open-scene") {
      document.querySelector("#scene-file").click();
      return;
    }
    if (command === "save-scene") {
      void this._saveScene();
      return;
    }
    if (command === "run") {
      if (this.controlSource === CONTROL_SOURCES.DISCONNECTED) {
        this._showInteractionFeedback(
          "Controller disconnected — Run cannot create PLC outputs",
        );
        return;
      }
      if (
        this.controlSource === CONTROL_SOURCES.LIVE_PLC &&
        !getLivePlcReadiness(this.livePlc.snapshot).ready
      ) {
        const readiness = getLivePlcReadiness(this.livePlc.snapshot);
        this._showInteractionFeedback(
          `Real PLC is not ready — ${readiness.label}`,
        );
        return;
      }
      const started = this.simulation?.setRunning(true);
      const status = this.simulation?.getStatus();
      this._showInteractionFeedback(
        started
          ? "Start accepted"
          : status?.message ?? "Start blocked by the active machine condition",
      );
      this._refreshUi();
      return;
    }
    if (command === "stop") {
      const stopMessage =
        this.controlSource === CONTROL_SOURCES.LIVE_PLC
          ? "Operator stop — visual scene held; real PLC remains connected and heartbeat stays active"
          : "Operator stop — scene held; Loop will not restart it";
      this.simulation?.setRunning(
        false,
        STOP_REASONS.OPERATOR,
        stopMessage,
      );
      this._showInteractionFeedback(stopMessage);
      this._refreshUi();
      return;
    }
    if (command === "reset") {
      this.simulation?.reset();
      this._showInteractionFeedback(
        this.controlSource === CONTROL_SOURCES.LIVE_PLC
          ? "Scene reset — visual model stopped; real PLC remains connected and heartbeat stays active"
          : "Scene reset — stopped and ready",
      );
      this._refreshUi();
      return;
    }
    if (command === "toggle-loop") {
      this._setLoopEnabled(!this.loopEnabled);
      this._refreshUi();
      return;
    }
    if (command === "toggle-fake-plc") {
      if (this.controlSource === CONTROL_SOURCES.LIVE_PLC) {
        this._showInteractionFeedback(
          "Disconnect the Real PLC before enabling the simulated controller",
        );
        return;
      }
      this._setControlSource(
        this.controlSource === CONTROL_SOURCES.FAKE_PLC
          ? CONTROL_SOURCES.DISCONNECTED
          : CONTROL_SOURCES.FAKE_PLC,
      );
      return;
    }
    if (command === "toggle-live-plc") {
      if (this.livePlc.connected) {
        void this._disconnectLivePlc("Real PLC disconnected by operator");
      } else {
        void this._openLivePlc();
      }
      return;
    }
    if (command === "clear-fake-forces") {
      if (this.simulation?.clearControllerForces()) {
        this._showInteractionFeedback("Fake PLC output forces cleared");
      } else {
        this._showInteractionFeedback("No Fake PLC output forces are active");
      }
      this._refreshUi();
      return;
    }
    if (command === "test-plc") {
      if (this.livePlc.connected) {
        this._showInteractionFeedback(
          "Disconnect the Real PLC before running the separate diagnostic",
        );
        return;
      }
      void this._openPlcTest();
      return;
    }
    if (command === "show-alarms") {
      this._openAlarmDialog();
      return;
    }
    if (command === "show-configuration") {
      this._openConfigurationGuide();
      return;
    }
    if (command === "show-hint") {
      this._openHintGuide();
      return;
    }
    if (command === "show-solution") {
      this._openSolutionGuide();
      return;
    }
    if (command === "fullscreen") {
      if (document.fullscreenElement) {
        void document.exitFullscreen();
      } else {
        void document.documentElement.requestFullscreen();
      }
      return;
    }
    if (command === "show-controls") {
      this._showDialog(
        "Player controls",
        `
          <dl class="shortcut-list">
            <dt>Space</dt><dd>Run or stop only when Fake PLC is enabled or a live controller is bound</dd>
            <dt>Alt+1 / 2 / 3</dt><dd>Switch View layouts A, B, and C</dd>
            <dt>Ctrl+O</dt><dd>Open a portable .plcscene file</dd>
            <dt>Ctrl+S</dt><dd>Save the active scene to the local library</dd>
            <dt>Fake PLC</dt><dd>Enable the reference controller and optional output forcing for offline tests</dd>
            <dt>Real PLC</dt><dd>Review and confirm the exact scene profile, then start a guarded DB exchange with the configured Siemens CPU</dd>
            <dt>Loop scene</dt><dd>After a normal system stop, reset the scene and request another start; operator and interlock stops remain latched</dd>
            <dt>F8</dt><dd>Open the current scene's local Faults &amp; Alarms window</dd>
            <dt>Test PLC</dt><dd>Run the separate read-only PLC setup diagnostic; it does not bind scene I/O</dd>
            <dt>Mouse</dt><dd>Orbit, pan, zoom, inspect, and operate 3D controls</dd>
          </dl>
        `,
      );
      return;
    }
    if (command === "show-about") {
      this._showDialog(
        "About RungProof",
        `
          <p>RungProof is a PLC visual simulator for proving ladder logic against versioned <code>.plcscene</code> industrial simulations.</p>
          <p>Scenes start with the controller disconnected. PC-owned inputs may change, but PLC-owned outputs remain at their safe values.</p>
          <p>Fake PLC is an explicit offline test controller. Its PLC-owned outputs can be forced so incorrect logic produces the corresponding incorrect plant response.</p>
          <p>A system stop holds the scene stopped and Start still obeys the active permissives. Loop scene resets and restarts only after normal program completion; it never automatically clears an operator stop or interlock stop.</p>
          <p>The Faults &amp; Alarms popup records simulated scene warnings, alarms, and interlocks. Acknowledgement is local to this player and never acknowledges a real PLC alarm.</p>
          <p>The Test PLC command may open a separate read-only S7 session to validate an interface profile; it does not bind live scene I/O.</p>
          <p>The PLC test cannot write PLC memory, toggle commands, change CPU state, or prove TIA symbolic-name and ladder-logic semantics.</p>
          <p>Connect Real PLC is a separate guarded runtime. It writes only the exact PC-owned DB scope confirmed in the dialog, reads only configured PLC-owned values, and stops its PC heartbeat if the browser cycle or scene session stops.</p>
          <p>Layouts A, B, and C remain available from the View menu.</p>
        `,
      );
      return;
    }
    if (command === "exit-player") {
      void this._exitPlayer();
    }
  }

  async _exitPlayer() {
    if (this.livePlc.connected) {
      await this._disconnectLivePlc(
        "Application exit — real PLC session disconnected",
        { keepalive: true },
      );
    }
    if (APP_WINDOW_MODE) {
      void postLocal("/api/app/exit", {
        keepalive: true,
      });
    } else {
      this._showInteractionFeedback(
        "Close this browser tab to exit the local player",
      );
    }
  }

  _setLoopEnabled(enabled) {
    this.loopEnabled = Boolean(enabled);
    this.simulation?.setLoopEnabled(this.loopEnabled);
    this._showInteractionFeedback(
      this.loopEnabled
        ? "Loop enabled — normal system stops will reset and restart"
        : "Loop disabled — system stops will remain stopped",
    );
    this._refreshUi();
  }

  _setControlSource(source) {
    if (!Object.values(CONTROL_SOURCES).includes(source)) {
      throw new Error(`Unsupported player control source "${source}".`);
    }
    if (
      source === CONTROL_SOURCES.LIVE_PLC &&
      !this.livePlc.connected
    ) {
      throw new Error("Live PLC control requires an active guarded session.");
    }
    this.controlSource = source;
    this.simulation?.setControlSource(source);
    const fake = source === CONTROL_SOURCES.FAKE_PLC;
    const live = source === CONTROL_SOURCES.LIVE_PLC;
    this._showInteractionFeedback(
      fake
        ? "FAKE PLC ENABLED — reference logic and output forcing are active"
        : live
          ? "REAL PLC CONNECTED — guarded DB exchange is active"
          : "CONTROLLER DISCONNECTED — scene outputs reset; verify the PLC watchdog state",
    );
    this._refreshUi();
  }

  _forceFakePlcPoint(pointName) {
    if (this.controlSource !== CONTROL_SOURCES.FAKE_PLC) {
      this._showInteractionFeedback("Enable Fake PLC before forcing outputs");
      return;
    }
    const tag = this.simulation
      ?.getTags()
      .find((candidate) => candidate.name === pointName);
    if (!tag || tag.owner !== "PLC") {
      this._showInteractionFeedback(`PLC output "${pointName}" is unavailable`);
      return;
    }

    let nextValue;
    if (tag.type === "BOOL") {
      nextValue = !Boolean(tag.value);
    } else {
      const entered = window.prompt(
        `Set Fake PLC output ${pointName} (${tag.type})`,
        String(tag.value),
      );
      if (entered === null) {
        return;
      }
      if (tag.type === "DINT") {
        nextValue = Number(entered);
        if (!Number.isInteger(nextValue)) {
          this._showInteractionFeedback("DINT output requires a whole number");
          return;
        }
      } else if (tag.type === "REAL") {
        nextValue = Number(entered);
        if (!Number.isFinite(nextValue)) {
          this._showInteractionFeedback("REAL output requires a finite number");
          return;
        }
      } else {
        nextValue = entered;
      }
    }

    if (!this.simulation?.setControllerPoint(pointName, nextValue)) {
      this._showInteractionFeedback(
        `Scene runtime cannot force output "${pointName}"`,
      );
      return;
    }
    this._showInteractionFeedback(
      `Fake PLC forced ${pointName} = ${String(nextValue).toUpperCase()}`,
    );
    this._refreshUi();
  }

  _openConfigurationGuide() {
    if (!this.sceneDocument) {
      this._showInteractionFeedback("No scene is loaded");
      return;
    }

    const { requiredTags, internalPoints } = getSceneConfiguration(
      this.sceneDocument,
    );
    const machineGuide = getSceneMachineGuide(this.sceneDocument);
    const progression = getSceneProgression(this.sceneDocument);
    const tagRows = requiredTags
      .map(
        (tag) => `
          <tr>
            <td><code>${escapeHtml(tag.name)}</code></td>
            <td>${escapeHtml(tag.type)}</td>
            <td>
              <span class="guide-direction guide-direction-${tag.owner.toLowerCase()}">
                ${escapeHtml(tag.direction)}
              </span>
            </td>
            <td><code>${escapeHtml(formatGuideValue(tag.initial))}</code></td>
            <td>${escapeHtml(tag.purpose)}</td>
          </tr>
        `,
      )
      .join("");
    const internalNote = internalPoints.length
      ? `
          <p class="scene-guide-note">
            Do not create interface tags for simulator-only or PLC memory
            points: <code>${internalPoints.map(escapeHtml).join("</code>, <code>")}</code>.
          </p>
        `
      : "";
    const guideSection = machineGuide
      ? `
          <section class="machine-guide">
            <h3>How the machine works</h3>
            <p>${escapeHtml(machineGuide.purpose ?? "")}</p>
            <h4>Starting conditions</h4>
            <ul>${(machineGuide.startConditions ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            <h4>Normal sequence</h4>
            <ol>${(machineGuide.normalSequence ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>
            <h4>Stop behavior</h4>
            <ul>${(machineGuide.stopBehavior ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            <h4>Fault behavior</h4>
            <ul>${(machineGuide.faultBehavior ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            <h4>Expected observations</h4>
            <ul>${(machineGuide.expectedObservations ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          </section>
        `
      : "";
    const progressionSection = progression?.sequenceNumber
      ? `
          <p class="scene-guide-note">
            Lab ${escapeHtml(String(progression.sequenceNumber))} inherits
            <code>${escapeHtml(progression.inheritsFrom ?? "the common foundation")}</code>.
            New tags: <code>${escapeHtml(progression.addedTags.join(", ") || "none")}</code>.
          </p>
        `
      : "";

    this._showDialog(
      "Scene configuration",
      `
        <div class="scene-guide">
          <div class="scene-guide-boundary">
            <strong>I/O CONTRACT — NOT A LADDER SOLUTION</strong>
            <span>${escapeHtml(this.sceneDocument.name)}</span>
          </div>
          ${guideSection}
          ${progressionSection}
          <p>
            Create or map the following symbols exactly. Names and data types
            are read directly from this scene, so spelling and case must match.
          </p>
          <ol class="scene-guide-setup">
            <li>Create a separate TIA project copy for this scene.</li>
            <li>Create the listed members in the scene interface DB with the shown initial values.</li>
            <li>Map each member in the external PLC interface profile using the exact simulator tag name.</li>
            <li>Confirm direction before testing: the simulator supplies inputs; the PLC supplies outputs.</li>
          </ol>
          <div class="scene-guide-table-wrap">
            <table class="scene-guide-table">
              <thead>
                <tr>
                  <th>Exact simulator tag</th>
                  <th>Type</th>
                  <th>Direction</th>
                  <th>Initial</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                ${
                  tagRows ||
                  '<tr><td colspan="5">This scene declares no external PLC tags.</td></tr>'
                }
              </tbody>
            </table>
          </div>
          ${internalNote}
          <p class="scene-guide-warning">
            <strong>Connect Real PLC</strong> binds only scenes with a matched
            external interface profile and requires confirmation of the exact
            DB write scope. <strong>Test PLC</strong> remains a separate
            read-only setup diagnostic.
          </p>
        </div>
      `,
      "guide",
    );
  }

  _openHintGuide() {
    if (!this.sceneDocument) {
      this._showInteractionFeedback("No scene is loaded");
      return;
    }

    const hints = getSceneHints(this.sceneDocument);
    if (hints.length === 0) {
      this._showDialog(
        "Scene hint",
        `
          <div class="scene-guide">
            <div class="scene-guide-boundary">
              <strong>NO HINT PROVIDED</strong>
              <span>This custom or demonstration scene has no training hints.</span>
            </div>
          </div>
        `,
        "guide",
      );
      return;
    }

    const sceneId = this.sceneDocument.id;
    const revealed = Math.min(
      hints.length,
      Math.max(1, this.hintLevels.get(sceneId) ?? 1),
    );
    this.hintLevels.set(sceneId, revealed);
    const hintMarkup = hints
      .slice(0, revealed)
      .map(
        (hint, index) => `
          <li>
            <strong>Hint ${index + 1}</strong>
            <span>${escapeHtml(hint)}</span>
          </li>
        `,
      )
      .join("");

    this._showDialog(
      "Scene hint",
      `
        <div class="scene-guide">
          <div class="scene-guide-boundary">
            <strong>PROGRESSIVE HINTS</strong>
            <span>${escapeHtml(this.sceneDocument.name)}</span>
          </div>
          <ol class="scene-hint-list">${hintMarkup}</ol>
          ${
            revealed < hints.length
              ? `
                  <button class="button scene-guide-reveal" type="button" data-reveal-next-hint>
                    Reveal hint ${revealed + 1}
                  </button>
                `
              : '<p class="scene-guide-note">All hints are shown. Open Solution only if you want the functional answer.</p>'
          }
        </div>
      `,
      "guide",
    );
  }

  _revealNextHint() {
    if (!this.sceneDocument) {
      return;
    }
    const hints = getSceneHints(this.sceneDocument);
    const current = this.hintLevels.get(this.sceneDocument.id) ?? 1;
    this.hintLevels.set(
      this.sceneDocument.id,
      Math.min(hints.length, current + 1),
    );
    this._openHintGuide();
  }

  _openSolutionGuide(reveal = false) {
    if (!this.sceneDocument) {
      this._showInteractionFeedback("No scene is loaded");
      return;
    }

    const solution = getSceneSolution(this.sceneDocument);
    if (!solution) {
      this._showDialog(
        "Scene solution",
        `
          <div class="scene-guide">
            <div class="scene-guide-boundary">
              <strong>NO SOLUTION PROVIDED</strong>
              <span>This custom or demonstration scene has no training solution.</span>
            </div>
          </div>
        `,
        "guide",
      );
      return;
    }

    if (!reveal) {
      this._showDialog(
        "Scene solution",
        `
          <div class="scene-guide">
            <div class="scene-guide-boundary scene-guide-boundary-solution">
              <strong>REFERENCE ANSWER</strong>
              <span>This reveals the functional solution for ${escapeHtml(this.sceneDocument.name)}.</span>
            </div>
            <p>
              Configuration shows only the tag contract. Continue here only
              when you intentionally want the answer.
            </p>
            <button class="button scene-guide-reveal solution-reveal" type="button" data-reveal-solution>
              Reveal reference solution
            </button>
          </div>
        `,
        "guide",
      );
      return;
    }

    const steps = solution.steps
      .map((step) => `<li>${escapeHtml(step)}</li>`)
      .join("");
    this._showDialog(
      "Scene solution",
      `
        <div class="scene-guide">
          <div class="scene-guide-boundary scene-guide-boundary-solution">
            <strong>REFERENCE SOLUTION REVEALED</strong>
            <span>${escapeHtml(this.sceneDocument.name)}</span>
          </div>
          <p>${escapeHtml(solution.summary)}</p>
          <ol class="scene-solution-steps">${steps}</ol>
          ${
            solution.acceptance
              ? `<p class="scene-guide-acceptance"><strong>Acceptance check:</strong> ${escapeHtml(solution.acceptance)}</p>`
              : ""
          }
        </div>
      `,
      "guide",
    );
  }

  async _loadPlcProfiles() {
    const response = await fetch("/api/plc/profiles", { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error ?? "PLC profiles could not be loaded.");
    }
    this.plcProfiles = Array.isArray(payload.profiles)
      ? payload.profiles
      : [];
    return payload;
  }

  _liveScopeMarkup(scope, direction) {
    if (!Array.isArray(scope) || scope.length === 0) {
      return '<li class="plc-scope-empty">No configured points</li>';
    }
    return scope
      .map(
        (item) => `
          <li>
            <span>${escapeHtml(direction)}</span>
            <code>${escapeHtml(item.address)}</code>
            <strong>${escapeHtml(item.name)}</strong>
            <small>${escapeHtml(item.dataType)} · ${escapeHtml(item.symbol)}</small>
          </li>
        `,
      )
      .join("");
  }

  _livePointMapMarkup(scope, direction) {
    if (!Array.isArray(scope) || scope.length === 0) {
      return '<li class="plc-scope-empty">No scene points mapped</li>';
    }
    return scope
      .map(
        (item) => `
          <li>
            <span>${escapeHtml(direction)}</span>
            <strong>${escapeHtml(item.name)}</strong>
            <code>${escapeHtml(item.address)}</code>
            <small>via ${escapeHtml(item.tag)} · ${escapeHtml(item.dataType)}</small>
          </li>
        `,
      )
      .join("");
  }

  async _openLivePlc() {
    if (!this.sceneDocument) {
      this._showInteractionFeedback("No scene is loaded");
      return;
    }
    if (this.livePlc.connected) {
      await this._disconnectLivePlc("Real PLC disconnected by operator");
      return;
    }

    this._showDialog(
      "Connect Real PLC",
      `
        <div class="plc-live-boundary">
          <strong>GUARDED REAL PLC CONNECTION</strong>
          <span>Loading the exact scene-to-PLC write scope…</span>
        </div>
      `,
      "plc-live",
    );

    try {
      const payload = await this._loadPlcProfiles();
      if (
        payload.writePathPresent !== true ||
        payload.liveWritePath !== "guarded"
      ) {
        throw new Error("This build does not expose the guarded live PLC path.");
      }
      const resolution = resolveScenePlcProfile(
        this.sceneDocument,
        this.plcProfiles,
      );
      if (resolution.status !== "matched") {
        throw new Error(
          resolution.status === "invalid"
            ? resolution.profile?.error ?? "The assigned PLC profile is invalid."
            : this.sceneDocument.plcTestProfile
              ? `The assigned profile ${this.sceneDocument.plcTestProfile} is unavailable.`
              : "This scene does not declare a PLC interface profile.",
        );
      }
      const profile = resolution.profile;
      if (
        !profile.live ||
        !Array.isArray(profile.live.writeScope) ||
        !Array.isArray(profile.live.readScope)
      ) {
        throw new Error(
          profile.live?.error ??
            "The assigned profile is unavailable for live PLC exchange.",
        );
      }

      this._showDialog(
        "Connect Real PLC",
        `
          <div class="plc-live-boundary">
            <strong>GUARDED REAL PLC CONNECTION</strong>
            <span>${escapeHtml(profile.label)} · ${escapeHtml(profile.live.ip)}</span>
          </div>
          <p>
            This is the real Siemens PLC path. RungProof will write only the
            configured PC-owned DB values below and will read the configured
            PLC-owned values. It does not change CPU state or force PLC tags.
          </p>
          <div class="plc-live-scope">
            <section>
              <h3>Scene feedback → PLC (${profile.live.pcPointScope?.length ?? 0})</h3>
              <ul>${this._livePointMapMarkup(profile.live.pcPointScope, "INPUT")}</ul>
            </section>
            <section>
              <h3>PLC → Scene commands (${profile.live.plcPointScope?.length ?? 0})</h3>
              <ul>${this._livePointMapMarkup(profile.live.plcPointScope, "OUTPUT")}</ul>
            </section>
            <section>
              <h3>Exact PC → PLC write scope (${profile.live.writeScope.length})</h3>
              <ul>${this._liveScopeMarkup(profile.live.writeScope, "WRITE")}</ul>
            </section>
            <section>
              <h3>Exact PLC → PC read scope (${profile.live.readScope.length})</h3>
              <ul>${this._liveScopeMarkup(profile.live.readScope, "READ")}</ul>
            </section>
          </div>
          <p class="plc-live-note">
            Rack ${escapeHtml(profile.live.rack)} / slot ${escapeHtml(profile.live.slot)}
            · ${escapeHtml(profile.live.cycleMs)} ms cycle
            · ${escapeHtml(profile.live.heartbeatTimeoutMs)} ms heartbeat timeout.
            If browser cycles stop, the PC heartbeat stops and the PLC watchdog
            must place outputs in their safe state.
          </p>
          <label class="plc-live-confirm" for="live-plc-confirm">
            <input id="live-plc-confirm" type="checkbox" />
            <span>
              I verified the active TIA project, DB14 standard/non-optimized
              layout, CPU address, and the exact write scope shown above.
            </span>
          </label>
          <button class="button button-plc-live plc-live-connect" type="button" data-live-plc-connect disabled>
            Connect to Real PLC
          </button>
          <div id="plc-live-result" class="plc-test-result" aria-live="polite">
            NOT CONNECTED
          </div>
        `,
        "plc-live",
      );
    } catch (error) {
      this._showDialog(
        "Connect Real PLC",
        `
          <div class="plc-live-boundary is-failed">
            <strong>REAL PLC CONNECTION UNAVAILABLE</strong>
            <span>${escapeHtml(error.message)}</span>
          </div>
          <p>No PLC connection was attempted.</p>
        `,
        "plc-live",
      );
    }
  }

  async _connectLivePlc() {
    const confirm = document.querySelector("#live-plc-confirm");
    const connectButton = document.querySelector("[data-live-plc-connect]");
    const resultMount = document.querySelector("#plc-live-result");
    if (!confirm?.checked || !connectButton || !resultMount) {
      this._showInteractionFeedback(
        "Confirm the exact PLC write scope before connecting",
      );
      return;
    }
    const resolution = resolveScenePlcProfile(
      this.sceneDocument,
      this.plcProfiles,
    );
    if (
      resolution.status !== "matched" ||
      !Array.isArray(resolution.profile.live?.writeScope)
    ) {
      resultMount.className = "plc-test-result is-failed";
      resultMount.textContent = "The active scene/profile changed. Reopen Connect Real PLC.";
      return;
    }

    connectButton.disabled = true;
    confirm.disabled = true;
    resultMount.className = "plc-test-result is-running";
    resultMount.textContent =
      "Opening the guarded Siemens session. Writes are limited to the confirmed scope.";

    if (this.controlSource !== CONTROL_SOURCES.DISCONNECTED) {
      this._setControlSource(CONTROL_SOURCES.DISCONNECTED);
    }
    try {
      await this.livePlc.connect({
        profileId: resolution.profile.id,
        sceneId: this.sceneDocument.id,
        authorizedWriteScope: resolution.profile.live.writeScope,
      });
      this.liveCycleAccumulatorMs = this.livePlc.cycleMs;
      this._setControlSource(CONTROL_SOURCES.LIVE_PLC);
      document.querySelector("#app-dialog").close();
      this._showInteractionFeedback(
        "REAL PLC CONNECTED — guarded exchange is starting; wait for HEALTHY before Run",
      );
      this._refreshUi();
    } catch (error) {
      resultMount.className = "plc-test-result is-failed";
      resultMount.innerHTML = `
        <strong>REAL PLC CONNECTION FAILED</strong>
        <span>${escapeHtml(error.message)}</span>
      `;
      connectButton.disabled = false;
      confirm.disabled = false;
    }
  }

  async _disconnectLivePlc(message, { keepalive = false } = {}) {
    const hadLiveSession =
      this.livePlc.connected ||
      this.controlSource === CONTROL_SOURCES.LIVE_PLC;
    this.liveCycleAccumulatorMs = 0;
    if (this.controlSource === CONTROL_SOURCES.LIVE_PLC) {
      this.controlSource = CONTROL_SOURCES.DISCONNECTED;
      this.simulation?.setControlSource(CONTROL_SOURCES.DISCONNECTED);
    }
    let disconnectError = null;
    try {
      await this.livePlc.disconnect({ keepalive });
    } catch (error) {
      disconnectError = error;
    }
    if (hadLiveSession) {
      this._showInteractionFeedback(
        disconnectError
          ? `${message}. Local exchange stopped; disconnect confirmation failed: ${disconnectError.message}`
          : message,
      );
    }
    this._refreshUi();
  }

  async _cycleLivePlc() {
    if (
      this.controlSource !== CONTROL_SOURCES.LIVE_PLC ||
      !this.livePlc.connected ||
      !this.sceneDocument ||
      !this.simulation
    ) {
      return;
    }
    try {
      const wasReady = getLivePlcReadiness(this.livePlc.snapshot).ready;
      await this.livePlc.step({
        sceneId: this.sceneDocument.id,
        tags: this.simulation.getTags(),
      });
      const readiness = getLivePlcReadiness(this.livePlc.snapshot);
      if (!readiness.ready && (wasReady || this.simulation.running)) {
        this.simulation.holdControllerSafe();
        this._showInteractionFeedback(
          `Real PLC control held safe — ${readiness.label}`,
        );
        this._refreshUi();
      }
    } catch (error) {
      if (this.controlSource === CONTROL_SOURCES.LIVE_PLC) {
        await this._disconnectLivePlc(
          `REAL PLC EXCHANGE STOPPED — ${error.message}`,
        );
      }
    }
  }

  async _openPlcTest() {
    this._showDialog(
      "Test PLC",
      `
        <div class="plc-test-boundary">
          <strong>READ-ONLY PLC DIAGNOSTIC</strong>
          <span>No PLC write method is available to this test.</span>
        </div>
        <p>Loading local PLC interface profiles…</p>
      `,
    );

    try {
      await this._loadPlcProfiles();
      const validProfiles = this.plcProfiles.filter((profile) => profile.valid);
      if (!validProfiles.length) {
        const problems = this.plcProfiles
          .map(
            (profile) =>
              `<li><strong>${escapeHtml(profile.label)}</strong>: ${escapeHtml(
                profile.error ?? "Profile is invalid.",
              )}</li>`,
          )
          .join("");
        this._showDialog(
          "Test PLC",
          `
            <div class="plc-test-boundary">
              <strong>PLC TEST UNAVAILABLE</strong>
              <span>No valid local interface profile was found.</span>
            </div>
            ${problems ? `<ul class="plc-test-items">${problems}</ul>` : ""}
            <p>Place a validated interface JSON file in the <code>plc-profiles</code> folder beside the packaged EXE.</p>
          `,
        );
        return;
      }

      const resolution = resolveScenePlcProfile(
        this.sceneDocument,
        this.plcProfiles,
      );
      if (resolution.status !== "matched") {
        const assignedProfile = this.sceneDocument?.plcTestProfile;
        const boundary =
          resolution.status === "not_configured"
            ? "NO PLC TEST PROFILE FOR THIS SCENE"
            : "SCENE PLC TEST PROFILE IS UNAVAILABLE";
        const detail =
          resolution.status === "invalid"
            ? resolution.profile?.error ?? "The assigned profile is invalid."
            : assignedProfile
              ? `The assigned profile ${assignedProfile} was not found.`
              : "This scene does not declare a plcTestProfile.";
        this._showDialog(
          "Test PLC",
          `
            <div class="plc-test-boundary">
              <strong>${escapeHtml(boundary)}</strong>
              <span>${escapeHtml(this.sceneDocument?.name ?? "The active scene")}</span>
            </div>
            <p>${escapeHtml(detail)}</p>
            <p>No substitute profile was selected and no PLC connection was attempted.</p>
          `,
        );
        return;
      }

      const preferred = resolution.profile;
      const profileOptions = [preferred]
        .map(
          (profile) => `
            <option
              value="${escapeHtml(profile.id)}"
              ${profile.id === preferred.id ? "selected" : ""}
            >
              ${escapeHtml(profile.label)} — ${escapeHtml(profile.ip)}
            </option>
          `,
        )
        .join("");

      this._showDialog(
        "Test PLC",
        `
          <div class="plc-test-boundary">
            <strong>READ-ONLY PLC DIAGNOSTIC</strong>
            <span>Connect → read configured DB tags twice → disconnect. Writes: 0.</span>
          </div>
          <p>This restores the original setup-test control without enabling live scene writes. It checks absolute DB address/type access and available status/heartbeat evidence.</p>
          <label class="field-label" for="plc-profile-select">Automatically loaded for ${escapeHtml(this.sceneDocument.name)}</label>
          <select id="plc-profile-select" class="plc-profile-select" disabled>
            ${profileOptions}
          </select>
          <p class="plc-test-note">
            Rack ${escapeHtml(preferred.rack)} / slot ${escapeHtml(preferred.slot)}
            &middot; ${escapeHtml(preferred.tagCount)} configured tags
            &middot; <code>${escapeHtml(preferred.id)}</code>.
            Confirm the DB14 layout and CPU before testing.
          </p>
          <button class="button button-plc-test plc-test-run" type="button" data-plc-test-run>
            Run read-only PLC test
          </button>
          <div id="plc-test-result" class="plc-test-result" aria-live="polite">
            NOT TESTED
          </div>
        `,
      );
    } catch (error) {
      this._showDialog(
        "Test PLC",
        `
          <div class="plc-test-boundary">
            <strong>PLC TEST UNAVAILABLE</strong>
            <span>${escapeHtml(error.message)}</span>
          </div>
        `,
      );
    }
  }

  async _runPlcTest() {
    const profileSelect = document.querySelector("#plc-profile-select");
    const runButton = document.querySelector("[data-plc-test-run]");
    const resultMount = document.querySelector("#plc-test-result");
    if (!profileSelect || !runButton || !resultMount) {
      return;
    }

    runButton.disabled = true;
    runButton.textContent = "Testing configured PLC tags…";
    resultMount.className = "plc-test-result is-running";
    resultMount.textContent =
      "Opening a read-only S7 session. No PLC writes are available.";

    try {
      const response = await postLocalJson(
        "/api/plc/test",
        { profileId: profileSelect.value },
        {
          headers: {
            "X-PLC-Test-Mode": "read-only",
          },
        },
      );
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "The PLC test could not run.");
      }
      this._renderPlcTestResult(payload);
    } catch (error) {
      resultMount.className = "plc-test-result is-failed";
      resultMount.innerHTML = `
        <strong>PLC TEST FAILED</strong>
        <span>${escapeHtml(error.message)}</span>
      `;
    } finally {
      runButton.disabled = false;
      runButton.textContent = "Run read-only PLC test";
    }
  }

  _renderPlcTestResult(result) {
    const resultMount = document.querySelector("#plc-test-result");
    if (!resultMount) {
      return;
    }
    const statusClass =
      result.status === "passed"
        ? "is-passed"
        : result.status === "passed_with_warnings"
          ? "is-warning"
          : "is-failed";
    const items = Array.isArray(result.items) ? result.items : [];
    const itemMarkup = items
      .map(
        (item) => `
          <li class="plc-test-item is-${escapeHtml(item.status)}">
            <strong>${escapeHtml(item.status).toUpperCase()} — ${escapeHtml(item.label)}</strong>
            <span>${escapeHtml(item.detail)}</span>
            ${item.fix ? `<em>Check: ${escapeHtml(item.fix)}</em>` : ""}
          </li>
        `,
      )
      .join("");
    resultMount.className = `plc-test-result ${statusClass}`;
    resultMount.innerHTML = `
      <strong>${escapeHtml(result.summary)}</strong>
      <span>
        ${escapeHtml(result.profile?.label ?? "PLC profile")} ·
        ${escapeHtml(result.durationMs ?? "—")} ms ·
        write attempted: ${result.writeAttempted ? "YES" : "NO"}
      </span>
      <ul class="plc-test-items">${itemMarkup}</ul>
    `;
  }

  _alarmRecordMarkup(record) {
    const raised = new Date(record.raisedAt).toLocaleTimeString();
    const cleared = record.clearedAt
      ? new Date(record.clearedAt).toLocaleTimeString()
      : null;
    const state = record.active
      ? record.acknowledged
        ? "ACTIVE · ACK"
        : "ACTIVE · UNACK"
      : "CLEARED";
    return `
      <article class="alarm-record severity-${escapeHtml(record.severity)} ${record.active ? "is-active" : "is-cleared"}">
        <div class="alarm-record-heading">
          <span class="alarm-severity">${escapeHtml(record.severity).toUpperCase()}</span>
          <code>${escapeHtml(record.code)}</code>
          <span class="alarm-state">${state}</span>
        </div>
        <strong>${escapeHtml(record.message)}</strong>
        <span class="alarm-source">Source: ${escapeHtml(record.source)} · Raised ${escapeHtml(raised)}${cleared ? ` · Cleared ${escapeHtml(cleared)}` : ""}</span>
        <p><b>First check:</b> ${escapeHtml(record.check)}</p>
      </article>
    `;
  }

  _alarmDialogMarkup() {
    const snapshot = this.alarmManager?.getSnapshot();
    if (!snapshot) {
      return "<p>No scene alarm session is available.</p>";
    }
    const clearedCount = snapshot.history.filter(
      (record) => !record.active,
    ).length;
    const records =
      snapshot.history.length === 0
        ? `
          <div class="alarm-empty">
            <strong>No active faults or alarms</strong>
            <span>This scene has not generated an alarm during the current load.</span>
          </div>
        `
        : snapshot.history
            .map((record) => this._alarmRecordMarkup(record))
            .join("");

    return `
      <div class="alarm-window" data-active-count="${snapshot.activeCount}">
        <div class="scene-guide-boundary alarm-boundary">
          <strong>SIMULATED SCENE ALARMS ONLY</strong>
          <span>Acknowledge changes only this local player. It does not acknowledge, reset, or write an alarm in a real PLC.</span>
        </div>
        <div class="alarm-summary ${snapshot.activeCount > 0 ? `severity-${snapshot.highestSeverity}` : "is-normal"}">
          <span>
            <small>CURRENT SCENE</small>
            <strong>${escapeHtml(snapshot.sceneName)}</strong>
            <code>${escapeHtml(snapshot.sceneId)}</code>
          </span>
          <span>
            <small>ACTIVE</small>
            <strong>${snapshot.activeCount}</strong>
          </span>
          <span>
            <small>UNACKNOWLEDGED</small>
            <strong>${snapshot.unacknowledgedCount}</strong>
          </span>
          <span>
            <small>HISTORY</small>
            <strong>${snapshot.history.length}</strong>
          </span>
        </div>
        <div class="alarm-toolbar">
          <button class="button" type="button" data-alarm-acknowledge ${snapshot.unacknowledgedCount === 0 ? "disabled" : ""}>
            Acknowledge active
          </button>
          <button class="button button-secondary" type="button" data-alarm-clear-history ${clearedCount === 0 ? "disabled" : ""}>
            Clear cleared history
          </button>
        </div>
        <div class="alarm-records">${records}</div>
      </div>
    `;
  }

  _openAlarmDialog() {
    if (!this.alarmManager) {
      this._showInteractionFeedback("No scene is loaded");
      return;
    }
    const snapshot = this.alarmManager.getSnapshot();
    this._showDialog(
      `Faults & Alarms — ${snapshot.sceneName}`,
      this._alarmDialogMarkup(),
      "alarms",
    );
    this.renderedAlarmRevision = snapshot.revision;
  }

  _renderOpenAlarmDialog() {
    const dialog = document.querySelector("#app-dialog");
    if (!dialog.open || dialog.dataset.kind !== "alarms" || !this.alarmManager) {
      return;
    }
    const snapshot = this.alarmManager.getSnapshot();
    document.querySelector("#app-dialog-title").textContent =
      `Faults & Alarms — ${snapshot.sceneName}`;
    document.querySelector("#app-dialog-content").innerHTML =
      this._alarmDialogMarkup();
    this.renderedAlarmRevision = snapshot.revision;
  }

  _refreshAlarmControls(snapshot) {
    const alarmButton = document.querySelector("#alarm-button");
    const alarmCount = document.querySelector("#alarm-button-count");
    const menuAlarms = document.querySelector("#menu-alarms");
    alarmButton.dataset.active = String(snapshot.activeCount > 0);
    alarmButton.dataset.severity = snapshot.highestSeverity ?? "normal";
    alarmButton.title =
      snapshot.activeCount === 0
        ? "Open Faults & Alarms — no active alarms"
        : `Open Faults & Alarms — ${snapshot.activeCount} active`;
    alarmCount.textContent = String(snapshot.activeCount);
    alarmCount.hidden = snapshot.activeCount === 0;
    menuAlarms.classList.toggle("is-selected", snapshot.activeCount > 0);
    menuAlarms.dataset.severity = snapshot.highestSeverity ?? "normal";
    menuAlarms.querySelector(".alarm-menu-count").textContent =
      snapshot.activeCount > 0 ? String(snapshot.activeCount) : "0";
    if (snapshot.revision !== this.renderedAlarmRevision) {
      this._renderOpenAlarmDialog();
    }
  }

  _showDialog(title, contents, kind = "") {
    const dialog = document.querySelector("#app-dialog");
    dialog.dataset.kind = kind;
    document.querySelector("#app-dialog-title").textContent = title;
    document.querySelector("#app-dialog-content").innerHTML = contents;
    if (!dialog.open) {
      dialog.showModal();
    }
  }

  _closeMenus() {
    document.querySelectorAll(".app-menu[open]").forEach((menu) => {
      menu.open = false;
    });
  }

  _populateScenes() {
    const select = document.querySelector("#scene-select");
    select.replaceChildren(
      ...this.sceneDescriptors.map((scene) => {
        const option = document.createElement("option");
        option.value = scene.id;
        option.textContent = scene.label;
        return option;
      }),
    );
  }

  async _refreshAvailableBuiltins() {
    const checks = await Promise.all(
      BUILTIN_SCENES.map(async (scene) => {
        try {
          const response = await fetch(scene.url, {
            method: "HEAD",
            cache: "no-store",
          });
          return response.ok ? scene : null;
        } catch {
          return null;
        }
      }),
    );
    const available = checks.filter((scene) => scene !== null);
    if (available.length === 0) {
      return;
    }
    const select = document.querySelector("#scene-select");
    const previousValue = select.value;
    const savedScenes = this.sceneDescriptors.filter((scene) =>
      scene.id.startsWith("saved:"),
    );
    this.availableBuiltinScenes = available;
    this.sceneDescriptors = [...available, ...savedScenes];
    this._populateScenes();
    if (this.sceneDescriptors.some((scene) => scene.id === previousValue)) {
      select.value = previousValue;
    }
  }

  async _refreshSavedScenes(selectedId = null) {
    try {
      const response = await fetch("/api/scenes", { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const payload = await response.json();
      const savedScenes = Array.isArray(payload.scenes)
        ? payload.scenes.filter(
            (scene) =>
              typeof scene?.id === "string" &&
              typeof scene?.label === "string" &&
              typeof scene?.url === "string",
          )
        : [];
      const select = document.querySelector("#scene-select");
      const previousValue = selectedId ?? select.value;
      this.sceneDescriptors = [
        ...this.availableBuiltinScenes,
        ...savedScenes,
      ];
      this._populateScenes();
      if (this.sceneDescriptors.some((scene) => scene.id === previousValue)) {
        select.value = previousValue;
      }
    } catch {
      // Static hosting remains usable; only the local saved-scene library is
      // unavailable when the API is not provided.
    }
  }

  _selectCustomScene(fileName) {
    const select = document.querySelector("#scene-select");
    let option = select.querySelector('option[value="custom"]');
    if (!option) {
      option = document.createElement("option");
      option.value = "custom";
      select.appendChild(option);
    }
    option.textContent = `Custom: ${fileName}`;
    select.value = "custom";
    const url = new URL(window.location.href);
    url.searchParams.delete("scene");
    window.history.replaceState(null, "", url);
  }

  async _saveScene() {
    if (!this.sceneDocument) {
      this._showInteractionFeedback("No scene is loaded");
      return;
    }
    const contents = serializeSceneDocument(this.sceneDocument);
    await this._withLoading(async () => {
      const response = await postLocal("/api/scenes", {
        contentType: SCENE_FILE_MIME,
        body: contents,
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error ?? `Save failed: HTTP ${response.status}.`);
      }
      await this._refreshSavedScenes(result.id);
      this._showInteractionFeedback(`Saved ${result.fileName}`);
    });
  }

  _selectVariant(variantId) {
    if (!VARIANTS.some((variant) => variant.id === variantId)) {
      return;
    }
    const url = new URL(window.location.href);
    const selectedSceneId = document.querySelector("#scene-select").value;
    url.searchParams.set("variant", variantId);
    if (selectedSceneId && selectedSceneId !== "custom") {
      url.searchParams.set("scene", selectedSceneId);
    }
    window.location.assign(url);
  }

  async loadBuiltIn(descriptor) {
    if (
      this.livePlc.connected ||
      this.controlSource === CONTROL_SOURCES.LIVE_PLC
    ) {
      await this._disconnectLivePlc(
        "Scene changed — real PLC session disconnected",
      );
    }
    const request = this.sceneLoads.begin();
    document.querySelector("#scene-select").value = descriptor.id;
    await this._withLoading(async () => {
      const scene = await loadSceneFromUrl(descriptor.url, {
        signal: request.signal,
      });
      if (request.isCurrent()) {
        this._installScene(scene, "Built-in JSON");
      }
    }, request);
  }

  async _withLoading(operation, request = null) {
    const loading = document.querySelector("#loading-overlay");
    const error = document.querySelector("#error-overlay");
    loading.hidden = false;
    error.hidden = true;
    try {
      await operation();
    } catch (caught) {
      if (caught?.name === "AbortError") {
        return;
      }
      console.error(caught);
      if (!request || request.isCurrent()) {
        error.textContent =
          caught instanceof Error ? caught.message : String(caught);
        error.hidden = false;
      }
    } finally {
      if (!request || request.isCurrent()) {
        loading.hidden = true;
      }
    }
  }

  _installScene(scene, sourceLabel) {
    if (this.livePlc.connected) {
      throw new Error(
        "Cannot install a different scene while a real PLC session is connected.",
      );
    }
    const staged = stageSceneSession({
      scene,
      factory: this.factory,
      createRoot: () => new THREE.Group(),
      createSimulation,
      createAlarmManager: (document) => new SceneAlarmManager(document),
      disposeRoot: (root) => {
        for (const child of [...root.children]) {
          root.remove(child);
          disposeObject(child);
        }
      },
    });
    staged.simulation.setControlSource(CONTROL_SOURCES.DISCONNECTED);
    staged.simulation.setLoopEnabled(this.loopEnabled);

    this.simulation?.setRunning(false);
    this.selected = null;
    if (this.selectionBox) {
      this.threeScene.remove(this.selectionBox);
      this.selectionBox.dispose();
      this.selectionBox = null;
    }
    for (const child of [...this.assetRoot.children]) {
      this.assetRoot.remove(child);
      disposeObject(child);
    }
    for (const child of [...staged.root.children]) {
      staged.root.remove(child);
      this.assetRoot.add(child);
    }

    this.sceneDocument = staged.scene;
    this.registry = staged.registry;
    this.controlSource = CONTROL_SOURCES.DISCONNECTED;
    this.simulation = staged.simulation;
    this.alarmManager = staged.alarmManager;
    this.renderedAlarmRevision = -1;
    if (this.interactionFeedbackTimer !== null) {
      clearTimeout(this.interactionFeedbackTimer);
      this.interactionFeedbackTimer = null;
    }
    const interactionFeedback = document.querySelector("#interaction-feedback");
    interactionFeedback.textContent = "";
    interactionFeedback.classList.remove("is-visible");
    this.loadCount += 1;
    this.camera.fov = scene.camera.fov;
    this.camera.position.fromArray(scene.camera.position);
    this.camera.updateProjectionMatrix();
    this.controls.target.fromArray(scene.camera.target);
    this.controls.update();

    document.querySelector("#scene-title").textContent = scene.name;
    document.querySelector("#scene-description").textContent =
      scene.description;
    document.querySelector("#scene-kind").textContent =
      `${scene.simulation.type
        .replaceAll(/([a-z])([A-Z])/g, "$1 $2")
        .toUpperCase()} · ${scene.equipment.length} ASSETS`;
    document.querySelector("#load-count").textContent =
      `${this.loadCount} load${this.loadCount === 1 ? "" : "s"}`;
    document.querySelector("#status-player").textContent = "READY";
    document.querySelector("#status-scene").textContent = "LOADED";
    const url = new URL(window.location.href);
    const selectedSceneId = document.querySelector("#scene-select").value;
    if (selectedSceneId && selectedSceneId !== "custom") {
      url.searchParams.set("scene", selectedSceneId);
      window.history.replaceState(null, "", url);
    }
    this._renderInspector(null, sourceLabel);
    this._refreshUi();
  }

  _resize() {
    const width = Math.max(1, this.mount.clientWidth);
    const height = Math.max(1, this.mount.clientHeight);
    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }

  _raycastAt(clientX, clientY) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
    this.raycaster.setFromCamera(this.pointer, this.camera);
    return this.raycaster.intersectObjects(
      this.assetRoot.children,
      true,
    )[0] ?? null;
  }

  _selectAt(event) {
    const hit = this._raycastAt(event.clientX, event.clientY);
    const root = hit?.object?.userData?.pickRoot ?? null;
    const selected = root
      ? this.registry.get(root.userData.equipmentId) ?? null
      : null;
    this._selectEquipment(selected);
    const action = hit?.object?.userData?.interactiveAction;
    if (action && selected) {
      if (!this.simulation?.canHandleAction(action)) {
        this._showInteractionFeedback(
          "Controller disconnected — this PLC command is disabled",
        );
        this._refreshUi();
        return;
      }
      const message =
        this.simulation?.handleAction(action) ??
        `${selected.definition.label} operated`;
      this._showInteractionFeedback(message);
      this._refreshUi();
    }
  }

  _showInteractionFeedback(message) {
    const feedback = document.querySelector("#interaction-feedback");
    feedback.textContent = message;
    feedback.classList.add("is-visible");
    if (this.interactionFeedbackTimer !== null) {
      clearTimeout(this.interactionFeedbackTimer);
    }
    this.interactionFeedbackTimer = window.setTimeout(() => {
      feedback.classList.remove("is-visible");
    }, 1800);
  }

  _selectEquipment(selected) {
    this.selected = selected;
    if (this.selectionBox) {
      this.threeScene.remove(this.selectionBox);
      this.selectionBox.dispose();
      this.selectionBox = null;
    }
    if (selected) {
      this.selectionBox = new THREE.BoxHelper(selected.group, 0x3dd6a5);
      this.threeScene.add(this.selectionBox);
    }
    this._renderInspector(selected);
  }

  _renderInspector(selected, sourceLabel = null) {
    const container = document.querySelector("#inspector-content");
    if (!selected) {
      container.innerHTML = `
        <div class="empty-state">
          <span class="selection-cube">◇</span>
          <p>Click equipment in the 3D scene to inspect it.</p>
          ${
            sourceLabel
              ? `<small>Current source: ${escapeHtml(sourceLabel)}</small>`
              : ""
          }
        </div>
      `;
      return;
    }

    const { definition, dynamic } = selected;
    const configRows = Object.entries(definition.config)
      .slice(0, 8)
      .map(
        ([key, value]) => `
          <dt>${escapeHtml(key.replaceAll(/([A-Z])/g, " $1"))}</dt>
          <dd>${escapeHtml(Array.isArray(value) ? value.join(", ") : String(value))}</dd>
        `,
      )
      .join("");
    const liveRows = [];
    if (
      [
        "motor",
        "conveyor",
        "pump",
        "fan",
        "drillPress",
        "robotArm",
        "rollerShutter",
        "machine",
      ].includes(dynamic?.kind)
    ) {
      liveRows.push(["running", dynamic.running ? "YES" : "NO"]);
      liveRows.push([
        "run indicator",
        dynamic.running ? "GREEN / ON" : "DARK / OFF",
      ]);
    }
    if (dynamic?.kind === "switch") {
      liveRows.push(["control state", dynamic.active ? "ENGAGED" : "RELEASED"]);
      liveRows.push(["3D action", dynamic.action]);
    }
    if (dynamic?.kind === "tank") {
      liveRows.push(["live level", `${(dynamic.level * 100).toFixed(1)} %`]);
    }
    if (dynamic?.kind === "photoeye") {
      liveRows.push(["live state", dynamic.blocked ? "BLOCKED" : "CLEAR"]);
    }
    if (dynamic?.kind === "levelSensor") {
      liveRows.push(["live state", dynamic.active ? "ACTIVE" : "INACTIVE"]);
      if (dynamic.sensorType === "analog") {
        liveRows.push(["signal", `${dynamic.currentMa.toFixed(2)} mA`]);
      }
    }
    if (dynamic?.kind === "radarLevelSensor") {
      liveRows.push(["level", `${(dynamic.level * 100).toFixed(1)} %`]);
      liveRows.push(["distance", `${dynamic.distanceM.toFixed(2)} m`]);
      liveRows.push(["signal", `${dynamic.currentMa.toFixed(2)} mA`]);
      liveRows.push(["echo", "GOOD"]);
    }
    if (dynamic?.kind === "pusher") {
      liveRows.push(["position", `${(dynamic.position * 100).toFixed(1)} %`]);
      liveRows.push(["extended limit", dynamic.extended ? "ON" : "OFF"]);
      liveRows.push(["retracted limit", dynamic.retracted ? "ON" : "OFF"]);
    }
    if (dynamic?.kind === "rotarySwitch") {
      liveRows.push([
        "selector position",
        `${dynamic.position} of ${dynamic.positionCount - 1}`,
      ]);
      liveRows.push(["3D action", dynamic.action]);
    }
    if (
      [
        "liftTable",
        "valve",
        "drillPress",
        "robotArm",
        "rollerShutter",
        "rotaryTable",
      ].includes(dynamic?.kind)
    ) {
      liveRows.push(["normalized position", `${(dynamic.position * 100).toFixed(1)} %`]);
    }

    container.innerHTML = `
      <div class="inspector-title">
        <span class="asset-type">${escapeHtml(definition.type)}</span>
        <h2>${escapeHtml(definition.label)}</h2>
        <code>${escapeHtml(definition.id)}</code>
      </div>
      <dl class="property-list">
        ${liveRows
          .map(
            ([key, value]) =>
              `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd>`,
          )
          .join("")}
        <dt>position</dt>
        <dd>${definition.position.map((value) => value.toFixed(2)).join(", ")}</dd>
        ${configRows}
      </dl>
    `;
  }

  _splitTagColumns(tags) {
    const byName = (items) => [...items].sort((a, b) => a.name.localeCompare(b.name));
    const splitEvenly = (items) => {
      const ordered = byName(items);
      const midpoint = Math.ceil(ordered.length / 2);
      return [ordered.slice(0, midpoint), ordered.slice(midpoint)];
    };
    const owner = (name) => tags.filter((tag) => tag.owner === name);
    switch (this.tagOrder) {
      case "sim-io":
        // A PLC command is a simulator input; PC-owned feedback is a
        // simulator output. Internal SIM values stay with diagnostics.
        return [
          byName(owner("PLC")),
          byName([...owner("PC"), ...owner("SIM")]),
          ["Simulation inputs", "Simulation outputs + diagnostics"],
        ];
      case "owner":
        return [
          byName(owner("PLC")),
          byName([...owner("PC"), ...owner("SIM")]),
          ["PLC-owned points", "PC feedback + SIM diagnostics"],
        ];
      case "type":
        return [
          byName(tags.filter((tag) => tag.type === "BOOL")),
          byName(tags.filter((tag) => tag.type !== "BOOL")),
          ["BOOL points", "Numeric, text + diagnostics"],
        ];
      case "name":
        return [...splitEvenly(tags), ["A–M", "N–Z"]];
      case "plc-io":
      default:
        return [
          byName(owner("PC")),
          byName([...owner("PLC"), ...owner("SIM")]),
          ["PLC inputs (simulation feedback)", "PLC outputs + diagnostics"],
        ];
    }
  }

  _tagRows(tags) {
    return tags
      .map((tag) => {
        const fakePlc = this.controlSource === CONTROL_SOURCES.FAKE_PLC;
        const forceAvailable =
          fakePlc && this.simulation.canSetControllerPoint(tag.name);
        const forceLabel = tag.type === "BOOL" ? "TOGGLE" : "SET";
        return `
          <tr>
            <td><code>${escapeHtml(tag.name)}</code></td>
            <td>${escapeHtml(tag.type)}</td>
            <td>
              <span class="tag-value ${tag.type === "BOOL" ? (tag.value ? "tag-on" : "tag-off") : ""}">
                ${escapeHtml(formatTagValue(tag))}
              </span>
              ${tag.forced ? '<span class="force-state">FORCED</span>' : ""}
            </td>
            <td>
              <span class="owner owner-${escapeHtml(tag.owner.toLowerCase())}">${escapeHtml(tag.owner)}</span>
              ${
                forceAvailable
                  ? `<button type="button" class="fake-plc-force" data-fake-plc-point="${escapeHtml(tag.name)}" title="Force this Fake PLC output to test incorrect logic">${escapeHtml(forceLabel)}</button>`
                  : ""
              }
            </td>
          </tr>
        `;
      })
      .join("");
  }

  _refreshUi() {
    if (!this.simulation) {
      return;
    }
    const fakePlc = this.controlSource === CONTROL_SOURCES.FAKE_PLC;
    const livePlc =
      this.controlSource === CONTROL_SOURCES.LIVE_PLC &&
      this.livePlc.connected;
    const disconnected = !fakePlc && !livePlc;
    const liveReadiness = getLivePlcReadiness(this.livePlcStatus);
    const liveHealth = liveReadiness.label;
    document.body.dataset.controlSource = this.controlSource;
    const sourceBadge = document.querySelector("#control-source-badge");
    sourceBadge.dataset.active = String(fakePlc || livePlc);
    sourceBadge.dataset.live = String(livePlc);
    sourceBadge.querySelector("span").textContent = livePlc
      ? `REAL PLC CONNECTED — ${liveHealth}`
      : fakePlc
        ? "FAKE PLC ACTIVE — TEST OUTPUTS"
        : "CONTROLLER DISCONNECTED — SCENE OUTPUTS SAFE";
    const fakeButton = document.querySelector("#fake-plc-button");
    fakeButton.classList.toggle("is-active", fakePlc);
    fakeButton.disabled = livePlc;
    fakeButton.textContent = fakePlc
      ? "Offline Fake PLC: ON"
      : "Offline Fake PLC: OFF";
    const liveButton = document.querySelector("#plc-live-button");
    liveButton.classList.toggle("is-active", livePlc);
    liveButton.textContent = livePlc
      ? "Disconnect Real PLC"
      : "Connect Real PLC";
    liveButton.title = livePlc
      ? `Guarded live PLC session: ${liveHealth}`
      : "Review the exact DB write scope before connecting";
    document.querySelector("#plc-test-button").disabled = livePlc;
    const menuLivePlc = document.querySelector("#menu-live-plc");
    menuLivePlc.classList.toggle("is-selected", livePlc);
    menuLivePlc.querySelector(".menu-check").textContent = livePlc ? "✓" : "";
    menuLivePlc.querySelector("span:nth-child(2)").textContent = livePlc
      ? "Disconnect Real PLC"
      : "Connect Real PLC…";
    const menuFakePlc = document.querySelector("#menu-fake-plc");
    menuFakePlc.classList.toggle("is-selected", fakePlc);
    menuFakePlc.querySelector(".menu-check").textContent = fakePlc ? "✓" : "";
    menuFakePlc.querySelector("span:nth-child(2)").textContent = fakePlc
      ? "Disable Fake PLC"
      : "Enable Fake PLC";
    document.querySelector("#io-source-badge").textContent = livePlc
      ? `REAL PLC — ${liveHealth}`
      : fakePlc
        ? "FAKE PLC — FORCE ENABLED"
        : "PLC DISCONNECTED";
    const hudSource = document.querySelector("#hud-controller-source");
    hudSource.dataset.active = String(fakePlc || livePlc);
    hudSource.dataset.live = String(livePlc);
    hudSource.querySelector("strong").textContent = livePlc
      ? "REAL PLC"
      : fakePlc
        ? "FAKE PLC"
        : "DISCONNECTED";
    hudSource.querySelector("small").textContent = livePlc
      ? liveHealth
      : fakePlc
        ? "TEST OUTPUTS"
        : "SCENE OUTPUTS SAFE";

    const status = this.simulation.getStatus();
    const tags = this.simulation.getTags();
    const alarmSnapshot = this.alarmManager?.observe(status, tags);
    if (alarmSnapshot) {
      this._refreshAlarmControls(alarmSnapshot);
    }
    const loopCheckbox = document.querySelector("#loop-scene-checkbox");
    loopCheckbox.checked = this.loopEnabled;
    const loopControl = loopCheckbox.closest(".loop-scene-control");
    loopControl.classList.toggle("is-active", this.loopEnabled);
    loopControl.querySelector("small").textContent = status.loopPending
      ? `Resetting in ${status.loopCountdown.toFixed(1)} s`
      : this.loopEnabled
        ? `Enabled · ${status.loopCount} completed loop${status.loopCount === 1 ? "" : "s"}`
        : "Auto-reset after a normal system stop";
    const menuLoop = document.querySelector("#menu-loop-scene");
    menuLoop.classList.toggle("is-selected", this.loopEnabled);
    menuLoop.querySelector(".menu-check").textContent = this.loopEnabled
      ? "✓"
      : "";
    document.querySelector("#status-player").textContent = disconnected
      ? "PLC WAIT"
      : livePlc && !liveReadiness.ready
        ? liveHealth
        : status.mode;
    document.querySelector("#status-player").dataset.active = String(
      status.running,
    );
    document.querySelector("#status-scene").textContent =
      this.sceneDocument?.name ?? "—";
    document.querySelector("#status-time").textContent =
      `${status.elapsed.toFixed(1)} s`;
    document.querySelector("#status-fps").textContent =
      `${this.fps || "—"} fps`;
    document.querySelector("#hud-scene").textContent =
      this.sceneDocument?.name ?? "No scene loaded";
    document.querySelector("#hud-state").textContent = disconnected
      ? "NO PLC"
      : livePlc && !liveReadiness.ready
        ? liveHealth
        : status.running
          ? "PLAYING"
          : status.mode;
    document.querySelector("#hud-state").dataset.active = String(
      status.running,
    );
    document.querySelector("#hud-time").textContent =
      `${status.elapsed.toFixed(1)} s`;
    document.querySelector("#hud-fps").textContent =
      `${this.fps || "—"} fps`;
    document.querySelector("#hud-live-track").classList.toggle(
      "is-running",
      status.running,
    );

    const runButton = document.querySelector("#run-button");
    const hudRunButton = document.querySelector("#hud-run-button");
    runButton.classList.toggle("is-active", status.running);
    const startBlockReason = this.simulation.getStartBlockReason();
    const controllerStartBlock = disconnected
      ? "Enable Fake PLC or bind a live PLC before running"
      : livePlc && !liveReadiness.ready
        ? `Real PLC is not ready — ${liveHealth}`
        : startBlockReason;
    runButton.title = controllerStartBlock ?? "Run scene";
    runButton.disabled = livePlc && !liveReadiness.ready;
    document.querySelector("#stop-button").classList.toggle(
      "is-active",
      !status.running,
    );
    hudRunButton.classList.toggle("is-active", status.running);
    hudRunButton.title = controllerStartBlock ?? "Run scene";
    hudRunButton.disabled = livePlc && !liveReadiness.ready;
    document
      .querySelectorAll('[data-player-command="run"]')
      .forEach((button) => {
        button.disabled = livePlc && !liveReadiness.ready;
        button.title = controllerStartBlock ?? "Run scene";
      });
    document.querySelector("#hud-stop-button").classList.toggle(
      "is-active",
      !status.running,
    );

    const [leftTags, rightTags, columnLabels] = this._splitTagColumns(tags);
    document.querySelector("#tag-column-left").textContent = columnLabels[0];
    document.querySelector("#tag-column-right").textContent = columnLabels[1];
    document.querySelector("#tag-table-body-left").innerHTML =
      this._tagRows(leftTags);
    document.querySelector("#tag-table-body-right").innerHTML =
      this._tagRows(rightTags);
    document.querySelector("#tag-order-select").value = this.tagOrder;

    const actions = this.simulation.getActions();
    const disabledActionTitle = livePlc
      ? "Use the player Run/Stop controls during a live PLC session"
      : "Controller disconnected";
    document.querySelector("#action-controls").innerHTML = actions
      .map(
        (action) => `
          <button
            type="button"
            class="button button-action ${action.active ? "is-active" : ""}"
            data-simulation-action="${escapeHtml(action.id)}"
            ${action.enabled === false ? "disabled" : ""}
            title="${action.enabled === false ? escapeHtml(disabledActionTitle) : ""}"
          >
            ${escapeHtml(action.label)}
          </button>
        `,
      )
      .join("");

    if (this.selected) {
      this._renderInspector(this.selected);
      this.selectionBox?.update();
    }
  }

  _animate(timestamp) {
    requestAnimationFrame(this._animate);
    const deltaSeconds = Math.min((timestamp - this.lastTimestamp) / 1000, 0.05);
    this.lastTimestamp = timestamp;

    this.simulation?.update(deltaSeconds);
    if (
      this.controlSource === CONTROL_SOURCES.LIVE_PLC &&
      this.livePlc.connected
    ) {
      this.liveCycleAccumulatorMs += deltaSeconds * 1000;
      if (this.liveCycleAccumulatorMs >= this.livePlc.cycleMs) {
        this.liveCycleAccumulatorMs %= this.livePlc.cycleMs;
        void this._cycleLivePlc();
      }
    } else {
      this.liveCycleAccumulatorMs = 0;
    }
    this.controls.update();
    this.renderer.render(this.threeScene, this.camera);
    this.selectionBox?.update();

    this.frameCount += 1;
    this.fpsAccumulator += deltaSeconds;
    this.uiAccumulator += deltaSeconds;
    if (this.fpsAccumulator >= 0.5) {
      this.fps = Math.round(this.frameCount / this.fpsAccumulator);
      this.frameCount = 0;
      this.fpsAccumulator = 0;
    }
    if (this.uiAccumulator >= 0.12) {
      this.uiAccumulator = 0;
      this._refreshUi();
    }
  }

  snapshot() {
    return {
      loadedSceneId: this.sceneDocument?.id ?? null,
      loadedSceneName: this.sceneDocument?.name ?? null,
      loadCount: this.loadCount,
      running: this.simulation?.running ?? false,
      equipmentCount: this.registry.size,
      variant: currentVariant(),
      appWindow: APP_WINDOW_MODE,
      controlSource: this.controlSource,
      livePlc: this.livePlc.snapshot,
      loopEnabled: this.loopEnabled,
      status: this.simulation?.getStatus() ?? null,
      tags: this.simulation?.getTags() ?? [],
      alarms: this.alarmManager?.getSnapshot() ?? null,
    };
  }
}

const variant = currentVariant();
renderShell(variant);
const player = new Player();

if (APP_WINDOW_MODE) {
  const sendHeartbeat = () => {
    void postLocal("/api/app/heartbeat").catch(() => {});
  };
  sendHeartbeat();
  window.setInterval(sendHeartbeat, 1500);
}

// Read-only test hook used by browser acceptance checks.
window.__PLC_PLAYER__ = Object.freeze({
  snapshot: () => player.snapshot(),
  loadBuiltIn: (id) => {
    const descriptor = player.sceneDescriptors.find((scene) => scene.id === id);
    if (!descriptor) {
      throw new Error(`Unknown built-in scene "${id}".`);
    }
    return player.loadBuiltIn(descriptor);
  },
  setControlSource: (source) => player._setControlSource(source),
  setControllerPoint: (name, value) =>
    player.simulation?.setControllerPoint(name, value) ?? false,
});
