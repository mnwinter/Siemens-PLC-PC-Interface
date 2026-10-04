import assert from "node:assert/strict";
import test from "node:test";

import {
  ASSET_BUILDER_TYPES,
} from "../prototype/src/assetFactory.js";
import {
  ASSET_CATALOG,
  EQUIPMENT_TYPES,
} from "../prototype/src/equipmentCatalog.js";

test("authoring catalog, validator, and 3D builders expose the same types", () => {
  const catalogTypes = ASSET_CATALOG.map((item) => item.type).sort();
  const validatorTypes = [...EQUIPMENT_TYPES].sort();
  const builderTypes = [...ASSET_BUILDER_TYPES].sort();

  assert.deepEqual(validatorTypes, catalogTypes);
  assert.deepEqual(builderTypes, catalogTypes);
});
