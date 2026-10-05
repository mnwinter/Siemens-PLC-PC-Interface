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
            return MathF.Abs(load.Position.Y - deckY) < 0.005f
                && load.Position.X >= palletBounds.Position.X && load.End.X <= palletBounds.End.X
                && load.Position.Z >= palletBounds.Position.Z && load.End.Z <= palletBounds.End.Z;
        }), "pallet_robot_both_containers_seated_within_pallet_deck");

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
    }
}
