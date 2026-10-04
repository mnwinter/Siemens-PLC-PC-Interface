import { STOP_REASONS } from "./simulations.js";

export const ALARM_SEVERITIES = Object.freeze({
  WARNING: "warning",
  ALARM: "alarm",
  FAULT: "fault",
});

const SEVERITY_RANK = Object.freeze({
  [ALARM_SEVERITIES.WARNING]: 1,
  [ALARM_SEVERITIES.ALARM]: 2,
  [ALARM_SEVERITIES.FAULT]: 3,
});

function compareValues(actual, operator, expected) {
  switch (operator) {
    case "isTrue":
      return actual === true;
    case "isFalse":
      return actual === false;
    case "eq":
      return actual === expected;
    case "neq":
      return actual !== expected;
    case "gt":
      return typeof actual === "number" && actual > expected;
    case "gte":
      return typeof actual === "number" && actual >= expected;
    case "lt":
      return typeof actual === "number" && actual < expected;
    case "lte":
      return typeof actual === "number" && actual <= expected;
    default:
      return false;
  }
}

function runtimeConditions(status) {
  const conditions = [];
  const message = String(status?.message ?? "");

  if (status?.stopReason === STOP_REASONS.INTERLOCK) {
    conditions.push({
      key: "runtime:interlock-stop",
      code: "INTERLOCK",
      severity: ALARM_SEVERITIES.FAULT,
      message: message || "Machine interlock is active",
      check: "Reset the physical or simulated interlock before requesting Start.",
      source: "runtime",
    });
  }

  if (status?.stopReason === STOP_REASONS.START_BLOCKED) {
    conditions.push({
      key: "runtime:start-blocked",
      code: "START BLOCKED",
      severity: ALARM_SEVERITIES.WARNING,
      message: message || "Start request rejected by an active permissive",
      check: "Open the scene points and find the permissive that is not satisfied.",
      source: "runtime",
    });
  }

  if (
    status?.stopReason === STOP_REASONS.SYSTEM &&
    !message.toLowerCase().startsWith("program complete")
  ) {
    conditions.push({
      key: "runtime:system-stop",
      code: "SYSTEM STOP",
      severity: ALARM_SEVERITIES.ALARM,
      message: message || "Scene logic requested a system stop",
      check: "Inspect the active scene condition before resetting or restarting.",
      source: "runtime",
    });
  }

  return conditions;
}

function ruleConditions(scene, tags) {
  const values = new Map(tags.map((tag) => [tag.name, tag.value]));
  return (scene.alarmRules ?? [])
    .filter((rule) =>
      compareValues(values.get(rule.point), rule.operator, rule.value),
    )
    .map((rule) => ({
      key: `rule:${rule.id}`,
      code: rule.id,
      severity: rule.severity,
      message: rule.message,
      check: rule.check,
      source: rule.point,
    }));
}

function cloneRecord(record) {
  return { ...record };
}

export class SceneAlarmManager {
  constructor(scene, now = () => Date.now()) {
    this.sceneId = scene.id;
    this.sceneName = scene.name;
    this.scene = scene;
    this.now = now;
    this.activeRecords = new Map();
    this.history = [];
    this.revision = 0;
    this.sequence = 0;
  }

  _timestamp() {
    return new Date(this.now()).toISOString();
  }

  observe(status, tags = []) {
    const conditions = [
      ...runtimeConditions(status),
      ...ruleConditions(this.scene, tags),
    ];
    const nextKeys = new Set(conditions.map((condition) => condition.key));
    let changed = false;

    for (const condition of conditions) {
      const existing = this.activeRecords.get(condition.key);
      if (existing) {
        if (
          existing.message !== condition.message ||
          existing.check !== condition.check ||
          existing.severity !== condition.severity
        ) {
          existing.message = condition.message;
          existing.check = condition.check;
          existing.severity = condition.severity;
          changed = true;
        }
        continue;
      }

      const record = {
        instanceId: `${condition.key}:${++this.sequence}`,
        ...condition,
        active: true,
        acknowledged: false,
        raisedAt: this._timestamp(),
        clearedAt: null,
      };
      this.activeRecords.set(condition.key, record);
      this.history.unshift(record);
      changed = true;
    }

    for (const [key, record] of this.activeRecords) {
      if (nextKeys.has(key)) {
        continue;
      }
      record.active = false;
      record.clearedAt = this._timestamp();
      this.activeRecords.delete(key);
      changed = true;
    }

    if (this.history.length > 100) {
      this.history = this.history.slice(0, 100);
    }
    if (changed) {
      this.revision += 1;
    }
    return this.getSnapshot();
  }

  acknowledgeActive() {
    let changed = false;
    for (const record of this.activeRecords.values()) {
      if (!record.acknowledged) {
        record.acknowledged = true;
        changed = true;
      }
    }
    if (changed) {
      this.revision += 1;
    }
    return changed;
  }

  clearHistory() {
    const retained = this.history.filter((record) => record.active);
    const changed = retained.length !== this.history.length;
    this.history = retained;
    if (changed) {
      this.revision += 1;
    }
    return changed;
  }

  getSnapshot() {
    const active = [...this.activeRecords.values()]
      .sort(
        (left, right) =>
          SEVERITY_RANK[right.severity] - SEVERITY_RANK[left.severity],
      )
      .map(cloneRecord);
    const highestSeverity = active.reduce(
      (highest, record) =>
        SEVERITY_RANK[record.severity] > SEVERITY_RANK[highest]
          ? record.severity
          : highest,
      ALARM_SEVERITIES.WARNING,
    );

    return {
      sceneId: this.sceneId,
      sceneName: this.sceneName,
      revision: this.revision,
      activeCount: active.length,
      unacknowledgedCount: active.filter((record) => !record.acknowledged)
        .length,
      highestSeverity:
        active.length === 0 ? null : highestSeverity,
      active,
      history: this.history.map(cloneRecord),
    };
  }
}
