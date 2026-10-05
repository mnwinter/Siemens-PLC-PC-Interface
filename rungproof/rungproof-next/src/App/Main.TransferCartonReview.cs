using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
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
