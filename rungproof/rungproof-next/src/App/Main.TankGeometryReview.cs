using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyTankAnalogMountGeometry(Action<bool, string> check)
    {
        AddMigratedScene("tank-level", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var tank = root.GetNode<Node3D>("process_tank");
        var sensor = root.GetNode<Node3D>("level_transmitter");
        MeshInstance3D Part(Node node, string name) => (MeshInstance3D)node.FindChild(name, true, false);
        var roof = ReviewBounds(Part(tank, "TANK_roof"));
        var liquid = ReviewBounds(Part(tank, "KIN_liquid"));
        var rod = ReviewBounds(Part(sensor, "PROBE_sensing_rod"));
        var tip = ReviewBounds(Part(sensor, "PROBE_tip_weight"));
        var flange = ReviewBounds(Part(sensor, "PROCESS_flange"));
        var nozzle = tank.FindChild("TANK_ANALOG_socket", true, false) as MeshInstance3D;
        check(nozzle is not null && MathF.Abs(ReviewBounds(nozzle).End.Y - flange.Position.Y) < 0.001f
            && ReviewBounds(nozzle).Position.Y < roof.End.Y,
            "tank_analog_process_flange_seated_on_roof_socket");
        var shell = ReviewBounds(Part(tank, "TANK_shell"));
        bool Inside(Aabb bounds) => new Vector2(bounds.GetCenter().X - shell.GetCenter().X,
            bounds.GetCenter().Z - shell.GetCenter().Z).Length() + MathF.Max(bounds.Size.X, bounds.Size.Z) / 2 < shell.Size.X / 2;
        check(Inside(rod) && Inside(tip) && MathF.Abs(tip.Position.Y - liquid.Position.Y) < 0.001f
            && rod.End.Y > liquid.Position.Y + liquid.Size.Y / 0.42f,
            "tank_analog_probe_inside_vessel_and_covers_full_rendered_level_range");
        check(rod.Intersects(ReviewBounds(Part(sensor, "PROBE_insulator"))) && rod.Intersects(tip),
            "tank_analog_probe_seated_in_insulator_and_tip_weight");
        check(MathF.Abs(rod.Size.X - 0.05f) < 0.001f && MathF.Abs(rod.Size.Z - 0.05f) < 0.001f
            && MathF.Abs(tip.Size.Y - 0.12f) < 0.001f,
            "tank_analog_installation_preserves_rod_diameter_and_tip_weight_size");
        var headParts = ReviewMeshes(sensor).Where(mesh => !mesh.Name.ToString().StartsWith("PROBE_", StringComparison.Ordinal)).ToArray();
        var tankObstacles = ReviewMeshes(tank).Where(mesh => mesh.Name.ToString().StartsWith("RAIL_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("MANWAY_", StringComparison.Ordinal)).ToArray();
        bool Clear(MeshInstance3D part, MeshInstance3D other)
        {
            var box = ReviewBounds(part);
            if (!box.Intersects(ReviewBounds(other))) return true;
            // Ring bounds include empty space. Narrow the screen to delivered
            // triangle bounds instead of calling the whole ring a solid disk.
            var faces = other.Mesh.GetFaces();
            for (var index = 0; index < faces.Length; index += 3)
            {
                var triangle = new Aabb(other.GlobalTransform * faces[index], Vector3.Zero)
                    .Expand(other.GlobalTransform * faces[index + 1]).Expand(other.GlobalTransform * faces[index + 2]);
                // Include planar faces whose unexpanded bounds have a zero
                // dimension; those must still catch a part crossing the face.
                var overlap = box.Intersection(triangle.Grow(0.001f)).Size;
                if (overlap.X > 0.001f && overlap.Y > 0.001f && overlap.Z > 0.001f) return false;
            }
            return true;
        }
        check(headParts.All(part => ReviewBounds(part).Position.Y >= roof.End.Y
            && tankObstacles.All(other => Clear(part, other))),
            "tank_analog_head_above_roof_and_clear_of_manway_and_guardrails");
        GD.Print($"TANK_ANALOG_MOUNT roof={roof} flange={flange} rod={rod} tip={tip}");
    }

    private void VerifyTankSwitchMountGeometry(Action<bool, string> check)
    {
        foreach (var (sceneId, tankId, lowId, highId, initial, low, high) in new[]
        {
            ("tank-high-low", "water_tank_hl", "hl_low_switch", "hl_high_switch", 0.5f, 0.25f, 0.75f),
            ("tank-level", "process_tank", "low_level_switch", "high_level_switch", 0.42f, 0.2f, 0.8f),
        })
        {
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var tank = root.GetNode<Node3D>(tankId);
            var shell = ReviewBounds((MeshInstance3D)tank.FindChild("TANK_shell", true, false));
            var liquid = ReviewBounds((MeshInstance3D)tank.FindChild("KIN_liquid", true, false));
            foreach (var (id, threshold) in new[] { (lowId, low), (highId, high) })
            {
                var sensor = root.GetNode<Node3D>(id);
                var tips = ReviewMeshes(sensor).Where(mesh => mesh.Name.ToString().StartsWith("FORK_tip", StringComparison.Ordinal)).ToArray();
                var elevation = liquid.Position.Y + liquid.Size.Y / initial * threshold;
                check(tips.Length == 2 && tips.All(tip =>
                {
                    var center = ReviewBounds(tip).GetCenter() - shell.GetCenter();
                    return MathF.Sqrt(center.X * center.X + center.Z * center.Z) < shell.Size.X / 2
                        && MathF.Abs(ReviewBounds(tip).GetCenter().Y - elevation) < 0.001f;
                }), $"{sceneId}_{id}_tips_inside_tank_at_actual_level_threshold");
                var nozzle = tank.FindChild($"TANK_SWITCH_{id}", true, false) as MeshInstance3D;
                var seal = ReviewBounds((MeshInstance3D)sensor.FindChild("PROCESS_seal", true, false));
                check(nozzle is not null && MathF.Abs(ReviewBounds(nozzle).End.Z - seal.Position.Z) < 0.001f
                    && ReviewBounds(nozzle).Position.Z < shell.End.Z,
                    $"{sceneId}_{id}_process_seal_seated_on_tank_nozzle");
                var separateSolids = root.GetChildren().OfType<Node3D>().Where(node => node != tank && node != sensor)
                    .SelectMany(ReviewMeshes).ToArray();
                check(ReviewMeshes(sensor).All(part => separateSolids.All(other =>
                {
                    var overlap = ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
                    return overlap.X <= 0.001f || overlap.Y <= 0.001f || overlap.Z <= 0.001f
                        || !OrientedBoxesPenetrate(part, other);
                })), $"{sceneId}_{id}_clear_of_separate_equipment");
                GD.Print($"TANK_SWITCH_MOUNT {sceneId} {id} elevation={elevation} tips={string.Join(';', tips.Select(ReviewBounds))}");
            }
        }
    }
}
