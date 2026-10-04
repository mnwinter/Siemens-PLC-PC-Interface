# Original PLC training scene catalog

## Scope and source boundary

The photographed exercises were used only to identify control concepts, I/O
relationships, and machine-sequence categories. The scenes below use original
names, layouts, dimensions, timings, equipment combinations, symbolic points,
descriptions, and acceptance cases. They do not reproduce the book diagrams,
wording, wiring illustrations, or proposed solutions.

All scenes remain offline. Point ownership describes the proposed PLC/PC
direction in the mock runtime; it does not authorize a PLC connection or write.

## Cumulative project foundation

Lab 2.1 establishes the common PLC/watchdog foundation documented in
`docs/PLC_BENCH_SETUP.md`. Each subsequent lab retains that foundation and
records its lineage, retained tags, added tags, and changed tags in the scene
document. The scene runtime remains a deterministic exercise contract; actual
TIA ladder blocks remain on the bench PLC until exported and reviewed.

## Scene inventory

| Ref. | Original simulator scene | Control concept retained | Material changes | Inputs / feedback | Outputs / commands | Acceptance proof | Scene file |
|---|---|---|---|---|---|---|---|
| 2.1 | Workstation Call Lamp | One normally-open input directly controls one lamp | Material-request use case, blue LED load, new symbols, and an original workstation layout. | `material_call_pressed` | `material_call_on` | The call lamp follows the button state: off when released and on when pressed. | `lab-2-01-workstation-call.plcscene` |
| 2.2 | Dual Confirmation Lamp | Two normally-open inputs in series | Non-safety handoff-confirmation scenario, separate operator and quality roles, new symbols, and an original panel layout. | `operator_confirmed, quality_confirmed` | `handoff_ready` | The ready lamp is on only when both confirmation inputs are active. | `lab-2-02-dual-confirmation.plcscene` |
| 2.3 | Service Marker Inhibit | One input inverts a normally-on lamp | Service-marker inhibit use case, white LED load, explicit raw input polarity, and an original layout. | `marker_inhibit_pressed` | `service_marker_on` | The marker is on with the button released and off while the inhibit input is active. | `lab-2-03-service-marker-inhibit.plcscene` |
| 2.4 | Two-Station Call Beacon | Two normally-open inputs in parallel | Two-station assistance-call scenario, shared amber beacon, new symbols, and an original panel layout. | `north_call_pressed, south_call_pressed` | `assistance_call_on` | The beacon is off with neither input and on when either or both call inputs are active. | `lab-2-04-two-station-call.plcscene` |
| 2.5 | Bay Light Selector | Two lamps selected together | Maintenance-bay setting, LED loads, new symbols, and a two-position isolation/energize selector. | `selector_position` | `bay_a_command, bay_b_command` | Position 0 de-energizes both lights; position 1 energizes both. | `lab-2-05-bay-light-selector.plcscene` |
| 2.6 | Ready / Attention Button | One button selects complementary lamps | Ready/attention annunciation with white and amber LEDs and new signal polarity. | `request_held` | `ready_light, attention_light` | Exactly one indication is on in both released and held states. | `lab-2-06-ready-attention.plcscene` |
| 2.7 | Dual-Contact Permissive | NO and NC inputs driving one lamp | Permissive-testing scenario with explicit raw NC contact state and inverted logic. | `reset_request, stop_contact_nc` | `permit_output` | Normal state is off; either logical request turns the permit lamp on. | `lab-2-07-dual-contact-permissive.plcscene` |
| 2.8 | Inspection Vote Stacklight | Two buttons and three mutually exclusive lamps | Dual-inspector voting with pass, hold, and conflict meanings. | `vote_a, vote_b` | `pass_indication, hold_indication, conflict_indication` | Single votes select green or amber; simultaneous votes select red only. | `lab-2-08-inspection-vote.plcscene` |
| 2.9 | Maintenance Beacon Selector | Four-position selector and three lamps | Maintenance-state beacon with mutually exclusive off/red/amber/green states. | `beacon_position` | `red_beacon, amber_beacon, green_beacon` | Each selector position produces exactly the documented beacon state. | `lab-2-09-maintenance-beacon.plcscene` |
| 2.10 | Dust Collector Seal-In | Start/stop self-hold | Dust-collection fan, separate latch point, and explicit run indication. | `collector-start, collector-stop` | `collector_run` | Start seals in the run command; stop removes it. | `lab-2-10-dust-collector-seal-in.plcscene` |
| 2.11 | Inbound Tote Stop | Package conveyor stops at a sensor | Reusable tote, barcode dwell, automatic release, 8 m conveyor, and new timing. | `tote_at_scanner, scan_complete` | `conveyor_run` | The tote stops at the scanner, records completion, clears, and leaves the conveyor stopped. | `lab-2-11-inbound-tote-stop.plcscene` |
| 2.12 | Ergonomic Assembly Lift | Pallet lift with up/down controls and end sensors | Ergonomic assembly table, 2.2 m travel, explicit motion commands, position feedback, and separate verification paths. | `top_limit, bottom_limit` | `lift_up, lift_down` | Raise stops at the top limit; lower stops at the bottom limit; opposed outputs are never on together. | `lab-2-12-assembly-lift.plcscene` |
| 2.13 | Coolant Jug Filling Cell | Fill moving containers to a level sensor | Coolant jug, metered valve/skid, 100% fill feedback, new distances and timings. | `jug_present, high_level_probe` | `conveyor_run, fill_valve_open, fill_skid_run` | The valve cannot remain open after the high probe; the filled jug exits and the conveyor stops. | `lab-2-13-coolant-jug-fill.plcscene` |
| 2.14 | Sump Dewatering Pump | Pump well with two float switches | Equipment-room sump, 78%/18% thresholds, explicit latch behavior, and visible pump/tank dynamics. | `high_float_active, low_float_active` | `pump_run` | High float starts the pump; it remains on through the deadband and stops only at low float. | `lab-2-14-sump-pump.plcscene` |
| 2.15 | Weld Fume Extractor | Hood light and three fan speeds | Weld-fume extractor with 35/65/100% speed commands and separate inspection light. | `hood_light_request, fan_selector_position` | `hood_light_on, fan_run, fan_speed_percent` | Light is independent; selector positions command off/35/65/100% and one speed indication. | `lab-2-15-fume-extractor.plcscene` |
| 2.16 | Fixture-Safe Drill Station | Two-hand drilling machine | Guarded fixture, explicit workpiece permissive, blocked-start proof, new travel and timing. | `left_hand_request, right_hand_request, workpiece_present, drill_at_top, drill_at_bottom` | `drill_run` | Start is blocked without both requests; a valid cycle drills, retracts, and stops at top. | `lab-2-16-safe-drill.plcscene` |
| 2.17 | Twin-Container Pallet Cell | Robot removes two containers from a pallet | Outbound process receiver, new robot poses, container geometry, 8 m conveyor, and explicit placed-count proof. | `pallet_ready` | `robot_run, conveyor_run` | Exactly two containers are placed before the pallet conveyor releases. | `lab-2-17-pallet-robot.plcscene` |
| 2.18 | Shipping Pallet Accumulation | Manual/automatic pallet conveyor | Loaded shipping pallet, fork-truck pickup point, explicit auto permissive, and bounded manual jog. | `auto_mode, pickup_sensor` | `conveyor_run` | Auto stops at the pickup sensor; manual jog moves only one bounded increment. | `lab-2-18-pallet-pickup.plcscene` |
| 2.19 | Service Door Shutter | Roller shutter with up/down/stop and NC limits | Service-door setting, 3.5 m travel, cable-monitored contact names, and separate open/close proofs. | `open_limit_nc, closed_limit_nc` | `motor_open, motor_close` | Each direction stops at its limit; open and close outputs are never on together. | `lab-2-19-service-door.plcscene` |
| 2.20 | Bottle Shuttle Conveyor | Bottle conveyor moves forward and back | Reusable bottle shuttle, explicit direction tag, 6 m sensor spacing, and complete round-trip proof. | `left_sensor_active, right_sensor_active` | `motor_run, motor_direction` | Right sensor reverses travel; left sensor stops the completed round trip. | `lab-2-20-bottle-shuttle.plcscene` |
| 2.21 | Chemical Tote Finishing Line | Multi-station container production line | Chemical tote finishing, five distinct stations, vision result, 13 m conveyor, and new cycle timing. | `inspection_ok` | `conveyor_run, fill_valve_open, capper_run, labeler_run, inspection_run` | Stations execute in order and every actuator is off after a passing tote discharges. | `lab-2-21-tote-finishing.plcscene` |
| 2.22 | Dual-Spindle Plate Cell | Two drilling machines and a plate indexer | Parallel pilot/countersink operations, independent travel, transfer permissive after both home, and new geometry. | `drill_a_home, drill_b_home` | `drill_a_run, drill_b_run, transfer_extend` | Transfer begins only after both spindles are home; all motion commands finish off. | `lab-2-22-dual-spindle.plcscene` |
| 2.23 | Parcel Size Sorter | Sort three package sizes onto three conveyors | Parcel hub layout, two reusable routing tables, new sensor meanings, and fixed three-parcel batch proof. | `large_detected, medium_detected, small_detected` | `conveyors_run, route_position` | One parcel reaches each lane and the sorted count ends at three. | `lab-2-23-parcel-sorter.plcscene` |
| 2.24 | Robot CNC Tending Cell | Robot and CNC machine coordinated by PLC | Explicit machine-ready handshake, infeed/outfeed split, new robot path, machining dwell, and offline interlock proof. | `blank_at_pickup, cnc_ready, machining_complete` | `infeed_run, outfeed_run, robot_run, cnc_run` | The CNC runs only while the robot is stopped; the part exits after machining complete. | `lab-2-24-robot-cnc.plcscene` |
| 2.25 | Inspection Light Toggle | One-button toggle lamp | Machine inspection-light use case with explicit memory bit and pulse terminology. | `toggle button pulse` | `inspection_light_on` | Odd pulses turn the light on; even pulses return it off. | `lab-2-25-inspection-toggle.plcscene` |
| 3.1 | Guarded Pallet Transfer | Guarded conveyor with pallet and access protection | Original transfer-lane layout, symbolic points, and permissive names. | `guard_closed, entry_clear, exit_clear` | `transfer_run, transfer_permissive` | The transfer runs only with protection closed and both path sensors clear. | `lab-3-01-guarded-pallet-transfer.plcscene` |
| 3.2 | Robot Cell Safe Restart | Robot cell with safety interlocks | Original cell identity, restart sequence, and handoff signals. | `gate_closed, reset_complete, robot_ready` | `robot_enable, cell_ready` | A restart request cannot enable motion until the gate is closed and the robot is ready. | `lab-3-02-robot-cell-safe-restart.plcscene` |
| 4.1 | Press-Count Lamp | Counter threshold drives one lamp | Original station context, tag names, threshold contract, and visual panel. | `pulse_received` | `threshold_lamp` | A Ladder CTU counts pulse_received rising edges and turns the lamp on at its preset. | `lab-4-01-press-count-lamp.plcscene` |
| 4.2 | Counter Reset Lamp | Counter state and reset | Original counter-reset station and state names. | `count_reached, reset_pressed` | `counter_lamp` | The lamp follows the count state and clears when reset is applied. | `lab-4-02-counter-reset-lamp.plcscene` |
| 4.3 | Repeat-Cycle Counter | Repeated count-controlled cycle | Original cycle names, station layout, and completion contract. | `cycle_request, cycle_count_complete` | `cycle_active, cycle_complete` | A repeated cycle runs until the configured count is complete, then reports completion. | `lab-4-03-repeat-cycle-counter.plcscene` |
| 4.4 | Sequence Light Tower | Ordered output sequence | Original tower sequence and operator interaction. | `sequence_start, sequence_step_due` | `tower_active, sequence_complete` | The tower advances in order and ends with every command off. | `lab-4-04-sequence-light-tower.plcscene` |
| 4.5 | Dual-Input Count Window | Two counters combined with a permissive | Original inspection station and independent count names. | `channel_a_ready, channel_b_ready` | `window_ready` | The ready indication is on only when both count conditions are satisfied. | `lab-4-05-dual-input-count-window.plcscene` |
| 4.6 | Multi-Press Confirmation | Multiple button presses and counter comparison | Original operator confirmation workflow and named result. | `button_a_pattern_ok, button_b_pattern_ok` | `confirmation_valid` | The confirmation is valid only when both independent press patterns are valid. | `lab-4-06-multi-press-confirmation.plcscene` |
| 4.7 | Parking Garage Entry | Barrier control from entry/exit sensors | Original parking layout, barrier state, and capacity contract. | `entry_detected, space_available, exit_clear` | `barrier_open, garage_available` | The barrier opens only when a vehicle is detected, a space is available, and the exit path is clear. | `lab-4-07-parking-garage-entry.plcscene` |
| 4.8 | Package Grouping Station | Package grouping on a conveyor | Original grouping lane, queue geometry, and count feedback. | `package_detected, group_count_reached, release_clear` | `group_conveyor_run, group_release` | The release command occurs only after the target group count and downstream clear signal. | `lab-4-08-package-grouping.plcscene` |
| 4.9 | Chain-Drive Lift | Chain drive and vertical lift interlock | Original lift cell, position states, and safe direction commands. | `box_present, lift_home, destination_clear` | `chain_run, lift_enable` | The chain and lift are enabled only with a box present, valid home, and clear destination. | `lab-4-09-chain-drive-lift.plcscene` |
| 4.10 | Cookie Packaging Cell | Multi-stage product packaging | Original food-handling layout, station names, and release condition. | `product_present, packaging_ready, batch_complete` | `infeed_run, packaging_enable` | Product advances only when packaging is ready and the current batch is not complete. | `lab-4-10-cookie-packaging.plcscene` |
| 4.11 | Barrel Fill Station | Container filling on a conveyor | Original fill skid, container, and interlock names. | `barrel_at_fill, fill_complete, downstream_clear` | `infeed_run, fill_valve_open` | The valve opens only at the fill position and the conveyor resumes after completion. | `lab-4-11-barrel-fill-station.plcscene` |
| 4.12 | Cable Cut-Length Cell | Encoder length measurement and cutter | Original cable cell, measurement tags, and cutter state model. | `cable_present, length_reached, cutter_home` | `feed_run, cutter_fire` | The cutter fires only at the target length and returns to home before the next cycle. | `lab-4-12-cable-cut-length.plcscene` |
| 5.1 | Delayed Lamp | On-delay timer | Original timer station and explicit reset behavior. | `timer_request` | `delayed_lamp` | A Ladder TON holds the lamp off until its preset expires, then energizes it while the request remains active. | `lab-5-01-delayed-lamp.plcscene` |
| 5.2 | Timed Lamp-Off | Off-delay or pulse timer | Original timed indicator and retrigger rules. | `start_pulse, time_active` | `timed_lamp` | The lamp is on only during the active timing window. | `lab-5-02-timed-lamp-off.plcscene` |
| 5.3 | Rotary Flasher | Rotary selector and flashing output | Original selector positions, flasher state, and reset behavior. | `flash_mode_selected, flash_tick` | `flash_lamp` | The lamp flashes only in the selected mode and is off when the selector is cleared. | `lab-5-03-rotary-flasher.plcscene` |
| 5.4 | Alternating Lamps | Alternating timer outputs | Original two-lamp status station and phase state. | `alternate_enable, alternate_phase` | `lamp_a, lamp_b` | The two lamps alternate without overlapping and both turn off when disabled. | `lab-5-04-alternating-lamps.plcscene` |
| 5.5 | Variable Flash Rate | Button-controlled flashing speed | Original speed selection and mutually bounded timing modes. | `flash_enable, fast_rate_selected, slow_rate_selected` | `rate_lamp` | The lamp uses exactly one selected rate and turns off when flash_enable is removed. | `lab-5-05-variable-flash-rate.plcscene` |
| 5.6 | Running-Light Tower | Running-light sequence | Original tower state names, timing contract, and reset behavior. | `tower_enable, step_pulse` | `tower_step_active` | Each step advances in order and reset returns the tower to its first state. | `lab-5-06-running-light-tower.plcscene` |
| 5.7 | Pedestrian Crossing | Timed traffic-signal sequence | Original crossing state machine, durations, and request handling. | `crossing_request, sequence_running, clear_to_finish` | `vehicle_stop, pedestrian_walk` | A crossing request stops vehicle traffic before enabling the pedestrian indication, then returns to idle. | `lab-5-07-pedestrian-crossing.plcscene` |
| 5.8 | Drawbridge Control | Drawbridge interlock and timing | Original bridge cell, limit feedback, and safe movement commands. | `traffic_stopped, bridge_request, bridge_home` | `bridge_raise, traffic_release` | Bridge motion and traffic release are mutually interlocked. | `lab-5-08-drawbridge-control.plcscene` |
| 5.9 | Bag Indexing Conveyor | Reversible bag conveyor | Original bag lane, pause workflow, and restart interlock. | `bag_at_entry, bag_at_exit, pause_clear` | `conveyor_run, conveyor_reverse` | The bag stops at the requested station and reverse motion is permitted only after pause_clear. | `lab-5-09-bag-indexing-conveyor.plcscene` |
| 5.10 | Coating Line | Painting/coating machine sequence | Original coating cell, enclosure, and exhaust permissive. | `workpiece_at_station, spray_ready, ventilation_ready` | `index_run, spray_enable, vent_run` | Spray is enabled only while the workpiece is positioned and ventilation is ready. | `lab-5-10-coating-line.plcscene` |
| 6.7 | Luggage Weight Sort | Analog weight classification and counting | Original baggage lane, weight classes, and category names. | `bag_present, weight_valid, class_selected` | `weigh_cycle, class_result` | A valid bag produces one category result and increments only its class counter. | `lab-6-07-luggage-weight-sort.plcscene` |
| 6.8 | Timed Hand-Dryer | Presence-triggered dryer with timer | Original hygiene station, output interlock, and timer status. | `hands_present, dryer_timer_active` | `blower_run, heater_enable` | The blower and heater run only during a valid hand-drying interval. | `lab-6-08-hand-dryer.plcscene` |
| 9.1 | Sum Function Block | Two-input addition function | Original named operands, function call handshake, and validation states. | `operand_a_valid, operand_b_valid, calculate_request` | `sum_result_valid` | The result-valid indication occurs only when both operands are valid and a calculation is requested. | `lab-9-01-sum-function.plcscene` |
| 9.2 | Product Function Block | Two-input multiplication function | Original operands, function identity, and result handshake. | `factor_a_valid, factor_b_valid, calculate_request` | `product_result_valid` | The product result becomes valid only after both factors and the request are valid. | `lab-9-02-product-function.plcscene` |
| 9.3 | Sum and Counter Function | Function block with internal counter | Original call-complete handshake and event counter contract. | `inputs_valid, calculate_request, call_complete` | `result_valid, event_counted` | Each completed call produces one valid result and one counter event. | `lab-9-03-sum-and-counter-function.plcscene` |
| 9.4 | Function Selector | Function block calling other functions | Original selector values, call routing, and result-valid contract. | `operand_set_valid, function_select_valid, calculate_request` | `selected_result_valid` | Only the selected calculation path may assert selected_result_valid. | `lab-9-04-function-selector.plcscene` |
| 9.10 | Box Volume Calculation | Volume calculation from three analog measurements | Original dimensional inputs, units, and result-ready handshake. | `length_valid, width_valid, height_valid` | `volume_result_valid` | Volume result-valid is asserted only when all three dimensions are valid. | `lab-9-10-box-volume.plcscene` |
| 9.11 | Pallet Count Function | Counting pallets by type | Original pallet taxonomy, count event, and result handshake. | `pallet_detected, pallet_type_valid, count_request` | `pallet_count_valid` | Each valid pallet event contributes to the selected count and produces a valid count result. | `lab-9-11-pallet-counting.plcscene` |
| 9.12 | EV Charging Manager | Multi-bay charging station and energy meter | Original bay allocation, authorization, and pulse-count contract. | `bay_occupied, customer_authorized, charger_ready` | `charge_enable, energy_session_active` | Charging is enabled only for an occupied, authorized, ready bay. | `lab-9-12-ev-charging-manager.plcscene` |
| 10.1 | Drive Alarm-Code String | Frequency-converter alarm string parsing | Original drive diagnostic panel, alarm-code contract, and search result. | `drive_alarm_string_valid, alarm_code_found, alarm_reset` | `drive_alarm_active, alarm_match_valid` | The alarm result is active only for a valid drive message containing the selected code. | `lab-10-01-drive-alarm-code-string.plcscene` |
| 10.2 | Chicken Label Print | Label formatting from measured product data | Original food-packaging station, text-field contract, and print handshake. | `product_weighed, printer_ready, label_data_valid` | `print_request, label_applied` | A label request is issued only when the product data and printer are ready. | `lab-10-02-chicken-label-print.plcscene` |
| 10.3 | Vision Package Sorter | Vision-camera package sorting | Original package classes, lane layout, and result-valid state. | `package_present, vision_result_valid, destination_clear` | `sort_conveyor_run, diverter_enable` | Sorting is enabled only for a present package with a valid vision result and clear destination. | `lab-10-03-vision-package-sorter.plcscene` |
| 10.4 | Motor Operating-State Enum | ENUM for motor operating state | Original motor state names, state transition inputs, and safe fallback. | `start_request, stop_request, fault_active` | `motor_running, state_valid` | A fault or stop request dominates start and leaves the motor in a safe stopped state. | `lab-10-04-motor-enum-state.plcscene` |
| 10.5 | Motor STRUCT Data | STRUCT for motor data | Original structured record fields, validation handshake, and diagnostic indication. | `motor_record_valid, temperature_valid, alarm_clear` | `motor_enable, record_ready` | The motor record is accepted only when its required fields are valid and alarms are clear. | `lab-10-05-motor-struct-data.plcscene` |
| 10.6 | Ten-Motor Array Startup | ARRAY and FOR loop motor startup | Original ten-motor lineup, staggered timing, and group alarm behavior. | `group_start_request, all_motors_ready, group_alarm_clear` | `motor_array_run, startup_sequence_active` | The array starts in order with a delay between motors and stops safely on a group alarm. | `lab-10-06-ten-motor-array-startup.plcscene` |
| 11.6 | Wastewater Collection | Multiple collection tanks and shared outlet | Original collection cell, level policy, and treatment permissive. | `source_level_high, treatment_ready, outlet_clear` | `transfer_pump_run, outlet_valve_open` | The pump and outlet valve run only when a source requires service and treatment is ready. | `lab-11-06-wastewater-collection.plcscene` |
| 11.7 | Multi-Conveyor Pallet Route | Multiple modular conveyor belts | Original zone layout, handoff signals, and energy-save stop behavior. | `zone_1_clear, zone_2_clear, zone_3_clear` | `zone_1_run, zone_2_run, zone_3_run` | A blocked zone removes the affected run command while preserving a diagnosable handoff state. | `lab-11-07-multi-conveyor-pallet-route.plcscene` |
| 11.11 | Service Elevator | Elevator control with floor requests | Original lift cell, landing handshakes, and door permissive. | `call_valid, doors_closed, landing_clear` | `lift_up_cmd, lift_down_cmd` | The elevator receives one direction command only when the doors are closed and the landing is clear. | `lab-11-11-service-elevator.plcscene` |
| 11.12 | Mobile Traffic Lights | Portable traffic-light synchronization | Original paired signal state machine and synchronization handshake. | `controller_ready, road_a_clear, road_b_clear` | `road_a_green, road_b_green` | Only one road receives a green command at a time, and both roads stop on a fault. | `lab-11-12-mobile-traffic-lights.plcscene` |
| 11.13 | XY Palletizing Cell | XY robot palletizing | Original pallet pattern, transfer handshake, and position contract. | `carton_at_pick, gantry_home, pallet_position_valid` | `vacuum_pick, gantry_cycle, layer_complete` | A carton is picked only at home and placed only at a valid pallet position. | `lab-11-13-xy-palletizing.plcscene` |
| 11.19 | Powder Batch Mixer | Powder batch mixing process | Original hopper arrangement, recipe handshake, and batch-complete contract. | `recipe_valid, dose_complete, mixer_ready` | `dose_run, mixer_run, discharge_valve_open` | Dosing precedes mixing, and discharge is permitted only after a complete batch. | `lab-11-19-powder-batch-mixer.plcscene` |

## Completed authored assets

These lesson-specific assets are implemented as reusable static training
accessories. PLC behavior remains defined by the scene's symbolic simulation
points; the accessory is visual and does not invent live I/O behavior.

| Authored asset | First training module | Implementation |
|---|---|---|
| safety light-curtain pair | Guarded Pallet Transfer | Reusable static training accessory included in the scene with a stable visual contract. |
| guarded access gate | Guarded Pallet Transfer | Reusable static training accessory included in the scene with a stable visual contract. |
| safety relay/status beacon | Guarded Pallet Transfer | Reusable static training accessory included in the scene with a stable visual contract. |
| machine-guarding fence | Robot Cell Safe Restart | Reusable static training accessory included in the scene with a stable visual contract. |
| coded safety gate switch | Robot Cell Safe Restart | Reusable static training accessory included in the scene with a stable visual contract. |
| emergency-stop station | Robot Cell Safe Restart | Reusable static training accessory included in the scene with a stable visual contract. |
| robot controller/status panel | Robot Cell Safe Restart | Reusable static training accessory included in the scene with a stable visual contract. |
| vehicle/load asset | Parking Garage Entry | Reusable static training accessory included in the scene with a stable visual contract. |
| parking barrier arm | Parking Garage Entry | Reusable static training accessory included in the scene with a stable visual contract. |
| occupancy counter display | Parking Garage Entry | Reusable static training accessory included in the scene with a stable visual contract. |
| powered roller conveyor | Package Grouping Station | Reusable static training accessory included in the scene with a stable visual contract. |
| package spacing sensor | Package Grouping Station | Reusable static training accessory included in the scene with a stable visual contract. |
| pallet receiver | Package Grouping Station | Reusable static training accessory included in the scene with a stable visual contract. |
| guided group stop | Package Grouping Station | Reusable static training accessory included in the scene with a stable visual contract. |
| chain conveyor | Chain-Drive Lift | Reusable static training accessory included in the scene with a stable visual contract. |
| chain hoist/vertical lift | Chain-Drive Lift | Reusable static training accessory included in the scene with a stable visual contract. |
| lift limit switches | Chain-Drive Lift | Reusable static training accessory included in the scene with a stable visual contract. |
| mechanical stop | Chain-Drive Lift | Reusable static training accessory included in the scene with a stable visual contract. |
| food product load | Chicken Label Print | Reusable static training accessory included in the scene with a stable visual contract. |
| indexing conveyor | Cookie Packaging Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| packaging machine | Cookie Packaging Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| product counter | Cookie Packaging Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| barrel/container load | Barrel Fill Station | Reusable static training accessory included in the scene with a stable visual contract. |
| flow meter | Barrel Fill Station | Reusable static training accessory included in the scene with a stable visual contract. |
| fill nozzle | Barrel Fill Station | Reusable static training accessory included in the scene with a stable visual contract. |
| payoff reel | Cable Cut-Length Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| cable dancer | Cable Cut-Length Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| length encoder | Cable Cut-Length Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| cable cutter | Cable Cut-Length Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| cut-length display | Cable Cut-Length Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| traffic signal head | Pedestrian Crossing | Reusable static training accessory included in the scene with a stable visual contract. |
| pedestrian signal head | Pedestrian Crossing | Reusable static training accessory included in the scene with a stable visual contract. |
| crosswalk/road module | Pedestrian Crossing | Reusable static training accessory included in the scene with a stable visual contract. |
| drawbridge deck | Drawbridge Control | Reusable static training accessory included in the scene with a stable visual contract. |
| road barrier | Drawbridge Control | Reusable static training accessory included in the scene with a stable visual contract. |
| bridge limit switches | Drawbridge Control | Reusable static training accessory included in the scene with a stable visual contract. |
| bag product load | Bag Indexing Conveyor | Reusable static training accessory included in the scene with a stable visual contract. |
| reversible drive | Bag Indexing Conveyor | Reusable static training accessory included in the scene with a stable visual contract. |
| manual pause station | Bag Indexing Conveyor | Reusable static training accessory included in the scene with a stable visual contract. |
| coating enclosure | Coating Line | Reusable static training accessory included in the scene with a stable visual contract. |
| spray head | Coating Line | Reusable static training accessory included in the scene with a stable visual contract. |
| workpiece load | Coating Line | Reusable static training accessory included in the scene with a stable visual contract. |
| ventilation damper | Coating Line | Reusable static training accessory included in the scene with a stable visual contract. |
| scale/load-cell platform | Luggage Weight Sort | Reusable static training accessory included in the scene with a stable visual contract. |
| luggage load | Luggage Weight Sort | Reusable static training accessory included in the scene with a stable visual contract. |
| weight display | Luggage Weight Sort | Reusable static training accessory included in the scene with a stable visual contract. |
| reject diverter | Luggage Weight Sort | Reusable static training accessory included in the scene with a stable visual contract. |
| hand-presence sensor | Timed Hand-Dryer | Reusable static training accessory included in the scene with a stable visual contract. |
| air outlet | Timed Hand-Dryer | Reusable static training accessory included in the scene with a stable visual contract. |
| heating element | Timed Hand-Dryer | Reusable static training accessory included in the scene with a stable visual contract. |
| progress display | Timed Hand-Dryer | Reusable static training accessory included in the scene with a stable visual contract. |
| function-block calculation panel | Product Function Block | Reusable static training accessory included in the scene with a stable visual contract. |
| numeric result display | Product Function Block | Reusable static training accessory included in the scene with a stable visual contract. |
| function-block panel | Function Selector | Reusable static training accessory included in the scene with a stable visual contract. |
| numeric selector/display | Function Selector | Reusable static training accessory included in the scene with a stable visual contract. |
| dimension sensors | Box Volume Calculation | Reusable static training accessory included in the scene with a stable visual contract. |
| numeric measurement display | Box Volume Calculation | Reusable static training accessory included in the scene with a stable visual contract. |
| pallet load | Pallet Count Function | Reusable static training accessory included in the scene with a stable visual contract. |
| pallet-type sensor | Pallet Count Function | Reusable static training accessory included in the scene with a stable visual contract. |
| count display | Pallet Count Function | Reusable static training accessory included in the scene with a stable visual contract. |
| EV/charger bay | EV Charging Manager | Reusable static training accessory included in the scene with a stable visual contract. |
| connector latch | EV Charging Manager | Reusable static training accessory included in the scene with a stable visual contract. |
| energy meter | EV Charging Manager | Reusable static training accessory included in the scene with a stable visual contract. |
| pulse-output meter | EV Charging Manager | Reusable static training accessory included in the scene with a stable visual contract. |
| authorization reader | EV Charging Manager | Reusable static training accessory included in the scene with a stable visual contract. |
| VFD diagnostic panel | Drive Alarm-Code String | Reusable static training accessory included in the scene with a stable visual contract. |
| fieldbus alarm-string display | Drive Alarm-Code String | Reusable static training accessory included in the scene with a stable visual contract. |
| drive status indicator | Drive Alarm-Code String | Reusable static training accessory included in the scene with a stable visual contract. |
| checkweigher | Chicken Label Print | Reusable static training accessory included in the scene with a stable visual contract. |
| label printer | Chicken Label Print | Reusable static training accessory included in the scene with a stable visual contract. |
| formatted label display | Chicken Label Print | Reusable static training accessory included in the scene with a stable visual contract. |
| industrial vision camera | Vision Package Sorter | Reusable static training accessory included in the scene with a stable visual contract. |
| package-class result display | Vision Package Sorter | Reusable static training accessory included in the scene with a stable visual contract. |
| four-lane diverter | Vision Package Sorter | Reusable static training accessory included in the scene with a stable visual contract. |
| destination conveyor bank | Vision Package Sorter | Reusable static training accessory included in the scene with a stable visual contract. |
| motor diagnostic faceplate | Motor STRUCT Data | Reusable static training accessory included in the scene with a stable visual contract. |
| temperature display | Motor STRUCT Data | Reusable static training accessory included in the scene with a stable visual contract. |
| structured-data monitor | Motor STRUCT Data | Reusable static training accessory included in the scene with a stable visual contract. |
| ten-motor lineup asset | Ten-Motor Array Startup | Reusable static training accessory included in the scene with a stable visual contract. |
| group motor status panel | Ten-Motor Array Startup | Reusable static training accessory included in the scene with a stable visual contract. |
| staggered-start sequence display | Ten-Motor Array Startup | Reusable static training accessory included in the scene with a stable visual contract. |
| collection tank bank | Wastewater Collection | Reusable static training accessory included in the scene with a stable visual contract. |
| level transmitters | Wastewater Collection | Reusable static training accessory included in the scene with a stable visual contract. |
| pipe manifold | Wastewater Collection | Reusable static training accessory included in the scene with a stable visual contract. |
| alarm beacon | Wastewater Collection | Reusable static training accessory included in the scene with a stable visual contract. |
| pallet roller conveyor zone | Multi-Conveyor Pallet Route | Reusable static training accessory included in the scene with a stable visual contract. |
| zone handoff sensor | Multi-Conveyor Pallet Route | Reusable static training accessory included in the scene with a stable visual contract. |
| common stop station | Multi-Conveyor Pallet Route | Reusable static training accessory included in the scene with a stable visual contract. |
| elevator car/shaft | Service Elevator | Reusable static training accessory included in the scene with a stable visual contract. |
| floor call station | Service Elevator | Reusable static training accessory included in the scene with a stable visual contract. |
| landing door | Service Elevator | Reusable static training accessory included in the scene with a stable visual contract. |
| floor-position sensor | Service Elevator | Reusable static training accessory included in the scene with a stable visual contract. |
| mobile traffic signal head | Mobile Traffic Lights | Reusable static training accessory included in the scene with a stable visual contract. |
| roadway module | Mobile Traffic Lights | Reusable static training accessory included in the scene with a stable visual contract. |
| signal synchronization link | Mobile Traffic Lights | Reusable static training accessory included in the scene with a stable visual contract. |
| XY gantry | XY Palletizing Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| vacuum gripper | XY Palletizing Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| pallet magazine | XY Palletizing Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| carton load | XY Palletizing Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| coordinate sensors | XY Palletizing Cell | Reusable static training accessory included in the scene with a stable visual contract. |
| bulk powder hopper | Powder Batch Mixer | Reusable static training accessory included in the scene with a stable visual contract. |
| slide-gate feeder | Powder Batch Mixer | Reusable static training accessory included in the scene with a stable visual contract. |
| load cell | Powder Batch Mixer | Reusable static training accessory included in the scene with a stable visual contract. |
| recipe selector | Powder Batch Mixer | Reusable static training accessory included in the scene with a stable visual contract. |
| powder discharge chute | Powder Batch Mixer | Reusable static training accessory included in the scene with a stable visual contract. |

## Reusable assets added

- `rotarySwitch`: configurable 2- to N-position selector.
- `liftTable`: animated scissor lift with normalized travel.
- `valve`: animated valve stem, handwheel, and flow lamp.
- `drillPress`: animated drill head and spindle.
- `robotArm`: reusable articulated robot with normalized pose.
- `rollerShutter`: animated slatted service door with drive.
- `rotaryTable`: indexed routing table.
- `machine`: reusable enclosed process-machine cabinet with run indication.

## Verification contract

Every generated scene contains machine-readable `verification.cases`.
`tools/verify_training_scenes.mjs` loads the same scene files through the
production validator, builds every 3D asset through the shared factory, runs
the declared actions and simulated time, and asserts the expected final tags.
Browser acceptance remains a separate rendering and interaction gate.

## In-player learning guides

Every generated training scene also contains three progressive hints and one
explicit reference solution. The player derives **Configuration** directly
from `simulation.points`; simulator-only values and PLC memory bits are
excluded from the external tag list. This keeps the tag contract separate from
the hints and answer while preventing tag-name or data-type drift.
