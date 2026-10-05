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
