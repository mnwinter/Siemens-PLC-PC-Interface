const LIVE_HEADERS = Object.freeze({
  "X-PLC-Live-Mode": "guarded-write",
});

function requireObject(value, label) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${label} must be an object.`);
  }
  return value;
}

function collectPcPoints(tags) {
  const values = {};
  for (const tag of tags ?? []) {
    if (tag?.owner !== "PC") {
      continue;
    }
    if (
      typeof tag.name !== "string" ||
      !["boolean", "number"].includes(typeof tag.value)
    ) {
      throw new Error("Live PLC feedback points must be named BOOL/number values.");
    }
    values[tag.name] = tag.value;
  }
  return values;
}

export function getLivePlcReadiness(snapshot) {
  if (!snapshot) {
    return { ready: false, label: "DISCONNECTED" };
  }
  const health = String(snapshot.health ?? "unknown")
    .replaceAll("_", " ")
    .toUpperCase();
  if (health !== "HEALTHY") {
    return { ready: false, label: health };
  }
  const status = snapshot.plcStatus ?? {};
  if (
    typeof status.simulation_enable !== "boolean" ||
    typeof status.simulation_comm_ok !== "boolean" ||
    typeof status.simulation_timeout !== "boolean"
  ) {
    return { ready: false, label: "PLC STATUS INCOMPLETE" };
  }
  if (status.simulation_timeout === true) {
    return { ready: false, label: "PLC TIMEOUT" };
  }
  if (status.simulation_enable !== true) {
    return { ready: false, label: "SIMULATION DISABLED" };
  }
  if (status.simulation_comm_ok !== true) {
    return { ready: false, label: "PLC COMM NOT OK" };
  }
  return { ready: true, label: "HEALTHY" };
}

export class LivePlcBinding {
  constructor({
    postJson,
    applyPlcPoint,
    holdControllerSafe,
    onStatus = () => {},
  }) {
    if (
      typeof postJson !== "function" ||
      typeof applyPlcPoint !== "function" ||
      typeof holdControllerSafe !== "function"
    ) {
      throw new Error(
        "LivePlcBinding requires postJson, applyPlcPoint, and holdControllerSafe.",
      );
    }
    this.postJson = postJson;
    this.applyPlcPoint = applyPlcPoint;
    this.holdControllerSafe = holdControllerSafe;
    this.onStatus = onStatus;
    this.session = null;
    this.generation = 0;
    this.inFlight = false;
  }

  get connected() {
    return this.session !== null;
  }

  get cycleMs() {
    return this.session?.cycleMs ?? 20;
  }

  get snapshot() {
    return this.session ? { ...this.session } : null;
  }

  async connect({
    profileId,
    sceneId,
    authorizedWriteScope,
  }) {
    if (this.connected) {
      throw new Error("A live PLC session is already connected.");
    }
    const generation = ++this.generation;
    const result = requireObject(
      await this.postJson(
        "/api/plc/live/connect",
        {
          profileId,
          sceneId,
          execute: true,
          authorizedWriteScope,
        },
        { headers: LIVE_HEADERS },
      ),
      "Live PLC connect response",
    );
    if (
      generation !== this.generation ||
      result.connected !== true ||
      typeof result.sessionId !== "string" ||
      result.sceneId !== sceneId
    ) {
      throw new Error("Live PLC connect response was invalid or stale.");
    }
    this.session = {
      sessionId: result.sessionId,
      sceneId,
      profileId,
      cycleMs: Math.max(20, Number(result.cycleMs) || 20),
      health: "starting",
      plcStatus: {},
    };
    this.onStatus(this.snapshot);
    return result;
  }

  async step({ sceneId, tags }) {
    if (!this.session) {
      throw new Error("No live PLC session is connected.");
    }
    if (this.inFlight) {
      return null;
    }
    if (sceneId !== this.session.sceneId) {
      await this.disconnect();
      throw new Error("Scene changed during live PLC exchange.");
    }

    const generation = this.generation;
    const sessionId = this.session.sessionId;
    this.inFlight = true;
    try {
      const result = requireObject(
        await this.postJson(
          "/api/plc/live/cycle",
          {
            sessionId,
            sceneId,
            pcPoints: collectPcPoints(tags),
          },
          { headers: LIVE_HEADERS },
        ),
        "Live PLC cycle response",
      );
      if (
        generation !== this.generation ||
        !this.session ||
        sessionId !== this.session.sessionId
      ) {
        return null;
      }
      const wasReady = getLivePlcReadiness(this.session).ready;
      if (result.connected === false) {
        if (wasReady) {
          this.holdControllerSafe({
            ready: false,
            label: String(result.health ?? "FAULT").toUpperCase(),
          });
        }
        this.session = null;
        this.generation += 1;
        this.onStatus(null);
        throw new Error(
          result.closedReason ?? "Guarded PLC session closed on a cycle fault.",
        );
      }
      const plcPoints = requireObject(
        result.plcPoints,
        "Live PLC output points",
      );
      const plcStatus = requireObject(
        result.plcStatus ?? {},
        "Live PLC status",
      );
      this.session.health = String(result.health ?? "unknown");
      this.session.plcStatus = plcStatus;
      this.onStatus(this.snapshot);
      const readiness = getLivePlcReadiness(this.session);
      if (!readiness.ready) {
        if (wasReady) {
          this.holdControllerSafe(readiness);
        }
        return result;
      }
      for (const [name, value] of Object.entries(plcPoints)) {
        if (!this.applyPlcPoint(name, value)) {
          await this.disconnect();
          throw new Error(
            `Scene rejected configured PLC output point "${name}".`,
          );
        }
      }
      return result;
    } finally {
      this.inFlight = false;
    }
  }

  async disconnect({ keepalive = false } = {}) {
    const session = this.session;
    this.session = null;
    this.generation += 1;
    this.onStatus(null);
    if (!session) {
      return { connected: false, closed: false };
    }
    return this.postJson(
      "/api/plc/live/disconnect",
      { sessionId: session.sessionId },
      {
        headers: LIVE_HEADERS,
        keepalive,
      },
    );
  }
}
