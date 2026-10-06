using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using RungProof.Next.Scenes;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _auditPalletizer;
    private void AuditPalletizer()
    {
        var failures = 0;
        void Check(bool condition, string label)
        { if (!condition) failures++; GD.Print($"PALLETIZER_CHECK {label}={condition}"); }
        try { VerifyPalletizerWorkflow(Check); }
        catch (Exception error) { failures++; GD.PushError($"PALLETIZER_EXCEPTION {error}"); }
        GD.Print($"PALLETIZER_RESULT failures={failures}; prescribed kinematics and sampled bounds only");
        DisableVirtualController(); GetTree().Quit(failures == 0 ? 0 : 1);
    }
    private void VerifyPalletizerWorkflow(Action<bool, string> check)
    {
        AddMigratedScene("lab-11-13-xy-palletizing", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!; var runtime = _sceneRuntime!;
        var gantry = root.GetNode<Node3D>("training_accessory_4");
        var carton = root.GetNode<Node3D>("box_2");
        var pallet = root.GetNode<Node3D>("training_accessory_6");
        var table = root.GetNode<Node3D>("training_accessory_8");
        var moving = ReviewMeshes(gantry).Where(mesh => mesh.Name.ToString().StartsWith("KIN_", StringComparison.Ordinal) || mesh.Name == "GANTRY_GRIPPER").ToArray();
        var posts = ReviewMeshes(gantry).Where(mesh => mesh.Name.ToString().StartsWith("GANTRY_POST", StringComparison.Ordinal)).ToArray();
        var tool = moving.Single(mesh => mesh.Name == "GANTRY_GRIPPER");
        var rod = moving.Single(mesh => mesh.Name.ToString().StartsWith("KIN_Z_AXIS", StringComparison.Ordinal));
        var bridge = moving.Single(mesh => mesh.Name.ToString().StartsWith("KIN_X_BRIDGE", StringComparison.Ordinal));
        var carriage = moving.Single(mesh => mesh.Name.ToString().StartsWith("KIN_Y_CARRIAGE", StringComparison.Ordinal));
        var home = moving.Select(part => part.Transform).ToArray();
        var palletBounds = ReviewBounds(pallet); var surface = ReviewBounds(table.FindChild("PICK_surface", true, false) as MeshInstance3D ?? throw new InvalidOperationException("Missing pickup surface."));
        bool BearsOn(Aabb box, Aabb support) => Math.Abs(box.Position.Y - support.End.Y) < .005f
            && box.Position.X >= support.Position.X - .001f && box.End.X <= support.End.X + .001f
            && box.Position.Z >= support.Position.Z - .001f && box.End.Z <= support.End.Z + .001f;
        bool Clear(MeshInstance3D a, MeshInstance3D b)
        { var overlap = ReviewBounds(a).Intersection(ReviewBounds(b)).Size; return overlap.X <= .002f || overlap.Y <= .002f || overlap.Z <= .002f || !OrientedBoxesPenetrate(a, b); }
        check(moving.Length == 4 && posts.Length == 4 && posts.All(post => !ReviewBounds(post).Intersects(palletBounds)), "pallet_inside_four_posts_without_intersection");
        check(BearsOn(ReviewBounds(carton), surface), "initial_carton_bears_on_reachable_pick_table");
        check(new[] { ("switch_9", "START"), ("switch_10", "LOAD"), ("switch_11", "PALLET") }.All(item => root.GetNode<Node3D>(item.Item1).GetNode<Label3D>("OperatorFaceLabel").Text == item.Item2), "buttons_identify_actual_operator_actions");
        check(runtime.Points["gantry_home"] is true && runtime.Points["carton_at_pick"] is true && !runtime.ExecuteAction("load-carton"), "home_feedback_and_occupied_station_reject_duplicate_load");
        check(!runtime.TryGetAction("toggle-gantry_home", out _) && !runtime.TryGetAction("toggle-carton_at_pick", out _), "geometry_feedback_has_no_manual_toggle_actions");
        var loaded = LadderEditorProjectJson.Load(FileAccess.GetFileAsString("res://programs/demos/05-integrated-cell-multi-fb-fc.rpproj.json"));
        check(loaded.IsReadable && loaded.Document is not null, "normal_saved_demo_document_is_editable");
        check(LadderEditorProjectJson.Save(loaded.Document!) == LadderEditorProjectJson.Save(AuthoredDemoLadderPrograms.TryCreate("lab-11-13-xy-palletizing", out var authored) ? authored : throw new InvalidOperationException("Missing Demo 5")), "saved_file_matches_demo_menu_document");
        RunActiveController(); _PhysicsProcess(.1);
        check(runtime.Points["gantry_cycle"] is false && moving.Select((part, i) => part.Transform == home[i]).All(same => same), "normal_run_alone_does_not_start_machine");
        var contacts = new HashSet<string>(); var samples = 0; var geometry = true; var bearing = true; var rodSeated = true; var bridgeSupported = true; var attachment = true; var feedback = true; var counts = true;
        for (var pick = 0; pick < 4; pick++)
        {
            if (pick > 0) check(runtime.ExecuteAction("load-carton"), $"load_carton_{pick + 1}_after_completed_home_return");
            runtime.ExecuteAction("start-palletizer");
            var ticks = 0; var sawAttached = false; var sawPlace = false; var sawAway = false;
            do
            {
                ticks++; samples++; _PhysicsProcess(.02);
                sawAttached |= runtime.Points["carton_attached"] is true;
                sawPlace |= runtime.Points["at_place"] is true;
                sawAway |= runtime.Points["gantry_home"] is false;
                var c = ReviewBounds(carriage); var b = ReviewBounds(bridge);
                bridgeSupported &= c.Position.Z >= b.Position.Z - .001f && c.End.Z <= b.End.Z + .001f && c.GetCenter().X >= b.Position.X && c.GetCenter().X <= b.End.X && c.Intersects(b);
                rodSeated &= ReviewBounds(rod).Intersects(c) && ReviewBounds(rod).Intersects(ReviewBounds(tool));
                foreach (var part in moving)
                foreach (var post in posts) geometry &= Clear(part, post);
                var cartons = root.GetChildren().OfType<Node3D>().Where(node => node == carton || node.Name.ToString().StartsWith("PlacedCarton_", StringComparison.Ordinal)).Where(node => node.Visible).ToArray();
                var obstacles = root.GetChildren().OfType<Node3D>().Except(cartons).SelectMany(ReviewMeshes).Where(mesh => mesh != tool).ToArray();
                // Internal gantry contacts are intentional bearings. Check all
                // four moving parts against the other equipment and placed stock.
                var peers = root.GetChildren().OfType<Node3D>().Where(node => node != gantry && node != carton && node.Visible).SelectMany(ReviewMeshes).ToArray();
                foreach (var part in moving)
                foreach (var peer in peers)
                    if (!Clear(part, peer)) { geometry = false; var key = $"{part.Name}/{peer.GetPath()}"; if (contacts.Add(key)) GD.Print($"PALLETIZER_CONTACT sample={samples} {key}"); }
                foreach (var box in cartons)
                foreach (var mesh in ReviewMeshes(box))
                foreach (var obstacle in obstacles)
                    if (!Clear(mesh, obstacle)) { geometry = false; var key = $"{box.Name}/{obstacle.GetPath()}"; if (contacts.Add(key)) GD.Print($"PALLETIZER_CONTACT sample={samples} {key}"); }
                foreach (var placed in cartons.Where(node => node != carton)) bearing &= BearsOn(ReviewBounds(placed), palletBounds);
                if (runtime.Points["carton_attached"] is true)
                    attachment &= Math.Abs(ReviewBounds(carton).End.Y - ReviewBounds(tool).Position.Y) < .005f && Math.Abs(ReviewBounds(carton).GetCenter().X - ReviewBounds(tool).GetCenter().X) < .001f && Math.Abs(ReviewBounds(carton).GetCenter().Z - ReviewBounds(tool).GetCenter().Z) < .001f;
                feedback &= runtime.Points["palletizer_fault"] is false && (runtime.Points["gantry_home"] is not true || runtime.Points["cycle_in_progress"] is false);
                counts &= _virtualController!.Snapshot.Counters["cycle_count"].Accumulated <= Convert.ToInt32(runtime.Points["placed_cartons"]);
            } while (ticks < 1500 && runtime.Points["gantry_cycle"] is not false);
            check(ticks < 1500 && sawAttached && sawPlace && sawAway && runtime.Points["pick_complete"] is true && runtime.Points["gantry_home"] is true && Convert.ToInt32(runtime.Points["placed_cartons"]) == pick + 1, $"carton_{pick + 1}_picked_carried_released_and_returned_home");
            check(_virtualController!.Snapshot.Counters["cycle_count"].Accumulated == pick + 1 && runtime.Points["vacuum_pick"] is false, $"counter_{pick + 1}_follows_completed_transfer_not_timer_alone");
        }
        check(geometry, "sampled_cartons_and_four_moving_parts_clear_fixed_solids_and_posts");
        check(bearing, "all_four_placed_cartons_bear_inside_pallet_footprint");
        check(attachment, "carried_carton_top_and_center_follow_tool_contact");
        check(rodSeated && bridgeSupported, "telescoping_rod_seated_and_carriage_supported_through_all_four_routes");
        check(feedback && counts, "home_progress_and_counter_feedback_match_actual_plant_events");
        check(runtime.Points["layer_complete"] is true && _virtualController!.Snapshot.NumericVariables["layer_count"] == 1 && runtime.Points["gantry_cycle"] is false, "four_carton_layer_completes_at_home_with_commands_off");
        var retained = root.GetNode<Node3D>("PlacedCarton_3").Transform;
        check(!runtime.ExecuteAction("load-carton"), "completed_layer_rejects_fifth_load"); runtime.ExecuteAction("start-palletizer"); _PhysicsProcess(2);
        check(root.GetNode<Node3D>("PlacedCarton_3").Transform == retained && Convert.ToInt32(runtime.Points["placed_cartons"]) == 4 && runtime.Points["gantry_cycle"] is false, "completed_start_retains_four_supported_cartons");
        // Deliberately act in the one-scan window after plant home return,
        // before the controller has consumed its completion feedback.
        foreach (var immediateStart in new[] { false, true })
        {
            ResetActiveController(); RunActiveController(); _PhysicsProcess(.04); runtime.ExecuteAction("start-palletizer");
            var ticks = 0;
            while (runtime.Points["pick_complete"] is not true && ticks++ < 1500) _PhysicsProcess(.02);
            check(ticks < 1500 && _virtualController!.Snapshot.Counters["cycle_count"].Accumulated == 0 && Convert.ToInt32(runtime.Points["placed_cartons"]) == 1, $"completion_boundary_before_next_scan_start_{immediateStart}");
            check(runtime.ExecuteAction("load-carton") && runtime.Points["pick_complete"] is true, $"immediate_load_preserves_unscanned_completion_start_{immediateStart}");
            if (immediateStart) runtime.ExecuteAction("start-palletizer");
            _PhysicsProcess(.02);
            check(_virtualController!.Snapshot.Counters["cycle_count"].Accumulated == 1 && runtime.Points["gantry_cycle"] is bool command && command == immediateStart, $"next_scan_counts_completion_without_automatic_restart_start_{immediateStart}");
            if (!immediateStart) runtime.ExecuteAction("start-palletizer");
            ticks = 0; do { ticks++; _PhysicsProcess(.02); } while (ticks < 1500 && runtime.Points["gantry_cycle"] is not false);
            check(ticks < 1500 && Convert.ToInt32(runtime.Points["placed_cartons"]) == 2 && _virtualController!.Snapshot.Counters["cycle_count"].Accumulated == 2 && runtime.Points["palletizer_fault"] is false, $"immediate_reload_next_transfer_counts_once_start_{immediateStart}");
        }
        foreach (var phase in new[] { "pickup", "carry", "release", "return" })
        {
            ResetActiveController(); RunActiveController(); _PhysicsProcess(.04); runtime.ExecuteAction("start-palletizer"); var ticks = 0;
            bool Reached() => phase == "pickup" ? runtime.Points["at_pickup"] is true : phase == "carry" ? runtime.Points["carton_attached"] is true && tool.GlobalPosition.X > -.7f : phase == "release" ? runtime.Points["at_place"] is true : Convert.ToInt32(runtime.Points["placed_cartons"]) == 1 && runtime.Points["gantry_home"] is false && tool.GlobalPosition.Y > 1.5f;
            while (!Reached() && ticks++ < 1500) _PhysicsProcess(.02);
            var pose = moving.Select(part => part.Transform).ToArray(); var boxPose = carton.Transform; var placed = runtime.Points["placed_cartons"];
            StopActiveController(); _PhysicsProcess(.5);
            GD.Print($"PALLETIZER_STOP_PROBE {phase} ticks={ticks} axes={moving.Select((part, i) => part.Transform == pose[i]).All(same => same)} box={carton.Transform == boxPose} inventory={Equals(placed, runtime.Points["placed_cartons"])} cycle={runtime.Points["gantry_cycle"]} vacuum={runtime.Points["vacuum_pick"]}");
            check(ticks < 1500 && moving.Select((part, i) => part.Transform == pose[i]).All(same => same) && carton.Transform == boxPose && Equals(placed, runtime.Points["placed_cartons"]) && runtime.Points["gantry_cycle"] is false && runtime.Points["vacuum_pick"] is false, $"stop_holds_{phase}_pose_attachment_and_inventory");
            RunActiveController(); _PhysicsProcess(.2);
            check(moving.Select((part, i) => part.Transform == pose[i]).All(same => same), $"run_alone_does_not_resume_{phase}");
            runtime.ExecuteAction("start-palletizer"); ticks = 0; do { ticks++; _PhysicsProcess(.02); } while (ticks < 1500 && runtime.Points["gantry_cycle"] is not false);
            check(ticks < 1500 && runtime.Points["palletizer_fault"] is false && runtime.Points["pick_complete"] is true, $"fresh_start_resumes_{phase}_to_placement_and_home");
        }
        ResetActiveController(); RunActiveController(); _PhysicsProcess(.04); runtime.ExecuteAction("start-palletizer"); _PhysicsProcess(.3);
        runtime.ExecuteAction("toggle-pallet_position_valid"); _PhysicsProcess(.02); var blocked = moving.Select(part => part.Transform).ToArray();
        _PhysicsProcess(.5); check(runtime.Points["gantry_cycle"] is false && moving.Select((part,i) => part.Transform == blocked[i]).All(same => same), "pallet_permissive_loss_removes_commands_and_holds_pose");
        runtime.ExecuteAction("toggle-pallet_position_valid"); _PhysicsProcess(.2); check(runtime.Points["gantry_cycle"] is false, "restoring_permissive_does_not_restart_without_fresh_start");
        ResetActiveController();
        check(runtime.Points["gantry_home"] is true && runtime.Points["carton_at_pick"] is true && Convert.ToInt32(runtime.Points["placed_cartons"]) == 0 && moving.Select((part,i) => part.Transform == home[i]).All(same => same) && _virtualController!.Snapshot.ScanNumber == 0 && _virtualController.Snapshot.State == VirtualControllerState.Stopped, "reset_restores_preloaded_carton_empty_pallet_home_and_stopped_scan_zero");
        RunActiveController(); _PhysicsProcess(.04); runtime.ExecuteAction("start-palletizer"); StopActiveController(); RunActiveController(); _PhysicsProcess(.2);
        check(runtime.Points["start_command"] is false && runtime.Points["gantry_cycle"] is false && runtime.Points["gantry_home"] is true, "unscanned_start_is_discarded_by_stop_and_cannot_fire_on_run");
        ResetActiveController();
        var faultPlant = new PalletizerPlantModel(); faultPlant.Step(1, true, false, true); faultPlant.Step(.02, true, true, true); faultPlant.Step(.02, true, false, true);
        check(faultPlant.Faulted && faultPlant.Attached && faultPlant.Placed == 0, "vacuum_loss_during_commanded_carry_latches_fault_without_false_placement");
        var invalid = true;
        foreach (var time in new[] { -1.0, double.NaN, double.PositiveInfinity })
            try { faultPlant.Step(time, false, false, true); invalid = false; } catch (ArgumentException) { }
        check(invalid, "invalid_elapsed_time_rejected_even_when_held_or_faulted");
        if (_visualSceneReview) VerifyGantryReviewClock(check);
        GD.Print($"PALLETIZER_CYCLE_SAMPLES {samples}"); GD.Print($"PALLETIZER_STATIC_CANDIDATES {LogBoundsCandidates(root)}");
    }
}
