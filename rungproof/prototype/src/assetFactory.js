import * as THREE from "../../vendor/three/three.module.min.js";

const COLORS = Object.freeze({
  steel: 0x5e6b73,
  darkSteel: 0x26343c,
  lightSteel: 0xaab7bd,
  safetyYellow: 0xf2b705,
  safetyOrange: 0xf58220,
  motorBlue: 0x176b87,
  belt: 0x273238,
  box: 0xc88a4b,
  sensorBlue: 0x2e8bd1,
  red: 0xe03c31,
  amber: 0xf2a900,
  green: 0x21a366,
  cyan: 0x38bdf8,
  fluid: 0x1597d4,
});

function material(color, options = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: options.roughness ?? 0.55,
    metalness: options.metalness ?? 0.25,
    transparent: options.transparent ?? false,
    opacity: options.opacity ?? 1,
    emissive: options.emissive ?? 0x000000,
    emissiveIntensity: options.emissiveIntensity ?? 0,
    side: options.side ?? THREE.FrontSide,
    depthWrite: options.depthWrite ?? true,
  });
}

function mesh(geometry, meshMaterial, { cast = true, receive = true } = {}) {
  const result = new THREE.Mesh(geometry, meshMaterial);
  result.castShadow = cast;
  result.receiveShadow = receive;
  return result;
}

function box(size, color, options = {}) {
  return mesh(
    new THREE.BoxGeometry(size[0], size[1], size[2]),
    material(color, options),
  );
}

function cylinder(radiusTop, radiusBottom, height, color, options = {}) {
  return mesh(
    new THREE.CylinderGeometry(radiusTop, radiusBottom, height, 32),
    material(color, options),
  );
}

function setTransform(group, definition) {
  group.position.fromArray(definition.position);
  group.rotation.set(
    THREE.MathUtils.degToRad(definition.rotation[0]),
    THREE.MathUtils.degToRad(definition.rotation[1]),
    THREE.MathUtils.degToRad(definition.rotation[2]),
  );
  group.scale.fromArray(definition.scale);
}

function tagForPicking(group, definition) {
  group.name = definition.label;
  group.userData.equipmentId = definition.id;
  group.userData.equipmentType = definition.type;
  group.userData.definition = definition;
  group.traverse((child) => {
    if (child.isMesh) {
      child.userData.pickRoot = group;
    }
  });
  return group;
}

function createRunLamp(parent, position, initialRunning = false) {
  const bezel = cylinder(0.12, 0.135, 0.065, COLORS.darkSteel, {
    metalness: 0.7,
    roughness: 0.25,
  });
  bezel.position.copy(position);
  parent.add(bezel);

  const lensMaterial = material(initialRunning ? COLORS.green : 0x17362d, {
    emissive: COLORS.green,
    emissiveIntensity: initialRunning ? 2.3 : 0.03,
    roughness: 0.2,
    metalness: 0.02,
  });
  const lens = mesh(new THREE.SphereGeometry(0.095, 20, 12), lensMaterial);
  lens.scale.y = 0.55;
  lens.position.copy(position);
  lens.position.y += 0.055;
  parent.add(lens);
  return lens;
}

function createShaftPivotX(parent, position, length, radius) {
  const pivot = new THREE.Group();
  pivot.position.copy(position);

  const shaft = cylinder(radius, radius, length, COLORS.lightSteel, {
    metalness: 0.9,
    roughness: 0.18,
  });
  shaft.rotation.z = Math.PI / 2;
  pivot.add(shaft);

  // The yellow key is offset from shaft center, so rotation is visible.
  const key = box([length * 0.72, radius * 0.32, radius * 0.28], COLORS.safetyYellow, {
    metalness: 0.25,
    roughness: 0.34,
  });
  key.position.y = radius * 0.82;
  pivot.add(key);
  parent.add(pivot);
  return pivot;
}

function createShaftPivotZ(parent, position, length, radius) {
  const pivot = new THREE.Group();
  pivot.position.copy(position);

  const shaft = cylinder(radius, radius, length, COLORS.lightSteel, {
    metalness: 0.9,
    roughness: 0.18,
  });
  shaft.rotation.x = Math.PI / 2;
  pivot.add(shaft);

  // The offset key makes rotation about the conveyor roller's Z axis visible.
  const key = box([radius * 0.28, radius * 0.32, length * 0.72], COLORS.safetyYellow, {
    metalness: 0.25,
    roughness: 0.34,
  });
  key.position.x = radius * 0.82;
  pivot.add(key);
  parent.add(pivot);
  return pivot;
}

function createMotorBody(config = {}) {
  const group = new THREE.Group();
  const length = config.length ?? 1.35;
  const diameter = config.diameter ?? 0.72;
  const initialRunning = Boolean(config.running);

  const body = cylinder(
    diameter / 2,
    diameter / 2,
    length,
    config.color ?? COLORS.motorBlue,
    { metalness: 0.4, roughness: 0.38 },
  );
  body.rotation.z = Math.PI / 2;
  body.position.y = diameter / 2 + 0.16;
  group.add(body);

  const runBandMaterial = material(
    initialRunning ? COLORS.green : 0x17362d,
    {
      emissive: COLORS.green,
      emissiveIntensity: initialRunning ? 1.8 : 0.02,
      metalness: 0.25,
      roughness: 0.25,
    },
  );
  const runBand = mesh(
    new THREE.TorusGeometry(diameter * 0.515, 0.035, 10, 40),
    runBandMaterial,
  );
  runBand.rotation.y = Math.PI / 2;
  runBand.position.set(-length * 0.18, body.position.y, 0);
  group.add(runBand);

  for (const x of [-length / 2 + 0.08, length / 2 - 0.08]) {
    const endBell = cylinder(
      diameter * 0.43,
      diameter * 0.43,
      0.13,
      COLORS.darkSteel,
      { metalness: 0.55 },
    );
    endBell.rotation.z = Math.PI / 2;
    endBell.position.set(x, body.position.y, 0);
    group.add(endBell);
  }

  const shaftPivot = createShaftPivotX(
    group,
    new THREE.Vector3(length / 2 + 0.18, body.position.y, 0),
    0.36,
    0.09,
  );

  const terminal = box([0.42, 0.24, 0.34], COLORS.darkSteel, {
    metalness: 0.35,
  });
  terminal.position.set(-0.1, diameter + 0.18, 0);
  group.add(terminal);
  const runLamp = createRunLamp(
    group,
    new THREE.Vector3(-0.1, diameter + 0.32, 0),
    initialRunning,
  );

  if (config.mountFeet !== false) {
    for (const z of [-diameter * 0.3, diameter * 0.3]) {
      const foot = box([length * 0.72, 0.16, 0.18], COLORS.darkSteel, {
        metalness: 0.55,
      });
      foot.position.set(0, 0.08, z);
      group.add(foot);
    }
  }

  group.userData.shaftPivot = shaftPivot;
  group.userData.runLamp = runLamp;
  group.userData.runBand = runBand;
  return group;
}

function createMotor(definition) {
  const group = createMotorBody(definition.config);
  group.userData.dynamic = {
    kind: "motor",
    shaftPivot: group.userData.shaftPivot,
    runLamp: group.userData.runLamp,
    runBand: group.userData.runBand,
    running: Boolean(definition.config.running),
  };
  return group;
}

function createConveyor(definition) {
  const config = definition.config;
  const length = config.length ?? 7;
  const width = config.width ?? 1.5;
  const deckHeight = config.deckHeight ?? 0.9;
  const beltThickness = 0.18;
  const group = new THREE.Group();

  const belt = box([length, beltThickness, width], config.beltColor ?? COLORS.belt, {
    metalness: 0.05,
    roughness: 0.86,
  });
  belt.position.y = deckHeight;
  group.add(belt);

  for (const z of [-width / 2 - 0.09, width / 2 + 0.09]) {
    const rail = box([length + 0.18, 0.22, 0.14], COLORS.steel, {
      metalness: 0.65,
      roughness: 0.3,
    });
    rail.position.set(0, deckHeight - 0.02, z);
    group.add(rail);
  }

  const rollers = [];
  const rollerCount = Math.max(6, Math.round(length / 0.55));
  for (let index = 0; index <= rollerCount; index += 1) {
    const isDriveRoller = index === rollerCount;
    const rollerRadius = isDriveRoller ? 0.14 : 0.12;
    const rollerPivot = new THREE.Group();
    rollerPivot.position.set(
      -length / 2 + (length * index) / rollerCount,
      deckHeight - 0.03,
      0,
    );
    const roller = cylinder(
      rollerRadius,
      rollerRadius,
      width,
      isDriveRoller ? COLORS.darkSteel : COLORS.lightSteel,
      {
        metalness: 0.7,
        roughness: 0.28,
      },
    );
    roller.rotation.x = Math.PI / 2;
    rollerPivot.add(roller);

    // A dark witness stripe makes correct rotation around the roller's Z axis
    // visible without changing the physical roller orientation.
    const witness = box([0.025, 0.025, width * 0.94], COLORS.darkSteel, {
      metalness: 0.4,
      roughness: 0.4,
    });
    witness.position.y = rollerRadius - 0.01;
    rollerPivot.add(witness);
    group.add(rollerPivot);
    rollers.push(rollerPivot);
  }

  const legX = [-length * 0.38, length * 0.38];
  for (const x of legX) {
    for (const z of [-width * 0.42, width * 0.42]) {
      const leg = box([0.16, deckHeight, 0.16], COLORS.darkSteel, {
        metalness: 0.6,
      });
      leg.position.set(x, deckHeight / 2 - 0.08, z);
      group.add(leg);
      const foot = box([0.42, 0.08, 0.32], COLORS.steel, { metalness: 0.6 });
      foot.position.set(x, 0.04, z);
      group.add(foot);
    }
  }

  // Real conveyor head drives place the gearmotor on the end roller's shaft.
  // This is a compact direct head-drive arrangement: drive roller -> keyed
  // shaft -> bearing/flange -> gearbox -> motor, all on the same Z axis.
  const driveRoller = rollers.at(-1);
  const driveEndX = length / 2;
  const shaftCenterY = deckHeight - 0.03;
  const railOuterZ = width / 2 + 0.16;
  const gearboxDepth = 0.42;
  const gearboxCenterZ = railOuterZ + gearboxDepth / 2 + 0.05;

  const driveShaftLength =
    gearboxCenterZ - gearboxDepth / 2 - width / 2 + 0.12;
  const driveShaftPivot = createShaftPivotZ(
    group,
    new THREE.Vector3(
      driveEndX,
      shaftCenterY,
      width / 2 + (driveShaftLength - 0.12) / 2,
    ),
    driveShaftLength,
    0.065,
  );

  const couplingGuard = cylinder(0.13, 0.13, 0.24, COLORS.safetyYellow, {
    metalness: 0.38,
    roughness: 0.36,
  });
  couplingGuard.rotation.x = Math.PI / 2;
  couplingGuard.position.set(
    driveEndX,
    shaftCenterY,
    width / 2 + 0.09,
  );
  group.add(couplingGuard);

  const bearingFlange = cylinder(0.21, 0.21, 0.12, COLORS.darkSteel, {
    metalness: 0.68,
    roughness: 0.28,
  });
  bearingFlange.rotation.x = Math.PI / 2;
  bearingFlange.position.set(
    driveEndX,
    shaftCenterY,
    gearboxCenterZ - gearboxDepth / 2 - 0.02,
  );
  group.add(bearingFlange);

  const gearbox = box([0.58, 0.58, gearboxDepth], COLORS.darkSteel, {
    metalness: 0.52,
    roughness: 0.34,
  });
  gearbox.position.set(driveEndX, shaftCenterY, gearboxCenterZ);
  group.add(gearbox);

  const mountingBracket = box([0.72, 0.12, 0.60], COLORS.steel, {
    metalness: 0.66,
    roughness: 0.3,
  });
  mountingBracket.position.set(
    driveEndX,
    shaftCenterY - 0.35,
    gearboxCenterZ - 0.05,
  );
  group.add(mountingBracket);

  for (const xOffset of [-0.21, 0.21]) {
    const bolt = cylinder(0.045, 0.045, 0.10, COLORS.lightSteel, {
      metalness: 0.9,
      roughness: 0.18,
    });
    bolt.rotation.x = Math.PI / 2;
    bolt.position.set(
      driveEndX + xOffset,
      shaftCenterY,
      railOuterZ + 0.015,
    );
    group.add(bolt);
  }

  const motorLength = 0.95;
  const motorDiameter = 0.5;
  const motorScale = 0.78;
  const motor = createMotorBody({
    length: motorLength,
    diameter: motorDiameter,
    mountFeet: false,
    running: Boolean(config.running),
  });
  motor.scale.setScalar(motorScale);
  const motorCenterZ =
    gearboxCenterZ +
    gearboxDepth / 2 +
    (motorLength * motorScale) / 2 +
    0.11;
  const motorBaseY =
    shaftCenterY - (motorDiameter / 2 + 0.16) * motorScale;
  motor.position.set(driveEndX, motorBaseY, motorCenterZ);
  motor.rotation.y = Math.PI / 2;
  group.add(motor);

  group.userData.dynamic = {
    kind: "conveyor",
    belt,
    rollers,
    shaftPivot: motor.userData.shaftPivot,
    driveShaftPivot,
    runLamp: motor.userData.runLamp,
    runBand: motor.userData.runBand,
    driveAssembly: {
      type: "direct-head-drive",
      driveEnd: "discharge",
      shaftAxis: "z",
      driveRoller,
      couplingGuard,
      bearingFlange,
      gearbox,
      mountingBracket,
      motor,
    },
    length,
    width,
    deckHeight,
    running: Boolean(config.running),
  };
  return group;
}

function createBox(definition) {
  const config = definition.config;
  const size = config.size ?? [0.8, 0.7, 0.7];
  const group = new THREE.Group();
  const carton = box(size, config.color ?? COLORS.box, {
    roughness: 0.92,
    metalness: 0,
  });
  carton.position.y = size[1] / 2;
  group.add(carton);

  const tape = box(
    [size[0] * 1.01, 0.015, Math.min(size[2] * 0.2, 0.15)],
    0xe6cf9a,
    { roughness: 1, metalness: 0 },
  );
  tape.position.y = size[1] + 0.008;
  group.add(tape);
  group.userData.dynamic = { kind: "box", size };
  return group;
}

function createPhotoeye(definition) {
  const config = definition.config;
  const span = config.span ?? 2.1;
  const height = config.height ?? 0.42;
  const group = new THREE.Group();
  const housings = [];

  for (const z of [-span / 2, span / 2]) {
    const post = box([0.16, height + 0.45, 0.16], COLORS.darkSteel, {
      metalness: 0.55,
    });
    post.position.set(0, (height + 0.45) / 2, z);
    group.add(post);

    const housing = box([0.3, 0.24, 0.24], COLORS.sensorBlue, {
      metalness: 0.25,
      roughness: 0.45,
    });
    housing.position.set(0, height + 0.25, z);
    group.add(housing);
    housings.push(housing);

    const lens = cylinder(0.07, 0.07, 0.035, COLORS.cyan, {
      emissive: COLORS.cyan,
      emissiveIntensity: 1.2,
      metalness: 0.05,
    });
    lens.rotation.x = Math.PI / 2;
    lens.position.set(0, height + 0.25, z - Math.sign(z) * 0.14);
    group.add(lens);
  }

  const beamMaterial = material(COLORS.cyan, {
    transparent: true,
    opacity: 0.55,
    emissive: COLORS.cyan,
    emissiveIntensity: 1.7,
    depthWrite: false,
  });
  const beam = mesh(new THREE.BoxGeometry(0.025, 0.025, span - 0.2), beamMaterial, {
    cast: false,
    receive: false,
  });
  beam.position.y = height + 0.25;
  group.add(beam);

  group.userData.dynamic = {
    kind: "photoeye",
    beam,
    housings,
    blocked: Boolean(config.blocked),
  };
  return group;
}

function createSwitch(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const pedestal = box([0.72, 1.05, 0.52], 0xc8ced1, {
    metalness: 0.4,
    roughness: 0.36,
  });
  pedestal.position.y = 0.525;
  group.add(pedestal);

  const face = box([0.6, 0.58, 0.05], COLORS.darkSteel, {
    metalness: 0.5,
  });
  face.position.set(0, 0.72, 0.285);
  face.userData.interactiveAction = config.action ?? "toggle";
  group.add(face);

  const isEmergency = config.style === "emergency";
  const buttonColor = isEmergency ? COLORS.red : config.color ?? COLORS.green;
  const button = cylinder(
    isEmergency ? 0.2 : 0.14,
    isEmergency ? 0.2 : 0.14,
    isEmergency ? 0.15 : 0.11,
    buttonColor,
    {
      emissive: config.active ? buttonColor : 0x000000,
      emissiveIntensity: config.active ? 0.65 : 0,
      roughness: 0.3,
    },
  );
  button.rotation.x = Math.PI / 2;
  button.position.set(0, 0.76, 0.37);
  button.userData.interactiveAction = config.action ?? "toggle";
  group.add(button);

  group.userData.dynamic = {
    kind: "switch",
    button,
    active: Boolean(config.active),
    action: config.action ?? "toggle",
    style: config.style ?? "pushbutton",
    releasedZ: 0.37,
    pressedZ: 0.325,
    color: buttonColor,
  };
  return group;
}

function createIndicator(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const base = cylinder(0.24, 0.3, 0.2, COLORS.darkSteel, { metalness: 0.6 });
  base.position.y = 0.1;
  group.add(base);

  const pole = cylinder(0.055, 0.055, 1.0, COLORS.lightSteel, {
    metalness: 0.85,
  });
  pole.position.y = 0.7;
  group.add(pole);

  const colors = config.colors ?? ["red", "amber", "green"];
  const colorValues = {
    red: COLORS.red,
    amber: COLORS.amber,
    green: COLORS.green,
    blue: COLORS.sensorBlue,
    white: 0xe9f2f5,
  };
  const lenses = new Map();
  const glows = new Map();
  const lights = new Map();
  colors.forEach((name, index) => {
    const color = colorValues[name] ?? COLORS.green;
    const initiallyActive = config.active === name;
    const lensMaterial = material(color, {
      transparent: true,
      opacity: initiallyActive ? 1 : 0.72,
      emissive: color,
      emissiveIntensity: initiallyActive ? 7 : 0.03,
      metalness: 0.05,
      roughness: 0.16,
    });
    const lens = mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.3, 24), lensMaterial);
    lens.position.y = 1.3 + index * 0.3;
    group.add(lens);
    lenses.set(name, lens);

    const glow = new THREE.Mesh(
      new THREE.CylinderGeometry(0.29, 0.29, 0.34, 24),
      new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity: initiallyActive ? 0.52 : 0,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      }),
    );
    glow.position.copy(lens.position);
    glow.visible = initiallyActive;
    group.add(glow);
    glows.set(name, glow);

    const light = new THREE.PointLight(color, initiallyActive ? 3.2 : 0, 3.2, 2);
    light.position.copy(lens.position);
    group.add(light);
    lights.set(name, light);
  });

  group.userData.dynamic = {
    kind: "indicator",
    lenses,
    glows,
    lights,
    active: config.active ?? null,
  };
  return group;
}

function createPump(definition) {
  const config = definition.config;
  const group = new THREE.Group();

  const motor = createMotorBody({
    length: 1.15,
    diameter: 0.65,
    color: config.color ?? COLORS.motorBlue,
    running: Boolean(config.running),
  });
  motor.position.x = -0.75;
  group.add(motor);

  const volute = mesh(
    new THREE.TorusGeometry(0.48, 0.2, 16, 32),
    material(COLORS.safetyOrange, { metalness: 0.45, roughness: 0.38 }),
  );
  volute.rotation.y = Math.PI / 2;
  volute.position.set(0.25, 0.52, 0);
  group.add(volute);

  const center = cylinder(0.27, 0.27, 0.35, COLORS.safetyOrange, {
    metalness: 0.45,
  });
  center.rotation.z = Math.PI / 2;
  center.position.set(0.25, 0.52, 0);
  group.add(center);

  const inlet = cylinder(0.18, 0.18, 0.65, COLORS.steel, { metalness: 0.7 });
  inlet.rotation.x = Math.PI / 2;
  inlet.position.set(0.25, 0.52, 0.58);
  group.add(inlet);

  const outlet = cylinder(0.16, 0.16, 0.68, COLORS.steel, { metalness: 0.7 });
  outlet.position.set(0.25, 1.08, 0);
  group.add(outlet);

  const skid = box([2.25, 0.12, 1.15], COLORS.darkSteel, { metalness: 0.65 });
  skid.position.set(-0.35, 0.06, 0);
  group.add(skid);

  group.userData.dynamic = {
    kind: "pump",
    shaftPivot: motor.userData.shaftPivot,
    runLamp: motor.userData.runLamp,
    runBand: motor.userData.runBand,
    running: Boolean(config.running),
  };
  return group;
}

function createFan(definition) {
  const config = definition.config;
  const diameter = config.diameter ?? 2.2;
  const radius = diameter / 2;
  const centerHeight = config.centerHeight ?? 2.0;
  const initialRunning = Boolean(config.running);
  const group = new THREE.Group();

  const base = box([1.45, 0.14, 1.05], COLORS.darkSteel, { metalness: 0.68 });
  base.position.y = 0.07;
  group.add(base);

  for (const x of [-0.52, 0.52]) {
    const foot = box([0.22, 0.12, 1.25], COLORS.steel, { metalness: 0.65 });
    foot.position.set(x, 0.2, 0);
    group.add(foot);
  }

  const post = box([0.18, centerHeight - 0.45, 0.18], COLORS.steel, {
    metalness: 0.72,
  });
  post.position.set(0, (centerHeight - 0.45) / 2 + 0.25, -0.2);
  group.add(post);

  const cageMaterial = material(COLORS.lightSteel, {
    metalness: 0.82,
    roughness: 0.24,
  });
  for (const z of [-0.2, 0.2]) {
    const ring = mesh(
      new THREE.TorusGeometry(radius, 0.045, 10, 64),
      cageMaterial.clone(),
    );
    ring.position.set(0, centerHeight, z);
    group.add(ring);
  }
  for (const angle of [0, Math.PI / 4, Math.PI / 2, (3 * Math.PI) / 4]) {
    const guard = box([diameter * 0.94, 0.035, 0.035], COLORS.lightSteel, {
      metalness: 0.78,
      roughness: 0.25,
    });
    guard.position.set(0, centerHeight, 0.21);
    guard.rotation.z = angle;
    group.add(guard);
  }

  const bladePivot = new THREE.Group();
  bladePivot.position.set(0, centerHeight, 0);
  const bladeColor = config.bladeColor ?? COLORS.safetyYellow;
  const bladeCount = config.bladeCount ?? 6;
  for (let index = 0; index < bladeCount; index += 1) {
    const bladeArm = new THREE.Group();
    bladeArm.rotation.z = (index / bladeCount) * Math.PI * 2;
    const blade = box([radius * 0.28, radius * 0.66, 0.09], bladeColor, {
      metalness: 0.28,
      roughness: 0.38,
    });
    blade.position.y = radius * 0.45;
    blade.rotation.z = -0.22;
    bladeArm.add(blade);
    bladePivot.add(bladeArm);
  }
  group.add(bladePivot);

  const hub = cylinder(radius * 0.16, radius * 0.16, 0.48, COLORS.darkSteel, {
    metalness: 0.7,
    roughness: 0.25,
  });
  hub.rotation.x = Math.PI / 2;
  hub.position.set(0, centerHeight, 0);
  group.add(hub);

  const rearMotor = cylinder(radius * 0.27, radius * 0.3, 0.58, COLORS.motorBlue, {
    metalness: 0.42,
    roughness: 0.38,
  });
  rearMotor.rotation.x = Math.PI / 2;
  rearMotor.position.set(0, centerHeight, -0.48);
  group.add(rearMotor);

  const runLamp = createRunLamp(
    group,
    new THREE.Vector3(0, centerHeight + radius * 0.4, -0.55),
    initialRunning,
  );
  group.userData.dynamic = {
    kind: "fan",
    bladePivot,
    runLamp,
    running: initialRunning,
  };
  return group;
}

function createPusher(definition) {
  const config = definition.config;
  const stroke = config.stroke ?? 1.35;
  const centerHeight = config.centerHeight ?? 0.78;
  const initialPosition = THREE.MathUtils.clamp(
    config.initialPosition ?? 0,
    0,
    1,
  );
  const group = new THREE.Group();

  const base = box([1.3, 0.14, 1.55], COLORS.darkSteel, { metalness: 0.68 });
  base.position.set(0, 0.07, -0.15);
  group.add(base);

  const cylinderBody = cylinder(0.32, 0.32, 1.15, COLORS.safetyOrange, {
    metalness: 0.48,
    roughness: 0.34,
  });
  cylinderBody.rotation.x = Math.PI / 2;
  cylinderBody.position.set(0, centerHeight, -0.2);
  group.add(cylinderBody);

  for (const z of [-0.72, 0.32]) {
    const cap = cylinder(0.36, 0.36, 0.12, COLORS.darkSteel, {
      metalness: 0.7,
      roughness: 0.27,
    });
    cap.rotation.x = Math.PI / 2;
    cap.position.set(0, centerHeight, z);
    group.add(cap);
  }

  const piston = new THREE.Group();
  piston.position.z = initialPosition * stroke;

  const rod = cylinder(0.095, 0.095, 0.9, COLORS.lightSteel, {
    metalness: 0.9,
    roughness: 0.16,
  });
  rod.rotation.x = Math.PI / 2;
  rod.position.set(0, centerHeight, 0.72);
  piston.add(rod);

  const pushPlate = box([0.78, 0.72, 0.13], COLORS.safetyYellow, {
    metalness: 0.34,
    roughness: 0.35,
  });
  pushPlate.position.set(0, centerHeight, 1.16);
  piston.add(pushPlate);
  group.add(piston);

  const manifold = box([0.55, 0.38, 0.5], COLORS.motorBlue, {
    metalness: 0.32,
    roughness: 0.4,
  });
  manifold.position.set(0.48, 0.3, -0.45);
  group.add(manifold);

  const createLimitLamp = (x, color, active) => {
    const lampMaterial = material(active ? color : 0x17362d, {
      emissive: color,
      emissiveIntensity: active ? 2.1 : 0.04,
      metalness: 0.03,
      roughness: 0.2,
    });
    const lamp = mesh(new THREE.SphereGeometry(0.085, 18, 12), lampMaterial);
    lamp.position.set(x, centerHeight + 0.4, -0.25);
    group.add(lamp);
    return lamp;
  };

  const retractedLamp = createLimitLamp(
    -0.16,
    COLORS.green,
    initialPosition <= 0.01,
  );
  const extendedLamp = createLimitLamp(
    0.16,
    COLORS.cyan,
    initialPosition >= 0.99,
  );

  group.userData.dynamic = {
    kind: "pusher",
    piston,
    stroke,
    position: initialPosition,
    retractedLamp,
    extendedLamp,
    retracted: initialPosition <= 0.01,
    extended: initialPosition >= 0.99,
  };
  return group;
}

function createTank(definition) {
  const config = definition.config;
  const height = config.height ?? 4.5;
  const diameter = config.diameter ?? 2.8;
  const radius = diameter / 2;
  const initialLevel = THREE.MathUtils.clamp(config.initialLevel ?? 0.45, 0, 1);
  const group = new THREE.Group();

  const shell = cylinder(radius, radius, height, 0x9fb3bd, {
    transparent: true,
    opacity: 0.2,
    metalness: 0.65,
    roughness: 0.2,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  shell.position.y = height / 2;
  shell.renderOrder = 2;
  group.add(shell);

  const bottom = cylinder(radius * 1.04, radius * 1.04, 0.16, COLORS.steel, {
    metalness: 0.75,
    roughness: 0.3,
  });
  bottom.position.y = 0.08;
  group.add(bottom);

  const topRing = mesh(
    new THREE.TorusGeometry(radius, 0.09, 12, 48),
    material(COLORS.lightSteel, { metalness: 0.8, roughness: 0.25 }),
  );
  topRing.rotation.x = Math.PI / 2;
  topRing.position.y = height;
  group.add(topRing);

  const bottomRing = topRing.clone();
  bottomRing.position.y = 0.16;
  group.add(bottomRing);

  for (const fraction of [0.25, 0.5, 0.75]) {
    const band = mesh(
      new THREE.TorusGeometry(radius * 1.01, 0.045, 10, 48),
      material(COLORS.steel, { metalness: 0.8, roughness: 0.3 }),
    );
    band.rotation.x = Math.PI / 2;
    band.position.y = height * fraction;
    group.add(band);
  }

  const fluidMaxHeight = height - 0.24;
  const fluid = cylinder(radius * 0.94, radius * 0.94, 1, config.fluidColor ?? COLORS.fluid, {
    transparent: true,
    opacity: 0.78,
    roughness: 0.16,
    metalness: 0.02,
    emissive: config.fluidColor ?? COLORS.fluid,
    emissiveIntensity: 0.1,
  });
  fluid.scale.y = Math.max(initialLevel * fluidMaxHeight, 0.001);
  fluid.position.y = 0.16 + (initialLevel * fluidMaxHeight) / 2;
  fluid.renderOrder = 1;
  group.add(fluid);

  const nozzle = cylinder(0.16, 0.16, 0.8, COLORS.steel, { metalness: 0.75 });
  nozzle.rotation.z = Math.PI / 2;
  nozzle.position.set(radius + 0.35, 0.48, 0);
  group.add(nozzle);

  group.userData.dynamic = {
    kind: "tank",
    fluid,
    level: initialLevel,
    height,
    radius,
    fluidMaxHeight,
  };
  return group;
}

function createLevelSensor(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const analog = config.sensorType === "analog";
  const bodyColor = analog ? COLORS.safetyOrange : COLORS.sensorBlue;

  const body = box(analog ? [0.52, 0.75, 0.38] : [0.48, 0.32, 0.38], bodyColor, {
    metalness: 0.28,
    roughness: 0.42,
  });
  body.position.y = analog ? 0.38 : 0.16;
  group.add(body);

  const probe = cylinder(0.055, 0.055, analog ? 1.1 : 0.55, COLORS.lightSteel, {
    metalness: 0.85,
  });
  probe.rotation.z = Math.PI / 2;
  probe.position.set(-0.5, analog ? 0.38 : 0.16, 0);
  group.add(probe);

  const lensColor = analog ? COLORS.green : COLORS.cyan;
  const lens = cylinder(0.07, 0.07, 0.03, lensColor, {
    emissive: lensColor,
    emissiveIntensity: config.active ? 1.5 : 0.05,
  });
  lens.rotation.x = Math.PI / 2;
  lens.position.set(0, analog ? 0.5 : 0.16, 0.205);
  group.add(lens);

  group.userData.dynamic = {
    kind: "levelSensor",
    sensorType: analog ? "analog" : "discrete",
    threshold: config.threshold ?? 0.5,
    mode: config.mode ?? "high",
    active: Boolean(config.active),
    lens,
    currentMa: 4,
  };
  return group;
}

function createRadarLevelSensor(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const mountSpan = config.mountSpan ?? 2.7;
  const beamRadius = config.beamRadius ?? 1.0;
  const initialLevel = THREE.MathUtils.clamp(config.initialLevel ?? 0.35, 0, 1);

  for (const z of [-0.24, 0.24]) {
    const mountingRail = box([mountSpan, 0.09, 0.13], COLORS.steel, {
      metalness: 0.78,
      roughness: 0.27,
    });
    mountingRail.position.set(0, -0.52, z);
    group.add(mountingRail);
  }

  const flange = cylinder(0.42, 0.42, 0.13, COLORS.lightSteel, {
    metalness: 0.82,
    roughness: 0.24,
  });
  flange.position.y = -0.42;
  group.add(flange);

  const neck = cylinder(0.12, 0.12, 0.38, COLORS.steel, {
    metalness: 0.72,
    roughness: 0.3,
  });
  neck.position.y = -0.17;
  group.add(neck);

  const head = box([0.78, 0.55, 0.62], COLORS.safetyOrange, {
    metalness: 0.28,
    roughness: 0.38,
  });
  head.position.y = 0.28;
  group.add(head);

  const display = box([0.42, 0.23, 0.035], 0x0f1c21, {
    metalness: 0.1,
    roughness: 0.3,
  });
  display.position.set(0, 0.31, 0.33);
  group.add(display);

  const echoLamp = cylinder(0.065, 0.065, 0.025, COLORS.green, {
    emissive: COLORS.green,
    emissiveIntensity: 1.8,
    metalness: 0.02,
    roughness: 0.2,
  });
  echoLamp.rotation.x = Math.PI / 2;
  echoLamp.position.set(0.13, 0.31, 0.355);
  group.add(echoLamp);

  const horn = mesh(
    new THREE.ConeGeometry(0.31, 0.48, 32, 1, true),
    material(COLORS.lightSteel, {
      metalness: 0.8,
      roughness: 0.23,
      side: THREE.DoubleSide,
    }),
  );
  horn.position.y = -0.77;
  group.add(horn);

  const beamApexY = -1.02;
  const beamMaterial = material(COLORS.cyan, {
    transparent: true,
    opacity: 0.2,
    emissive: COLORS.cyan,
    emissiveIntensity: 0.75,
    side: THREE.DoubleSide,
    depthWrite: false,
    metalness: 0,
    roughness: 0.2,
  });
  const beam = mesh(
    new THREE.ConeGeometry(beamRadius, 1, 32, 1, true),
    beamMaterial,
    { cast: false, receive: false },
  );
  beam.position.y = beamApexY - 1.5;
  beam.scale.y = 3;
  beam.renderOrder = 3;
  group.add(beam);

  const surfaceRing = mesh(
    new THREE.TorusGeometry(beamRadius, 0.035, 10, 48),
    material(COLORS.cyan, {
      transparent: true,
      opacity: 0.72,
      emissive: COLORS.cyan,
      emissiveIntensity: 1.1,
      depthWrite: false,
    }),
    { cast: false, receive: false },
  );
  surfaceRing.rotation.x = Math.PI / 2;
  surfaceRing.position.y = beamApexY - 3;
  surfaceRing.renderOrder = 4;
  group.add(surfaceRing);

  group.userData.dynamic = {
    kind: "radarLevelSensor",
    beam,
    beamApexY,
    surfaceRing,
    echoLamp,
    level: initialLevel,
    distanceM: 0,
    currentMa: 4 + 16 * initialLevel,
    beamRadius,
  };
  return group;
}

function createPipe(definition) {
  const config = definition.config;
  const length = config.length ?? 2;
  const diameter = config.diameter ?? 0.32;
  const group = new THREE.Group();
  const pipeColor = config.color ?? 0x74858d;
  const pipe = cylinder(diameter / 2, diameter / 2, length, pipeColor, {
    metalness: 0.78,
    roughness: 0.28,
  });
  const axis = config.axis ?? "x";
  if (axis === "x") {
    pipe.rotation.z = Math.PI / 2;
  } else if (axis === "z") {
    pipe.rotation.x = Math.PI / 2;
  }
  group.add(pipe);

  const flangeThickness = Math.max(0.08, diameter * 0.26);
  const flangeRadius = diameter * 0.82;
  for (const direction of [-1, 1]) {
    const flange = cylinder(
      flangeRadius,
      flangeRadius,
      flangeThickness,
      COLORS.lightSteel,
      { metalness: 0.84, roughness: 0.24 },
    );
    if (axis === "x") {
      flange.rotation.z = Math.PI / 2;
      flange.position.x = direction * length / 2;
    } else if (axis === "z") {
      flange.rotation.x = Math.PI / 2;
      flange.position.z = direction * length / 2;
    } else {
      flange.position.y = direction * length / 2;
    }
    group.add(flange);
  }

  const arrow = mesh(
    new THREE.ConeGeometry(diameter * 0.68, diameter * 1.5, 16),
    material(COLORS.cyan, {
      emissive: COLORS.cyan,
      emissiveIntensity: 0.55,
      metalness: 0.05,
      roughness: 0.28,
    }),
  );
  if (axis === "x") {
    arrow.rotation.z = -Math.PI / 2;
    arrow.position.x = length * 0.12;
  } else if (axis === "z") {
    arrow.rotation.x = Math.PI / 2;
    arrow.position.z = length * 0.12;
  } else {
    arrow.position.y = length * 0.12;
  }
  group.add(arrow);

  if (config.showSupport) {
    const supportHeight = config.supportHeight ?? 0.65;
    const post = box([0.16, supportHeight, 0.16], COLORS.darkSteel, {
      metalness: 0.65,
    });
    post.position.y = -supportHeight / 2;
    group.add(post);
    const supportFoot = box([0.65, 0.1, 0.55], COLORS.steel, {
      metalness: 0.68,
    });
    supportFoot.position.y = -supportHeight;
    group.add(supportFoot);
  }
  group.userData.dynamic = { kind: "pipe", axis };
  return group;
}

function createRotarySwitch(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const positionCount = Math.max(2, Math.round(config.positionCount ?? 2));
  const initialPosition = THREE.MathUtils.clamp(
    Math.round(config.initialPosition ?? 0),
    0,
    positionCount - 1,
  );

  const pedestal = box([0.9, 1.05, 0.62], 0xc8ced1, {
    metalness: 0.38,
    roughness: 0.38,
  });
  pedestal.position.y = 0.525;
  group.add(pedestal);

  const face = box([0.74, 0.72, 0.05], COLORS.darkSteel, {
    metalness: 0.52,
  });
  face.position.set(0, 0.72, 0.335);
  face.userData.interactiveAction = config.action ?? "selector-next";
  group.add(face);

  const dial = cylinder(0.27, 0.27, 0.055, COLORS.lightSteel, {
    metalness: 0.75,
    roughness: 0.28,
  });
  dial.rotation.x = Math.PI / 2;
  dial.position.set(0, 0.75, 0.395);
  dial.userData.interactiveAction = config.action ?? "selector-next";
  group.add(dial);

  const knob = box([0.13, 0.48, 0.12], config.color ?? 0xe8ecef, {
    metalness: 0.2,
    roughness: 0.34,
  });
  knob.position.set(0, 0.75, 0.47);
  knob.userData.interactiveAction = config.action ?? "selector-next";
  group.add(knob);

  group.userData.dynamic = {
    kind: "rotarySwitch",
    action: config.action ?? "selector-next",
    knob,
    position: initialPosition,
    positionCount,
    minimumAngle: THREE.MathUtils.degToRad(config.minimumAngleDeg ?? -60),
    maximumAngle: THREE.MathUtils.degToRad(config.maximumAngleDeg ?? 60),
  };
  return group;
}

function createLiftTable(definition) {
  const config = definition.config;
  const width = config.width ?? 2.8;
  const depth = config.depth ?? 1.8;
  const minimumHeight = config.minimumHeight ?? 0.55;
  const travel = config.travel ?? 2.1;
  const initialPosition = THREE.MathUtils.clamp(config.initialPosition ?? 0, 0, 1);
  const group = new THREE.Group();

  const base = box([width * 0.9, 0.16, depth * 0.86], COLORS.darkSteel, {
    metalness: 0.68,
  });
  base.position.y = 0.08;
  group.add(base);

  const platform = box([width, 0.2, depth], COLORS.safetyYellow, {
    metalness: 0.42,
    roughness: 0.34,
  });
  group.add(platform);

  const scissorMaterial = material(COLORS.steel, {
    metalness: 0.72,
    roughness: 0.28,
  });
  const scissorArms = [];
  for (const z of [-depth * 0.32, depth * 0.32]) {
    for (const direction of [-1, 1]) {
      const arm = mesh(
        new THREE.BoxGeometry(width * 0.78, 0.13, 0.13),
        scissorMaterial.clone(),
      );
      arm.position.set(0, minimumHeight * 0.5, z);
      arm.rotation.z = direction * 0.48;
      group.add(arm);
      scissorArms.push({ arm, direction });
    }
  }

  for (const x of [-width * 0.34, width * 0.34]) {
    const roller = cylinder(0.12, 0.12, depth * 0.68, COLORS.lightSteel, {
      metalness: 0.82,
    });
    roller.rotation.x = Math.PI / 2;
    roller.position.set(x, 0.22, 0);
    group.add(roller);
  }

  group.userData.dynamic = {
    kind: "liftTable",
    platform,
    scissorArms,
    minimumHeight,
    travel,
    position: initialPosition,
  };
  return group;
}

function createValve(definition) {
  const config = definition.config;
  const initialPosition = THREE.MathUtils.clamp(config.initialPosition ?? 0, 0, 1);
  const group = new THREE.Group();

  const body = cylinder(0.32, 0.32, 0.7, COLORS.safetyOrange, {
    metalness: 0.52,
    roughness: 0.32,
  });
  body.rotation.z = Math.PI / 2;
  body.position.y = 0.48;
  group.add(body);

  const nozzle = cylinder(0.15, 0.15, 1.35, COLORS.lightSteel, {
    metalness: 0.82,
    roughness: 0.24,
  });
  nozzle.position.y = 1.15;
  group.add(nozzle);

  const stemGroup = new THREE.Group();
  const stem = cylinder(0.08, 0.08, 0.65, COLORS.lightSteel, {
    metalness: 0.88,
  });
  stem.position.y = 0.72;
  stemGroup.add(stem);
  const wheel = mesh(
    new THREE.TorusGeometry(0.34, 0.055, 10, 32),
    material(COLORS.red, { metalness: 0.48, roughness: 0.3 }),
  );
  wheel.rotation.x = Math.PI / 2;
  wheel.position.y = 1.08;
  stemGroup.add(wheel);
  group.add(stemGroup);

  const flowLamp = createRunLamp(
    group,
    new THREE.Vector3(0.42, 0.7, 0),
    initialPosition > 0.01,
  );
  group.userData.dynamic = {
    kind: "valve",
    stemGroup,
    wheel,
    flowLamp,
    position: initialPosition,
  };
  return group;
}

function createDrillPress(definition) {
  const config = definition.config;
  const travel = config.travel ?? 1.35;
  const initialPosition = THREE.MathUtils.clamp(config.initialPosition ?? 0, 0, 1);
  const initialRunning = Boolean(config.running);
  const group = new THREE.Group();

  const base = box([2.3, 0.18, 1.7], COLORS.darkSteel, { metalness: 0.7 });
  base.position.y = 0.09;
  group.add(base);

  const column = box([0.28, 3.7, 0.32], COLORS.steel, { metalness: 0.72 });
  column.position.set(-0.82, 1.95, -0.45);
  group.add(column);

  const table = box([1.65, 0.16, 1.25], COLORS.lightSteel, {
    metalness: 0.78,
    roughness: 0.25,
  });
  table.position.set(0.1, 1.05, 0);
  group.add(table);

  const headGroup = new THREE.Group();
  headGroup.position.set(0.05, 3.05, 0);
  const head = box([1.7, 0.65, 1.0], config.color ?? COLORS.motorBlue, {
    metalness: 0.42,
    roughness: 0.36,
  });
  head.position.x = -0.05;
  headGroup.add(head);
  const spindlePivot = new THREE.Group();
  spindlePivot.position.set(0.28, -0.62, 0);
  const spindle = cylinder(0.12, 0.12, 1.0, COLORS.lightSteel, {
    metalness: 0.9,
    roughness: 0.16,
  });
  spindle.position.y = -0.32;
  spindlePivot.add(spindle);
  const bit = mesh(
    new THREE.ConeGeometry(0.15, 0.48, 20),
    material(COLORS.darkSteel, { metalness: 0.88, roughness: 0.18 }),
  );
  bit.position.y = -1.04;
  spindlePivot.add(bit);
  headGroup.add(spindlePivot);
  group.add(headGroup);

  const runLamp = createRunLamp(
    group,
    new THREE.Vector3(-0.4, 3.48, 0.52),
    initialRunning,
  );
  group.userData.dynamic = {
    kind: "drillPress",
    headGroup,
    spindlePivot,
    homeY: 3.05,
    travel,
    position: initialPosition,
    runLamp,
    running: initialRunning,
  };
  return group;
}

function createRobotArm(definition) {
  const config = definition.config;
  const initialPosition = THREE.MathUtils.clamp(config.initialPosition ?? 0, 0, 1);
  const initialRunning = Boolean(config.running);
  const group = new THREE.Group();

  const base = cylinder(0.75, 0.9, 0.36, COLORS.darkSteel, { metalness: 0.72 });
  base.position.y = 0.18;
  group.add(base);

  const waist = new THREE.Group();
  waist.position.y = 0.42;
  const shoulderHousing = cylinder(0.44, 0.44, 0.48, COLORS.safetyOrange, {
    metalness: 0.42,
  });
  shoulderHousing.position.y = 0.25;
  waist.add(shoulderHousing);

  const shoulder = new THREE.Group();
  shoulder.position.y = 0.55;
  const upperArm = box([0.48, 2.2, 0.52], COLORS.safetyOrange, {
    metalness: 0.4,
    roughness: 0.34,
  });
  upperArm.position.y = 1.05;
  shoulder.add(upperArm);

  const elbow = new THREE.Group();
  elbow.position.y = 2.05;
  const forearm = box([0.42, 1.8, 0.46], COLORS.safetyOrange, {
    metalness: 0.4,
    roughness: 0.34,
  });
  forearm.position.y = 0.85;
  elbow.add(forearm);
  const gripper = box([0.85, 0.28, 0.55], COLORS.darkSteel, {
    metalness: 0.72,
  });
  gripper.position.y = 1.82;
  elbow.add(gripper);
  shoulder.add(elbow);
  waist.add(shoulder);
  group.add(waist);

  const runLamp = createRunLamp(
    group,
    new THREE.Vector3(0.55, 0.7, 0),
    initialRunning,
  );
  group.userData.dynamic = {
    kind: "robotArm",
    waist,
    shoulder,
    elbow,
    position: initialPosition,
    runLamp,
    running: initialRunning,
  };
  return group;
}

function createRollerShutter(definition) {
  const config = definition.config;
  const width = config.width ?? 4.0;
  const height = config.height ?? 3.4;
  const initialPosition = THREE.MathUtils.clamp(config.initialPosition ?? 1, 0, 1);
  const group = new THREE.Group();

  for (const x of [-width / 2 - 0.16, width / 2 + 0.16]) {
    const guide = box([0.28, height + 0.5, 0.3], COLORS.darkSteel, {
      metalness: 0.7,
    });
    guide.position.set(x, (height + 0.5) / 2, 0);
    group.add(guide);
  }
  const header = box([width + 0.62, 0.5, 0.55], COLORS.steel, {
    metalness: 0.72,
  });
  header.position.y = height + 0.25;
  group.add(header);

  const curtain = new THREE.Group();
  const slatCount = Math.max(8, Math.round(height / 0.22));
  for (let index = 0; index < slatCount; index += 1) {
    const slat = box([width, height / slatCount * 0.88, 0.16], 0x6d7c83, {
      metalness: 0.72,
      roughness: 0.28,
    });
    slat.position.y = height - (index + 0.5) * (height / slatCount);
    curtain.add(slat);
  }
  group.add(curtain);

  const motor = createMotorBody({ length: 0.9, diameter: 0.48, running: false });
  motor.scale.setScalar(0.7);
  motor.position.set(width / 2 + 0.72, height, 0);
  motor.rotation.y = Math.PI / 2;
  group.add(motor);

  group.userData.dynamic = {
    kind: "rollerShutter",
    curtain,
    height,
    position: initialPosition,
    shaftPivot: motor.userData.shaftPivot,
    runLamp: motor.userData.runLamp,
    runBand: motor.userData.runBand,
    running: false,
  };
  return group;
}

function createRotaryTable(definition) {
  const config = definition.config;
  const radius = config.radius ?? 1.45;
  const initialPosition = THREE.MathUtils.clamp(config.initialPosition ?? 0, 0, 1);
  const group = new THREE.Group();

  const pedestal = cylinder(radius * 0.72, radius * 0.86, 0.58, COLORS.darkSteel, {
    metalness: 0.68,
  });
  pedestal.position.y = 0.29;
  group.add(pedestal);

  const tablePivot = new THREE.Group();
  tablePivot.position.y = 0.66;
  const table = cylinder(radius, radius, 0.2, COLORS.lightSteel, {
    metalness: 0.82,
    roughness: 0.24,
  });
  tablePivot.add(table);
  const indexMark = box([radius * 0.8, 0.05, 0.12], COLORS.safetyYellow, {
    metalness: 0.25,
  });
  indexMark.position.set(radius * 0.45, 0.13, 0);
  tablePivot.add(indexMark);
  group.add(tablePivot);

  group.userData.dynamic = {
    kind: "rotaryTable",
    tablePivot,
    position: initialPosition,
    angleRange: THREE.MathUtils.degToRad(config.angleRangeDeg ?? 180),
  };
  return group;
}

function createMachine(definition) {
  const config = definition.config;
  const size = config.size ?? [2.2, 2.7, 1.8];
  const initialRunning = Boolean(config.running);
  const group = new THREE.Group();

  const cabinet = box(size, config.color ?? 0x536873, {
    metalness: 0.58,
    roughness: 0.32,
  });
  cabinet.position.y = size[1] / 2;
  group.add(cabinet);

  const window = box([size[0] * 0.55, size[1] * 0.38, 0.045], 0x163541, {
    transparent: true,
    opacity: 0.72,
    metalness: 0.08,
    roughness: 0.2,
  });
  window.position.set(0, size[1] * 0.58, size[2] / 2 + 0.03);
  group.add(window);

  const accessDoor = box([size[0] * 0.76, size[1] * 0.36, 0.04], COLORS.darkSteel, {
    metalness: 0.62,
  });
  accessDoor.position.set(0, size[1] * 0.23, size[2] / 2 + 0.03);
  group.add(accessDoor);

  const runLamp = createRunLamp(
    group,
    new THREE.Vector3(size[0] * 0.34, size[1] * 0.88, size[2] / 2 + 0.08),
    initialRunning,
  );
  group.userData.dynamic = {
    kind: "machine",
    runLamp,
    running: initialRunning,
  };
  return group;
}

function createPalletLoad(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const width = config.caseWidthM ?? 0.5;
  const height = config.caseHeightM ?? 0.32;
  const depth = config.caseDepthM ?? 0.42;
  const layers = Math.max(1, Math.round(config.layers ?? 2));
  const columns = 2;
  const rows = 2;
  const pallet = box([columns * width + 0.18, 0.16, rows * depth + 0.18], 0x8b5a2b, { roughness: 0.82 });
  pallet.position.y = 0.08;
  group.add(pallet);
  for (let layer = 0; layer < layers; layer += 1) {
    for (let column = 0; column < columns; column += 1) {
      for (let row = 0; row < rows; row += 1) {
        const carton = box([width - 0.025, height - 0.02, depth - 0.025], config.color ?? COLORS.box, { roughness: 0.72 });
        carton.position.set((column - 0.5) * width, 0.16 + height * (layer + 0.5), (row - 0.5) * depth);
        group.add(carton);
      }
    }
  }
  return group;
}

function stationFrame(config = {}) {
  const group = new THREE.Group();
  const size = config.size ?? [1.8, 2.5, 1.4];
  const frameColor = config.color ?? COLORS.motorBlue;
  for (const x of [-size[0] * 0.42, size[0] * 0.42]) {
    const post = box([0.14, size[1], 0.14], frameColor, { metalness: 0.62 });
    post.position.set(x, size[1] / 2, 0);
    group.add(post);
  }
  const header = box([size[0], 0.18, 0.2], frameColor, { metalness: 0.62 });
  header.position.y = size[1] - 0.12;
  group.add(header);
  return group;
}

function createToteFiller(definition) {
  const group = stationFrame({ size: [1.5, 2.5, 1.2], color: COLORS.motorBlue });
  const supply = cylinder(0.18, 0.18, 0.7, COLORS.lightSteel, { metalness: 0.8 });
  supply.position.set(0, 2.08, 0);
  group.add(supply);
  const nozzle = cylinder(0.055, 0.035, 0.65, COLORS.safetyYellow, { metalness: 0.65 });
  nozzle.position.set(0, 1.45, 0);
  group.add(nozzle);
  return group;
}

function createToteCapper(definition) {
  const group = stationFrame(definition.config);
  const head = cylinder(0.28, 0.22, 0.5, COLORS.darkSteel, { metalness: 0.72 });
  head.position.set(0, 1.7, 0);
  group.add(head);
  const chuck = cylinder(0.12, 0.12, 0.35, COLORS.safetyYellow, { metalness: 0.55 });
  chuck.position.set(0, 1.28, 0);
  group.add(chuck);
  return group;
}

function createToteLabeler(definition) {
  const group = stationFrame(definition.config);
  const reel = cylinder(0.32, 0.32, 0.12, COLORS.lightSteel, { metalness: 0.55 });
  reel.rotation.x = Math.PI / 2;
  reel.position.set(-0.34, 1.65, 0.18);
  group.add(reel);
  const applicator = box([0.18, 0.58, 0.42], COLORS.safetyYellow, { metalness: 0.35 });
  applicator.position.set(0.35, 1.3, 0.15);
  group.add(applicator);
  return group;
}

function createToteVision(definition) {
  const group = stationFrame(definition.config);
  for (const x of [-0.42, 0.42]) {
    const camera = box([0.26, 0.2, 0.34], COLORS.sensorBlue, { metalness: 0.35 });
    camera.position.set(x, 1.62, 0.15);
    camera.rotation.z = x < 0 ? -0.35 : 0.35;
    group.add(camera);
    const lens = cylinder(0.07, 0.07, 0.12, 0x101820, { metalness: 0.4 });
    lens.rotation.x = Math.PI / 2;
    lens.position.set(x, 1.58, 0.36);
    group.add(lens);
  }
  return group;
}

function createMeteringSkid(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const base = box([2.0, 0.16, 1.3], COLORS.darkSteel, { metalness: 0.72 });
  base.position.y = 0.08;
  group.add(base);
  const reservoir = cylinder(0.42, 0.42, 1.4, config.color ?? COLORS.motorBlue, { metalness: 0.42 });
  reservoir.position.set(-0.45, 0.86, 0);
  group.add(reservoir);
  const meter = cylinder(0.24, 0.24, 0.32, COLORS.lightSteel, { metalness: 0.78 });
  meter.rotation.z = Math.PI / 2;
  meter.position.set(0.5, 0.62, 0);
  group.add(meter);
  const pipe = cylinder(0.08, 0.08, 1.0, COLORS.lightSteel, { metalness: 0.82 });
  pipe.rotation.z = Math.PI / 2;
  pipe.position.set(0.2, 0.35, 0);
  group.add(pipe);
  return group;
}

function createContainerReceiver(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const size = config.size ?? [2.1, 2.7, 1.7];
  const base = box([size[0], 0.16, size[2]], COLORS.darkSteel, { metalness: 0.7 });
  base.position.y = 0.08;
  group.add(base);
  for (const x of [-size[0] * 0.4, size[0] * 0.4]) {
    const guide = box([0.15, size[1] * 0.72, 0.15], config.color ?? COLORS.steel, { metalness: 0.62 });
    guide.position.set(x, size[1] * 0.36, 0);
    guide.rotation.z = x < 0 ? -0.16 : 0.16;
    group.add(guide);
  }
  return group;
}

function createSizeSensorBank(definition) {
  const config = definition.config;
  const group = new THREE.Group();
  const span = config.span ?? 2.05;
  const heights = config.beamHeightsM ?? [0.95, 1.3, 1.65];
  for (const x of [-span / 2, span / 2]) {
    const post = box([0.12, 2.05, 0.12], COLORS.sensorBlue, { metalness: 0.48 });
    post.position.set(x, 1.025, 0);
    group.add(post);
    heights.forEach((height) => {
      const emitter = box([0.18, 0.12, 0.2], COLORS.safetyYellow, { emissive: COLORS.amber, emissiveIntensity: 0.25 });
      emitter.position.set(x, height, 0);
      group.add(emitter);
    });
  }
  heights.forEach((height) => {
    const beam = box([span, 0.018, 0.018], COLORS.red, { emissive: COLORS.red, emissiveIntensity: 1.6, transparent: true, opacity: 0.72 });
    beam.position.y = height;
    group.add(beam);
  });
  return group;
}

const BUILDERS = Object.freeze({
  motor: createMotor,
  conveyor: createConveyor,
  box: createBox,
  photoeye: createPhotoeye,
  switch: createSwitch,
  indicator: createIndicator,
  pump: createPump,
  fan: createFan,
  pusher: createPusher,
  tank: createTank,
  levelSensor: createLevelSensor,
  radarLevelSensor: createRadarLevelSensor,
  pipe: createPipe,
  rotarySwitch: createRotarySwitch,
  liftTable: createLiftTable,
  valve: createValve,
  drillPress: createDrillPress,
  robotArm: createRobotArm,
  rollerShutter: createRollerShutter,
  rotaryTable: createRotaryTable,
  machine: createMachine,
  palletLoad: createPalletLoad,
  containerReceiver: createContainerReceiver,
  toteFiller: createToteFiller,
  toteCapper: createToteCapper,
  toteLabeler: createToteLabeler,
  toteVision: createToteVision,
  meteringSkid: createMeteringSkid,
  sizeSensorBank: createSizeSensorBank,
});

export const ASSET_BUILDER_TYPES = Object.freeze(Object.keys(BUILDERS));

export class AssetFactory {
  create(definition) {
    const builder = BUILDERS[definition.type];
    if (!builder) {
      throw new Error(`No 3D asset builder exists for "${definition.type}".`);
    }
    const group = builder(definition);
    const dynamicEntry = { dynamic: group.userData.dynamic ?? null };
    if (dynamicEntry.dynamic?.kind === "rotarySwitch") {
      setSelectorPosition(dynamicEntry, dynamicEntry.dynamic.position);
    } else if (
      [
        "pusher",
        "liftTable",
        "valve",
        "drillPress",
        "robotArm",
        "rollerShutter",
        "rotaryTable",
      ].includes(dynamicEntry.dynamic?.kind)
    ) {
      setAssetPosition(dynamicEntry, dynamicEntry.dynamic.position);
    }
    setTransform(group, definition);
    return tagForPicking(group, definition);
  }
}

export function setIndicatorState(entry, activeColor) {
  if (!entry?.dynamic || entry.dynamic.kind !== "indicator") {
    return;
  }
  entry.dynamic.active = activeColor;
  for (const [name, lens] of entry.dynamic.lenses) {
    const active = name === activeColor;
    lens.material.opacity = active ? 1 : 0.72;
    lens.material.emissiveIntensity = active ? 7 : 0.03;
    const glow = entry.dynamic.glows?.get(name);
    if (glow) {
      glow.visible = active;
      glow.material.opacity = active ? 0.52 : 0;
    }
    const light = entry.dynamic.lights?.get(name);
    if (light) {
      light.intensity = active ? 3.2 : 0;
    }
  }
}

export function setEquipmentRunning(entry, running) {
  if (
    !entry?.dynamic ||
    ![
      "motor",
      "conveyor",
      "pump",
      "fan",
      "drillPress",
      "robotArm",
      "rollerShutter",
      "machine",
    ].includes(entry.dynamic.kind)
  ) {
    return;
  }
  const active = Boolean(running);
  entry.dynamic.running = active;
  if (entry.dynamic.runLamp) {
    entry.dynamic.runLamp.material.color.setHex(
      active ? COLORS.green : 0x17362d,
    );
    entry.dynamic.runLamp.material.emissiveIntensity = active ? 2.3 : 0.03;
  }
  if (entry.dynamic.runBand) {
    entry.dynamic.runBand.material.color.setHex(
      active ? COLORS.green : 0x17362d,
    );
    entry.dynamic.runBand.material.emissiveIntensity = active ? 1.8 : 0.02;
  }
}

export function setSwitchState(entry, active) {
  if (!entry?.dynamic || entry.dynamic.kind !== "switch") {
    return;
  }
  const engaged = Boolean(active);
  entry.dynamic.active = engaged;
  entry.dynamic.button.position.z = engaged
    ? entry.dynamic.pressedZ
    : entry.dynamic.releasedZ;
  entry.dynamic.button.material.emissive.setHex(
    engaged ? entry.dynamic.color : 0x000000,
  );
  entry.dynamic.button.material.emissiveIntensity = engaged ? 0.75 : 0;
}

export function setPhotoeyeState(entry, blocked) {
  if (!entry?.dynamic || entry.dynamic.kind !== "photoeye") {
    return;
  }
  entry.dynamic.blocked = blocked;
  const color = blocked ? COLORS.red : COLORS.cyan;
  entry.dynamic.beam.material.color.setHex(color);
  entry.dynamic.beam.material.emissive.setHex(color);
  entry.dynamic.beam.material.opacity = blocked ? 0.85 : 0.48;
}

export function setLevelSensorState(entry, active, currentMa = null) {
  if (!entry?.dynamic || entry.dynamic.kind !== "levelSensor") {
    return;
  }
  entry.dynamic.active = active;
  entry.dynamic.lens.material.emissiveIntensity = active ? 2 : 0.05;
  if (currentMa !== null) {
    entry.dynamic.currentMa = currentMa;
  }
}

export function setRadarLevelState(entry, level, tankEntry) {
  if (
    !entry?.dynamic ||
    entry.dynamic.kind !== "radarLevelSensor" ||
    !tankEntry?.dynamic ||
    tankEntry.dynamic.kind !== "tank"
  ) {
    return;
  }

  const safeLevel = THREE.MathUtils.clamp(level, 0, 1);
  const fluidSurfaceY =
    tankEntry.group.position.y +
    0.16 +
    safeLevel * tankEntry.dynamic.fluidMaxHeight;
  const beamApexWorldY =
    entry.group.position.y + entry.dynamic.beamApexY;
  const distanceM = Math.max(0.08, beamApexWorldY - fluidSurfaceY);

  entry.dynamic.level = safeLevel;
  entry.dynamic.distanceM = distanceM;
  entry.dynamic.currentMa = 4 + 16 * safeLevel;
  entry.dynamic.beam.scale.y = distanceM;
  entry.dynamic.beam.position.y =
    entry.dynamic.beamApexY - distanceM / 2;
  entry.dynamic.surfaceRing.position.y =
    entry.dynamic.beamApexY - distanceM;
  entry.dynamic.echoLamp.material.emissiveIntensity = 2.1;
}

export function setPusherPosition(entry, position) {
  if (!entry?.dynamic || entry.dynamic.kind !== "pusher") {
    return;
  }
  const safePosition = THREE.MathUtils.clamp(position, 0, 1);
  const retracted = safePosition <= 0.01;
  const extended = safePosition >= 0.99;

  entry.dynamic.position = safePosition;
  entry.dynamic.retracted = retracted;
  entry.dynamic.extended = extended;
  entry.dynamic.piston.position.z = safePosition * entry.dynamic.stroke;

  entry.dynamic.retractedLamp.material.color.setHex(
    retracted ? COLORS.green : 0x17362d,
  );
  entry.dynamic.retractedLamp.material.emissiveIntensity = retracted
    ? 2.1
    : 0.04;
  entry.dynamic.extendedLamp.material.color.setHex(
    extended ? COLORS.cyan : 0x17362d,
  );
  entry.dynamic.extendedLamp.material.emissiveIntensity = extended
    ? 2.1
    : 0.04;
}

export function setSelectorPosition(entry, position) {
  if (!entry?.dynamic || entry.dynamic.kind !== "rotarySwitch") {
    return;
  }
  const safePosition = THREE.MathUtils.clamp(
    Math.round(position),
    0,
    entry.dynamic.positionCount - 1,
  );
  const fraction =
    entry.dynamic.positionCount <= 1
      ? 0
      : safePosition / (entry.dynamic.positionCount - 1);
  entry.dynamic.position = safePosition;
  entry.dynamic.knob.rotation.z = THREE.MathUtils.lerp(
    entry.dynamic.minimumAngle,
    entry.dynamic.maximumAngle,
    fraction,
  );
}

export function setAssetPosition(entry, position) {
  if (!entry?.dynamic) {
    return;
  }
  const safePosition = THREE.MathUtils.clamp(Number(position) || 0, 0, 1);
  const dynamic = entry.dynamic;

  if (dynamic.kind === "pusher") {
    setPusherPosition(entry, safePosition);
    return;
  }
  dynamic.position = safePosition;

  if (dynamic.kind === "liftTable") {
    const height = dynamic.minimumHeight + dynamic.travel * safePosition;
    dynamic.platform.position.y = height;
    const angle = THREE.MathUtils.lerp(0.28, 1.02, safePosition);
    for (const { arm, direction } of dynamic.scissorArms) {
      arm.position.y = height * 0.5;
      arm.rotation.z = direction * angle;
    }
  } else if (dynamic.kind === "valve") {
    dynamic.stemGroup.position.y = safePosition * 0.28;
    dynamic.wheel.rotation.y = safePosition * Math.PI;
    dynamic.flowLamp.material.color.setHex(
      safePosition > 0.01 ? COLORS.green : 0x17362d,
    );
    dynamic.flowLamp.material.emissiveIntensity =
      safePosition > 0.01 ? 2.3 : 0.03;
  } else if (dynamic.kind === "drillPress") {
    dynamic.headGroup.position.y = dynamic.homeY - dynamic.travel * safePosition;
  } else if (dynamic.kind === "robotArm") {
    dynamic.waist.rotation.y = THREE.MathUtils.lerp(-0.95, 1.05, safePosition);
    dynamic.shoulder.rotation.z = THREE.MathUtils.lerp(-0.28, 0.68, safePosition);
    dynamic.elbow.rotation.z = THREE.MathUtils.lerp(0.82, -0.74, safePosition);
  } else if (dynamic.kind === "rollerShutter") {
    const visibleFraction = Math.max(0.035, safePosition);
    dynamic.curtain.scale.y = visibleFraction;
    dynamic.curtain.position.y = dynamic.height * (1 - visibleFraction);
  } else if (dynamic.kind === "rotaryTable") {
    dynamic.tablePivot.rotation.y = dynamic.angleRange * safePosition;
  }
}

export function setTankLevel(entry, level) {
  if (!entry?.dynamic || entry.dynamic.kind !== "tank") {
    return;
  }
  const safeLevel = THREE.MathUtils.clamp(level, 0, 1);
  const height = safeLevel * entry.dynamic.fluidMaxHeight;
  entry.dynamic.level = safeLevel;
  entry.dynamic.fluid.scale.y = Math.max(height, 0.001);
  entry.dynamic.fluid.position.y = 0.16 + height / 2;
}
