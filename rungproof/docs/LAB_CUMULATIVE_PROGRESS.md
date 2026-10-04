# Cumulative Lab Progression

Lab 2.1 is the starting point for the PLC/watchdog foundation. Every later
lab retains that foundation and adds the next control concept. The simulator
scene files describe the required contract and acceptance behavior; the actual
TIA ladder blocks remain in the student's cumulative bench project.

## Progression groups

| Labs | Development focus | What remains from the previous lab |
|---|---|---|
| 2.1 | Watchdog, heartbeat, first input/output | Common `DB_SimulationProof`, watchdog, watch table |
| 2.2–2.4 | Series, inversion, parallel logic | Watchdog, project, prior troubleshooting method |
| 2.5–2.10 | Selectors, complementary outputs, permissives, memory, seal-in | Watchdog and prior project foundation; new tags are additive |
| 2.11–2.15 | Photoeyes, conveyors, tanks, pumps, analog/discrete feedback | Watchdog, prior blocks, and documented tag conventions |
| 2.16–2.20 | Guarded drilling, robot motion, limits, shutters, shuttle travel | Watchdog, prior blocks, and cumulative acceptance checks |
| 2.21–2.25 | Multi-station sequences, valves, CNC handshakes, sorting, toggle memory | Watchdog, prior blocks, all documented setup discipline |

## Rule for each new lab

1. Open the previous lab's TIA project copy.
2. Confirm the common watchdog and earlier acceptance checks still pass.
3. Add only the new symbols, networks, blocks, and equipment required by the
   new lab.
4. Do not rename or delete retained tags without recording a `changedTags`
   entry and reviewing every dependent rung.
5. Run the previous lab checks before running the new acceptance cases.
6. Save the project as the next cumulative lab revision.

## Simulator contract

The Setup view is the authoritative list of exact simulator point names. It
shows direction and type so a student can create matching PLC symbols or map
them in a verified external profile. The simulator follows PLC-owned outputs;
it does not synthesize missing ladder logic to make a lab pass.

## Current repository boundary

This repository does not contain the student's TIA Portal project or ladder
blocks. It now records the cumulative lineage, machine guide, tag delta, and
previous acceptance identity in every generated lab scene. Once TIA blocks are
exported, the cumulative project can be checked against those contracts.
