using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _auditChainLiftInstallation;
    private void AuditChainLiftInstallation()
    {
        var failures = 0;
        void Check(bool condition, string label)
        { if (!condition) failures++; GD.Print($"CHAIN_LIFT_INSTALLATION {label}={condition}"); }
        try
        {
            AddMigratedScene("lab-4-09-chain-drive-lift", _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var runtime = _sceneRuntime!;
            var lift = root.GetNode<Node3D>("liftTable_1");
            var motion = lift.GetNode<ChainLiftDriveVisual>("ChainLiftMotion");
            var feed = root.GetNode<Node3D>("conveyor_0").FindChildren("*", "", true, false).OfType<ChainFeedMotion>().Single();
            var box = root.GetNode<Node3D>("box_2");
            var carriage = lift.GetNode<Node3D>("KIN_chain_lift_carriage");
            var deck = carriage.GetNode<MeshInstance3D>("LIFT_carrying_deck");
            foreach (var equipment in root.GetChildren().OfType<Node3D>().Where(node => ReviewMeshes(node).Length > 0)) GD.Print($"CHAIN_LIFT_BOUNDS {equipment.Name} {ReviewBounds(equipment)}");
            bool Bears()
            {
                var load = ReviewBounds(box); var surface = ReviewBounds(deck);
                return MathF.Abs(load.Position.Y - surface.End.Y) < .002f
                    && load.Position.X >= surface.Position.X && load.End.X <= surface.End.X
                    && load.Position.Z >= surface.Position.Z && load.End.Z <= surface.End.Z;
            }
            Check(Bears(), "staged_carton_bears_on_home_platform");
            var deckSupports = ReviewMeshes(carriage).Where(mesh => mesh.Name.ToString().StartsWith("LIFT_deck_support_", StringComparison.Ordinal)).ToArray();
            Check(deckSupports.Length == 2 && deckSupports.All(part => ReviewBounds(part).Intersects(ReviewBounds(deck))), "deck_bears_on_two_carriage_crossmembers");
            var limits = root.GetNode<Node3D>("training_accessory_6");
            var mounts = ReviewMeshes(limits).Where(mesh => mesh.Name.ToString().StartsWith("LIMIT_mount_", StringComparison.Ordinal)).ToArray();
            var guides = ReviewMeshes(lift).Where(mesh => mesh.Name.ToString().StartsWith("LIFT_guide_", StringComparison.Ordinal)).ToArray();
            Check(mounts.Length == 2 && mounts.All(mount => guides.Any(guide => ReviewBounds(mount).Intersects(ReviewBounds(guide)))), "both_limit_brackets_bear_on_fixed_guide_post");
            var rollers = ReviewMeshes(limits).Where(mesh => mesh.Name.ToString().StartsWith("LIMIT_roller_", StringComparison.Ordinal)).OrderBy(mesh => mesh.GlobalPosition.Y).ToArray();
            var shoe = ReviewMeshes(carriage).Single(mesh => mesh.Name.ToString().StartsWith("LIFT_guide_shoe_-", StringComparison.Ordinal) && mesh.GlobalPosition.Z > 0);
            var limitContact = true;
            for (var endpoint = 0; endpoint <= 1; endpoint++)
            {
                motion.SetPositionNormalized(endpoint); motion.ProjectDrive();
                limitContact &= ReviewBounds(rollers[endpoint]).Intersects(ReviewBounds(shoe));
            }
            Check(limitContact, "moving_guide_shoe_meets_limit_roller_at_each_endpoint");
            runtime.ResetSimulation();
            Check(ReviewMeshes(root).All(mesh => !mesh.Name.ToString().StartsWith("PALLET", StringComparison.Ordinal)
                && !mesh.Name.ToString().Contains("KNEE", StringComparison.Ordinal)
                && !mesh.Name.ToString().StartsWith("KIN_scissor", StringComparison.Ordinal)), "unrelated_demonstration_load_mill_and_scissor_props_removed");
            Check(ReviewMeshes(root).All(mesh => ReviewBounds(mesh).Position.Y >= -.002f), "all_equipment_clears_floor");
            Check(motion.PositionPercent == 0 && !motion.RunCommand && !feed.RunCommand, "initial_drive_commands_and_height_are_zero");
            var feedBridge = root.GetNode<Node3D>("training_accessory_4").GetNode<MeshInstance3D>("TRANSFER_bridge");
            var receivingBridge = root.GetNode<Node3D>("training_accessory_5").GetNode<MeshInstance3D>("TRANSFER_bridge");
            Check(MathF.Abs(ReviewBounds(feedBridge).End.Y - ReviewBounds(deck).End.Y) < .001f
                && MathF.Abs(ReviewBounds(feedBridge).End.X - ReviewBounds(deck).Position.X) < .001f, "lower_bridge_terminates_at_home_platform_edge");
            var obstacles = root.GetChildren().OfType<Node3D>().Where(node => node != lift && node != box
                && node.Name != "training_accessory_6").SelectMany(ReviewMeshes).ToArray();
            var moving = ReviewMeshes(carriage).Concat(ReviewMeshes(box)).ToArray();
            var fixedParts = ReviewMeshes(lift).Where(part => !carriage.IsAncestorOf(part)
                && !part.Name.ToString().StartsWith("LIFT_guide_", StringComparison.Ordinal)
                && !part.Name.ToString().StartsWith("LIFT_chain_link_", StringComparison.Ordinal)).ToArray();
            var supported = true; var clear = true; var contacts = new HashSet<string>();
            for (var sample = 0; sample <= 210; sample++)
            {
                motion.SetPositionNormalized(sample / 210f); motion.ProjectDrive();
                supported &= Bears();
                foreach (var part in moving)
                foreach (var other in obstacles.Concat(fixedParts))
                {
                    var overlap = ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
                    if (overlap.X < .002f || overlap.Y < .002f || overlap.Z < .002f || !OrientedBoxesPenetrate(part, other)) continue;
                    clear = false;
                    if (contacts.Count < 12 && contacts.Add($"{part.Name}/{other.Name}")) GD.Print($"CHAIN_LIFT_CONTACT sample={sample} {part.Name}/{other.Name}");
                }
            }
            Check(supported, "carton_remains_supported_at_211_lift_positions");
            Check(clear, "carriage_and_carton_clear_other_equipment_and_non_guide_frame_at_211_positions");
            Check(MathF.Abs(ReviewBounds(receivingBridge).End.Y - ReviewBounds(deck).End.Y) < .001f
                && MathF.Abs(ReviewBounds(receivingBridge).Position.X - ReviewBounds(deck).End.X) < .001f, "upper_bridge_terminates_at_raised_platform_edge");
            var receiving = ReviewMeshes(root.GetNode<Node3D>("receiving_conveyor"))
                .Single(mesh => mesh.Name.ToString().Contains("belt_surface", StringComparison.OrdinalIgnoreCase));
            GD.Print($"CHAIN_LIFT_RECEIVING_SURFACE {ReviewBounds(receiving)}");
            Check(MathF.Abs(ReviewBounds(receiving).End.Y - ReviewBounds(deck).End.Y) < .002f
                && MathF.Abs(ReviewBounds(receiving).Position.X - ReviewBounds(receivingBridge).End.X) < .002f,
                "upper_receiver_and_bridge_form_aligned_carrying_surface");
            runtime.ResetSimulation();
            runtime.CommitVirtualControllerOutputs(new Dictionary<string, bool> { ["chain_run"] = true, ["lift_enable"] = true });
            Check(motion.RunCommand && feed.RunCommand, "plc_commands_reach_actual_lift_and_chain_adapters");
            var slat = feed.GetParent().FindChildren("KIN_CHAIN_SLAT_*", "MeshInstance3D", true, false).OfType<Node3D>().First();
            var slatHome = slat.Transform; var loadHome = box.Transform;
            var sprocketHomes = feed.GetParent().FindChildren("SPROCKET*", "MeshInstance3D", true, false).OfType<Node3D>()
                .ToDictionary(part => part, part => part.Basis);
            feed._PhysicsProcess(.4); motion._PhysicsProcess(.4);
            Check(slat.Transform != slatHome && box.Position.Y > loadHome.Origin.Y && Bears(), "commanded_chain_and_supported_load_move");
            runtime.CommitVirtualControllerOutputs(new Dictionary<string, bool> { ["chain_run"] = false, ["lift_enable"] = false });
            var held = box.Transform; var chainHeld = slat.Transform;
            feed._PhysicsProcess(2); motion._PhysicsProcess(2);
            Check(box.Transform.IsEqualApprox(held) && slat.Transform.IsEqualApprox(chainHeld), "removed_commands_hold_lift_and_chain_pose");
            runtime.ResetSimulation();
            Check(Bears() && motion.PositionPercent == 0 && slat.Transform.IsEqualApprox(slatHome), "reset_restores_platform_load_chain_and_drive");
            Check(sprocketHomes.Count > 0 && sprocketHomes.All(pair => pair.Key.Basis.IsEqualApprox(pair.Value)), "reset_restores_every_feed_sprocket_without_another_run_command");
            // An explicitly optional manual-permissive reference proves the
            // normal editor/controller path for this installation checkpoint.
            // It is not a continuous carton-transfer program.
            var document = CreateChainLiftInstallationReference();
            System.IO.File.WriteAllText(ProjectSettings.GlobalizePath("res://.tools/chain-lift-installation-reference.rpproj.json"), LadderEditorProjectJson.Save(document));
            var loaded = LadderEditorProjectJson.Load(FileAccess.GetFileAsString("res://programs/examples/chain-lift-installation-reference.rpproj.json"));
            Check(loaded.IsReadable && loaded.Document is not null && LadderEditorProjectJson.Save(loaded.Document) == LadderEditorProjectJson.Save(document), "saved_installation_reference_matches_reviewed_program");
            EnableVirtualControllerProgram((loaded.Document ?? document).BuildProgram());
            RunActiveController(); _PhysicsProcess(.04);
            Check(!motion.RunCommand && !feed.RunCommand, "run_scans_without_start_cannot_move_installation");
            runtime.ExecuteAction("start-lift-installation"); _PhysicsProcess(.04);
            Check(!motion.RunCommand && !feed.RunCommand, "start_with_missing_manual_permissives_is_discarded");
            foreach (var point in new[] { "box_present", "lift_home", "destination_clear" }) runtime.ExecuteAction($"toggle-{point}");
            _PhysicsProcess(.04);
            Check(!motion.RunCommand && !feed.RunCommand, "restoring_permissives_does_not_reuse_old_start");
            runtime.ExecuteAction("start-lift-installation"); _PhysicsProcess(.04);
            Check(motion.RunCommand && feed.RunCommand && runtime.Points["lift_start"] is false, "fresh_start_with_manual_permissives_commands_both_drives_and_clears_pulse");
            motion._PhysicsProcess(1); feed._PhysicsProcess(1);
            Check(Bears() && motion.PositionPercent > 24, "actual_offline_controller_moves_supported_load");
            StopActiveController(); var stoppedLoad = box.Transform;
            motion._PhysicsProcess(1); feed._PhysicsProcess(1);
            Check(box.Transform.IsEqualApprox(stoppedLoad) && !motion.RunCommand && !feed.RunCommand, "controller_stop_holds_supported_load");
            RunActiveController(); _PhysicsProcess(.04);
            Check(!motion.RunCommand && !feed.RunCommand, "controller_run_after_stop_requires_fresh_start");
            runtime.ExecuteAction("start-lift-installation"); _PhysicsProcess(.04);
            Check(motion.RunCommand && feed.RunCommand, "fresh_start_after_stop_resumes_installation_drive");
            runtime.ExecuteAction("toggle-destination_clear"); _PhysicsProcess(.04);
            Check(!motion.RunCommand && !feed.RunCommand, "lost_manual_destination_permissive_clears_drive_seal");
            ResetActiveController();
            Check(Bears() && motion.PositionPercent == 0 && !motion.RunCommand && !feed.RunCommand
                && runtime.Points["box_present"] is false && runtime.Points["lift_home"] is false && runtime.Points["destination_clear"] is false,
                "global_reset_restores_home_and_manual_input_contract");
            GD.Print($"CHAIN_LIFT_STATIC_CANDIDATES {LogBoundsCandidates(root)}");

        }
        catch (Exception error) { failures++; GD.PushError($"CHAIN_LIFT_INSTALLATION_EXCEPTION {error}"); }
        GD.Print($"CHAIN_LIFT_INSTALLATION_RESULT failures={failures}; installation/drive checks only; continuous carton transfer and automatic feedback remain open");
        DisableVirtualController();
        GetTree().Quit(failures == 0 ? 0 : 1);
    }

    private static LadderEditorDocument CreateChainLiftInstallationReference()
    {
        var document = new LadderEditorDocument();
        document.ResetProject("reference-chain-lift-installation", "Chain_Lift_Installation", TimeSpan.FromMilliseconds(20));
        document.SourceSceneId = "lab-4-09-chain-drive-lift";
        foreach (var input in new[] { "box_present", "lift_home", "destination_clear", "lift_start" }) document.AddTag(input, PlcVariableRole.Input, input);
        document.AddTag("stop_command", PlcVariableRole.Input, "operator.stop");
        document.AddTag("start_edge", PlcVariableRole.Memory);
        foreach (var output in new[] { "chain_run", "lift_enable" }) document.AddTag(output, PlcVariableRole.Output, output);
        document.AddRung("Sample momentary installation Start", "start_edge");
        document.InsertEdgeContact(0, 0, 0, "lift_start", LadderEdgeMode.Rising);
        document.AddRung("Lift drive seal with manual test permissives", "lift_enable");
        document.AddContact(1, 0, "start_edge", false);
        document.AddParallelBranch(1); document.AddContact(1, 1, "lift_enable", false);
        foreach (var branch in new[] { 0, 1 })
        {
            foreach (var input in new[] { "box_present", "lift_home", "destination_clear" }) document.AddContact(1, branch, input, false);
            document.AddContact(1, branch, "stop_command", true);
        }
        document.AddRung("Chain drive follows installation enable", "chain_run");
        document.AddContact(2, 0, "lift_enable", false);
        return document;
    }
}
