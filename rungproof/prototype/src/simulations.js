import * as THREE from "../../vendor/three/three.module.min.js";
import {
  setAssetPosition,
  setEquipmentRunning,
  setIndicatorState,
  setLevelSensorState,
  setPhotoeyeState,
  setPusherPosition,
  setRadarLevelState,
  setSelectorPosition,
  setSwitchState,
  setTankLevel,
} from "./assetFactory.js";

export const CONTROL_SOURCES = Object.freeze({
  DISCONNECTED: "disconnected",
  FAKE_PLC: "fake-plc",
  LIVE_PLC: "live-plc",
});

export const STOP_REASONS = Object.freeze({
  RESET: "reset",
  OPERATOR: "operator-stop",
  SYSTEM: "system-stop",
  INTERLOCK: "interlock-stop",
  START_BLOCKED: "start-blocked",
});

const VALID_CONTROL_SOURCES = new Set(Object.values(CONTROL_SOURCES));

function safePointValue(point) {
  if (Object.hasOwn(point, "safe")) {
    return point.safe;
  }
  if (point.type === "BOOL") {
    return false;
  }
  if (["DINT", "REAL"].includes(point.type)) {
    return 0;
  }
  return "";
}

function entry(registry, id, expectedType = null) {
  const found = registry.get(id);
  if (!found) {
    throw new Error(`Simulation references missing equipment "${id}".`);
  }
  if (expectedType !== null && found.definition.type !== expectedType) {
    throw new Error(
      `Equipment "${id}" must be type "${expectedType}", not "${found.definition.type}".`,
    );
  }
  return found;
}

function optionalEntry(registry, id, expectedTypes) {
  if (id === undefined || id === null || id === "") {
    return null;
  }
  const found = entry(registry, id);
  const allowedTypes = Array.isArray(expectedTypes)
    ? expectedTypes
    : [expectedTypes];
  if (!allowedTypes.includes(found.definition.type)) {
    throw new Error(
      `Equipment "${id}" must be one of: ${allowedTypes.join(", ")}; received "${found.definition.type}".`,
    );
  }
  return found;
}

function setActionSwitches(registry, actionId, active) {
  for (const equipment of registry.values()) {
    if (
      equipment.dynamic?.kind === "switch" &&
      equipment.dynamic.action === actionId
    ) {
      setSwitchState(equipment, active);
    }
  }
}

function animateConveyorDrive(conveyor, speedMps, deltaSeconds) {
  for (const roller of conveyor.dynamic.rollers) {
    roller.rotation.z -= (speedMps / 0.12) * deltaSeconds;
  }
  if (conveyor.dynamic.driveShaftPivot) {
    conveyor.dynamic.driveShaftPivot.rotation.z -=
      (speedMps / 0.12) * deltaSeconds;
  }
  if (conveyor.dynamic.shaftPivot) {
    conveyor.dynamic.shaftPivot.rotation.x += 8 * deltaSeconds;
  }
}

class BaseSimulation {
  constructor(scene, registry) {
    this.scene = scene;
    this.registry = registry;
    this.declaredPoints = Array.isArray(scene.simulation?.points)
      ? scene.simulation.points
      : [];
    this.controlSource = CONTROL_SOURCES.DISCONNECTED;
    this.running = false;
    this.elapsed = 0;
    this.loopEnabled = false;
    this.loopPending = false;
    this.loopCountdown = 0;
    this.loopCount = 0;
    this.loopDelaySeconds = Math.max(
      0.1,
      Number(scene.simulation?.loopDelaySeconds) || 0.75,
    );
    this.stopReason = STOP_REASONS.RESET;
    this.stopMessage = "Scene reset and ready";
  }

  getStartBlockReason() {
    if (!this.hasController()) {
      return "Controller disconnected — Start cannot create PLC outputs";
    }
    return null;
  }

  _acceptStart() {
    this.running = true;
    this.loopPending = false;
    this.loopCountdown = 0;
    this.stopReason = null;
    this.stopMessage = "";
    return true;
  }

  _rejectStart(message) {
    if (!this.running) {
      this.loopPending = false;
      this.loopCountdown = 0;
      this.stopReason = STOP_REASONS.START_BLOCKED;
    }
    this.stopMessage = message;
    return false;
  }

  setRunning(
    running,
    reason = STOP_REASONS.OPERATOR,
    message = "Operator stop — scene held",
  ) {
    if (running) {
      const blockedReason = this.getStartBlockReason();
      return blockedReason
        ? this._rejectStart(blockedReason)
        : this._acceptStart();
    }
    this.running = false;
    this.loopPending = false;
    this.loopCountdown = 0;
    this.stopReason = reason;
    this.stopMessage = message;
    return true;
  }

  completeSystemStop(message = "Program complete — system stop active") {
    this.running = false;
    this.stopReason = STOP_REASONS.SYSTEM;
    this.stopMessage = message;
    this.loopPending = this.loopEnabled && this.hasController();
    this.loopCountdown = this.loopPending ? this.loopDelaySeconds : 0;
    return true;
  }

  setLoopEnabled(enabled) {
    this.loopEnabled = Boolean(enabled);
    if (!this.loopEnabled) {
      this.loopPending = false;
      this.loopCountdown = 0;
    } else if (
      !this.running &&
      this.stopReason === STOP_REASONS.SYSTEM &&
      this.hasController()
    ) {
      this.loopPending = true;
      this.loopCountdown = this.loopDelaySeconds;
    }
    return this.loopEnabled;
  }

  setControlSource(source) {
    if (!VALID_CONTROL_SOURCES.has(source)) {
      throw new Error(`Unsupported control source "${source}".`);
    }
    const previous = this.controlSource;
    this.controlSource = source;
    this._onControlSourceChanged(previous, source);
  }

  _onControlSourceChanged() {
    this.reset();
  }

  getControlSource() {
    return this.controlSource;
  }

  hasController() {
    return this.controlSource !== CONTROL_SOURCES.DISCONNECTED;
  }

  canHandleAction() {
    return this.hasController();
  }

  setControllerPoint() {
    return false;
  }

  canSetControllerPoint() {
    return false;
  }

  clearControllerForces() {
    return false;
  }

  holdControllerSafe() {
    this.setRunning(
      false,
      STOP_REASONS.INTERLOCK,
      "Controller not ready — scene commands held safe",
    );
    return true;
  }

  reset() {
    this.elapsed = 0;
    this.running = false;
    this.loopPending = false;
    this.loopCountdown = 0;
    this.stopReason = STOP_REASONS.RESET;
    this.stopMessage = "Scene reset and ready";
  }

  update(deltaSeconds) {
    if (this.loopPending) {
      this.loopCountdown = Math.max(0, this.loopCountdown - deltaSeconds);
      if (this.loopCountdown <= 0) {
        this.loopPending = false;
        this.reset();
        if (this.setRunning(true)) {
          this.loopCount += 1;
        }
      }
    }
    if (this.running) {
      this.elapsed += deltaSeconds;
    }
  }

  getStatus() {
    const mode = this.running
      ? "RUNNING"
      : this.loopPending
        ? "LOOP RESET"
        : this.stopReason === STOP_REASONS.SYSTEM
          ? "SYSTEM STOP"
          : this.stopReason === STOP_REASONS.START_BLOCKED
            ? "START BLOCKED"
            : this.stopReason === STOP_REASONS.INTERLOCK
              ? "INTERLOCK STOP"
            : this.stopReason === STOP_REASONS.OPERATOR
              ? "OPERATOR STOP"
              : "STOPPED";
    return {
      running: this.running,
      mode,
      elapsed: this.elapsed,
      stopReason: this.stopReason,
      message: this.stopMessage,
      loopEnabled: this.loopEnabled,
      loopPending: this.loopPending,
      loopCountdown: this.loopCountdown,
      loopCount: this.loopCount,
    };
  }

  getTags() {
    return [];
  }

  /**
   * Project changing runtime values through the scene's declared point
   * contract. Custom runtimes may calculate values, but they do not get to
   * redeclare tag names, types, ownership, or engineering units.
   */
  declaredTags(pointValues) {
    const values = pointValues ?? {};
    const declaredNames = new Set(
      this.declaredPoints.map((point) => point.name),
    );
    const undeclaredNames = Object.keys(values).filter(
      (name) => !declaredNames.has(name),
    );
    if (undeclaredNames.length > 0) {
      throw new Error(
        `Simulation "${this.scene.id}" supplied undeclared runtime point(s): ${undeclaredNames.join(", ")}.`,
      );
    }

    return this.declaredPoints
      .filter((point) => !point.hidden)
      .map((point) => {
        if (!Object.hasOwn(values, point.name)) {
          throw new Error(
            `Simulation "${this.scene.id}" did not supply declared runtime point "${point.name}".`,
          );
        }
        return {
          name: point.name,
          type: point.type,
          value: values[point.name],
          ...(point.unit ? { unit: point.unit } : {}),
          owner: point.owner,
        };
      });
  }

  getActions() {
    return [];
  }

  handleAction() {
    return null;
  }
}

class ConveyorSimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    const config = scene.simulation;
    this.conveyor = entry(registry, config.conveyorId, "conveyor");
    this.photoeye = entry(registry, config.photoeyeId, "photoeye");
    this.indicator = entry(registry, config.indicatorId, "indicator");
    this.products = (config.productIds ?? []).map((id) =>
      entry(registry, id, "box"),
    );
    if (this.products.length === 0) {
      throw new Error("Conveyor simulation requires at least one productId.");
    }
    this.speed = config.speedMps ?? 1.05;
    this.spacing = config.spacingM ?? 2.6;
    this.completed = 0;
    this.blocked = false;
    this.initialPositions = this.products.map((product) =>
      product.group.position.clone(),
    );
    this.reset();
  }

  reset() {
    super.reset();
    if (!this.products) {
      return;
    }
    this.completed = 0;
    this.blocked = false;
    this.products.forEach((product, index) => {
      product.group.position.copy(this.initialPositions[index]);
    });
    setPhotoeyeState(this.photoeye, false);
    setIndicatorState(this.indicator, "amber");
    setEquipmentRunning(this.conveyor, false);
    setActionSwitches(this.registry, "conveyor_run", false);
  }

  update(deltaSeconds) {
    const wasRunning = this.running;
    super.update(deltaSeconds);
    setEquipmentRunning(this.conveyor, wasRunning);
    setActionSwitches(this.registry, "conveyor_run", wasRunning);

    if (wasRunning) {
      const conveyorLength = this.conveyor.dynamic.length;
      const conveyorCenter = this.conveyor.group.position.x;
      const start = conveyorCenter - conveyorLength / 2 - 0.8;
      const end = conveyorCenter + conveyorLength / 2 + 0.8;

      for (const product of this.products) {
        product.group.position.x += this.speed * deltaSeconds;
        if (product.group.position.x > end) {
          const trailingX = Math.min(
            ...this.products
              .filter((candidate) => candidate !== product)
              .map((candidate) => candidate.group.position.x),
          );
          product.group.position.x = Math.min(start, trailingX - this.spacing);
          this.completed += 1;
        }
      }

      for (const roller of this.conveyor.dynamic.rollers) {
        roller.rotation.z -= (this.speed / 0.12) * deltaSeconds;
      }
      if (this.conveyor.dynamic.shaftPivot) {
        this.conveyor.dynamic.shaftPivot.rotation.x += 8 * deltaSeconds;
      }
      if (this.conveyor.dynamic.driveShaftPivot) {
        this.conveyor.dynamic.driveShaftPivot.rotation.z -=
          (this.speed / 0.12) * deltaSeconds;
      }
    }

    const sensorX = this.photoeye.group.position.x;
    this.blocked = this.products.some((product) => {
      const productWidth = product.dynamic.size[0];
      return Math.abs(product.group.position.x - sensorX) <= productWidth / 2;
    });
    setPhotoeyeState(this.photoeye, this.blocked);
    setIndicatorState(this.indicator, wasRunning ? "green" : "amber");
  }

  handleAction(actionId) {
    if (actionId === "conveyor_run") {
      if (!this.hasController()) {
        return "Controller disconnected — conveyor command ignored";
      }
      this.setRunning(!this.running);
      setEquipmentRunning(this.conveyor, this.running);
      setActionSwitches(this.registry, "conveyor_run", this.running);
      setIndicatorState(this.indicator, this.running ? "green" : "amber");
      return this.running ? "Conveyor started" : "Conveyor stopped";
    }
    return null;
  }

  getTags() {
    return this.declaredTags({
      conveyor_run: this.running,
      photoeye_blocked: this.blocked,
      conveyor_speed: this.running ? this.speed : 0,
      parts_completed: this.completed,
    });
  }
}

class ConveyorStopSimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    const config = scene.simulation;
    this.conveyor = entry(registry, config.conveyorId, "conveyor");
    this.photoeye = entry(registry, config.photoeyeId, "photoeye");
    this.product = entry(registry, config.productId, "box");
    this.indicator = entry(registry, config.indicatorId, "indicator");
    this.lengthM = config.lengthM ?? 1.0;
    this.speedMps = config.speedMps ?? 0.5;
    this.objectLengthM = config.objectLengthM ?? 0.2;
    this.photoeyePositionM = config.photoeyePositionM ?? 0.5;
    this.initialProductPosition = this.product.group.position.clone();
    this.leadingEdgeM = 0;
    this.objectPresent = true;
    this.blocked = false;
    this.conveyorRun = false;
    this.completed = 0;
    this.componentState = "stopped_loaded";
    this.reset();
  }

  reset() {
    super.reset();
    if (!this.product) {
      return;
    }
    this.leadingEdgeM = 0;
    this.objectPresent = true;
    this.blocked = false;
    this.conveyorRun = false;
    this.completed = 0;
    this.componentState = "stopped_loaded";
    this._projectState();
  }

  _isPhotoeyeBlocked() {
    if (!this.objectPresent) {
      return false;
    }
    const trailingEdgeM = this.leadingEdgeM - this.objectLengthM;
    return (
      trailingEdgeM <= this.photoeyePositionM &&
      this.photoeyePositionM <= this.leadingEdgeM
    );
  }

  _projectProduct() {
    this.product.group.visible = this.objectPresent;
    if (!this.objectPresent) {
      return;
    }
    const conveyorLength = this.conveyor.dynamic.length;
    const conveyorStart =
      this.conveyor.group.position.x - conveyorLength / 2 + 0.2;
    const visualTravel = conveyorLength - 0.4;
    const leadingFraction = THREE.MathUtils.clamp(
      this.leadingEdgeM / this.lengthM,
      0,
      1,
    );
    this.product.group.position.set(
      conveyorStart +
        leadingFraction * visualTravel -
        this.product.dynamic.size[0] / 2,
      this.initialProductPosition.y,
      this.initialProductPosition.z,
    );
  }

  _projectState() {
    this._projectProduct();
    setPhotoeyeState(this.photoeye, this.blocked);
    setEquipmentRunning(this.conveyor, this.conveyorRun);
    setActionSwitches(this.registry, "scene-toggle", this.running);
    const stoppedByLogic = [
      STOP_REASONS.SYSTEM,
      STOP_REASONS.START_BLOCKED,
    ].includes(this.stopReason);
    setIndicatorState(
      this.indicator,
      stoppedByLogic ? "red" : this.running ? "green" : "amber",
    );
  }

  getStartBlockReason() {
    const baseReason = super.getStartBlockReason();
    if (baseReason) {
      return baseReason;
    }
    if (this.blocked) {
      return "Start blocked — the stop photoeye is still blocked";
    }
    return null;
  }

  update(deltaSeconds) {
    const wasRunning = this.running;
    super.update(deltaSeconds);
    if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      this.conveyorRun = this.running && !this.blocked;
    } else if (this.controlSource === CONTROL_SOURCES.DISCONNECTED) {
      this.conveyorRun = false;
    }

    if (this.conveyorRun && this.objectPresent) {
      this.leadingEdgeM += this.speedMps * deltaSeconds;
      const trailingEdgeM = this.leadingEdgeM - this.objectLengthM;
      if (trailingEdgeM >= this.lengthM) {
        this.objectPresent = false;
        this.completed += 1;
      }
      animateConveyorDrive(this.conveyor, this.speedMps, deltaSeconds);
    }

    this.blocked = this._isPhotoeyeBlocked();
    if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      this.conveyorRun = this.running && !this.blocked;
    }
    if (
      this.controlSource === CONTROL_SOURCES.FAKE_PLC &&
      wasRunning &&
      this.running &&
      this.blocked
    ) {
      this.completeSystemStop(
        "System stop — package is blocking the stop photoeye",
      );
      this.conveyorRun = false;
    }
    this.componentState = this.objectPresent
      ? this.conveyorRun
        ? "running_loaded"
        : "stopped_loaded"
      : this.conveyorRun
        ? "running_empty"
        : "stopped_empty";
    this._projectState();
  }

  canHandleAction(actionId) {
    return (
      actionId === "scene-toggle" &&
      this.controlSource === CONTROL_SOURCES.FAKE_PLC
    );
  }

  handleAction(actionId) {
    if (actionId !== "scene-toggle") {
      return null;
    }
    if (this.controlSource === CONTROL_SOURCES.LIVE_PLC) {
      return "Use the player Stop control to hold the scene or Disconnect Real PLC to close the session";
    }
    if (!this.hasController()) {
      return "Controller disconnected — Scene 1 command ignored";
    }
    if (this.running) {
      this.setRunning(
        false,
        STOP_REASONS.OPERATOR,
        "Operator stop — Scene 1 held",
      );
      this.conveyorRun = false;
      this._projectState();
      return "Operator stop — Scene 1 held";
    }
    const started = this.setRunning(true);
    this._projectState();
    return started ? "Scene 1 start accepted" : this.getStatus().message;
  }

  setControllerPoint(name, value) {
    if (
      this.controlSource !== CONTROL_SOURCES.LIVE_PLC ||
      name !== "conveyor_running" ||
      typeof value !== "boolean"
    ) {
      return false;
    }
    this.conveyorRun = value;
    this._projectState();
    return true;
  }

  holdControllerSafe() {
    super.holdControllerSafe();
    this.conveyorRun = false;
    this._projectState();
    return true;
  }

  canSetControllerPoint(name) {
    return name === "conveyor_running";
  }

  getTags() {
    return this.declaredTags({
      conveyor_running: this.conveyorRun,
      simulated_photoeye: this.blocked,
      object_position: this.leadingEdgeM,
      component_state: this.componentState,
      parts_completed: this.completed,
    });
  }
}

class ConveyorPusherSimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    const config = scene.simulation;
    this.conveyor = entry(registry, config.conveyorId, "conveyor");
    this.photoeye = entry(registry, config.photoeyeId, "photoeye");
    this.product = entry(registry, config.productId, "box");
    this.pusher = entry(registry, config.pusherId, "pusher");
    this.indicator = entry(registry, config.indicatorId, "indicator");
    this.lengthM = config.lengthM ?? 1.0;
    this.speedMps = config.speedMps ?? 0.5;
    this.objectLengthM = config.objectLengthM ?? 0.2;
    this.photoeyePositionM = config.photoeyePositionM ?? 0.5;
    this.pusherStrokeTimeS = config.pusherStrokeTimeS ?? 0.3;
    this.transferPositionFraction =
      config.transferPositionFraction ?? 0.8;
    this.repeatLoadSeconds = config.repeatLoadSeconds ?? 2.5;
    if (
      !Number.isFinite(this.repeatLoadSeconds) ||
      this.repeatLoadSeconds < 0.05 ||
      this.repeatLoadSeconds > 3600
    ) {
      throw new Error(
        "conveyorPusher.repeatLoadSeconds must be from 0.05 to 3600 seconds.",
      );
    }
    this.initialProductPosition = this.product.group.position.clone();
    this.reset();
  }

  reset() {
    super.reset();
    if (!this.product) {
      return;
    }
    this.leadingEdgeM = 0;
    this.objectPresent = true;
    this.partAtPusher = false;
    this.pusherPosition = 0;
    this.pusherExtended = false;
    this.pusherRetracted = true;
    this.pusherExtend = false;
    this.conveyorRun = false;
    this.completed = 0;
    this.nextLoadAt = this.repeatLoadSeconds;
    this.componentState = "stopped_loaded";
    this._projectState();
  }

  _isPhotoeyeBlocked() {
    if (!this.objectPresent) {
      return false;
    }
    const trailingEdgeM = this.leadingEdgeM - this.objectLengthM;
    return (
      trailingEdgeM <= this.photoeyePositionM &&
      this.photoeyePositionM <= this.leadingEdgeM
    );
  }

  _evaluatePlcLogic() {
    if (!this.running) {
      this.pusherExtend = false;
      this.conveyorRun = false;
      return;
    }

    // Mirrors the proven Scene 2 ladder order: set, then reset, then conveyor
    // permissive. Reset intentionally wins if both limit conditions occur.
    if (this.partAtPusher && this.pusherRetracted) {
      this.pusherExtend = true;
    }
    if (this.pusherExtended) {
      this.pusherExtend = false;
    }
    this.conveyorRun =
      this.pusherRetracted &&
      !this.partAtPusher &&
      !this.pusherExtend;
  }

  _loadProductIfDue() {
    while (this.elapsed >= this.nextLoadAt) {
      if (!this.objectPresent) {
        this.objectPresent = true;
        this.leadingEdgeM = 0;
      }
      this.nextLoadAt += this.repeatLoadSeconds;
    }
  }

  _projectProduct() {
    this.product.group.visible = this.objectPresent;
    if (!this.objectPresent) {
      return;
    }
    const conveyorLength = this.conveyor.dynamic.length;
    const conveyorStart =
      this.conveyor.group.position.x - conveyorLength / 2 + 0.2;
    const visualTravel = conveyorLength - 0.4;
    const leadingFraction = THREE.MathUtils.clamp(
      this.leadingEdgeM / this.lengthM,
      0,
      1,
    );
    const pushedOffset =
      this.partAtPusher || this.pusherPosition > 0
        ? this.pusherPosition * this.pusher.dynamic.stroke
        : 0;
    this.product.group.position.set(
      conveyorStart +
        leadingFraction * visualTravel -
        this.product.dynamic.size[0] / 2,
      this.initialProductPosition.y,
      this.initialProductPosition.z + pushedOffset,
    );
  }

  _projectState() {
    this._projectProduct();
    setPhotoeyeState(this.photoeye, this.partAtPusher);
    setPusherPosition(this.pusher, this.pusherPosition);
    setEquipmentRunning(this.conveyor, this.conveyorRun);
    setActionSwitches(this.registry, "scene-toggle", this.running);
    setIndicatorState(
      this.indicator,
      this.running
        ? this.pusherExtend || this.pusherPosition > 0
          ? "amber"
          : "green"
        : "amber",
    );
  }

  update(deltaSeconds) {
    super.update(deltaSeconds);
    if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      this._evaluatePlcLogic();
    } else if (this.controlSource === CONTROL_SOURCES.DISCONNECTED) {
      this.conveyorRun = false;
      this.pusherExtend = false;
    }

    if (this.running) {
      if (this.conveyorRun && this.objectPresent) {
        this.leadingEdgeM += this.speedMps * deltaSeconds;
        animateConveyorDrive(this.conveyor, this.speedMps, deltaSeconds);
      }

      const previousPusherPosition = this.pusherPosition;
      const positionDelta = deltaSeconds / this.pusherStrokeTimeS;
      this.pusherPosition = this.pusherExtend
        ? Math.min(1, this.pusherPosition + positionDelta)
        : Math.max(0, this.pusherPosition - positionDelta);

      this.partAtPusher = this._isPhotoeyeBlocked();
      const crossedTransferPosition =
        this.pusherExtend &&
        previousPusherPosition < this.transferPositionFraction &&
        this.pusherPosition >= this.transferPositionFraction;
      if (
        crossedTransferPosition &&
        this.objectPresent &&
        this.partAtPusher
      ) {
        this.objectPresent = false;
        this.partAtPusher = false;
        this.completed += 1;
      }

      this.pusherExtended = this.pusherPosition >= 1 - 1e-9;
      this.pusherRetracted = this.pusherPosition <= 1e-9;
      this._loadProductIfDue();
      this.partAtPusher = this._isPhotoeyeBlocked();
      if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
        this._evaluatePlcLogic();
      }
    }

    this.componentState = this.pusherExtend && !this.pusherExtended
      ? "pushing"
      : this.pusherPosition > 0 && !this.pusherExtend
        ? "retracting"
        : this.pusherExtended
          ? "extended"
          : this.objectPresent
            ? this.conveyorRun
              ? "running_loaded"
              : "stopped_loaded"
            : this.conveyorRun
              ? "running_empty"
              : "stopped_empty";
    this._projectState();
  }

  canHandleAction(actionId) {
    return (
      actionId === "scene-toggle" &&
      this.controlSource === CONTROL_SOURCES.FAKE_PLC
    );
  }

  handleAction(actionId) {
    if (actionId !== "scene-toggle") {
      return null;
    }
    if (this.controlSource === CONTROL_SOURCES.LIVE_PLC) {
      return "Use the player Stop control to hold the scene or Disconnect Real PLC to close the session";
    }
    if (!this.hasController()) {
      return "Controller disconnected — Scene 2 command ignored";
    }
    if (this.running) {
      this.setRunning(
        false,
        STOP_REASONS.OPERATOR,
        "Operator stop — Scene 2 held",
      );
    } else {
      this.setRunning(true);
    }
    this._evaluatePlcLogic();
    this._projectState();
    return this.running ? "Scene 2 start accepted" : "Operator stop — Scene 2 held";
  }

  setControllerPoint(name, value) {
    if (
      this.controlSource !== CONTROL_SOURCES.LIVE_PLC ||
      typeof value !== "boolean"
    ) {
      return false;
    }
    if (name === "conveyor_running") {
      this.conveyorRun = value;
    } else if (name === "pusher_extend") {
      this.pusherExtend = value;
    } else {
      return false;
    }
    this._projectState();
    return true;
  }

  holdControllerSafe() {
    super.holdControllerSafe();
    this.conveyorRun = false;
    this.pusherExtend = false;
    this._projectState();
    return true;
  }

  canSetControllerPoint(name) {
    return ["conveyor_running", "pusher_extend"].includes(name);
  }

  getTags() {
    return this.declaredTags({
      part_at_pusher: this.partAtPusher,
      pusher_extended: this.pusherExtended,
      pusher_retracted: this.pusherRetracted,
      conveyor_running: this.conveyorRun,
      pusher_extend: this.pusherExtend,
      pusher_position: this.pusherPosition * 100,
      component_state: this.componentState,
      parts_completed: this.completed,
    });
  }
}

class TankSimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    const config = scene.simulation;
    this.tank = entry(registry, config.tankId, "tank");
    this.pump = entry(registry, config.pumpId, "pump");
    this.lowSensor = optionalEntry(
      registry,
      config.lowSensorId,
      "levelSensor",
    );
    this.highSensor = optionalEntry(
      registry,
      config.highSensorId,
      "levelSensor",
    );
    this.transmitter = optionalEntry(
      registry,
      config.transmitterId,
      ["levelSensor", "radarLevelSensor"],
    );
    this.indicator = entry(registry, config.indicatorId, "indicator");
    this.initialLevel = THREE.MathUtils.clamp(
      config.initialLevel ?? this.tank.dynamic.level,
      0,
      1,
    );
    this.inletRate = config.inletRatePerSecond ?? 0.055;
    this.outletRate = config.outletRatePerSecond ?? 0.035;
    this.lowThreshold = config.lowThreshold ?? 0.2;
    this.highThreshold = config.highThreshold ?? 0.8;
    this.pumpOn = false;
    this.drainOpen = false;
    this.level = this.initialLevel;
    this.lowActive = false;
    this.highActive = false;
    this.currentMa = 4;
    this.reset();
  }

  reset() {
    super.reset();
    if (!this.tank) {
      return;
    }
    this.level = this.initialLevel;
    this.pumpOn = false;
    this.drainOpen = false;
    this._projectState();
  }

  setRunning(running, reason, message) {
    const accepted = super.setRunning(running, reason, message);
    if (!running) {
      this.pumpOn = false;
      this.drainOpen = false;
    }
    this._projectState();
    return accepted;
  }

  update(deltaSeconds) {
    super.update(deltaSeconds);
    if (this.running) {
      const change =
        (this.pumpOn ? this.inletRate : 0) -
        (this.drainOpen ? this.outletRate : 0);
      this.level = THREE.MathUtils.clamp(
        this.level + change * deltaSeconds,
        0,
        1,
      );
    }

    if (this.pumpOn && this.running && this.pump.dynamic.shaftPivot) {
      this.pump.dynamic.shaftPivot.rotation.x += 10 * deltaSeconds;
    }
    this._projectState();
  }

  _projectState() {
    this.lowActive = this.level <= this.lowThreshold;
    this.highActive = this.level >= this.highThreshold;
    this.currentMa = 4 + 16 * this.level;
    setEquipmentRunning(this.pump, this.running && this.pumpOn);
    setActionSwitches(this.registry, "toggle-pump", this.pumpOn);
    setActionSwitches(this.registry, "toggle-drain", this.drainOpen);
    setTankLevel(this.tank, this.level);
    if (this.lowSensor) {
      setLevelSensorState(this.lowSensor, this.lowActive);
    }
    if (this.highSensor) {
      setLevelSensorState(this.highSensor, this.highActive);
    }
    if (this.transmitter?.definition.type === "radarLevelSensor") {
      setRadarLevelState(this.transmitter, this.level, this.tank);
    } else if (this.transmitter) {
      setLevelSensorState(this.transmitter, true, this.currentMa);
    }

    const alarmActive =
      (this.highSensor && this.highActive) ||
      (this.lowSensor && this.lowActive);
    const alarmColor = alarmActive ? "red" : "green";
    setIndicatorState(this.indicator, this.running ? alarmColor : "amber");
  }

  getActions() {
    return [
      {
        id: "toggle-pump",
        label: this.pumpOn ? "Stop inlet pump" : "Start inlet pump",
        active: this.pumpOn,
      },
      {
        id: "toggle-drain",
        label: this.drainOpen ? "Close drain valve" : "Open drain valve",
        active: this.drainOpen,
      },
    ];
  }

  handleAction(actionId) {
    if (!this.hasController()) {
      return "Controller disconnected — process command ignored";
    }
    if (actionId === "toggle-pump") {
      this.pumpOn = !this.pumpOn;
      this._projectState();
      return this.pumpOn ? "Inlet pump command on" : "Inlet pump command off";
    }
    if (actionId === "toggle-drain") {
      this.drainOpen = !this.drainOpen;
      this._projectState();
      return this.drainOpen ? "Drain valve opened" : "Drain valve closed";
    }
    return null;
  }

  getTags() {
    const values = {
      inlet_pump_run: this.pumpOn,
      drain_valve_open: this.drainOpen,
      tank_level: this.level * 100,
    };

    if (this.transmitter?.definition.type === "radarLevelSensor") {
      values.radar_level = this.level * 100;
      values.radar_distance = this.transmitter.dynamic.distanceM;
      values.radar_signal = this.transmitter.dynamic.currentMa;
      values.radar_echo_ok = true;
    } else if (this.transmitter) {
      values.level_transmitter = this.currentMa;
    }

    if (this.lowSensor) {
      values.low_level_switch = this.lowActive;
    }
    if (this.highSensor) {
      values.high_level_switch = this.highActive;
    }
    return this.declaredTags(values);
  }
}

class BooleanPanelSimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    const config = scene.simulation;
    this.config = config;
    this.pointDefinitions = (config.points ?? []).map((point) => ({
      type: "BOOL",
      owner: "SIM",
      initial: false,
      role: "input",
      ...point,
    }));
    if (this.pointDefinitions.length === 0) {
      throw new Error("Boolean-panel simulation requires at least one point.");
    }
    const pointNames = new Set();
    for (const point of this.pointDefinitions) {
      if (typeof point.name !== "string" || point.name.trim() === "") {
        throw new Error("Boolean-panel point names must be non-empty strings.");
      }
      if (pointNames.has(point.name)) {
        throw new Error(`Duplicate Boolean-panel point "${point.name}".`);
      }
      pointNames.add(point.name);
    }
    this.points = new Map();
    this.controllerOverrides = new Map();
    this.previousPoints = new Map();
    this.pulseRemaining = new Map();
    this.actions = (config.actions ?? []).map((action) => ({ ...action }));
    this.bindings = (config.pointBindings ?? []).map((binding) => ({
      ...binding,
      equipment: entry(registry, binding.equipmentId),
    }));
    this.reset();
  }

  reset() {
    super.reset();
    if (!this.pointDefinitions) {
      return;
    }
    this.controllerOverrides?.clear();
    this.previousPoints?.clear();
    this.pulseRemaining?.clear();
    this.points.clear();
    for (const point of this.pointDefinitions) {
      const value =
        point.owner === "PLC" && !this.hasController()
          ? safePointValue(point)
          : point.initial;
      this.points.set(point.name, value);
      this.previousPoints.set(point.name, value);
    }
    this._evaluate(false);
  }

  update(deltaSeconds) {
    super.update(deltaSeconds);
    let released = false;
    for (const [name, remaining] of [...this.pulseRemaining]) {
      const next = remaining - deltaSeconds;
      if (next > 0) {
        this.pulseRemaining.set(name, next);
        continue;
      }
      this.pulseRemaining.delete(name);
      this.points.set(name, false);
      released = true;
    }
    if (released) {
      this._evaluate();
    }
  }

  setRunning(running, reason, message) {
    return super.setRunning(running, reason, message);
  }

  _onControlSourceChanged(_previous, source) {
    this.running = false;
    this.controllerOverrides.clear();
    for (const point of this.pointDefinitions) {
      if (point.owner === "PLC") {
        this.points.set(
          point.name,
          source === CONTROL_SOURCES.FAKE_PLC
            ? point.initial
            : safePointValue(point),
        );
      }
      this.previousPoints.set(point.name, this.points.get(point.name));
    }
    this._evaluate(false);
  }

  _applyRuleValues(values, operation) {
    for (const [name, value] of Object.entries(values ?? {})) {
      if (!this.points.has(name)) {
        throw new Error(
          `Boolean-panel ${operation} writes unknown point "${name}".`,
        );
      }
      const point = this.pointDefinitions.find(
        (definition) => definition.name === name,
      );
      if (point?.owner === "PC") {
        throw new Error(
          `Fake PLC ${operation} may not write PC-owned point "${name}".`,
        );
      }
      this.points.set(name, value);
    }
  }

  _evaluate(detectEdges = true) {
    if (this.controlSource === CONTROL_SOURCES.DISCONNECTED) {
      for (const point of this.pointDefinitions) {
        if (point.owner === "PLC" || point.role === "output") {
          this.points.set(point.name, safePointValue(point));
        }
      }
    } else if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      for (const point of this.pointDefinitions) {
        if (point.role === "output") {
          this.points.set(point.name, point.initial);
        }
      }

      if (detectEdges) {
        for (const rule of this.config.edgeRules ?? []) {
          const inputName = rule.rising;
          const rising =
            Boolean(this.points.get(inputName)) &&
            !Boolean(this.previousPoints.get(inputName));
          if (!rising) {
            continue;
          }
          this._applyRuleValues(rule.set, "edge rule");
          for (const name of rule.toggle ?? []) {
            if (!this.points.has(name)) {
              throw new Error(
                `Boolean-panel edge rule toggles unknown point "${name}".`,
              );
            }
            const point = this.pointDefinitions.find(
              (definition) => definition.name === name,
            );
            if (point?.owner === "PC") {
              throw new Error(
                `Fake PLC edge rule may not toggle PC-owned point "${name}".`,
              );
            }
            this.points.set(name, !Boolean(this.points.get(name)));
          }
        }
      }

      const matchingRules = (this.config.rules ?? []).filter((rule) =>
        Object.entries(rule.when ?? {}).every(
          ([name, expected]) => this.points.get(name) === expected,
        ),
      );
      for (const rule of matchingRules) {
        this._applyRuleValues(rule.set, "rule");
      }
      for (const [name, value] of this.controllerOverrides) {
        this.points.set(name, value);
      }
    }
    this._projectBindings();
    for (const point of this.pointDefinitions) {
      if (
        point.owner === "PC" ||
        this.controlSource === CONTROL_SOURCES.FAKE_PLC
      ) {
        this.previousPoints.set(point.name, this.points.get(point.name));
      }
    }
  }

  _projectBindings() {
    const indicatorStates = new Map();
    for (const binding of this.bindings) {
      const value = this.points.get(binding.point);
      if (binding.mode === "indicator") {
        if (!indicatorStates.has(binding.equipment)) {
          indicatorStates.set(binding.equipment, binding.inactiveColor ?? null);
        }
        if (value) {
          indicatorStates.set(
            binding.equipment,
            binding.activeColor ?? "green",
          );
        }
      } else if (binding.mode === "running") {
        setEquipmentRunning(binding.equipment, Boolean(value));
      } else if (binding.mode === "switch") {
        setSwitchState(binding.equipment, Boolean(value));
      } else if (binding.mode === "selector") {
        setSelectorPosition(binding.equipment, Number(value));
      } else if (binding.mode === "position") {
        setAssetPosition(binding.equipment, Number(value));
      }
    }
    for (const [equipment, activeColor] of indicatorStates) {
      setIndicatorState(equipment, activeColor);
    }
  }

  getActions() {
    return this.actions.map((action) => {
      const value = this.points.get(action.point);
      const displayValue =
        action.type === "cycle"
          ? ` (${String(value)})`
          : "";
      return {
        id: action.id,
        label: `${action.label}${displayValue}`,
        active: action.type !== "cycle" && Boolean(value),
        enabled: this.canHandleAction(action.id),
      };
    });
  }

  canHandleAction(actionId) {
    const action = this.actions.find((candidate) => candidate.id === actionId);
    if (!action) {
      return false;
    }
    const point = this.pointDefinitions.find(
      (candidate) => candidate.name === action.point,
    );
    return point?.owner !== "PLC" || this.hasController();
  }

  handleAction(actionId) {
    const action = this.actions.find((candidate) => candidate.id === actionId);
    if (!action) {
      return null;
    }
    if (!this.points.has(action.point)) {
      throw new Error(`Action "${action.id}" references unknown point "${action.point}".`);
    }
    if (!this.canHandleAction(actionId)) {
      return "Controller disconnected — PLC output command ignored";
    }

    if (action.type === "toggle") {
      this.points.set(action.point, !Boolean(this.points.get(action.point)));
    } else if (action.type === "set") {
      this.points.set(action.point, action.value);
    } else if (action.type === "pulse") {
      if (Boolean(this.points.get(action.point))) {
        this.points.set(action.point, false);
        this.pulseRemaining.delete(action.point);
        this._evaluate();
      }
      this.points.set(action.point, true);
      this.pulseRemaining.set(
        action.point,
        Math.max(0.05, Number(action.durationS) || 0.15),
      );
    } else if (action.type === "cycle") {
      const values = action.values ?? [];
      if (values.length === 0) {
        throw new Error(`Cycle action "${action.id}" requires values.`);
      }
      const currentIndex = values.findIndex(
        (value) => value === this.points.get(action.point),
      );
      this.points.set(
        action.point,
        values[(currentIndex + 1 + values.length) % values.length],
      );
    } else {
      throw new Error(`Boolean-panel action type "${action.type}" is not supported.`);
    }

    this._evaluate();
    return action.message ?? `${action.label} operated`;
  }

  setControllerPoint(name, value) {
    if (!this.hasController()) {
      return false;
    }
    const point = this.pointDefinitions.find(
      (candidate) => candidate.name === name,
    );
    if (point?.owner !== "PLC") {
      return false;
    }
    if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      this.controllerOverrides.set(name, value);
    }
    this.points.set(name, value);
    this._projectBindings();
    return true;
  }

  canSetControllerPoint(name) {
    return this.pointDefinitions.some(
      (point) => point.name === name && point.owner === "PLC",
    );
  }

  clearControllerForces() {
    if (this.controlSource !== CONTROL_SOURCES.FAKE_PLC) {
      return false;
    }
    this.controllerOverrides.clear();
    this._evaluate();
    return true;
  }

  getTags() {
    return this.pointDefinitions
      .filter((point) => !point.hidden)
      .map((point) => ({
        name: point.name,
        type: point.type,
        value: this.points.get(point.name),
        unit: point.unit,
        owner: point.owner,
        forced: this.controllerOverrides.has(point.name),
      }));
  }
}

class SequenceSimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    this.config = scene.simulation;
    this.pointDefinitions = (this.config.points ?? []).map((point) => ({
      type: "BOOL",
      owner: "SIM",
      initial: false,
      ...point,
    }));
    this.points = new Map();
    this.controllerOverrides = new Map();
    this.actions = (this.config.actions ?? []).map((action) => ({ ...action }));
    this.sequences = this.config.sequences ?? {};
    this.defaultSequence =
      this.config.defaultSequence ?? Object.keys(this.sequences)[0] ?? null;
    if (!this.defaultSequence || !Array.isArray(this.sequences[this.defaultSequence])) {
      throw new Error("Sequence simulation requires a valid default sequence.");
    }
    this.bindings = (this.config.pointBindings ?? []).map((binding) => ({
      ...binding,
      equipment: entry(registry, binding.equipmentId),
    }));
    this.initialTransforms = new Map(
      [...registry.entries()].map(([id, equipment]) => [
        id,
        {
          position: equipment.group.position.clone(),
          rotation: equipment.group.rotation.clone(),
          visible: equipment.group.visible,
          assetPosition: equipment.dynamic?.position ?? null,
          tankLevel: equipment.dynamic?.level ?? null,
        },
      ]),
    );
    this.activeSequence = null;
    this.stepIndex = 0;
    this.stepElapsed = 0;
    this.reset();
  }

  reset() {
    super.reset();
    if (!this.pointDefinitions) {
      return;
    }
    this.activeSequence = null;
    this.stepIndex = 0;
    this.stepElapsed = 0;
    this.controllerOverrides?.clear();
    this.points.clear();
    for (const point of this.pointDefinitions) {
      const value =
        point.owner === "PLC" && this.controlSource !== CONTROL_SOURCES.FAKE_PLC
          ? safePointValue(point)
          : point.initial;
      this.points.set(point.name, value);
    }
    for (const [id, transform] of this.initialTransforms) {
      const equipment = this.registry.get(id);
      equipment.group.position.copy(transform.position);
      equipment.group.rotation.copy(transform.rotation);
      equipment.group.visible = transform.visible;
      if (transform.assetPosition !== null) {
        setAssetPosition(equipment, transform.assetPosition);
      }
      if (transform.tankLevel !== null) {
        setTankLevel(equipment, transform.tankLevel);
      }
      setEquipmentRunning(equipment, false);
    }
    this._projectBindings();
  }

  _startActionFor(sequenceId) {
    return this.actions.find(
      (action) =>
        action.type === "start" &&
        (action.sequence ?? this.defaultSequence) === sequenceId,
    ) ?? null;
  }

  getStartBlockReason(sequenceId = this.defaultSequence) {
    if (this.controlSource !== CONTROL_SOURCES.FAKE_PLC) {
      return "Reference sequence requires the explicit Fake PLC controller";
    }
    const action = this._startActionFor(sequenceId);
    const unmetRequirement = Object.entries(action?.requires ?? {}).find(
      ([name, expected]) => this.points.get(name) !== expected,
    );
    if (unmetRequirement) {
      const [name] = unmetRequirement;
      return action?.blockedMessage ?? `Start blocked by ${name}`;
    }
    return null;
  }

  setRunning(
    running,
    reason = STOP_REASONS.OPERATOR,
    message = "Operator stop — sequence held",
  ) {
    if (running) {
      if (this.activeSequence === null) {
        const blockedReason = this.getStartBlockReason(this.defaultSequence);
        if (blockedReason) {
          return this._rejectStart(blockedReason);
        }
        this._startSequence(this.defaultSequence);
      } else {
        this._acceptStart();
      }
      return true;
    }
    super.setRunning(false, reason, message);
    this.activeSequence = null;
    this.stepIndex = 0;
    this.stepElapsed = 0;
    this._applyState(this.config.safeState ?? {});
    return true;
  }

  _onControlSourceChanged() {
    this.reset();
  }

  _startSequence(sequenceId) {
    const steps = this.sequences[sequenceId];
    if (!Array.isArray(steps) || steps.length === 0) {
      throw new Error(`Sequence "${sequenceId}" is missing or empty.`);
    }
    this.activeSequence = sequenceId;
    this.stepIndex = 0;
    this.stepElapsed = 0;
    this.elapsed = 0;
    this._acceptStart();
    this._enterStep();
  }

  _currentStep() {
    return this.activeSequence === null
      ? null
      : this.sequences[this.activeSequence][this.stepIndex] ?? null;
  }

  _enterStep() {
    const step = this._currentStep();
    if (!step) {
      return;
    }
    this._applyState(step.set ?? {});
    this._projectMotions(step, 0);
  }

  _applyState(values) {
    for (const [name, value] of Object.entries(values)) {
      if (!this.points.has(name)) {
        throw new Error(`Sequence writes unknown point "${name}".`);
      }
      const point = this.pointDefinitions.find(
        (definition) => definition.name === name,
      );
      if (point?.owner === "PLC") {
        if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
          this.points.set(name, value);
        } else if (this.controlSource === CONTROL_SOURCES.DISCONNECTED) {
          this.points.set(name, safePointValue(point));
        }
      } else {
        this.points.set(name, value);
      }
    }
    if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      for (const [name, value] of this.controllerOverrides) {
        this.points.set(name, value);
      }
    }
    this._projectBindings();
  }

  _projectBindings() {
    const runningStates = new Map();
    for (const binding of this.bindings) {
      const value = this.points.get(binding.point);
      if (binding.mode === "running") {
        runningStates.set(
          binding.equipment,
          Boolean(value) || Boolean(runningStates.get(binding.equipment)),
        );
      } else if (binding.mode === "indicator") {
        const color =
          typeof value === "string"
            ? value
            : value
              ? binding.activeColor ?? "green"
              : binding.inactiveColor ?? null;
        setIndicatorState(binding.equipment, color);
      } else if (binding.mode === "switch") {
        setSwitchState(binding.equipment, Boolean(value));
      } else if (binding.mode === "selector") {
        setSelectorPosition(binding.equipment, Number(value));
      } else if (binding.mode === "photoeye") {
        setPhotoeyeState(binding.equipment, Boolean(value));
      } else if (binding.mode === "levelSensor") {
        setLevelSensorState(binding.equipment, Boolean(value));
      } else if (binding.mode === "position") {
        setAssetPosition(binding.equipment, Number(value));
      } else if (binding.mode === "tankLevel") {
        setTankLevel(binding.equipment, Number(value));
      } else if (binding.mode === "visibility") {
        binding.equipment.group.visible = Boolean(value);
      }
    }
    for (const [equipment, running] of runningStates) {
      setEquipmentRunning(equipment, running);
    }
  }

  _projectMotions(step, progress) {
    for (const motion of step.motions ?? []) {
      const equipment = entry(this.registry, motion.equipmentId);
      const value = THREE.MathUtils.lerp(motion.from ?? 0, motion.to ?? 1, progress);
      if (motion.type === "translate") {
        const axis = motion.axis ?? "x";
        if (!["x", "y", "z"].includes(axis)) {
          throw new Error(`Motion axis "${axis}" is not supported.`);
        }
        equipment.group.position[axis] = value;
      } else if (motion.type === "rotate") {
        const axis = motion.axis ?? "y";
        equipment.group.rotation[axis] = THREE.MathUtils.degToRad(value);
      } else if (motion.type === "position") {
        setAssetPosition(equipment, value);
      } else if (motion.type === "tankLevel") {
        setTankLevel(equipment, value);
      } else if (motion.type === "visibility") {
        equipment.group.visible = progress < 1 ? Boolean(motion.from) : Boolean(motion.to);
      } else {
        throw new Error(`Motion type "${motion.type}" is not supported.`);
      }
    }
  }

  _animateDrives(deltaSeconds) {
    for (const equipment of this.registry.values()) {
      const dynamic = equipment.dynamic;
      if (!dynamic?.running) {
        continue;
      }
      if (dynamic.kind === "conveyor") {
        animateConveyorDrive(equipment, this.config.conveyorSpeedMps ?? 0.75, deltaSeconds);
      } else if (["motor", "pump"].includes(dynamic.kind) && dynamic.shaftPivot) {
        dynamic.shaftPivot.rotation.x += 9 * deltaSeconds;
      } else if (dynamic.kind === "fan") {
        dynamic.bladePivot.rotation.z -= 8 * deltaSeconds;
      } else if (dynamic.kind === "drillPress") {
        dynamic.spindlePivot.rotation.y += 12 * deltaSeconds;
      } else if (dynamic.kind === "rollerShutter" && dynamic.shaftPivot) {
        dynamic.shaftPivot.rotation.x += 8 * deltaSeconds;
      }
    }
  }

  update(deltaSeconds) {
    super.update(deltaSeconds);
    this._animateDrives(deltaSeconds);
    if (!this.running || this.activeSequence === null) {
      return;
    }

    const step = this._currentStep();
    const duration = Math.max(0.05, Number(step.durationS) || 0.05);
    this.stepElapsed += deltaSeconds;
    const progress = THREE.MathUtils.clamp(this.stepElapsed / duration, 0, 1);
    this._projectMotions(step, progress);
    if (progress < 1) {
      return;
    }

    if (step.systemStop === true) {
      const stoppedSequence = this.activeSequence;
      this.activeSequence = null;
      this._applyState({
        ...(this.config.safeState ?? {}),
        ...(step.stopState ?? {}),
      });
      this.completeSystemStop(
        step.stopMessage ??
          `System stop — ${step.name ?? stoppedSequence} requested a stop`,
      );
      return;
    }

    this.stepIndex += 1;
    this.stepElapsed = 0;
    const steps = this.sequences[this.activeSequence];
    if (this.stepIndex < steps.length) {
      this._enterStep();
      return;
    }

    const completedSequence = this.activeSequence;
    if (this.config.loopSequences?.includes(completedSequence)) {
      this.stepIndex = 0;
      this._enterStep();
      return;
    }
    this.activeSequence = null;
    this._applyState(this.config.completionState ?? {});
    this.completeSystemStop(
      `Program complete — ${completedSequence} reached its final step`,
    );
  }

  getActions() {
    return this.actions.map((action) => ({
      id: action.id,
      label: action.label,
      active:
        action.type === "start" &&
        this.running &&
        this.activeSequence === (action.sequence ?? this.defaultSequence),
      enabled: this.canHandleAction(action.id),
    }));
  }

  canHandleAction(actionId) {
    const action = this.actions.find((candidate) => candidate.id === actionId);
    if (!action) {
      return false;
    }
    if (["start", "stop"].includes(action.type)) {
      return this.controlSource === CONTROL_SOURCES.FAKE_PLC;
    }
    if (action.type === "reset") {
      return true;
    }
    if (["togglePoint", "setPoint"].includes(action.type)) {
      const point = this.pointDefinitions.find(
        (candidate) => candidate.name === action.point,
      );
      return point?.owner !== "PLC" || this.hasController();
    }
    return false;
  }

  handleAction(actionId) {
    const action = this.actions.find((candidate) => candidate.id === actionId);
    if (!action) {
      return null;
    }
    if (!this.canHandleAction(actionId)) {
      return "Controller disconnected — reference sequence is disabled";
    }
    if (action.type === "start") {
      const sequenceId = action.sequence ?? this.defaultSequence;
      const blockedReason = this.getStartBlockReason(sequenceId);
      if (blockedReason) {
        this._rejectStart(blockedReason);
        return blockedReason;
      }
      this._startSequence(sequenceId);
    } else if (action.type === "stop") {
      this.setRunning(
        false,
        STOP_REASONS.OPERATOR,
        "Operator stop — sequence held",
      );
    } else if (action.type === "reset") {
      this.reset();
    } else if (action.type === "togglePoint") {
      if (!this.points.has(action.point)) {
        throw new Error(`Action "${action.id}" references unknown point "${action.point}".`);
      }
      this.points.set(action.point, !Boolean(this.points.get(action.point)));
      this._projectBindings();
    } else if (action.type === "setPoint") {
      if (!this.points.has(action.point)) {
        throw new Error(`Action "${action.id}" references unknown point "${action.point}".`);
      }
      this.points.set(action.point, action.value);
      this._projectBindings();
    } else {
      throw new Error(`Sequence action type "${action.type}" is not supported.`);
    }
    return action.message ?? `${action.label} operated`;
  }

  setControllerPoint(name, value) {
    if (!this.hasController()) {
      return false;
    }
    const point = this.pointDefinitions.find(
      (candidate) => candidate.name === name,
    );
    if (point?.owner !== "PLC") {
      return false;
    }
    if (this.controlSource === CONTROL_SOURCES.FAKE_PLC) {
      this.controllerOverrides.set(name, value);
    }
    this.points.set(name, value);
    this._projectBindings();
    return true;
  }

  canSetControllerPoint(name) {
    return this.pointDefinitions.some(
      (point) => point.name === name && point.owner === "PLC",
    );
  }

  clearControllerForces() {
    if (this.controlSource !== CONTROL_SOURCES.FAKE_PLC) {
      return false;
    }
    this.controllerOverrides.clear();
    for (const point of this.pointDefinitions) {
      if (point.owner === "PLC") {
        this.points.set(point.name, point.initial);
      }
    }
    const step = this._currentStep();
    if (step) {
      this._applyState(step.set ?? {});
    } else {
      this._projectBindings();
    }
    return true;
  }

  getStatus() {
    const status = super.getStatus();
    const step = this._currentStep();
    return {
      ...status,
      mode: this.running
        ? String(step?.name ?? this.activeSequence ?? "RUNNING").toUpperCase()
        : status.mode,
    };
  }

  getTags() {
    return this.pointDefinitions
      .filter((point) => !point.hidden)
      .map((point) => ({
        name: point.name,
        type: point.type,
        value: this.points.get(point.name),
        unit: point.unit,
        owner: point.owner,
        forced: this.controllerOverrides.has(point.name),
      }));
  }
}

class GallerySimulation extends BaseSimulation {
  constructor(scene, registry) {
    super(scene, registry);
    this.phase = 0;
    this.level = 0.5;
    this.estopLatched = false;
  }

  reset() {
    super.reset();
    this.phase = 0;
    this.level = 0.5;
    this.estopLatched = false;
    this._projectRunningState();
  }

  update(deltaSeconds) {
    super.update(deltaSeconds);
    this._projectRunningState();
    if (!this.running) {
      return;
    }
    this.phase += deltaSeconds;
    this.level = 0.5 + Math.sin(this.phase * 0.55) * 0.32;

    for (const equipment of this.registry.values()) {
      const dynamic = equipment.dynamic;
      if (!dynamic) {
        continue;
      }
      if (dynamic.kind === "motor" && dynamic.shaftPivot) {
        dynamic.shaftPivot.rotation.x += 7 * deltaSeconds;
      }
      if (dynamic.kind === "pump" && dynamic.shaftPivot) {
        dynamic.shaftPivot.rotation.x += 9 * deltaSeconds;
      }
      if (dynamic.kind === "conveyor") {
        for (const roller of dynamic.rollers) {
          roller.rotation.z -= 4 * deltaSeconds;
        }
        if (dynamic.shaftPivot) {
          dynamic.shaftPivot.rotation.x += 6 * deltaSeconds;
        }
        if (dynamic.driveShaftPivot) {
          dynamic.driveShaftPivot.rotation.z -= 4 * deltaSeconds;
        }
      }
      if (dynamic.kind === "fan") {
        dynamic.bladePivot.rotation.z -= 7 * deltaSeconds;
      }
      if (dynamic.kind === "drillPress") {
        dynamic.spindlePivot.rotation.y += 9 * deltaSeconds;
        setAssetPosition(equipment, 0.5 + Math.sin(this.phase) * 0.45);
      }
      if (dynamic.kind === "robotArm") {
        setAssetPosition(equipment, 0.5 + Math.sin(this.phase * 0.45) * 0.5);
      }
      if (dynamic.kind === "liftTable") {
        setAssetPosition(equipment, 0.5 + Math.sin(this.phase * 0.6) * 0.45);
      }
      if (dynamic.kind === "rollerShutter") {
        setAssetPosition(equipment, 0.55 + Math.sin(this.phase * 0.45) * 0.4);
      }
      if (dynamic.kind === "rotaryTable") {
        setAssetPosition(equipment, (this.phase * 0.08) % 1);
      }
      if (dynamic.kind === "valve") {
        setAssetPosition(equipment, 0.5 + Math.sin(this.phase * 0.5) * 0.5);
      }
      if (dynamic.kind === "tank") {
        setTankLevel(equipment, this.level);
      }
      if (dynamic.kind === "indicator") {
        const colors = [...dynamic.lenses.keys()];
        const active = colors[Math.floor(this.phase) % colors.length];
        setIndicatorState(equipment, active);
      }
      if (dynamic.kind === "levelSensor") {
        const active =
          dynamic.sensorType === "analog"
            ? true
            : dynamic.mode === "low"
              ? this.level <= dynamic.threshold
              : this.level >= dynamic.threshold;
        setLevelSensorState(equipment, active, 4 + 16 * this.level);
      }
    }
  }

  getStartBlockReason() {
    const baseReason = super.getStartBlockReason();
    if (baseReason) {
      return baseReason;
    }
    if (this.estopLatched) {
      return "Start blocked — emergency stop is latched";
    }
    return null;
  }

  setRunning(running, reason, message) {
    const accepted = super.setRunning(running, reason, message);
    this._projectRunningState();
    return accepted;
  }

  _projectRunningState() {
    for (const equipment of this.registry.values()) {
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
        ].includes(equipment.dynamic?.kind)
      ) {
        setEquipmentRunning(equipment, this.running);
      }
    }
    setActionSwitches(this.registry, "toggle-gallery", this.running);
    setActionSwitches(this.registry, "stop-all", this.estopLatched);
  }

  handleAction(actionId) {
    if (!this.hasController()) {
      return "Controller disconnected — gallery command ignored";
    }
    if (actionId === "toggle-gallery") {
      if (this.running) {
        this.setRunning(
          false,
          STOP_REASONS.OPERATOR,
          "Operator stop — gallery held",
        );
        return "Gallery equipment stopped";
      }
      const started = this.setRunning(true);
      return started ? "Gallery equipment started" : this.getStatus().message;
    }
    if (actionId === "stop-all") {
      this.estopLatched = !this.estopLatched;
      if (this.estopLatched) {
        this.setRunning(
          false,
          STOP_REASONS.INTERLOCK,
          "Interlock stop — emergency stop is latched",
        );
      } else {
        this.stopReason = STOP_REASONS.RESET;
        this.stopMessage = "Emergency stop reset — scene ready";
        this._projectRunningState();
      }
      return this.estopLatched
        ? "Emergency stop latched — all equipment stopped"
        : "Emergency stop reset";
    }
    return null;
  }

  getTags() {
    return this.declaredTags({
      gallery_animation: this.running,
      industrial_fan_run: this.running,
      emergency_stop: this.estopLatched,
      demo_tank_level: this.level * 100,
      demo_level_signal: 4 + 16 * this.level,
    });
  }
}

export function createSimulation(scene, registry) {
  switch (scene.simulation.type) {
    case "conveyor":
      return new ConveyorSimulation(scene, registry);
    case "conveyorStop":
      return new ConveyorStopSimulation(scene, registry);
    case "conveyorPusher":
      return new ConveyorPusherSimulation(scene, registry);
    case "tank":
      return new TankSimulation(scene, registry);
    case "gallery":
      return new GallerySimulation(scene, registry);
    case "booleanPanel":
      return new BooleanPanelSimulation(scene, registry);
    case "sequence":
      return new SequenceSimulation(scene, registry);
    case "static":
      return new BaseSimulation(scene, registry);
    default:
      throw new Error(
        `No simulation runtime exists for "${scene.simulation.type}".`,
      );
  }
}
