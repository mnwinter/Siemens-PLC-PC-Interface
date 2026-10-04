import assert from "node:assert/strict";
import test from "node:test";

import { SceneLoadCoordinator } from "../prototype/src/sceneLoadCoordinator.js";

test("only the newest scene load can commit", async () => {
  const coordinator = new SceneLoadCoordinator();
  const first = coordinator.begin();
  const second = coordinator.begin();

  assert.equal(first.signal.aborted, true);
  assert.equal(first.isCurrent(), false);
  assert.equal(coordinator.isCurrent(first), false);
  assert.equal(second.signal.aborted, false);
  assert.equal(coordinator.isCurrent(second), true);
});

