import test from "node:test";
import assert from "node:assert/strict";

import {
  LivePlcBinding,
  getLivePlcReadiness,
} from "../prototype/src/livePlcBinding.js";

test("live PLC readiness requires heartbeat and PLC simulation status", () => {
  assert.deepEqual(getLivePlcReadiness(null), {
    ready: false,
    label: "DISCONNECTED",
  });
  assert.deepEqual(
    getLivePlcReadiness({
      health: "starting",
      plcStatus: {},
    }),
    { ready: false, label: "STARTING" },
  );
  assert.deepEqual(
    getLivePlcReadiness({
      health: "healthy",
      plcStatus: {
        simulation_enable: false,
        simulation_comm_ok: true,
        simulation_timeout: false,
      },
    }),
    { ready: false, label: "SIMULATION DISABLED" },
  );
  assert.deepEqual(
    getLivePlcReadiness({
      health: "healthy",
      plcStatus: {
        simulation_enable: true,
        simulation_comm_ok: false,
        simulation_timeout: false,
      },
    }),
    { ready: false, label: "PLC COMM NOT OK" },
  );
  assert.deepEqual(
    getLivePlcReadiness({
      health: "healthy",
      plcStatus: {
        simulation_enable: true,
        simulation_comm_ok: true,
        simulation_timeout: false,
      },
    }),
    { ready: true, label: "HEALTHY" },
  );
  assert.deepEqual(
    getLivePlcReadiness({
      health: "healthy",
      plcStatus: {
        simulation_enable: true,
        simulation_comm_ok: true,
      },
    }),
    { ready: false, label: "PLC STATUS INCOMPLETE" },
  );
});

test("guarded browser binding sends PC points and applies PLC points", async () => {
  const requests = [];
  const applied = [];
  const postJson = async (path, payload, options) => {
    requests.push({ path, payload, options });
    if (path.endsWith("/connect")) {
      return {
        sessionId: "session-one",
        sceneId: "scene-2-conveyor-pusher",
        cycleMs: 20,
        connected: true,
      };
    }
    if (path.endsWith("/cycle")) {
      return {
        sessionId: "session-one",
        sceneId: "scene-2-conveyor-pusher",
        connected: true,
        health: "healthy",
        plcPoints: {
          conveyor_running: true,
          pusher_extend: false,
        },
        plcStatus: {
          simulation_enable: true,
          simulation_comm_ok: true,
          simulation_timeout: false,
        },
      };
    }
    throw new Error(`Unexpected path ${path}`);
  };
  const binding = new LivePlcBinding({
    postJson,
    applyPlcPoint: (name, value) => {
      applied.push([name, value]);
      return true;
    },
    holdControllerSafe: () => {},
  });

  await binding.connect({
    profileId: "scene-2-db14-pusher-interface.json",
    sceneId: "scene-2-conveyor-pusher",
    authorizedWriteScope: [{ name: "pc_heartbeat", address: "DB14.DBD2" }],
  });
  const result = await binding.step({
    sceneId: "scene-2-conveyor-pusher",
    tags: [
      { name: "part_at_pusher", owner: "PC", value: true },
      { name: "conveyor_running", owner: "PLC", value: false },
      { name: "parts_completed", owner: "SIM", value: 0 },
    ],
  });

  assert.equal(result.health, "healthy");
  assert.deepEqual(
    requests[1].payload.pcPoints,
    { part_at_pusher: true },
  );
  assert.deepEqual(applied, [
    ["conveyor_running", true],
    ["pusher_extend", false],
  ]);
  assert.equal(
    requests[1].options.headers["X-PLC-Live-Mode"],
    "guarded-write",
  );
});

test("starting or PLC-disabled cycles never apply command outputs", async () => {
  const applied = [];
  let safeHoldCount = 0;
  let cycleNumber = 0;
  const binding = new LivePlcBinding({
    postJson: async (path) => {
      if (path.endsWith("/connect")) {
        return {
          sessionId: "session-one",
          sceneId: "scene-2-conveyor-pusher",
          connected: true,
          cycleMs: 20,
        };
      }
      cycleNumber += 1;
      return {
        connected: true,
        health: cycleNumber === 1 ? "starting" : "healthy",
        plcPoints: { conveyor_running: true },
        plcStatus:
          cycleNumber === 1
            ? {}
            : {
                simulation_enable: false,
                simulation_comm_ok: true,
                simulation_timeout: false,
              },
      };
    },
    applyPlcPoint: (name, value) => {
      applied.push([name, value]);
      return true;
    },
    holdControllerSafe: () => {
      safeHoldCount += 1;
    },
  });
  await binding.connect({
    profileId: "scene-2-db14-pusher-interface.json",
    sceneId: "scene-2-conveyor-pusher",
    authorizedWriteScope: [],
  });

  await binding.step({
    sceneId: "scene-2-conveyor-pusher",
    tags: [],
  });
  await binding.step({
    sceneId: "scene-2-conveyor-pusher",
    tags: [],
  });

  assert.deepEqual(applied, []);
  assert.equal(safeHoldCount, 0);
  assert.equal(binding.connected, true);
  assert.deepEqual(getLivePlcReadiness(binding.snapshot), {
    ready: false,
    label: "SIMULATION DISABLED",
  });
});

test("losing PLC readiness clears previously applied command outputs", async () => {
  const applied = [];
  let safeHoldCount = 0;
  let cycleNumber = 0;
  const binding = new LivePlcBinding({
    postJson: async (path) => {
      if (path.endsWith("/connect")) {
        return {
          sessionId: "session-one",
          sceneId: "scene-2-conveyor-pusher",
          connected: true,
          cycleMs: 20,
        };
      }
      cycleNumber += 1;
      return {
        connected: true,
        health: "healthy",
        plcPoints: { conveyor_running: true },
        plcStatus: {
          simulation_enable: cycleNumber === 1,
          simulation_comm_ok: true,
          simulation_timeout: false,
        },
      };
    },
    applyPlcPoint: (name, value) => {
      applied.push([name, value]);
      return true;
    },
    holdControllerSafe: () => {
      safeHoldCount += 1;
    },
  });
  await binding.connect({
    profileId: "scene-2-db14-pusher-interface.json",
    sceneId: "scene-2-conveyor-pusher",
    authorizedWriteScope: [],
  });

  await binding.step({
    sceneId: "scene-2-conveyor-pusher",
    tags: [],
  });
  await binding.step({
    sceneId: "scene-2-conveyor-pusher",
    tags: [],
  });

  assert.deepEqual(applied, [["conveyor_running", true]]);
  assert.equal(safeHoldCount, 1);
  assert.equal(binding.connected, true);
  assert.deepEqual(getLivePlcReadiness(binding.snapshot), {
    ready: false,
    label: "SIMULATION DISABLED",
  });
});

test("a cycle finishing after disconnect cannot apply stale PLC outputs", async () => {
  let resolveCycle;
  const applied = [];
  const postJson = async (path) => {
    if (path.endsWith("/connect")) {
      return {
        sessionId: "session-one",
        sceneId: "scene-2-conveyor-pusher",
        connected: true,
        cycleMs: 20,
      };
    }
    if (path.endsWith("/disconnect")) {
      return { connected: false, closed: true };
    }
    return new Promise((resolve) => {
      resolveCycle = resolve;
    });
  };
  const binding = new LivePlcBinding({
    postJson,
    applyPlcPoint: (name, value) => {
      applied.push([name, value]);
      return true;
    },
    holdControllerSafe: () => {},
  });
  await binding.connect({
    profileId: "scene-2-db14-pusher-interface.json",
    sceneId: "scene-2-conveyor-pusher",
    authorizedWriteScope: [],
  });

  const pending = binding.step({
    sceneId: "scene-2-conveyor-pusher",
    tags: [],
  });
  await binding.disconnect();
  resolveCycle({
    connected: true,
    health: "healthy",
    plcPoints: { conveyor_running: true },
    plcStatus: {},
  });
  await pending;

  assert.deepEqual(applied, []);
  assert.equal(binding.connected, false);
});

test("a faulted cycle closes without applying returned PLC outputs", async () => {
  const applied = [];
  const statuses = [];
  const postJson = async (path) => {
    if (path.endsWith("/connect")) {
      return {
        sessionId: "session-one",
        sceneId: "scene-2-conveyor-pusher",
        connected: true,
        cycleMs: 20,
      };
    }
    if (path.endsWith("/cycle")) {
      return {
        connected: false,
        closedReason: "PLC cycle health fault",
        health: "fault",
        plcPoints: { conveyor_running: true },
        plcStatus: {},
      };
    }
    throw new Error(`Unexpected path ${path}`);
  };
  const binding = new LivePlcBinding({
    postJson,
    applyPlcPoint: (name, value) => {
      applied.push([name, value]);
      return true;
    },
    holdControllerSafe: () => {},
    onStatus: (status) => statuses.push(status),
  });
  await binding.connect({
    profileId: "scene-2-db14-pusher-interface.json",
    sceneId: "scene-2-conveyor-pusher",
    authorizedWriteScope: [],
  });

  await assert.rejects(
    binding.step({
      sceneId: "scene-2-conveyor-pusher",
      tags: [],
    }),
    /PLC cycle health fault/,
  );

  assert.deepEqual(applied, []);
  assert.equal(binding.connected, false);
  assert.equal(statuses.at(-1), null);
});
