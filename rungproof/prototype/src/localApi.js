let sessionPromise = null;

async function getSessionToken() {
  if (sessionPromise === null) {
    sessionPromise = fetch("/api/session", { cache: "no-store" })
      .then(async (response) => {
        const payload = await response.json();
        if (!response.ok || typeof payload.token !== "string") {
          throw new Error(payload.error ?? "Local application session failed.");
        }
        return payload.token;
      })
      .catch((error) => {
        sessionPromise = null;
        throw error;
      });
  }
  return sessionPromise;
}

export async function postLocal(
  path,
  {
    body = "{}",
    contentType = "application/json",
    headers = {},
    keepalive = false,
  } = {},
) {
  const token = await getSessionToken();
  return fetch(path, {
    method: "POST",
    cache: "no-store",
    keepalive,
    headers: {
      "Content-Type": contentType,
      "X-RungProof-Token": token,
      ...headers,
    },
    body,
  });
}

export function postLocalJson(path, payload, options = {}) {
  return postLocal(path, {
    ...options,
    body: JSON.stringify(payload),
    contentType: "application/json",
  });
}

