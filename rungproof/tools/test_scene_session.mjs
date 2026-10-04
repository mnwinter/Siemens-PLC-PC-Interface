import assert from "node:assert/strict";
import test from "node:test";

import { stageSceneSession } from "../prototype/src/sceneSession.js";

function fakeGroup(id = "root") {
  return {
    id,
    children: [],
    userData: {},
    add(child) {
      this.children.push(child);
    },
  };
}

test("failed runtime construction disposes staging and leaves ownership outside", () => {
  const disposed = [];
  const activeRoot = fakeGroup("active");

  assert.throws(
    () =>
      stageSceneSession({
        scene: {
          equipment: [{ id: "motor-1" }],
        },
        factory: {
          create: (definition) => fakeGroup(definition.id),
        },
        createRoot: () => fakeGroup("staging"),
        createSimulation: () => {
          throw new Error("invalid runtime graph");
        },
        createAlarmManager: () => ({}),
        disposeRoot: (root) => disposed.push(root.id),
      }),
    /invalid runtime graph/,
  );

  assert.deepEqual(disposed, ["staging"]);
  assert.deepEqual(activeRoot.children, []);
});

test("successful staging returns a complete session without side effects", () => {
  const session = stageSceneSession({
    scene: {
      equipment: [{ id: "motor-1", type: "motor" }],
    },
    factory: {
      create: (definition) => {
        const group = fakeGroup(definition.id);
        group.userData.dynamic = { kind: definition.type };
        return group;
      },
    },
    createRoot: () => fakeGroup("staging"),
    createSimulation: (_scene, registry) => ({ count: registry.size }),
    createAlarmManager: () => ({ active: 0 }),
    disposeRoot: () => assert.fail("successful staging must not dispose"),
  });

  assert.equal(session.registry.size, 1);
  assert.equal(session.simulation.count, 1);
  assert.equal(session.root.children.length, 1);
});
