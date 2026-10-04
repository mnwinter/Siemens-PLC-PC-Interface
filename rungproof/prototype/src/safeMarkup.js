/**
 * Encode untrusted values before interpolating them into an HTML template.
 *
 * Prefer `textContent` when creating a single DOM node. This helper exists for
 * the table/dialog templates that are intentionally rendered as one fragment.
 */
export function escapeHtml(value) {
  const replacements = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(value).replace(
    /[&<>"']/g,
    (character) => replacements[character],
  );
}

export function symbolicName(value, path = "name") {
  const name = String(value ?? "").trim();
  if (!/^[A-Za-z][A-Za-z0-9_.:-]{0,127}$/.test(name)) {
    throw new Error(
      `${path} must start with a letter and contain only letters, digits, _, ., :, or -.`,
    );
  }
  return name;
}

