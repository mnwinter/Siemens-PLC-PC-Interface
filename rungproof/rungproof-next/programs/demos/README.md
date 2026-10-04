# RungProof Ladder Demonstration Projects

These five `.rpproj.json` files are reloadable offline Ladder projects. Open
them from **File -> Open Ladder Agent Project...**. Each project carries its
associated `sourceSceneId`; RungProof requests that scene before Verify + Load.

| Demo | Project | Focus | Associated scene |
|---|---|---|---|
| 1 | `01-press-count-starter.rpproj.json` | Rising edge, CTU, output coil | Lab 4.1 Press-Count Lamp |
| 2 | `02-delayed-lamp-timer.rpproj.json` | TON timer, `.Q` status, output coil | Lab 5.1 Delayed Lamp |
| 3 | `03-conveyor-sequence.rpproj.json` | Seal-in, NC interlocks, photoeye edge, CTU | Conveyor Stop |
| 4 | `04-batch-process-blocks.rpproj.json` | Timer, counter, REAL tags, arithmetic, recipe permissive | Lab 9.11 Pallet Counting |
| 5 | `05-integrated-cell-multi-fb-fc.rpproj.json` | OB1 plus two FBs and two FCs, CALL/RETURN, periodic task, TON, CTU, edge, compare, SCALE, ADD, JMP/LABEL | Conveyor Inspection Cell |

Demo 5 is intentionally an integration exercise. It keeps the FB/FC names
visible in the Project objects tree and combines safety permissives, sequence
control, analog scaling, production reporting, and a final conveyor command.
All five remain simulator-only: no physical PLC transport, address mapping, or
live I/O is included.
