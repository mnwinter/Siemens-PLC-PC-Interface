import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const playerSource = await readFile(
  new URL("../prototype/src/player.js", import.meta.url),
  "utf8",
);
const stylesSource = await readFile(
  new URL("../prototype/styles.css", import.meta.url),
  "utf8",
);

test("the application menu is consolidated into the product header", () => {
  const brandStart = playerSource.indexOf("function brandMarkup");
  const menuStart = playerSource.indexOf("function applicationMenuMarkup");
  const shellStart = playerSource.indexOf("function renderShell");
  const shellEnd = playerSource.indexOf("function formatTagValue");

  assert.ok(brandStart >= 0 && menuStart > brandStart);
  assert.match(
    playerSource.slice(brandStart, menuStart),
    /\$\{applicationMenuMarkup\(variantId\)\}/,
  );
  assert.doesNotMatch(
    playerSource.slice(shellStart, shellEnd),
    /applicationMenuMarkup/,
  );
  assert.doesNotMatch(playerSource, /class="application-title"/);
  assert.doesNotMatch(
    stylesSource,
    /grid-template-rows:\s*34px\s+minmax\(0,\s*1fr\)\s+68px/,
  );
});

test("the player exposes guarded real PLC controls and lifecycle hooks", () => {
  assert.match(playerSource, /id="plc-live-button"/);
  assert.match(playerSource, /data-player-command="toggle-live-plc"/);
  assert.match(playerSource, /data-live-plc-connect/);
  assert.match(playerSource, /new LivePlcBinding/);
  assert.match(playerSource, /async _cycleLivePlc\(\)/);
  assert.match(playerSource, /window\.addEventListener\("pagehide"/);
  assert.match(playerSource, /Scene changed — real PLC session disconnected/);
});

test("Stop and Reset preserve an intentional real PLC connection", () => {
  const stopStart = playerSource.indexOf('if (command === "stop")');
  const resetStart = playerSource.indexOf('if (command === "reset")');
  const loopStart = playerSource.indexOf('if (command === "toggle-loop")');
  const stopBranch = playerSource.slice(stopStart, resetStart);
  const resetBranch = playerSource.slice(resetStart, loopStart);

  assert.ok(stopStart >= 0 && resetStart > stopStart && loopStart > resetStart);
  assert.match(stopBranch, /simulation\?\.setRunning/);
  assert.doesNotMatch(stopBranch, /_disconnectLivePlc/);
  assert.match(stopBranch, /real PLC remains connected/i);
  assert.match(resetBranch, /simulation\?\.reset/);
  assert.doesNotMatch(resetBranch, /_disconnectLivePlc/);
  assert.match(resetBranch, /real PLC remains connected/i);
});

test("Run is disabled while a live PLC session is not ready", () => {
  assert.match(
    playerSource,
    /runButton\.disabled\s*=\s*livePlc\s*&&\s*!liveReadiness\.ready/,
  );
  assert.match(
    playerSource,
    /hudRunButton\.disabled\s*=\s*livePlc\s*&&\s*!liveReadiness\.ready/,
  );
});
