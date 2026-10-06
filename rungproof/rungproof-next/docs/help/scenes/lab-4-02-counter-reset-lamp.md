# Lab 4.2 - Counter Reset Lamp help

Scene ID: `lab-4-02-counter-reset-lamp`  
Migrated source: `prototype/scenes/lab-4-02-counter-reset-lamp.plcscene`  
Scene contract: `res://scenes/migrated/lab-4-02-counter-reset-lamp.scene.json`

## Purpose

Count raw operator pulses in the PLC counter, light the lamp at its preset,
and clear the count with a momentary reset. The previous `count_reached`
manual result input is replaced by `pulse_received`; update older projects to
count this input instead of treating counter completion as simulator feedback.
This scene has no automatically loaded solution. Author or explicitly open a
compatible ladder controller before Run.

## Expected I/O to operate this scene

These are symbolic points, not physical addresses. PC-owned inputs are simulator
button events. The PLC owns the accumulated counter/done state in its program
and the lamp output. The scene does not calculate a hidden counter result.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `pulse_received` | `BOOL` | **PC** | `False` |
| `reset_pressed` | `BOOL` | **PC** | `False` |
| `counter_lamp` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Count pulse` | `pulse` | `pulse_received` |
| `Reset counter` | `pulse` | `reset_pressed` |

Both buttons deliver one high input scan, then return false after the accepted
local scan. Wait for the input to return false before pressing again; repeated
clicks before a scan are coalesced into the same high input, not an event queue.

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `pulse_received` | `switch_0` | `switch` |
| `reset_pressed` | `switch_2` | `switch` |
| `counter_lamp` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Count pulse button (COUNT) |
| `indicator_1` | `indicator` | Counter Reset Lamp indicator |
| `switch_2` | `switch` | Counter reset button (RESET) |

## Machine guide

1. Author a CTU, a reset rung and a lamp rung; use the counter's done state to
   drive `counter_lamp`. The reference preset is three, inherited from Demo 1;
   it is a software example value.
2. Inhibit the count rung while `reset_pressed` is true. Execute reset before
   the lamp rung so coincident count/reset gives reset priority.
3. Run and press COUNT three times. The reference lamp stays off after one/two
   and turns green after three. Idle scans must not increase the count.
4. Press RESET. The counter and lamp clear while the controller stays running.
   The next COUNT starts at one.

The geometry/workflow verifier writes an explicit ignored QA project to
`.tools/plant-review-counter-reset.rpproj.json`. Open it through File -> Open
Ladder Agent Project to exercise the reference; it does not replace the empty
training editor or add an authored demo.

## Stop and safety boundary

Local Stop removes the lamp command and discards unscanned momentary actions,
while the controller retains its counter. Run resumes the retained state;
a completed counter commands the lamp again. The operator RESET button clears
only the counter through ladder logic. The bottom application Reset clears all
controller/scene state, restores false inputs and output, and stays stopped.
These symbolic checks do not prove a physical counter interface, PLC transport,
safety function or commissioning result.
