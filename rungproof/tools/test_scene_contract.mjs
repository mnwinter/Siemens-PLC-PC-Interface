import assert from "node:assert/strict";
import test from "node:test";

import {
  loadSceneFromFile,
  MAX_SCENE_FILE_BYTES,
  validateSceneDocument,
} from "../prototype/src/sceneLoader.js";

function validScene() {
  return {
    fileType: "plc-visual-scene",
    version: 1,
    id: "contract_test",
    name: "Contract test",
    equipment: [
      {
        id: "fan_1",
        type: "fan",
        config: { diameter: 1.4, bladeCount: 6 },
      },
      {
        id: "lamp_1",
        type: "indicator",
        config: { colors: ["red", "green"], active: null },
      },
    ],
    simulation: {
      type: "booleanPanel",
      points: [
        {
          name: "fan_run",
          type: "BOOL",
          owner: "PLC",
          initial: false,
        },
      ],
      actions: [
        {
          id: "toggle_fan",
          label: "Toggle fan",
          type: "toggle",
          point: "fan_run",
        },
      ],
      pointBindings: [
        {
          point: "fan_run",
          equipmentId: "fan_1",
          mode: "running",
        },
      ],
      rules: [],
    },
  };
}

test("asset allocations are type checked and bounded before rendering", () => {
  const scene = validScene();
  scene.equipment[0].config.bladeCount = 1_000_000_000;
  assert.throws(
    () => validateSceneDocument(scene),
    /bladeCount must be from 2 to 24/,
  );

  const wrongType = validScene();
  wrongType.equipment[0].config.bladeCount = "six";
  assert.throws(
    () => validateSceneDocument(wrongType),
    /bladeCount must be a finite number/,
  );
});

test("runtime point writes and equipment references are validated eagerly", () => {
  const wrongWrite = validScene();
  wrongWrite.simulation.rules = [
    { when: { fan_run: false }, set: { fan_run: "not-a-bool" } },
  ];
  assert.throws(
    () => validateSceneDocument(wrongWrite),
    /must be a boolean for fan_run/,
  );

  const missingEquipment = validScene();
  missingEquipment.simulation.pointBindings[0].equipmentId = "missing_fan";
  assert.throws(
    () => validateSceneDocument(missingEquipment),
    /references missing equipment/,
  );
});

test("markup is accepted as text only where text is allowed, never as an id", () => {
  const textScene = validScene();
  textScene.name = `<img src=x onerror="alert(1)">`;
  assert.equal(validateSceneDocument(textScene).name, textScene.name);

  const idScene = validScene();
  idScene.equipment[0].id = `<img onerror=x>`;
  assert.throws(() => validateSceneDocument(idScene), /must start with a letter/);
});

test("portable scene files are size-gated before reading or parsing", async () => {
  let readAttempted = false;
  const oversized = {
    name: "oversized.plcscene",
    size: MAX_SCENE_FILE_BYTES + 1,
    async text() {
      readAttempted = true;
      return JSON.stringify(validScene());
    },
  };

  await assert.rejects(
    loadSceneFromFile(oversized),
    /exceeds the .* scene limit/,
  );
  assert.equal(readAttempted, false);
});

test("conveyor pusher repeat interval cannot create a non-terminating loop", () => {
  const scene = validScene();
  scene.simulation.type = "conveyorPusher";
  scene.simulation.repeatLoadSeconds = 0;

  assert.throws(
    () => validateSceneDocument(scene),
    /repeatLoadSeconds must be from 0.05 to 3600 seconds/,
  );
});
