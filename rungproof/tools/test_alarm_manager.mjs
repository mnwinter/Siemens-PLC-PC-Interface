import { SceneAlarmManager } from "../prototype/src/alarmManager.js";
import { validateSceneDocument } from "../prototype/src/sceneLoader.js";
import { STOP_REASONS } from "../prototype/src/simulations.js";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

let clockMs = Date.parse("2026-07-30T18:00:00.000Z");
const now = () => {
  clockMs += 1000;
  return clockMs;
};

const scene = validateSceneDocument({
  fileType: "plc-visual-scene",
  version: 1,
  id: "alarm-test-scene",
  name: "Alarm test scene",
  equipment: [
    {
      id: "test_motor",
      type: "motor",
      position: [0, 0, 0],
    },
  ],
  simulation: {
    type: "static",
    points: [
      {
        name: "motor_overload",
        type: "BOOL",
        owner: "SIM",
        initial: false,
      },
    ],
  },
  alarmRules: [
    {
      id: "MOTOR_OVERLOAD",
      severity: "fault",
      point: "motor_overload",
      operator: "isTrue",
      message: "Motor overload relay is tripped",
      check: "Check the overload relay and motor current.",
    },
  ],
});

const manager = new SceneAlarmManager(scene, now);
const resetStatus = {
  running: false,
  stopReason: STOP_REASONS.RESET,
  message: "Scene reset and ready",
};

manager.observe(resetStatus, [{ name: "motor_overload", value: false }]);
assert(
  manager.getSnapshot().activeCount === 0,
  "A reset scene must begin with no active alarms.",
);

const systemStopStatus = {
  running: false,
  stopReason: STOP_REASONS.SYSTEM,
  message: "System stop — package is blocking the stop photoeye",
};
manager.observe(systemStopStatus, [{ name: "motor_overload", value: false }]);
manager.observe(systemStopStatus, [{ name: "motor_overload", value: false }]);
let snapshot = manager.getSnapshot();
assert(
  snapshot.activeCount === 1 &&
    snapshot.history.length === 1 &&
    snapshot.active[0].code === "SYSTEM STOP",
  "One persistent system stop must create one active alarm cycle.",
);
console.log("SYSTEM_STOP_ALARM: PASS");

assert(
  manager.acknowledgeActive() &&
    manager.getSnapshot().unacknowledgedCount === 0,
  "Acknowledging an active alarm must change only its local acknowledgement state.",
);
console.log("LOCAL_ACKNOWLEDGEMENT: PASS");

manager.observe(resetStatus, [{ name: "motor_overload", value: false }]);
snapshot = manager.getSnapshot();
assert(
  snapshot.activeCount === 0 &&
    snapshot.history.length === 1 &&
    snapshot.history[0].active === false &&
    snapshot.history[0].clearedAt !== null,
  "Clearing the machine condition must retain a cleared history record.",
);
console.log("CLEARED_HISTORY_RETAINED: PASS");

manager.observe(
  {
    running: false,
    stopReason: STOP_REASONS.START_BLOCKED,
    message: "Start blocked — guard input is open",
  },
  [{ name: "motor_overload", value: false }],
);
snapshot = manager.getSnapshot();
assert(
  snapshot.activeCount === 1 &&
    snapshot.active[0].severity === "warning" &&
    snapshot.active[0].code === "START BLOCKED",
  "A rejected start must raise an active warning.",
);
console.log("START_BLOCKED_WARNING: PASS");

manager.observe(resetStatus, [{ name: "motor_overload", value: true }]);
snapshot = manager.getSnapshot();
assert(
  snapshot.activeCount === 1 &&
    snapshot.active[0].severity === "fault" &&
    snapshot.active[0].code === "MOTOR_OVERLOAD",
  "A declarative point rule must raise its configured scene fault.",
);
console.log("DECLARATIVE_POINT_FAULT: PASS");

manager.clearHistory();
snapshot = manager.getSnapshot();
assert(
  snapshot.history.length === 1 &&
    snapshot.history[0].code === "MOTOR_OVERLOAD" &&
    snapshot.history[0].active,
  "Clearing history must never remove an active alarm.",
);
console.log("ACTIVE_ALARM_NOT_CLEARED: PASS");

manager.observe(
  {
    running: false,
    stopReason: STOP_REASONS.INTERLOCK,
    message: "Interlock stop — emergency stop is latched",
  },
  [{ name: "motor_overload", value: false }],
);
snapshot = manager.getSnapshot();
assert(
  snapshot.active.some(
    (record) => record.code === "INTERLOCK" && record.severity === "fault",
  ),
  "A latched interlock must raise a fault.",
);
console.log("INTERLOCK_FAULT: PASS");

manager.observe(
  {
    running: false,
    stopReason: STOP_REASONS.SYSTEM,
    message: "Program complete — sequence reached its final step",
  },
  [{ name: "motor_overload", value: false }],
);
snapshot = manager.getSnapshot();
assert(
  snapshot.activeCount === 0,
  "Normal program completion must not be reported as a fault or alarm.",
);
console.log("PROGRAM_COMPLETE_NOT_ALARM: PASS");
console.log("PLC_CONNECTION_ATTEMPTED: FALSE");
