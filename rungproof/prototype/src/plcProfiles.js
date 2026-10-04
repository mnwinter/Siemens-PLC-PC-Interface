/**
 * Resolve the read-only PLC test profile explicitly referenced by a scene.
 *
 * Scene files choose a profile by local file name only. Physical addresses,
 * connection settings, and write policy remain in the external profile.
 */
export function resolveScenePlcProfile(scene, profiles) {
  const profileId = scene?.plcTestProfile;
  if (typeof profileId !== "string" || !profileId) {
    return {
      status: "not_configured",
      profile: null,
      profileId: null,
    };
  }
  const profile = (profiles ?? []).find(
    (candidate) => candidate.id === profileId,
  );
  if (!profile) {
    return { status: "unavailable", profile: null, profileId };
  }
  return profile.valid
    ? { status: "matched", profile }
    : { status: "invalid", profile, profileId };
}
