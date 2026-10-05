using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
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
