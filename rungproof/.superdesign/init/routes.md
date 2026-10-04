# Routes and navigation

RungProof is a one-window native desktop application with no URL router.

| Navigation | Native target | Implementation |
| --- | --- | --- |
| Startup | Scene 2 Conveyor Pusher | `RungProofWindow` |
| View > A | Operator console | `set_view_mode("A")` |
| View > B | Immersive floor | `set_view_mode("B")` |
| View > C | Engineering split | `set_view_mode("C")` |
| PLC > Test PLC - Read-only | Isolated zero-write diagnostic dialog | `_test_plc` |
| Scene menu | Direct Scene Editor action plus Production Scenes and Training Labs | Header menu only |

There must be no main-workspace scene chooser. Unsupported scene entries are
visible migration markers and remain disabled until they have a native runtime
and an exact, approved PLC profile.
