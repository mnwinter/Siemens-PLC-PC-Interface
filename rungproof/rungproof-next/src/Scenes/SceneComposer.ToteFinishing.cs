using System;
using System.Linq;
using Godot;
using RungProof.Next.App;
using RungProof.Next.Catalog;

namespace RungProof.Next.Scenes;

public static partial class SceneComposer
{
    // The catalog masters surround a floor-standing reference tote. This
    // installation adapts their mounting geometry to a 900 mm conveyor.
    // Only the finishing-line scene opts in; the masters remain unchanged.
    private static Node3D CreateToteFinishingStation(SceneEquipment equipment,
        AssetCatalogDocument candidates, bool runCommand)
    {
        var assetId = equipment.Type switch
        {
            "toteFiller" => "process.packaging.filler.tote-volumetric.v1",
            "toteCapper" => "process.packaging.capper.tote-inline.v1",
            "toteLabeler" => "process.packaging.labeler.tote-pressure-sensitive.v1",
            "toteVision" => "inspection.vision.tote-multicamera.v1",
            _ => throw new InvalidOperationException("Unsupported tote finishing station."),
        };
        var model = CreateMappedAsset(equipment, candidates, assetId);
        var parts = model.FindChildren("*", "MeshInstance3D", true, false).OfType<MeshInstance3D>().ToArray();
        MeshInstance3D Part(string name) => parts.Single(part => part.Name == name);
        // All imported parts are siblings. Rotate their actual transforms so
        // the capper/filler cantilevers reach across, rather than along, the belt.
        void TurnAcrossBelt()
        {
            var turn = new Transform3D(new Basis(Vector3.Up, Mathf.Pi / 2), Vector3.Zero);
            foreach (var part in parts) part.Transform = turn * part.Transform;
        }
        void Place(MeshInstance3D part, Vector3 size, Vector3 center)
        {
            var bounds = part.Transform * part.GetAabb();
            var basis = Basis.FromScale(size / bounds.Size) * part.Basis;
            part.Transform = new Transform3D(basis, center - basis * part.GetAabb().GetCenter());
        }
        void Beam(string name, Vector3 size, Vector3 center, Material material)
            => AddBox(model, size, center, material).Name = name;
        void Attach(Node3D child, Node3D parent)
        {
            var local = parent.Transform.AffineInverse() * child.Transform;
            child.Owner = null;
            child.GetParent().RemoveChild(child);
            parent.AddChild(child);
            child.Transform = local;
        }

        if (equipment.Type == "toteFiller")
        {
            TurnAcrossBelt();
            foreach (var part in parts.Where(part => !part.Name.ToString().StartsWith("DRIP_TRAY", StringComparison.Ordinal)
                && part.Name != "FILLER_BASE" && part.Name != "FILLER_COLUMN"
                && part.Name != "SUPPLY_RESERVOIR" && part.Name != "SUPPLY_SIGHT_GLASS"))
                part.Position += Vector3.Up * 0.9f;
            var column = Part("FILLER_COLUMN");
            var steel = column.GetActiveMaterial(0)!;
            Place(column, new Vector3(0.30f, 3.30f, 0.28f), new Vector3(-0.4f, 1.77f, -1.30f));
            Place(Part("FILLER_BASE"), new Vector3(0.60f, 0.12f, 0.60f), new Vector3(-0.4f, 0.06f, -1.30f));
            Place(Part("NOZZLE_BOOM"), new Vector3(0.30f, 0.26f, 1.70f), new Vector3(-0.10f, 3.24f, -0.55f));
            foreach (var name in new[] { "FILLER_CONTROL_PANEL", "FILLER_HMI", "FILLER_ESTOP" })
                Part(name).Position += new Vector3(-0.35f, -0.9f, -0.70f);
            Beam("FINISHING_control_mount", new Vector3(0.40f, 0.12f, 0.12f), new Vector3(-0.23f, 1.6f, -1.30f), steel);
            foreach (var name in new[] { "SUPPLY_RESERVOIR", "SUPPLY_SIGHT_GLASS" })
                Part(name).Position += new Vector3(0, -0.035f, 0.95f);
            Beam("FINISHING_supply_base", new Vector3(0.90f, 0.12f, 0.85f), new Vector3(-0.36f, 0.06f, 1.55f), steel);
            PoseTube(Part("SUPPLY_PIPE_RISER"), new Vector3(-0.36f, 1.37f, 1.57f), new Vector3(-0.36f, 3.45f, 1.57f));
            PoseTube(Part("SUPPLY_PIPE_HEADER"), new Vector3(-0.36f, 3.45f, 1.57f), new Vector3(-0.10f, 3.45f, -0.28f));
            PoseTube(Part("PRODUCT_HOSE"), new Vector3(-0.10f, 3.45f, -0.28f), new Vector3(-0.10f, 3.61f, -0.28f));
            PoseTube(Part("PRODUCT_HOSE_DROP"), new Vector3(-0.10f, 3.0f, -0.28f), new Vector3(0, 3.05f, 0));
            Part("FLOW_METER").Position = new Vector3(-0.25f, 3.45f, 0.80f);
            // The original tray belongs below a floor-mounted tote. Relocate
            // it below the belt, clear of the conveyor frame; it is not a deck.
            Place(Part("DRIP_TRAY"), new Vector3(1.28f, 0.12f, 0.96f), new Vector3(0, 0.20f, 0));
            foreach (var part in parts.Where(part => part.Name.ToString().StartsWith("DRIP_TRAY_DRAIN", StringComparison.Ordinal)))
                part.Position += Vector3.Down * 0.035f;
            var nozzle = Part("KIN_fill_nozzle");
            var stream = Part("VISIBLE_LIQUID_STREAM");
            stream.Name = "FINISHING_stream";
            stream.Visible = false;
            Attach(Part("NOZZLE_TIP"), nozzle);
            Attach(stream, nozzle);
            model.AddChild(new EquipmentMotionController
            {
                Name = "FinishingNozzleController", Kind = EquipmentMotionController.MotionKind.LinearY,
                TargetPrefix = "KIN_fill_nozzle", TravelM = -0.12f, TravelTimeSeconds = 0.35f,
                RunCommand = runCommand, PositionVisibilityChildName = "FINISHING_stream",
            });
        }
        else if (equipment.Type == "toteCapper")
        {
            TurnAcrossBelt();
            foreach (var part in parts.Where(part => part.Name != "CAPPER_BASE" && part.Name != "CAPPER_COLUMN"))
                part.Position += Vector3.Up;
            var column = Part("CAPPER_COLUMN");
            var steel = column.GetActiveMaterial(0)!;
            Place(column, new Vector3(0.34f, 3.40f, 0.30f), new Vector3(-0.38f, 1.82f, -1.90f));
            Place(Part("CAPPER_BASE"), new Vector3(0.80f, 0.12f, 0.60f), new Vector3(-0.38f, 0.06f, -1.90f));
            Place(Part("CAPPER_CANTILEVER"), new Vector3(0.38f, 0.30f, 2.40f), new Vector3(-0.10f, 3.22f, -0.85f));
            foreach (var name in new[] { "CAPPER_CONTROL_PANEL", "CAPPER_HMI" })
                Part(name).Position += new Vector3(-0.20f, -1, -1.20f);
            Beam("FINISHING_control_mount", new Vector3(0.48f, 0.12f, 0.12f), new Vector3(-0.20f, 1.62f, -1.90f), steel);
            var guard = Part("GUARD_FRONT");
            guard.Transform = new Transform3D(Basis.Identity, new Vector3(0, 2.72f, -1.0f));
            Beam("FINISHING_guard_mount", new Vector3(1.18f, 0.10f, 1.05f), new Vector3(0, 2.20f, -1.45f), steel);
            // The chuck follows the spindle rotation instead of remaining an
            // independent stationary sibling. Axial cap application is not
            // modeled by this rotation-only command.
            var spindle = Part("KIN_capper_spindle");
            foreach (var name in new[] { "TORQUE_CHUCK", "TORQUE_CHUCK_BODY", "CHUCK_GRIP_RING", "CAP_UNDER_CHUCK" })
                Attach(Part(name), spindle);
            model.AddChild(new EquipmentMotionController
            {
                Name = "FinishingCapperController", Kind = EquipmentMotionController.MotionKind.ContinuousRotation,
                TargetPrefix = "KIN_capper_spindle", SpeedRpm = 180, RunCommand = runCommand,
                RotationAxis = spindle.Basis.Inverse() * Vector3.Up,
            });
        }
        else if (equipment.Type == "toteLabeler")
        {
            TurnAcrossBelt();
            foreach (var part in parts) part.Position += Vector3.Back * 1.12f;
            var basePart = Part("LABELER_BASE");
            Place(basePart, new Vector3(1.30f, 0.12f, 1.25f), new Vector3(0, 0.06f, 1.77f));
            // Side-facing applicator stays outside the swept tote envelope.
            // Its existing command animates the roll, not a fabricated tamp.
            model.AddChild(new EquipmentMotionController
            {
                Name = "FinishingLabelerController", Kind = EquipmentMotionController.MotionKind.ContinuousRotation,
                TargetPrefix = "KIN_label_roll", SpeedRpm = 55, RunCommand = runCommand,
                RotationAxis = Part("KIN_label_roll").Basis.Inverse() * Vector3.Right,
            });
        }
        else
        {
            var post = Part("VISION_ARCH_POST_0_72");
            var steel = post.GetActiveMaterial(0)!;
            foreach (var part in parts.Where(part => !part.Name.ToString().StartsWith("VISION_", StringComparison.Ordinal)
                && part.Name != "BACKLIGHT_PANEL"))
                part.Position += new Vector3(0, 0, -1.75f);
            foreach (var (name, side) in new[] { ("VISION_ARCH_POST_0_72", 1), ("VISION_ARCH_POST_-0_72", -1) })
                Place(Part(name), new Vector3(0.18f, 2.48f, 0.22f), new Vector3(0, 1.36f, side * 1.90f));
            Place(Part("VISION_ARCH_HEADER"), new Vector3(0.22f, 0.20f, 4.02f), new Vector3(0, 2.60f, 0));
            Place(Part("VISION_BASE"), new Vector3(0.60f, 0.12f, 0.60f), new Vector3(0, 0.06f, -1.90f));
            Beam("FINISHING_vision_front_foot", new Vector3(0.60f, 0.12f, 0.60f), new Vector3(0, 0.06f, 1.90f), steel);
            Place(Part("BACKLIGHT_PANEL"), new Vector3(1.20f, 1.08f, 0.05f), new Vector3(0, 1.55f, 1.12f));
            Beam("FINISHING_backlight_mount", new Vector3(0.12f, 0.12f, 0.90f), new Vector3(0, 1.55f, 1.55f), steel);
            Beam("FINISHING_camera_rail", new Vector3(1.55f, 0.10f, 0.10f), new Vector3(0, 1.58f, -1.55f), steel);
            Beam("FINISHING_camera_mount", new Vector3(0.12f, 0.12f, 0.80f), new Vector3(0, 1.58f, -1.55f), steel);
            Beam("FINISHING_camera_vertical_mount", new Vector3(0.12f, 0.70f, 0.10f), new Vector3(0, 1.88f, -1.85f), steel);
            Attach(Part("MAIN_OPTIC_GLASS"), Part("KIN_vision_lens"));
            model.AddChild(new EquipmentMotionController
            {
                Name = "FinishingVisionController", Kind = EquipmentMotionController.MotionKind.OscillatingRotation,
                TargetPrefix = "KIN_vision_lens", TravelDegrees = 8, RunCommand = runCommand,
            });
        }
        return model;
    }
}
