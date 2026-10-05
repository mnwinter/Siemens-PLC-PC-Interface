using System;
using System.Linq;
using Godot;
using RungProof.Next.App;
using RungProof.Next.Catalog;

namespace RungProof.Next.Scenes;

public static partial class SceneComposer
{
    private static Node3D CreatePusherAsset(SceneEquipment equipment, AssetCatalogDocument candidates,
        bool runCommand, float travelTimeSeconds)
    {
        var model = CreateMappedAsset(equipment, candidates, "actuation.pneumatic-pusher.1350mm.v1");
        var stroke = (float)Number(equipment.Config, "stroke", 1.35);
        if (!float.IsFinite(stroke) || stroke <= 0)
            throw new InvalidOperationException($"Pusher '{equipment.Id}' requires a positive finite stroke.");

        // Installation changes are explicit and happen before the motion
        // controller captures its home transforms. Other catalog uses retain
        // the delivered geometry. This is visual mounting, not cylinder sizing.
        if (Text(equipment.Config, "installation", string.Empty) == "conveyorPusher")
        {
            var centerHeight = (float)Number(equipment.Config, "centerHeight", 1.38);
            if (!float.IsFinite(centerHeight) || centerHeight < 0.8f)
                throw new InvalidOperationException($"Pusher '{equipment.Id}' requires centerHeight >= 0.8 m.");
            ConfigureConveyorPusher(model, centerHeight, stroke);
        }
        model.AddChild(new EquipmentMotionController
        {
            Name = "PneumaticPusherController", Kind = EquipmentMotionController.MotionKind.PneumaticPusher,
            TargetPrefix = "KIN_pusher_", RunCommand = runCommand,
            TravelM = stroke, TravelTimeSeconds = travelTimeSeconds,
        });
        return model;
    }

    private static void ConfigureConveyorPusher(Node3D model, float centerHeight, float stroke)
    {
        var meshes = model.FindChildren("*", "MeshInstance3D", true, false).OfType<MeshInstance3D>().ToArray();
        MeshInstance3D Part(string name) => meshes.Single(mesh => mesh.Name.ToString() == name);
        Aabb Bounds(MeshInstance3D mesh) => mesh.Transform * mesh.GetAabb();
        void SizeAndCenter(MeshInstance3D mesh, Vector3 size, Vector3 center)
        {
            var scale = size / Bounds(mesh).Size;
            var basis = Basis.FromScale(scale) * mesh.Basis;
            mesh.Transform = new Transform3D(basis, center - basis * mesh.GetAabb().GetCenter());
        }
        var lift = centerHeight - Bounds(Part("KIN_pusher_rod")).GetCenter().Y;
        foreach (var mesh in meshes)
        {
            var name = mesh.Name.ToString();
            if (name.StartsWith("FRAME_", StringComparison.Ordinal)) continue;
            // Plate fasteners were delivered as fixed siblings. They must
            // follow the plate rather than hang at home during extension.
            if (name.StartsWith("PLATE_bolt", StringComparison.Ordinal))
                mesh.Name = "KIN_pusher_" + name;
            // The source rails are below the conveyor and have no connection
            // to a receiver. Do not imply that they carry the departing carton.
            if (name.StartsWith("TRANSFER_wear_rail", StringComparison.Ordinal))
            {
                mesh.Visible = false;
                continue;
            }
            mesh.Position += Vector3.Up * lift;
        }

        // Separate guide rods from the round cylinder end caps. Widen the
        // moving crossmember so both outboard brackets stay attached to it.
        const float guideOffset = 0.40f;
        foreach (var mesh in meshes)
        {
            var name = mesh.Name.ToString();
            if (name.StartsWith("KIN_pusher_guide_shaft", StringComparison.Ordinal)
                || name.StartsWith("GUIDE_bearing", StringComparison.Ordinal)
                || name.StartsWith("KIN_pusher_bracket", StringComparison.Ordinal)
                || name.StartsWith("KIN_pusher_guide_locknut", StringComparison.Ordinal))
            {
                var center = Bounds(mesh).GetCenter();
                center.Z = MathF.CopySign(guideOffset, center.Z);
                if (name.StartsWith("KIN_pusher_guide_shaft", StringComparison.Ordinal))
                {
                    // Rigid guide shafts slide through their bearings. Extend
                    // their rear tails, preserving the front bracket seat.
                    var bounds = Bounds(mesh);
                    var length = bounds.Size.X + stroke;
                    center.X = bounds.End.X - length / 2;
                    SizeAndCenter(mesh, new Vector3(length, bounds.Size.Y, bounds.Size.Z), center);
                }
                else mesh.Position += center - Bounds(mesh).GetCenter();
            }
        }
        var crossmember = Part("KIN_pusher_crossmember");
        var crossBounds = Bounds(crossmember);
        SizeAndCenter(crossmember, new Vector3(crossBounds.Size.X, crossBounds.Size.Y, 0.94f), crossBounds.GetCenter());

        // Keep the floor base grounded, terminate it behind the conveyor, and
        // put actual supports beneath the barrel and the fixed guide bearings.
        SizeAndCenter(Part("FRAME_base"), new Vector3(2.10f, 0.14f, 0.95f), new Vector3(-0.10f, 0.07f, 0));
        var pedestals = meshes.Where(mesh => mesh.Name.ToString().StartsWith("FRAME_pedestal", StringComparison.Ordinal))
            .OrderBy(mesh => Bounds(mesh).GetCenter().X).ToArray();
        if (pedestals.Length != 3)
            throw new InvalidOperationException("Pusher installation requires its three delivered support columns.");
        var barrelBottom = Bounds(Part("CYLINDER_barrel")).Position.Y;
        var bearing = meshes.First(mesh => mesh.Name.ToString().StartsWith("GUIDE_bearing", StringComparison.Ordinal));
        var bearingBottom = Bounds(bearing).Position.Y;
        var supportXs = new[] { -0.65f, -0.15f, 0.82f };
        for (var index = 0; index < pedestals.Length; index++)
        {
            var top = index == 2 ? bearingBottom : barrelBottom;
            SizeAndCenter(pedestals[index], new Vector3(index == 2 ? 0.20f : 0.13f, top - 0.14f, index == 2 ? 0.95f : 0.58f),
                new Vector3(supportXs[index], (top + 0.14f) / 2, 0));
        }
        var manifold = Bounds(Part("VALVE_manifold"));
        model.AddChild(new MeshInstance3D
        {
            Name = "FRAME_manifold_post",
            Mesh = new BoxMesh { Size = new Vector3(0.10f, manifold.Position.Y - 0.14f, 0.10f) },
            Position = new Vector3(manifold.GetCenter().X, (manifold.Position.Y + 0.14f) / 2, manifold.GetCenter().Z),
            MaterialOverride = Part("FRAME_base").GetActiveMaterial(0),
        });
    }
}
