import assert from "node:assert/strict";
import test from "node:test";

import {
  escapeHtml,
  symbolicName,
} from "../prototype/src/safeMarkup.js";

test("scene-controlled markup is encoded as inert text", () => {
  const malicious = `<img src=x onerror="globalThis.compromised=true">'&`;
  assert.equal(
    escapeHtml(malicious),
    "&lt;img src=x onerror=&quot;globalThis.compromised=true&quot;&gt;&#039;&amp;",
  );
  assert.equal(escapeHtml(42), "42");
});

test("symbolic names reject markup and whitespace", () => {
  assert.equal(symbolicName("Motor_1.Run"), "Motor_1.Run");
  assert.throws(() => symbolicName(`<img onerror=x>`), /must start/);
  assert.throws(() => symbolicName("motor run"), /must start/);
});

