using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyPalletRobotInstallationGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-17-pallet-robot", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var conveyor = root.GetNode<Node3D>("robot_pallet_conveyor");
        var pallet = root.GetNode<Node3D>("robot_pallet");
        var receiver = root.GetNode<Node3D>("process_receiver");
        var sensor = root.GetNode<Node3D>("pallet_ready_sensor");
        var belt = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
        var palletBounds = ReviewBounds(pallet);

        var runners = ReviewMeshes(pallet).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_bottom_runner", StringComparison.Ordinal)).ToArray();
        check(runners.Length == 3 && runners.All(mesh => MathF.Abs(ReviewBounds(mesh).Position.Y - belt.End.Y) < 0.001f)
            && palletBounds.Position.X >= belt.Position.X && palletBounds.End.X <= belt.End.X
            && palletBounds.Position.Z >= belt.Position.Z && palletBounds.End.Z <= belt.End.Z,
            "pallet_robot_all_three_bottom_runners_seated_on_belt");
        var boards = ReviewMeshes(pallet).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_top_board", StringComparison.Ordinal)).ToArray();
        var deckY = boards.Max(mesh => ReviewBounds(mesh).End.Y);
        check(new[] { "container_a", "container_b" }.All(id =>
        {
            var load = ReviewBounds(root.GetNode(id));
            return MathF.Abs(load.Position.Y - deckY) < 0.001f
                && load.Position.X >= palletBounds.Position.X && load.End.X <= palletBounds.End.X
                && load.Position.Z >= palletBounds.Position.Z && load.End.Z <= palletBounds.End.Z;
        }), "pallet_robot_both_containers_seated_within_pallet_deck");
        check(ReviewMeshes(pallet).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_top_nail", StringComparison.Ordinal))
            .All(mesh => ReviewBounds(mesh).End.Y <= deckY + 0.001f), "pallet_robot_top_nail_heads_do_not_protrude_into_staged_loads");

        bool Clear(MeshInstance3D a, MeshInstance3D b)
        {
            var overlap = ReviewBounds(a).Intersection(ReviewBounds(b)).Size;
            if (overlap.X <= 0.001f || overlap.Y <= 0.001f || overlap.Z <= 0.001f || !OrientedBoxesPenetrate(a, b)) return true;
            // Routed cable bounds enclose empty space. Check the actual cable
            // triangles before reporting a solid installation conflict.
            if (b.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase))
            {
                var faces = b.Mesh.GetFaces();
                var bounds = ReviewBounds(a);
                for (var index = 0; index < faces.Length; index += 3)
                {
                    var triangle = new Aabb(b.GlobalTransform * faces[index], Vector3.Zero)
                        .Expand(b.GlobalTransform * faces[index + 1]).Expand(b.GlobalTransform * faces[index + 2]);
                    var size = bounds.Intersection(triangle).Size;
                    if (size.X > 0.001f && size.Y > 0.001f && size.Z > 0.001f) return false;
                }
                return true;
            }
            GD.Print($"PALLET_ROBOT_INSTALLATION_CONFLICT {a.Name}/{b.Name}");
            return false;
        }
        var others = root.GetChildren().OfType<Node3D>().Where(node => node != receiver)
            .SelectMany(ReviewMeshes).Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)).ToArray();
        check(ReviewMeshes(receiver).All(a => others.All(b => Clear(a, b))),
            "pallet_robot_receiver_clear_of_all_separate_equipment_at_home");
        check(ReviewMeshes(sensor).Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal))
                .All(a => ReviewMeshes(conveyor).All(b => Clear(a, b))),
            "pallet_robot_sensor_hardware_clear_of_conveyor");
        check(new[] { "TX", "RX" }.All(side =>
        {
            var cable = ReviewBounds((MeshInstance3D)sensor.FindChild($"{side}_cable", true, false));
            var post = ReviewBounds((MeshInstance3D)sensor.FindChild($"{side}_post", true, false));
            var housing = ReviewBounds((MeshInstance3D)sensor.FindChild($"{side}_housing", true, false));
            var connector = ReviewBounds((MeshInstance3D)sensor.FindChild($"{side}_m12_connector", true, false));
            return MathF.Abs(cable.GetCenter().Z - post.GetCenter().Z) < 0.001f
                && cable.Grow(0.002f).Intersects(housing)
                && MathF.Abs(cable.Position.Y - connector.End.Y) < 0.002f;
        }), "pallet_robot_each_sensor_pigtail_follows_its_stand_and_connects_at_both_ends");
        GD.Print($"PALLET_ROBOT_DATUM belt={belt} pallet={palletBounds} deckY={deckY} receiver={ReviewBounds(receiver)}");
        VerifyPalletOutboundGeometry(check);
    }

    private void VerifyPalletOutboundGeometry(Action<bool, string> check)
    {
        var root = _sceneCompositionRoot!;
        var outbound = root.GetNodeOrNull<Node3D>("robot_pallet_outbound");
        var bridge = root.GetNodeOrNull<Node3D>("robot_pallet_transfer_bridge");
        check(outbound is not null && bridge is not null, "pallet_robot_outbound_conveyor_and_transfer_bridge_present");
        if (outbound is null || bridge is null) return;
        var inbound = root.GetNode<Node3D>("robot_pallet_conveyor");
        var pallet = root.GetNode<Node3D>("robot_pallet");
        Aabb FlatBelt(Node3D conveyor)
        {
            var belt = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
            var tailX = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_tail_drum", true, false)).GetCenter().X;
            var driveX = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_drive_drum", true, false)).GetCenter().X;
            return new Aabb(new Vector3(tailX, belt.End.Y, belt.Position.Z), new Vector3(driveX - tailX, 0, belt.Size.Z));
        }
        var staging = FlatBelt(inbound); var receiving = FlatBelt(outbound);
        var deck = ReviewBounds((MeshInstance3D)bridge.FindChild("PALLET_TRANSFER_deck", true, false));
        check(MathF.Abs(staging.Position.Y - receiving.Position.Y) < 0.001f
            && MathF.Abs(deck.End.Y - staging.Position.Y) < 0.001f
            && deck.Position.X > staging.End.X && deck.End.X < receiving.Position.X,
            "pallet_robot_both_belts_and_bridge_share_carrying_height");

        var feet = ReviewMeshes(bridge).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_TRANSFER_foot", StringComparison.Ordinal)).ToArray();
        var posts = ReviewMeshes(bridge).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_TRANSFER_post", StringComparison.Ordinal)).ToArray();
        var bearer = ReviewBounds((MeshInstance3D)bridge.FindChild("PALLET_TRANSFER_bearer", true, false));
        check(feet.Length == 2 && posts.Length == 2 && feet.All(foot => MathF.Abs(ReviewBounds(foot).Position.Y) < 0.001f)
            && posts.All(post => feet.Any(foot => MathF.Abs(ReviewBounds(post).Position.Y - ReviewBounds(foot).End.Y) < 0.001f
                && ReviewBounds(foot).Grow(0.001f).Intersects(ReviewBounds(post)))
                && MathF.Abs(ReviewBounds(post).End.Y - bearer.Position.Y) < 0.001f)
            && MathF.Abs(bearer.End.Y - deck.Position.Y) < 0.001f,
            "pallet_robot_transfer_bridge_has_grounded_connected_supports");
        var obstacles = root.GetChildren().OfType<Node3D>().Where(node => node != pallet)
            .SelectMany(ReviewMeshes).Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)).ToArray();
        check(new[] { outbound, bridge }.All(equipment => ReviewMeshes(equipment).All(part =>
            root.GetChildren().OfType<Node3D>().Where(node => node != equipment).SelectMany(ReviewMeshes)
                .Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal))
                .All(other => PalletTransferPartsClear(part, other)))),
            "pallet_robot_outbound_and_bridge_clear_of_separate_equipment");
        check(new[] { inbound, outbound }.All(conveyor =>
            MathF.Abs(ReviewBounds((MeshInstance3D)conveyor.FindChild("BELT_vulcanized_splice", true, false)).End.Y - staging.Position.Y) < 0.001f),
            "pallet_robot_both_visual_splice_witnesses_flush_with_belt");

        var runtime = _sceneRuntime!;
        // Exercise the same standalone reference clock as --visual-plant-review.
        // The normal controller-owned shell must keep its separate clock/outputs.
        var originalClock = runtime.UsesExternalClock;
        var runners = ReviewMeshes(pallet).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_bottom_runner", StringComparison.Ordinal)).ToArray();
        var surfaces = new[] { staging, receiving, new Aabb(deck.Position with { Y = deck.End.Y }, deck.Size with { Y = 0 }) };
        var supported = true; var moved = false; var commandsTogether = true; var sweepClear = true;
        var receiver = root.GetNode<Node3D>("process_receiver");
        var loads = new[] { root.GetNode<Node3D>("container_a"), root.GetNode<Node3D>("container_b") };
        var loadObstacles = root.GetChildren().OfType<Node3D>().Where(node => !loads.Contains(node))
            .SelectMany(ReviewMeshes).Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)).ToArray();
        var loadSweepClear = true; var countRequiresLanding = true;
        bool Landed(int index)
        {
            var side = index == 0 ? "left" : "right";
            var rollers = ReviewMeshes(receiver).Where(mesh => mesh.Name.ToString() == $"KIN_receiver_roller_{side}"
                || mesh.Name.ToString().StartsWith($"RECEIVER_ROLLER_{side}_", StringComparison.Ordinal)).ToArray();
            if (rollers.Length != 5) return false;
            var carrying = ReviewBounds(rollers[0]);
            foreach (var roller in rollers.Skip(1)) carrying = carrying.Merge(ReviewBounds(roller));
            var load = ReviewBounds(loads[index]);
            return MathF.Abs(load.Position.Y - carrying.End.Y) < 0.001f
                && load.Position.X >= carrying.Position.X && load.End.X <= carrying.End.X
                && load.Position.Z >= carrying.Position.Z && load.End.Z <= carrying.End.Z;
        }
        var startX = pallet.Position.X;
        var drives = new[] { inbound, outbound }.Select(node => node.FindChildren("*", string.Empty, true, false)
            .OfType<ConveyorController>().Single()).ToArray();
        try
        {
            runtime.UsesExternalClock = false;
            runtime.ResetSimulation();
            runtime.RunDefault();
            for (var tick = 0; tick < 4000; tick++)
            {
                runtime.AdvanceSimulation(0.01);
                // Test the actual timed reference, including the transfer path,
                // rather than accepting placed_count as evidence of placement.
                if (loadSweepClear)
                    loadSweepClear = loads.All(load => ReviewMeshes(load).All(part =>
                        loadObstacles.All(other => PalletTransferPartsClear(part, other))))
                        && ReviewMeshes(loads[0]).All(part => ReviewMeshes(loads[1]).All(other => PalletTransferPartsClear(part, other)));
                var placed = Convert.ToInt32(runtime.Points["placed_count"]);
                if (placed >= 1) countRequiresLanding &= Landed(0);
                if (placed >= 2) countRequiresLanding &= Landed(1);
                moved |= pallet.Position.X > startX + 0.001f;
                commandsTogether &= drives.All(drive => drive.RunCommand == (runtime.Points["conveyor_run"] is true));
                foreach (var runner in runners)
                {
                    var bounds = ReviewBounds(runner);
                    var contactLength = surfaces.Where(surface => bounds.Position.Z >= surface.Position.Z - 0.001f
                            && bounds.End.Z <= surface.End.Z + 0.001f && MathF.Abs(bounds.Position.Y - surface.Position.Y) < 0.001f)
                        .Sum(surface => MathF.Max(0, MathF.Min(bounds.End.X, surface.End.X) - MathF.Max(bounds.Position.X, surface.Position.X)));
                    supported &= contactLength >= 0.10f;
                }
                if (moved) sweepClear &= ReviewMeshes(pallet).All(part => obstacles.All(other => PalletTransferPartsClear(part, other)));
                if (runtime.Points["cycle_complete"] is true) break;
            }
            var final = ReviewBounds(pallet);
            check(moved && supported, "pallet_robot_all_three_runners_supported_through_actual_reference_release");
            check(moved && sweepClear, "pallet_robot_complete_pallet_mesh_clear_through_actual_reference_release");
            check(runtime.Points["cycle_complete"] is true && final.Position.X >= receiving.Position.X
                && final.End.X <= receiving.End.X, "pallet_robot_empty_pallet_finishes_fully_on_outbound_flat_belt");
            check(commandsTogether && drives.All(drive => !drive.RunCommand),
                "pallet_robot_one_existing_command_drives_both_conveyors_and_stops_at_completion");
            check(Landed(0) && Landed(1), "pallet_robot_both_transferred_containers_land_within_actual_receiver_rollers");
            check(countRequiresLanding, "pallet_robot_placed_count_requires_each_container_already_seated");
            check(loadSweepClear, "pallet_robot_container_meshes_clear_separate_equipment_through_reference_transfer");
            GD.Print($"PALLET_RECEIVER_LANDING left={ReviewBounds(loads[0])} right={ReviewBounds(loads[1])}");
            GD.Print($"PALLET_OUTBOUND_DATUM staging={staging} bridge={deck} receiving={receiving} final={final}");
        }
        finally
        {
            runtime.ResetSimulation();
            runtime.UsesExternalClock = originalClock;
        }
        check(MathF.Abs(pallet.Position.X - startX) < 0.001f && drives.All(drive => !drive.RunCommand),
            "pallet_robot_reset_restores_staged_pallet_and_stops_both_conveyors");
    }

    private static bool PalletTransferPartsClear(MeshInstance3D a, MeshInstance3D b)
    {
        var overlap = ReviewBounds(a).Intersection(ReviewBounds(b)).Size;
        if (overlap.X <= 0.001f || overlap.Y <= 0.001f || overlap.Z <= 0.001f || !OrientedBoxesPenetrate(a, b)) return true;
        bool Curved(MeshInstance3D mesh) => mesh.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase)
            || mesh.Name.ToString().StartsWith("KIN_belt_surface", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("KIN_drive_drum", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("KIN_tail_drum", StringComparison.Ordinal);
        if (!Curved(b) && Curved(a)) return PalletTransferPartsClear(b, a);
        if (Curved(b))
        {
            // Curved belt wraps, round drums and cable routes enclose empty space. Test
            // actual transformed triangles against the other part's bounds.
            var faces = b.Mesh.GetFaces(); var bounds = ReviewBounds(a);
            for (var index = 0; index < faces.Length; index += 3)
            {
                var triangle = new Aabb(b.GlobalTransform * faces[index], Vector3.Zero)
                    .Expand(b.GlobalTransform * faces[index + 1]).Expand(b.GlobalTransform * faces[index + 2]);
                var size = bounds.Intersection(triangle).Size;
                if (size.X > 0.001f && size.Y > 0.001f && size.Z > 0.001f)
                { GD.Print($"PALLET_TRANSFER_CONFLICT {a.Name}/{b.Name}"); return false; }
            }
            return true;
        }
        GD.Print($"PALLET_TRANSFER_CONFLICT {a.Name}/{b.Name}");
        return false;
    }
}
