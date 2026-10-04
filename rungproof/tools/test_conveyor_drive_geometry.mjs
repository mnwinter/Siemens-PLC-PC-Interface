import assert from "node:assert/strict";
import test from "node:test";

import * as THREE from "../vendor/three/three.module.min.js";
import { AssetFactory } from "../prototype/src/assetFactory.js";

function worldPosition(object) {
  return object.getWorldPosition(new THREE.Vector3());
}

function assertAligned(actual, expected, axis, message) {
  assert.ok(
    Math.abs(actual[axis] - expected[axis]) < 1e-9,
    `${message}: ${axis} differs (${actual[axis]} versus ${expected[axis]}).`,
  );
}

test("conveyor gearmotor is mounted on the discharge drive-roller axis", () => {
  const factory = new AssetFactory();
  const conveyor = factory.create({
    id: "geometry_test_conveyor",
    type: "conveyor",
    label: "Geometry test conveyor",
    position: [0, 0, 0],
    rotation: [0, 0, 0],
    scale: [1, 1, 1],
    config: {
      length: 7,
      width: 1.5,
      deckHeight: 0.9,
      running: false,
    },
  });
  conveyor.updateMatrixWorld(true);

  const dynamic = conveyor.userData.dynamic;
  const assembly = dynamic.driveAssembly;
  assert.equal(assembly.type, "direct-head-drive");
  assert.equal(assembly.driveEnd, "discharge");
  assert.equal(assembly.shaftAxis, "z");
  assert.equal(assembly.driveRoller, dynamic.rollers.at(-1));
  assert.ok(assembly.couplingGuard, "The rotating coupling must be guarded.");
  assert.ok(assembly.mountingBracket, "The gearbox must be frame-supported.");

  const driveRoller = worldPosition(assembly.driveRoller);
  const driveShaft = worldPosition(dynamic.driveShaftPivot);
  const gearbox = worldPosition(assembly.gearbox);
  const motorShaft = worldPosition(assembly.motor.userData.shaftPivot);

  for (const component of [driveShaft, gearbox, motorShaft]) {
    assertAligned(component, driveRoller, "x", "Drive component is not at the end roller");
    assertAligned(component, driveRoller, "y", "Drive component is not on the roller centerline");
  }

  assert.equal(driveRoller.x, dynamic.length / 2);
  assert.ok(
    gearbox.z > dynamic.width / 2,
    "The gearbox should be mounted outside the conveyor side frame.",
  );
  assert.ok(
    assembly.motor.position.z > assembly.gearbox.position.z,
    "The motor should extend outward from the side-mounted gearbox.",
  );
});
