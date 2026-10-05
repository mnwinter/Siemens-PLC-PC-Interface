using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Godot;
using RungProof.Next.Scenes;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyNumericSceneOutputTypes(Action<bool, string> check)
    {
        using var definition = JsonDocument.Parse("""
            {"type":"booleanPanel","points":[
              {"name":"integer","type":"INT","owner":"PLC","initial":0,"role":"output"},
              {"name":"double_integer","type":"DINT","owner":"PLC","initial":0,"role":"output"},
              {"name":"real","type":"REAL","owner":"PLC","initial":0.0,"role":"output"}]}
            """);
        var root = new Node3D();
        var runtime = new SceneSimulationRuntime(definition.RootElement, root);
        try
        {
            runtime.ResetSimulation();
            runtime.CommitVirtualControllerNumericOutputs(new Dictionary<string, double>
            { ["integer"] = double.MaxValue, ["double_integer"] = double.MinValue, ["real"] = 1.25 });
            var upperInt = Equals(runtime.Points["integer"], (long)short.MaxValue);
            var lowerDInt = Equals(runtime.Points["double_integer"], (long)int.MinValue);
            check(runtime.Points["real"] is double number && number == 1.25,
                "scene_real_output_remains_double_without_integer_truncation");
            runtime.CommitVirtualControllerNumericOutputs(new Dictionary<string, double>
            { ["integer"] = double.MinValue, ["double_integer"] = double.MaxValue });
            var lowerInt = Equals(runtime.Points["integer"], (long)short.MinValue);
            var upperDInt = Equals(runtime.Points["double_integer"], (long)int.MaxValue);
            runtime.CommitVirtualControllerNumericOutputs(new Dictionary<string, double>
            { ["integer"] = 1.9, ["double_integer"] = -1.9 });
            check(upperInt && lowerInt && Equals(runtime.Points["integer"], 1L),
                "scene_int_output_is_boxed_integer_truncated_and_range_clamped");
            check(lowerDInt && upperDInt && Equals(runtime.Points["double_integer"], -1L),
                "scene_dint_output_is_boxed_integer_truncated_and_range_clamped");
        }
        finally { runtime.Free(); root.Free(); }
    }

    private void VerifyPalletCountReadoutWorkflow(Action<bool, string> check)
    {
        AddMigratedScene("lab-9-11-pallet-counting", _candidateCatalog!, _mainCamera!, false, false);
        var display = _sceneCompositionRoot!.GetNode<Node3D>("training_accessory_6");
        var readout = display.GetNodeOrNull<Label3D>("NumericReadout");
        check(readout?.Text == "COUNT\n0"
            && display.FindChild("COUNT_DISPLAY_static_legend", true, false) is MeshInstance3D { Visible: false },
            "pallet_count_live_readout_replaces_static_legend_at_initial_zero");
        AuthoredDemoLadderPrograms.TryCreate("lab-9-11-pallet-counting", out var document);
        EnableVirtualControllerProgram(document.BuildProgram());
        try
        {
            var runtime = _sceneRuntime!;
            _virtualController!.Run();
            runtime.ExecuteAction("toggle-count_request");
            _PhysicsProcess(0.04);
            runtime.ExecuteAction("toggle-pallet_detected");
            _PhysicsProcess(0.04);
            GD.Print($"PALLET_COUNT_READOUT_PROBE type={runtime.Points["pallet_count"]?.GetType().Name} value={runtime.Points["pallet_count"]} text={readout?.Text.Replace('\n', '|')}");
            check(Equals(runtime.Points["pallet_count"], 0L) && readout?.Text == "COUNT\n0",
                "pallet_count_invalid_type_event_is_not_published_as_a_count");
            runtime.ExecuteAction("toggle-pallet_type_valid");
            _PhysicsProcess(0.04);
            check(Equals(runtime.Points["pallet_count"], 0L) && readout?.Text == "COUNT\n0",
                "pallet_count_later_permissive_does_not_recount_held_detection");
            var correct = true;
            for (var count = 1; count <= 5; count++)
            {
                runtime.ExecuteAction("toggle-pallet_detected"); // release old detection
                _PhysicsProcess(0.04);
                runtime.ExecuteAction("toggle-pallet_detected"); // next detection edge
                _PhysicsProcess(0.04);
                correct &= Equals(runtime.Points["pallet_count"], (long)count)
                    && readout?.Text == $"COUNT\n{count}"
                    && Equals(runtime.Points["pallet_count_valid"], count == 5);
            }
            check(correct, "pallet_count_five_valid_scene_edges_publish_same_scan_count_and_readout");
            _PhysicsProcess(1.0);
            check(Equals(runtime.Points["pallet_count"], 5L) && readout?.Text == "COUNT\n5",
                "pallet_count_held_detection_keeps_five_on_display");
            runtime.ExecuteAction("toggle-pallet_type_valid");
            _PhysicsProcess(0.04);
            check(runtime.Points["pallet_count_valid"] is false
                && Equals(runtime.Points["pallet_count"], 5L) && readout?.Text == "COUNT\n5",
                "pallet_count_permissive_loss_clears_validity_without_erasing_count");
            CommitVirtualControllerSnapshot(_virtualController.Stop());
            check(Equals(runtime.Points["pallet_count"], 0L) && readout?.Text == "COUNT\n0"
                && _virtualController.Snapshot.Counters["batch_count"].Accumulated == 5,
                "pallet_count_stop_clears_numeric_output_image_and_retains_counter_memory");
            _virtualController.Run();
            _PhysicsProcess(0.04);
            check(Equals(runtime.Points["pallet_count"], 5L) && readout?.Text == "COUNT\n5",
                "pallet_count_run_republishes_retained_counter_without_new_event");
            runtime.ResetSimulation();
            CommitVirtualControllerSnapshot(_virtualController.Reset());
            check(Equals(runtime.Points["pallet_count"], 0L) && readout?.Text == "COUNT\n0"
                && runtime.Points["pallet_detected"] is false && runtime.Points["pallet_count_valid"] is false
                && _virtualController.Snapshot.Counters["batch_count"].Accumulated == 0,
                "pallet_count_reset_clears_readout_inputs_outputs_and_memory");
        }
        finally { DisableVirtualController(); }
    }

    private void VerifyPalletCountPropGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-9-11-pallet-counting", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var fixture = root.GetNode<Node3D>("training_accessory_5");
        var display = root.GetNode<Node3D>("training_accessory_6");
        var fixtureMeshes = ReviewMeshes(fixture);
        var displayMeshes = ReviewMeshes(display);
        check(fixtureMeshes.Count(mesh => mesh.Name.ToString().StartsWith("PROFILE_head_", StringComparison.Ordinal)) == 4
            && fixture.FindChild("PROFILE_crossbeam", true, false) is not null
            && !fixtureMeshes.Any(mesh => mesh.Name.ToString().Contains("PALLET", StringComparison.OrdinalIgnoreCase)),
            "pallet_count_fixture_is_optical_profile_geometry_not_pallet");
        check(display.FindChild("COUNT_DISPLAY_screen", true, false) is not null
            && display.FindChild("COUNT_DISPLAY_static_legend", true, false) is not null
            && display.FindChild("KIN_bottom_bar", true, false) is null,
            "pallet_count_display_is_static_readout_not_shutter");
        var feet = fixtureMeshes.Where(mesh => mesh.Name.ToString().StartsWith("PROFILE_foot_", StringComparison.Ordinal)).ToArray();
        var posts = fixtureMeshes.Where(mesh => mesh.Name.ToString().StartsWith("PROFILE_post_", StringComparison.Ordinal)).ToArray();
        check(feet.Length == 2 && posts.Length == 2
            && feet.All(foot => MathF.Abs(ReviewBounds(foot).Position.Y) < 0.001f)
            && posts.All(post => feet.Any(foot => ReviewBounds(post).Intersects(ReviewBounds(foot).Grow(0.001f)))),
            "pallet_count_profile_posts_seated_on_grounded_feet");
        var baseMesh = (MeshInstance3D)display.FindChild("COUNT_DISPLAY_base", true, false);
        var mast = (MeshInstance3D)display.FindChild("COUNT_DISPLAY_mast", true, false);
        var housing = (MeshInstance3D)display.FindChild("COUNT_DISPLAY_housing", true, false);
        check(MathF.Abs(ReviewBounds(baseMesh).Position.Y) < 0.001f
            && ReviewBounds(mast).Intersects(ReviewBounds(baseMesh).Grow(0.001f))
            && ReviewBounds(mast).Intersects(ReviewBounds(housing)),
            "pallet_count_readout_mast_seated_on_base_and_housing");
        bool Clear(MeshInstance3D a, MeshInstance3D b)
        {
            var overlap = ReviewBounds(a).Intersection(ReviewBounds(b)).Size;
            return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f || !OrientedBoxesPenetrate(a, b);
        }
        var otherSolids = root.GetChildren().OfType<Node3D>().Where(node => node != fixture && node != display)
            .SelectMany(ReviewMeshes).ToArray();
        foreach (var part in fixtureMeshes)
            foreach (var other in otherSolids.Where(other => !Clear(part, other)))
                GD.Print($"PALLET_PROFILE_COLLISION {part.Name} {other.GetParent().Name}/{other.Name} {ReviewBounds(part)} {ReviewBounds(other)}");
        check(fixtureMeshes.All(part => otherSolids.All(other => Clear(part, other))),
            "pallet_count_profile_fixture_clear_of_conveyor_carton_and_other_equipment");
        check(displayMeshes.All(part => otherSolids.Concat(fixtureMeshes).All(other => Clear(part, other))),
            "pallet_count_readout_clear_of_separate_equipment");
    }

    private void VerifyCutLengthDisplayGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-4-12-cable-cut-length", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var display = root.GetNode<Node3D>("training_accessory_8");
        check(display.FindChild("LENGTH_DISPLAY_screen", true, false) is not null
            && display.FindChild("LENGTH_DISPLAY_static_legend", true, false) is not null
            && display.FindChild("KIN_bottom_bar", true, false) is null,
            "cut_length_display_is_readout_not_shutter");
        var baseMesh = (MeshInstance3D)display.FindChild("LENGTH_DISPLAY_base", true, false);
        var mast = (MeshInstance3D)display.FindChild("LENGTH_DISPLAY_mast", true, false);
        var housing = (MeshInstance3D)display.FindChild("LENGTH_DISPLAY_housing", true, false);
        check(MathF.Abs(ReviewBounds(baseMesh).Position.Y) < 0.001f
            && ReviewBounds(mast).Intersects(ReviewBounds(baseMesh).Grow(0.001f))
            && ReviewBounds(mast).Intersects(ReviewBounds(housing)),
            "cut_length_display_grounded_and_housing_supported");
        var others = root.GetChildren().OfType<Node3D>().Where(node => node != display).SelectMany(ReviewMeshes).ToArray();
        bool Clear(MeshInstance3D part, MeshInstance3D other)
        {
            var overlap = ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
            return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f || !OrientedBoxesPenetrate(part, other);
        }
        check(ReviewMeshes(display).All(part => others.All(other => Clear(part, other))),
            "cut_length_display_clear_of_separate_equipment");
        var labels = new[] { "CABLE", "LENGTH", "HOME" };
        check(labels.Select((label, index) => root.GetNode<Node3D>($"switch_{index + 9}")
                .FindChild("OperatorFaceLabel", true, false) is Label3D plate && plate.Text == label).All(value => value),
            "cut_length_manual_input_plates_match_their_functions");
    }

    private void VerifyStaticTrainingReadouts(Action<bool, string> check)
    {
        foreach (var (sceneId, displayId) in new[]
        {
            ("lab-4-07-parking-garage-entry", "training_accessory_6"),
            ("lab-6-08-hand-dryer", "training_accessory_6"),
            ("lab-6-07-luggage-weight-sort", "training_accessory_6"),
            ("lab-9-04-function-selector", "training_accessory_4"),
            ("lab-9-10-box-volume", "training_accessory_4")
        })
        {
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var display = root.GetNode<Node3D>(displayId);
            var parts = ReviewMeshes(display);
            check(display.FindChild("STATIC_READOUT_screen", true, false) is not null
                && display.FindChild("STATIC_READOUT_static_legend", true, false) is not null
                && display.FindChild("KIN_bottom_bar", true, false) is null
                && display.FindChild("KIN_selector_handle", true, false) is null,
                $"{sceneId}_static_readout_identity_without_shutter_or_selector");
            var baseMesh = (MeshInstance3D)display.FindChild("STATIC_READOUT_base", true, false);
            var mast = (MeshInstance3D)display.FindChild("STATIC_READOUT_mast", true, false);
            var housing = (MeshInstance3D)display.FindChild("STATIC_READOUT_housing", true, false);
            check(MathF.Abs(ReviewBounds(baseMesh).Position.Y) < 0.001f
                && ReviewBounds(mast).Intersects(ReviewBounds(baseMesh).Grow(0.001f))
                && ReviewBounds(mast).Intersects(ReviewBounds(housing)),
                $"{sceneId}_static_readout_grounded_and_supported");
            var others = root.GetChildren().OfType<Node3D>().Where(node => node != display).SelectMany(ReviewMeshes).ToArray();
            bool Clear(MeshInstance3D part, MeshInstance3D other)
            {
                var overlap = ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
                return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f || !OrientedBoxesPenetrate(part, other);
            }
            foreach (var part in parts)
                foreach (var other in others.Where(other => !Clear(part, other)))
                    GD.Print($"STATIC_READOUT_COLLISION {sceneId} {part.Name} {other.GetParent().Name}/{other.Name} {ReviewBounds(part)} {ReviewBounds(other)}");
            check(parts.All(part => others.All(other => Clear(part, other))),
                $"{sceneId}_static_readout_clear_of_separate_equipment");
        }
    }

    private void VerifyArithmeticValidityLayouts(Action<bool, string> check)
    {
        foreach (var (sceneId, firstId, firstLabel, secondLabel) in new[]
        {
            ("lab-9-01-sum-function", "switch_1", "A VALID", "B VALID"),
            ("lab-9-02-product-function", "switch_1", "A VALID", "B VALID"),
            ("lab-9-04-function-selector", "switch_0", "OPERANDS", "FUNC VALID")
        })
        {
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            // These scenes retain Boolean validity inputs. Neither a CNC nor
            // a bearing mislabeled as a calculation panel participates in them.
            check(root.GetNodeOrNull<Node3D>("machine_0") is null
                && root.GetNodeOrNull<Node3D>("machine_1") is null
                && root.GetNodeOrNull<Node3D>("training_accessory_3") is null,
                $"{sceneId}_unrelated_cnc_and_bearing_props_removed");
            check(new[] { (firstId, firstLabel), ("switch_5", secondLabel), ("switch_6", "CALCULATE") }
                .All(item => root.GetNode<Node3D>(item.Item1).FindChild("OperatorFaceLabel", true, false)
                    is Label3D label && label.Text == item.Item2),
                $"{sceneId}_manual_input_plates_match_validity_and_request");
        }
    }

    private void VerifyArithmeticNumericWorkflows(Action<bool, string> check)
    {
        foreach (var (sceneId, referenceName, inputPrefix, result, label, expected) in new[]
        {
            ("lab-9-01-sum-function", "sum", "operand", "sum_result", "SUM", 7L),
            ("lab-9-02-product-function", "product", "factor", "product_result", "PRODUCT", 10L)
        })
        {
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var runtime = _sceneRuntime!;
            Label3D Readout(string id) => root.GetNode<Node3D>(id).GetNode<Label3D>("NumericReadout");
            var displays = new[] { "numeric_display_0", "numeric_display_1", "training_accessory_4" };
            check(displays.All(id => Readout(id).Text.EndsWith("\n0", StringComparison.Ordinal))
                && root.GetNode<Node3D>("training_accessory_4").FindChild("STATIC_READOUT_static_legend", true, false) is null,
                $"{sceneId}_initial_live_numeric_readouts");
            bool Clear(MeshInstance3D a, MeshInstance3D b)
            {
                var overlap = ReviewBounds(a).Intersection(ReviewBounds(b)).Size;
                return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f || !OrientedBoxesPenetrate(a, b);
            }
            var equipment = root.GetChildren().OfType<Node3D>().ToArray();
            check(equipment.All(a => equipment.Where(b => b != a)
                .All(b => ReviewMeshes(a).All(am => ReviewMeshes(b).All(bm => Clear(am, bm))))),
                $"{sceneId}_separate_equipment_clearance");
            var reference = LadderEditorProjectJson.Load(FileAccess.GetFileAsString(
                $"res://programs/examples/09-{referenceName}-function-reference.rpproj.json"));
            check(reference.IsReadable, $"{sceneId}_reference_readable");
            if (reference.Document is null) throw new InvalidOperationException($"Unreadable arithmetic reference: {sceneId}");
            EnableVirtualControllerProgram(reference.Document.BuildProgram());
            try
            {
                _virtualController!.Run();
                void Scan() => _PhysicsProcess(0.04);
                void Toggle(string point) { runtime.ExecuteAction("toggle-" + point); Scan(); }
                var a = inputPrefix + "_a";
                var b = inputPrefix + "_b";
                runtime.ExecuteAction("cycle-" + a); runtime.ExecuteAction("cycle-" + a);
                for (var i = 0; i < 3; i++) runtime.ExecuteAction("cycle-" + b);
                Scan();
                check(Readout(displays[0]).Text == "A NEXT\n2" && Readout(displays[1]).Text == "B NEXT\n5",
                    $"{sceneId}_pc_numeric_cycles_update_readouts");
                Toggle("calculate_request"); Toggle(a + "_valid");
                check(runtime.Points[result + "_valid"] is false && Equals(runtime.Points[result], 0L),
                    $"{sceneId}_missing_b_valid_blocks_calculation");
                Toggle(b + "_valid");
                check(runtime.Points[result + "_valid"] is true && Equals(runtime.Points[result], expected)
                    && Readout(displays[2]).Text == $"{label}\n{expected}",
                    $"{sceneId}_valid_calculation_publishes_same_scan_result");
                runtime.ExecuteAction("cycle-" + a); Scan(); // A: 2 -> 5
                var updated = referenceName == "sum" ? 10L : 25L;
                check(Equals(runtime.Points[result], updated) && Readout(displays[2]).Text == $"{label}\n{updated}",
                    $"{sceneId}_changed_operand_recalculates_live_result");
                Toggle(a + "_valid");
                check(runtime.Points[result + "_valid"] is false && Equals(runtime.Points[result], updated),
                    $"{sceneId}_permissive_loss_clears_validity_retains_result");
                CommitVirtualControllerSnapshot(_virtualController.Stop());
                check(Readout(displays[2]).Text == $"{label}\n0" && runtime.Points[result + "_valid"] is false,
                    $"{sceneId}_stop_clears_output_image");
                _virtualController.Run(); Scan();
                check(Equals(runtime.Points[result], 0L) && runtime.Points[result + "_valid"] is false,
                    $"{sceneId}_restart_with_missing_permissive_keeps_result_zero");
                Toggle(a + "_valid");
                check(Equals(runtime.Points[result], updated) && runtime.Points[result + "_valid"] is true,
                    $"{sceneId}_restored_permissive_recalculates");
                runtime.ResetSimulation(); CommitVirtualControllerSnapshot(_virtualController.Reset());
                check(displays.All(id => Readout(id).Text.EndsWith("\n0", StringComparison.Ordinal))
                    && runtime.Points["calculate_request"] is false && runtime.Points[result + "_valid"] is false,
                    $"{sceneId}_reset_clears_manual_inputs_and_numeric_values");
            }
            finally { DisableVirtualController(); }
        }
    }

    private void VerifySumCounterWorkflow(Action<bool, string> check)
    {
        AddMigratedScene("lab-9-03-sum-and-counter-function", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        Label3D Readout(int index) => root.GetNode<Node3D>($"numeric_display_{index}").GetNode<Label3D>("NumericReadout");
        check(root.GetNodeOrNull<Node3D>("machine_0") is null
            && Enumerable.Range(0, 4).All(i => Readout(i).Text.EndsWith("\n0", StringComparison.Ordinal)),
            "sum_counter_initial_live_readouts_and_no_unbound_cnc");
        bool Clear(MeshInstance3D a, MeshInstance3D b)
        {
            var overlap = ReviewBounds(a).Intersection(ReviewBounds(b)).Size;
            return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f || !OrientedBoxesPenetrate(a, b);
        }
        var equipment = root.GetChildren().OfType<Node3D>().ToArray();
        check(equipment.All(a => equipment.Where(b => b != a)
            .All(b => ReviewMeshes(a).All(am => ReviewMeshes(b).All(bm => Clear(am, bm))))),
            "sum_counter_separate_equipment_clearance");
        var reference = LadderEditorProjectJson.Load(FileAccess.GetFileAsString(
            "res://programs/examples/09-sum-counter-reference.rpproj.json"));
        check(reference.IsReadable, "sum_counter_opt_in_reference_project_readable");
        if (reference.Document is null) throw new InvalidOperationException("Sum/counter reference is unreadable.");
        EnableVirtualControllerProgram(reference.Document.BuildProgram());
        try
        {
            _virtualController!.Run();
            void Scan() => _PhysicsProcess(0.04);
            void Toggle(string point) { runtime.ExecuteAction("toggle-" + point); Scan(); }
            runtime.ExecuteAction("cycle-operand_a"); runtime.ExecuteAction("cycle-operand_a");
            for (var i = 0; i < 3; i++) runtime.ExecuteAction("cycle-operand_b");
            Scan();
            check(Readout(0).Text == "A NEXT\n2" && Readout(1).Text == "B NEXT\n5",
                "sum_counter_pc_operand_cycles_update_live_readouts");
            Toggle("call_complete"); // Invalid event; no permissives yet.
            Toggle("inputs_valid"); Toggle("calculate_request");
            check(Equals(runtime.Points["event_count"], 0L),
                "sum_counter_later_permissive_does_not_count_held_invalid_completion");
            Toggle("call_complete"); Toggle("call_complete");
            check(Equals(runtime.Points["sum_result"], 7L) && Readout(2).Text == "SUM\n7"
                && Equals(runtime.Points["event_count"], 1L) && Readout(3).Text == "COUNT\n1",
                "sum_counter_valid_edge_publishes_sum_and_same_scan_count");
            _PhysicsProcess(1.0);
            check(Equals(runtime.Points["event_count"], 1L), "sum_counter_held_completion_does_not_recount");
            Toggle("inputs_valid");
            check(runtime.Points["result_valid"] is false && Equals(runtime.Points["event_count"], 1L),
                "sum_counter_permissive_loss_clears_validity_preserves_count");
            CommitVirtualControllerSnapshot(_virtualController.Stop());
            check(Readout(2).Text == "SUM\n0" && Readout(3).Text == "COUNT\n0"
                && _virtualController.Snapshot.Counters["completed_calls"].Accumulated == 1,
                "sum_counter_stop_zeroes_output_image_preserves_counter_memory");
            _virtualController.Run(); Scan();
            check(Readout(3).Text == "COUNT\n1", "sum_counter_run_republishes_retained_count");
            runtime.ResetSimulation(); CommitVirtualControllerSnapshot(_virtualController.Reset());
            check(Enumerable.Range(0, 4).All(i => Readout(i).Text.EndsWith("\n0", StringComparison.Ordinal))
                && runtime.Points["call_complete"] is false
                && _virtualController.Snapshot.Counters["completed_calls"].Accumulated == 0,
                "sum_counter_reset_clears_operands_inputs_outputs_and_memory");
        }
        finally { DisableVirtualController(); }
    }

    private void VerifyRadarMountAndBeam(Action<bool, string> check)
    {
        AddMigratedScene("tank-radar", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var tank = root.GetNode<Node3D>("water_tank_radar");
        var transmitter = root.GetNode<Node3D>("radar_transmitter");
        var roof = (MeshInstance3D)tank.FindChild("TANK_roof", true, false);
        var flange = (MeshInstance3D)transmitter.FindChild("PROCESS_flange", true, false);
        var lens = (MeshInstance3D)transmitter.FindChild("ANTENNA_dielectric_lens", true, false);
        var head = (MeshInstance3D)transmitter.FindChild("RADAR_head", true, false);
        var beam = (MeshInstance3D)transmitter.FindChild("KIN_radar_beam", true, false);
        var liquid = (MeshInstance3D)tank.FindChild("KIN_liquid", true, false);
        var shell = (MeshInstance3D)tank.FindChild("TANK_shell", true, false);
        GD.Print($"RADAR_MOUNT roof={ReviewBounds(roof)} flange={ReviewBounds(flange)} head={ReviewBounds(head)}");
        check(MathF.Abs(ReviewBounds(flange).Position.Y - ReviewBounds(roof).End.Y) < 0.001f,
            "radar_process_flange_seats_on_delivered_roof");
        var electronics = ReviewMeshes(transmitter).Where(mesh => !mesh.Name.ToString().StartsWith("PROCESS_", StringComparison.Ordinal)
            && !mesh.Name.ToString().StartsWith("ANTENNA_", StringComparison.Ordinal)
            && mesh != beam).ToArray();
        bool Clear(MeshInstance3D part, MeshInstance3D other)
        {
            if (!OrientedBoxesPenetrate(part, other)) return true;
            if (other.Name != "RAIL_top") return false;
            // The circular rail's bounding box fills its empty center. Check
            // the imported ring's inner radius instead of treating it as a disk.
            var center = ReviewBounds(other).GetCenter();
            float Radius(Vector3 point) => new Vector2(point.X - center.X, point.Z - center.Z).Length();
            var innerRadius = Enumerable.Range(0, other.Mesh.GetSurfaceCount())
                .SelectMany(surface => other.Mesh.SurfaceGetArrays(surface)[(int)Mesh.ArrayType.Vertex].AsVector3Array())
                .Select(vertex => Radius(other.GlobalTransform * vertex)).Min();
            var bounds = ReviewBounds(part);
            var maxRadius = Enumerable.Range(0, 8).Select(corner => Radius(bounds.Position + bounds.Size * new Vector3(
                (corner & 1) == 0 ? 0 : 1, (corner & 2) == 0 ? 0 : 1, (corner & 4) == 0 ? 0 : 1))).Max();
            GD.Print($"RADAR_RAIL_CLEARANCE {part.Name} innerRadius={innerRadius} outerPartRadius={maxRadius}");
            return maxRadius + 0.005f < innerRadius;
        }
        foreach (var part in electronics)
            foreach (var other in ReviewMeshes(tank).Where(other => !Clear(part, other)))
                GD.Print($"RADAR_MOUNT_CANDIDATE {part.Name}/{other.Name}");
        check(ReviewBounds(head).Position.Y > ReviewBounds(roof).End.Y
            && electronics.All(part => ReviewMeshes(tank).All(other => Clear(part, other))),
            "radar_electronics_above_roof_and_clear_of_manway_and_guard");
        bool BeamMatches()
        {
            var actual = Convert.ToDouble(_sceneRuntime!.Points["radar_distance"]);
            var expected = ReviewBounds(lens).Position.Y - ReviewBounds(liquid).End.Y;
            var shellBounds = ReviewBounds(shell);
            var center = shellBounds.GetCenter();
            var shellRadius = shellBounds.Size.X * 0.5f;
            var beamInside = Enumerable.Range(0, beam.Mesh.GetSurfaceCount())
                .SelectMany(surface => beam.Mesh.SurfaceGetArrays(surface)[(int)Mesh.ArrayType.Vertex].AsVector3Array())
                .Select(vertex => beam.GlobalTransform * vertex)
                .All(point => new Vector2(point.X - center.X, point.Z - center.Z).Length() < shellRadius - 0.005f);
            return Math.Abs(actual - expected) < 0.001
                && beamInside
                && MathF.Abs(ReviewBounds(beam).End.Y - ReviewBounds(lens).Position.Y) < 0.001f
                && MathF.Abs(ReviewBounds(beam).Position.Y - ReviewBounds(liquid).End.Y) < 0.001f;
        }
        var runtime = _sceneRuntime!;
        GD.Print($"RADAR_INITIAL_DISTANCE {runtime.Points["radar_distance"]}");
        check(BeamMatches(), "radar_initial_beam_and_distance_share_lens_and_surface_datums");
        runtime.UsesExternalClock = true;
        runtime.SetControllerPlaybackRunning(true);
        runtime.CommitVirtualControllerOutputs(new Dictionary<string, bool> { ["inlet_pump_run"] = true, ["drain_valve_open"] = false });
        var initialDistance = Convert.ToDouble(runtime.Points["radar_distance"]);
        var consistent = true;
        for (var sample = 0; sample < 200; sample++) { runtime.AdvanceSimulation(0.02); consistent &= BeamMatches(); }
        var filledDistance = Convert.ToDouble(runtime.Points["radar_distance"]);
        check(consistent && filledDistance < initialDistance, "radar_sampled_fill_shortens_beam_and_distance_together");
        runtime.CommitVirtualControllerOutputs(new Dictionary<string, bool> { ["inlet_pump_run"] = false, ["drain_valve_open"] = true });
        for (var sample = 0; sample < 200; sample++) { runtime.AdvanceSimulation(0.02); consistent &= BeamMatches(); }
        var drainedDistance = Convert.ToDouble(runtime.Points["radar_distance"]);
        check(consistent && drainedDistance > filledDistance, "radar_sampled_drain_lengthens_beam_and_distance_together");
        runtime.SetControllerPlaybackRunning(false);
        runtime.AdvanceSimulation(1);
        check(BeamMatches() && Math.Abs(Convert.ToDouble(runtime.Points["radar_distance"]) - drainedDistance) < 0.001,
            "radar_stopped_clock_holds_surface_range_and_beam");
        runtime.ResetSimulation();
        check(BeamMatches() && Math.Abs(Convert.ToDouble(runtime.Points["radar_distance"]) - initialDistance) < 0.001,
            "radar_reset_restores_initial_surface_range_and_beam");
    }

    private void VerifyBoxVolumeFixture(Action<bool, string> check)
    {
        AddMigratedScene("lab-9-10-box-volume", _candidateCatalog!, _mainCamera!, false, false);
        var carton = _sceneCompositionRoot!.GetNode<Node3D>("box_0");
        var fixture = _sceneCompositionRoot.GetNode<Node3D>("training_accessory_3");
        var floor = (MeshInstance3D)fixture.FindChild("DIMENSION_tabletop", true, false);
        var bounds = ReviewBounds(carton);
        var floorBounds = ReviewBounds(floor);
        GD.Print($"BOX_VOLUME_BENCH_CONTACT carton={bounds} bench={floorBounds}");
        // The formerly floor-supported carton now belongs on the carrying bench.
        check(MathF.Abs(bounds.Position.Y - floorBounds.End.Y) < 0.001f
            && bounds.Position.X >= floorBounds.Position.X && bounds.End.X <= floorBounds.End.X
            && bounds.Position.Z >= floorBounds.Position.Z && bounds.End.Z <= floorBounds.End.Z,
            "box_volume_carton_contacts_bench_with_full_footprint");
        var heads = ReviewMeshes(fixture).Where(mesh => mesh.Name.ToString().StartsWith("DIMENSION_head_", StringComparison.Ordinal)).ToArray();
        check(heads.Length == 3 && fixture.FindChild("KIN_bottom_bar", true, false) is null
            && _sceneCompositionRoot.GetNodeOrNull<Node3D>("machine_1") is null,
            "box_volume_fixture_has_three_heads_without_shutter_or_cnc");
        var fixtureParts = ReviewMeshes(fixture);
        var feet = fixtureParts.Where(mesh => mesh.Name.ToString().Contains("foot", StringComparison.Ordinal)).ToArray();
        var supports = fixtureParts.Where(mesh => mesh.Name.ToString().Contains("leg", StringComparison.Ordinal)
            || mesh.Name.ToString().Contains("post", StringComparison.Ordinal)).ToArray();
        check(feet.Length == 7 && feet.All(foot => MathF.Abs(ReviewBounds(foot).Position.Y) < 0.001f)
            && supports.All(support => feet.Any(foot => ReviewBounds(support).Intersects(ReviewBounds(foot)))),
            "box_volume_table_and_sensor_supports_seat_on_grounded_feet");
        var crossbeam = (MeshInstance3D)fixture.FindChild("DIMENSION_crossbeam", true, false);
        check(supports.Where(mesh => mesh.Name.ToString().Contains("table_leg", StringComparison.Ordinal))
                .All(leg => ReviewBounds(leg).Intersects(floorBounds))
            && supports.Where(mesh => mesh.Name.ToString().Contains("portal_post", StringComparison.Ordinal))
                .All(post => ReviewBounds(post).Intersects(ReviewBounds(crossbeam)))
            && heads.All(head => supports.Append(crossbeam).Any(support => ReviewBounds(head).Intersects(ReviewBounds(support)))),
            "box_volume_bench_portal_and_sensor_heads_have_connected_supports");
        check(new[] { ("switch_5", "LENGTH"), ("switch_6", "WIDTH"), ("switch_7", "HEIGHT") }
            .All(item => _sceneCompositionRoot.GetNode<Node3D>(item.Item1).FindChild("OperatorFaceLabel", true, false)
                is Label3D label && label.Text == item.Item2), "box_volume_manual_input_plates_match_dimensions");
        var others = _sceneCompositionRoot.GetChildren().OfType<Node3D>()
            .Where(node => node != carton).SelectMany(ReviewMeshes).ToArray();
        check(ReviewMeshes(carton).All(part => others.All(other =>
        {
            var overlap = ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
            return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f
                || !OrientedBoxesPenetrate(part, other);
        })), "box_volume_carton_clear_of_separate_equipment");
        var separate = _sceneCompositionRoot.GetChildren().OfType<Node3D>()
            .Where(node => node != carton && node != fixture).SelectMany(ReviewMeshes).ToArray();
        check(fixtureParts.All(part => separate.All(other =>
        {
            var overlap = ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
            return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f
                || !OrientedBoxesPenetrate(part, other);
        })), "box_volume_fixture_clear_of_controls_and_readout");
    }

    private void VerifyBaseConveyorCartonSupport(Action<bool, string> check)
    {
        foreach (var number in new[] { 1, 2 })
        {
            var sceneId = number == 1 ? "scene-1-conveyor-stop" : "scene-2-conveyor-pusher";
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var runtime = _sceneRuntime!;
            var carton = root.GetNode<Node3D>($"scene{number}_product");
            var initial = carton.Transform;
            var conveyor = root.GetNode<Node3D>($"scene{number}_conveyor");
            var belt = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
            bool Supported()
            {
                var load = ReviewBounds(carton);
                return MathF.Abs(load.Position.Y - belt.End.Y) < 0.001f
                    && load.Position.X >= belt.Position.X && load.End.X <= belt.End.X
                    && load.Position.Z >= belt.Position.Z && load.End.Z <= belt.End.Z;
            }
            GD.Print($"BASE_CONVEYOR_SUPPORT {sceneId} carton={ReviewBounds(carton)} belt={belt}");
            check(Supported(), $"{sceneId}_initial_carton_contact_and_full_belt_footprint");
            // Symbolic plant probe only: command through the same typed output
            // boundary and clock as the controller. No ladder or transport proof.
            runtime.UsesExternalClock = true;
            runtime.SetControllerPlaybackRunning(true);
            runtime.CommitVirtualControllerOutputs(new Dictionary<string, bool> { ["conveyor_running"] = true });
            var feedback = number == 1 ? "simulated_photoeye" : "part_at_pusher";
            var support = true;
            for (var sample = 0; sample < 100 && runtime.Points[feedback] is not true; sample++)
            {
                runtime.AdvanceSimulation(0.02);
                support &= Supported();
            }
            check(support && runtime.Points[feedback] is true,
                $"{sceneId}_carton_supported_through_first_photoeye_detection");
            var sensor = root.GetNode<Node3D>($"scene{number}_photoeye");
            var beam = (MeshInstance3D)sensor.FindChild("KIN_beam*", true, false);
            var beamCenter = ReviewBounds(beam).GetCenter();
            var detectedLoad = ReviewBounds(carton);
            check(runtime.Points[feedback] is true
                && beamCenter.X >= detectedLoad.Position.X && beamCenter.X <= detectedLoad.End.X
                && beamCenter.Y > detectedLoad.Position.Y && beamCenter.Y < detectedLoad.End.Y,
                $"{sceneId}_first_detection_has_carton_in_optical_envelope");
            runtime.CommitVirtualControllerOutputs(new Dictionary<string, bool> { ["conveyor_running"] = false });
            runtime.SetControllerPlaybackRunning(false);
            var stopped = carton.Transform;
            runtime.AdvanceSimulation(0.5);
            check(carton.Transform.IsEqualApprox(stopped) && Supported(), $"{sceneId}_stopped_clock_holds_supported_carton");
            runtime.ResetSimulation();
            check(carton.Transform.IsEqualApprox(initial) && Supported() && runtime.Points[feedback] is false,
                $"{sceneId}_reset_restores_supported_load_end");
        }
    }

    private void VerifyTransferCartonSupport(Action<bool, string> check)
    {
        foreach (var sceneId in new[]
        {
            "lab-3-01-guarded-pallet-transfer",
            "lab-4-08-package-grouping",
            "lab-5-09-bag-indexing-conveyor",
            "lab-6-07-luggage-weight-sort",
            "lab-9-11-pallet-counting"
        })
        {
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var carton = root.GetNode<Node3D>("box_1");
            var load = ReviewBounds(carton);
            var conveyor = root.GetNode<Node3D>("conveyor_0");
            var belt = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
            GD.Print($"TRANSFER_CARTON_SUPPORT {sceneId} carton={load} belt={belt}");
            // Use delivered, transformed meshes: equipment origin and catalog
            // nominal height alone did not catch cartons buried below the bed.
            check(MathF.Abs(load.Position.Y - belt.End.Y) < 0.001f
                && load.Position.X >= belt.Position.X && load.End.X <= belt.End.X
                && load.Position.Z >= belt.Position.Z && load.End.Z <= belt.End.Z,
                $"{sceneId}_carton_resting_within_carrying_belt");
            var cartonParts = ReviewMeshes(carton);
            var solids = root.GetChildren().OfType<Node3D>().Where(node => node != carton)
                .SelectMany(ReviewMeshes).ToArray();
            check(cartonParts.All(part => solids.All(solid =>
            {
                var overlap = ReviewBounds(part).Intersection(ReviewBounds(solid)).Size;
                return overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f
                    || !OrientedBoxesPenetrate(part, solid);
            })), $"{sceneId}_carton_clear_of_separate_equipment_solids");
        }
    }
}
