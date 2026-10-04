import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import { resolveScenePlcProfile } from "../prototype/src/plcProfiles.js";
import { validateSceneDocument } from "../prototype/src/sceneLoader.js";

const profiles = [
  {
    id: "scene-1-db14-interface.json",
    label: "Scene 1 DB14 Interface",
    valid: true,
    ip: "10.70.9.201",
    rack: 0,
    slot: 1,
    tagCount: 7,
  },
  {
    id: "scene-2-db14-pusher-interface.json",
    label: "Scene 2 DB14 Pusher Interface",
    valid: true,
    ip: "10.70.9.201",
    rack: 0,
    slot: 1,
    tagCount: 10,
  },
];

const sceneOneMatch = resolveScenePlcProfile(
  {
    id: "scene-1-conveyor-stop",
    plcTestProfile: "scene-1-db14-interface.json",
  },
  profiles,
);

assert.equal(sceneOneMatch.status, "matched");
assert.equal(sceneOneMatch.profile.id, "scene-1-db14-interface.json");

const sceneTwoMatch = resolveScenePlcProfile(
  {
    id: "scene-2-conveyor-pusher",
    plcTestProfile: "scene-2-db14-pusher-interface.json",
  },
  profiles,
);

assert.equal(sceneTwoMatch.status, "matched");
assert.equal(sceneTwoMatch.profile.id, "scene-2-db14-pusher-interface.json");

const labWithoutProfile = resolveScenePlcProfile(
  { id: "lab-2-01-workstation-call" },
  profiles,
);

assert.deepEqual(labWithoutProfile, {
  status: "not_configured",
  profile: null,
  profileId: null,
});

const invalidReferencedProfile = resolveScenePlcProfile(
  {
    id: "scene-1-conveyor-stop",
    plcTestProfile: "scene-1-db14-interface.json",
  },
  [
    {
      id: "scene-1-db14-interface.json",
      label: "Scene 1 DB14 Interface",
      valid: false,
      error: "Profile failed validation.",
    },
  ],
);

assert.equal(invalidReferencedProfile.status, "invalid");
assert.equal(invalidReferencedProfile.profile.error, "Profile failed validation.");

const sceneOne = validateSceneDocument(
  JSON.parse(
    await readFile(
      new URL(
        "../prototype/scenes/scene-1-conveyor-stop.plcscene",
        import.meta.url,
      ),
      "utf8",
    ),
  ),
);
const sceneTwo = validateSceneDocument(
  JSON.parse(
    await readFile(
      new URL(
        "../prototype/scenes/scene-2-conveyor-pusher.plcscene",
        import.meta.url,
      ),
      "utf8",
    ),
  ),
);

assert.equal(sceneOne.plcTestProfile, "scene-1-db14-interface.json");
assert.equal(
  sceneTwo.plcTestProfile,
  "scene-2-db14-pusher-interface.json",
);

const unsafeProfileReference = structuredClone(sceneOne);
unsafeProfileReference.plcTestProfile = "../outside-profile.json";
assert.throws(
  () => validateSceneDocument(unsafeProfileReference),
  /plcTestProfile must be one local JSON file name/,
);

console.log("SCENE_1_PROFILE_AUTO_SELECTED: PASS");
console.log("SCENE_2_PROFILE_AUTO_SELECTED: PASS");
console.log("UNCONFIGURED_SCENE_FAILS_CLOSED: PASS");
console.log("INVALID_REFERENCED_PROFILE_REJECTED: PASS");
console.log("BUILTIN_SCENE_PROFILE_REFERENCES: PASS");
console.log("UNSAFE_PROFILE_REFERENCE_REJECTED: PASS");
