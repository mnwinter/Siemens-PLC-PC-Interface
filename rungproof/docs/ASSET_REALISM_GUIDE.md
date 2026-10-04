# Industrial asset realism guide

## Purpose

RungProof equipment should communicate the real machine topology at a glance.
An asset is not acceptable merely because its individual shapes resemble a
motor, sensor, cylinder, or conveyor. The components must also be mounted,
aligned, guarded, and supported as they would be on actual equipment.

## Reference requirement

Before adding or substantially changing an equipment asset:

1. Find at least one primary manufacturer source for the same equipment type.
2. Record the manufacturer, product family, and the mounting or operating
   feature being used as the reference.
3. Distinguish the selected arrangement from valid alternatives. Do not blend
   incompatible arrangements into one model.
4. Check the power path, structural support, access, and guarding.
5. Add a geometry or source-contract test for the defining relationship when
   practical.

Search-result thumbnails and generated images may help find terminology, but
they are not engineering references. Prefer manufacturer product pages,
catalogs, installation manuals, and CAD views.

## Conveyor drive baseline

The reusable conveyor currently uses a **direct head drive**:

```text
discharge roller -> guarded shaft/coupling -> bearing/flange
                 -> frame-mounted gearbox -> gearmotor
```

The drive roller, gearbox output, and motor output are on the same cross-belt
axis. The assembly is mounted at the discharge end because the head drive
pulls the conveying surface. The gearbox has a visible frame bracket, and the
coupling is guarded. A disconnected floor motor is not a valid conveyor drive.

Valid alternatives must be modeled explicitly:

- An indirect side drive needs the motor, drive and driven pulleys or
  sprockets, a belt or chain, tensioning provisions, a mounting plate, and a
  guard.
- A center drive belongs below the conveying surface and needs its own belt
  path and take-up geometry.
- A motorized roller contains the drive within a conveyor roller; it should not
  also show an unrelated external motor.

## Primary references used

- [mk Technology Group - Drives for Conveyor Technology](https://www.mk-group.com/en/products/conveyor-technology/drives.html):
  defines head, center, direct, and indirect drive locations. mk states that
  its standard head drive is at the discharge end; its AF direct head drive
  connects the motor directly to the drive shaft.
- [Dorner - 2200 Modular Belt End Drive Conveyor](https://www.dornerconveyors.com/products/2200-series/2200-modular-belt-conveyor-2/end-drive):
  identifies the end-drive shaft and drive-mount package as part of the
  conveyor assembly.
- [Dorner - Bottom Mount Drive Package Manual](https://www.dornerconveyors.com/wp-content/uploads/2017/09/851-256j.pdf):
  shows the conveyor, mounting bracket, gearmotor, transmission, drive pulley,
  driven pulley, tensioner, and cover as one mounted drive system.
- [Interroll - RollerDrive](https://www.interroll.com/products/rollerdrive):
  documents the motorized-roller alternative for roller and belt conveyors.

## Review checklist

- Where does force enter the machine?
- Are the coupled components on a believable shared axis or transmission path?
- Is every major component supported by the machine frame?
- Are rotating shafts, belts, chains, and couplings guarded?
- Does the asset show only the selected drive arrangement?
- Would a controls or maintenance technician recognize how it works without a
  label?
