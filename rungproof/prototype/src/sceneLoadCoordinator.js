/**
 * Coordinates asynchronous scene loads.
 *
 * Interface guarantee: only the most recently started request can commit UI
 * state. Starting a newer request aborts the prior fetch when supported.
 */
export class SceneLoadCoordinator {
  constructor() {
    this.generation = 0;
    this.controller = null;
  }

  begin() {
    this.controller?.abort();
    this.controller = new AbortController();
    const generation = ++this.generation;
    return Object.freeze({
      generation,
      signal: this.controller.signal,
      isCurrent: () =>
        generation === this.generation && !this.controller.signal.aborted,
    });
  }

  isCurrent(request) {
    return request?.generation === this.generation && request.isCurrent();
  }
}

