/**
 * Transactionally stage a scene before replacing the active plant session.
 *
 * The implementation deliberately accepts its renderer/runtime dependencies
 * as arguments. That keeps the lifecycle rule deterministic and testable
 * without importing Three.js.
 */
export function stageSceneSession({
  scene,
  factory,
  createRoot,
  createSimulation,
  createAlarmManager,
  disposeRoot,
}) {
  const root = createRoot();
  const registry = new Map();

  try {
    for (const definition of scene.equipment) {
      const group = factory.create(definition);
      root.add(group);
      registry.set(definition.id, {
        definition,
        group,
        dynamic: group.userData.dynamic ?? null,
      });
    }

    const simulation = createSimulation(scene, registry);
    const alarmManager = createAlarmManager(scene);
    return Object.freeze({
      scene,
      root,
      registry,
      simulation,
      alarmManager,
    });
  } catch (error) {
    disposeRoot(root);
    throw error;
  }
}

