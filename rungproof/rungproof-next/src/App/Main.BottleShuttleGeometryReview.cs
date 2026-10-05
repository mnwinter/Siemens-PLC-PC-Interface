using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyBottleShuttlePlacement(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-20-bottle-shuttle", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var conveyor = root.GetNode<Node3D>("shuttle_conveyor");
        var bottle = root.GetNode<Node3D>("shuttle_bottle");
        var body = (MeshInstance3D)bottle.FindChild("BOTTLE_BODY", true, false);
        var belt = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
        GD.Print($"BOTTLE_SHUTTLE_DATUM body={ReviewBounds(body)} belt={belt} root={bottle.Position}");
        check(MathF.Abs(ReviewBounds(body).Position.Y - belt.End.Y) < 0.0001f,
            "bottle_shuttle_body_seated_on_belt");
        var tail = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_tail_drum", true, false)).GetCenter().X;
        var drive = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_drive_drum", true, false)).GetCenter().X;
        var start = bottle.Position;
        var supported = true;
        // Authored route samples screen support; they do not prove runtime
        // reversal, sensor timing, acceleration, slip or dynamic stability.
        for (var index = 0; index <= 120; index++)
        {
            bottle.Position = new Vector3(-3 + index * 0.05f, start.Y, start.Z);
            var bounds = ReviewBounds(body);
            supported &= MathF.Abs(bounds.Position.Y - belt.End.Y) < 0.0001f
                && bounds.Position.X > MathF.Min(tail, drive) && bounds.End.X < MathF.Max(tail, drive)
                && bounds.Position.Z > belt.Position.Z && bounds.End.Z < belt.End.Z;
        }
        bottle.Position = start;
        check(supported, "bottle_shuttle_body_supported_through_121_authored_route_samples");

        var label = ReviewBounds((MeshInstance3D)bottle.FindChild("BOTTLE_LABEL", true, false));
        var band = ReviewBounds((MeshInstance3D)bottle.FindChild("BOTTLE_LABEL_BAND", true, false));
        var process = bottle.FindChild("BOTTLE_PRINT_PROCESS", true, false) as MeshInstance3D;
        var capacity = bottle.FindChild("BOTTLE_PRINT_CAPACITY", true, false) as MeshInstance3D;
        bool WithinPanel(MeshInstance3D? text, Aabb panel)
        {
            if (text is null) return false;
            var bounds = ReviewBounds(text);
            GD.Print($"BOTTLE_LABEL_DATUM {text.Name}={bounds} panel={panel}");
            return bounds.Position.X > panel.Position.X + 0.005f && bounds.End.X < panel.End.X - 0.005f
                && bounds.Position.Y > panel.Position.Y + 0.005f && bounds.End.Y < panel.End.Y - 0.005f;
        }
        check(WithinPanel(process, label) && process is not null && ReviewBounds(process).Position.Y > band.End.Y + 0.005f,
            "bottle_shuttle_process_legend_fits_label_above_color_band");
        check(WithinPanel(capacity, band), "bottle_shuttle_capacity_legend_fits_color_band");

        var sensors = new[] { root.GetNode<Node3D>("left_sensor"), root.GetNode<Node3D>("right_sensor") };
        check(sensors.All(sensor => ReviewMeshes(sensor).Where(mesh => mesh.Name.ToString().EndsWith("_foot", StringComparison.Ordinal))
            .All(mesh => MathF.Abs(ReviewBounds(mesh).Position.Y) < 0.001f)), "bottle_shuttle_sensor_feet_grounded");
        var clear = true;
        foreach (var sensor in sensors)
        foreach (var part in ReviewMeshes(sensor).Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)))
        foreach (var fixedPart in ReviewMeshes(conveyor))
        {
            var overlap = ReviewBounds(part).Intersection(ReviewBounds(fixedPart)).Size;
            if (overlap.X > 0.005f && overlap.Y > 0.005f && overlap.Z > 0.005f)
            {
                clear = false;
                GD.Print($"BOTTLE_SENSOR_CLEARANCE {sensor.Name}/{part.Name} vs {fixedPart.Name} overlap={overlap}");
            }
        }
        check(clear, "bottle_shuttle_sensor_mounts_and_cable_bounds_clear_conveyor");
        var neighborsClear = true;
        foreach (var sensor in sensors)
        foreach (var part in ReviewMeshes(sensor).Where(mesh => !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)))
        foreach (var neighbor in new[] { root.GetNode<Node3D>("shuttle_start"), root.GetNode<Node3D>("shuttle_status") })
        foreach (var fixedPart in ReviewMeshes(neighbor))
        {
            var overlap = ReviewBounds(part).Intersection(ReviewBounds(fixedPart)).Size;
            if (overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f) continue;
            neighborsClear = false;
            GD.Print($"BOTTLE_SENSOR_NEIGHBOR {sensor.Name}/{part.Name} vs {neighbor.Name}/{fixedPart.Name} overlap={overlap}");
        }
        check(neighborsClear, "bottle_shuttle_sensor_bounds_clear_start_station_and_status");
        var optical = true;
        for (var index = 0; index < sensors.Length; index++)
        {
            bottle.Position = new Vector3(index == 0 ? -3 : 3, start.Y, start.Z);
            for (var side = 0; side < sensors.Length; side++)
            {
                var from = ReviewBounds((MeshInstance3D)sensors[side].FindChild("RX_lens", true, false)).GetCenter();
                var to = ReviewBounds((MeshInstance3D)sensors[side].FindChild("TX_lens", true, false)).GetCenter();
                // The existing double-sided segment/triangle helper applies
                // to any mesh, including this cylindrical bottle body.
                optical &= LineHitsCableSurface(from, to, body) == (side == index);
            }
        }
        bottle.Position = start;
        check(optical, "bottle_shuttle_endpoint_rays_cross_only_the_corresponding_body_mesh");
    }
}
