using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _auditDualSpindle;

    // Deliberately separate from the accepted geometry regression suite:
    // this audit reproduces unresolved cell requirements and exits nonzero
    // until the delivered cell actually satisfies them. No PLC is contacted.
    private void AuditDualSpindle()
    {
        var failures = 0;
        void Check(bool condition, string requirement)
        {
            if (!condition) failures++;
            GD.Print($"DUAL_SPINDLE_AUDIT {requirement}={condition}");
        }
        try
        {
            AddMigratedScene("lab-2-22-dual-spindle", _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var runtime = _sceneRuntime!;
            runtime.UsesExternalClock = false; // Explicit reference preview only.
            var fixture = root.GetNode<Node3D>("metal_plate");
            var slide = root.GetNode<Node3D>("plate_transfer");
            var drills = new[] { root.GetNode<Node3D>("drill_a"), root.GetNode<Node3D>("drill_b") };
            MeshInstance3D Part(Node node, string name) => (MeshInstance3D)node.FindChild(name, true, false);
            var stock = Part(fixture, "STEEL_WORKPIECE");
            var subplate = Part(fixture, "FIXTURE_SUBPLATE");
            var bits = drills.Select(drill => Part(drill, "DRILL_bit")).ToArray();
            var spindles = drills.Select(drill => (Node3D)drill.FindChild("KIN_spindle", true, false)).ToArray();
            var home = spindles.Select(spindle => spindle.GlobalPosition).ToArray();
            var fixtureHome = fixture.Transform;
            foreach (var equipment in root.GetChildren().OfType<Node3D>())
            foreach (var mesh in ReviewMeshes(equipment))
                GD.Print($"DUAL_SPINDLE_MESH {equipment.Name}/{mesh.Name} {ReviewBounds(mesh)}");
            var stockBounds = ReviewBounds(stock);
            bool AxesOverStock() => bits.All(bit =>
            {
                var center = ReviewBounds(bit).GetCenter();
                return center.X >= stockBounds.Position.X && center.X <= stockBounds.End.X
                    && center.Z >= stockBounds.Position.Z && center.Z <= stockBounds.End.Z;
            });
            Check(AxesOverStock(), "both_drill_axes_over_the_shared_steel_workpiece");
            Check(drills.All(drill => ReviewMeshes(drill).All(mesh => mesh.Name != "DRILL_workpiece")),
                "one_shared_workpiece_without_separate_drill_coupons");
            // Necessary mounting contact, not a proof of load capacity. The
            // fixture's actual bottom must bear on an existing table/slide.
            bool HasBearingContact()
            {
                var bottom = ReviewBounds(subplate);
                return root.GetChildren().OfType<Node3D>().Where(node => node != fixture)
                    .SelectMany(ReviewMeshes).Any(mesh =>
                    {
                        var support = ReviewBounds(mesh);
                        return MathF.Abs(support.End.Y - bottom.Position.Y) <= 0.002f
                            && support.Position.X < bottom.End.X && support.End.X > bottom.Position.X
                            && support.Position.Z < bottom.End.Z && support.End.Z > bottom.Position.Z;
                    });
            }
            Check(HasBearingContact(), "fixture_has_actual_bearing_surface_at_home");
            var controllers = root.FindChildren("*", "", true, false).OfType<EquipmentMotionController>().ToArray();
            var slidePlate = Part(slide, "KIN_pusher_plate");
            var plateHome = slidePlate.GlobalPosition;
            var maximumFeed = new float[2];
            var maximumSlide = 0.0f;
            var supported = true;
            var contactAtTransfer = true;
            var transferObserved = false;
            runtime.ExecuteAction("start-dual-drill");
            for (var tick = 0; tick < 3000; tick++)
            {
                runtime.AdvanceSimulation(0.002);
                foreach (var controller in controllers) controller._PhysicsProcess(0.002);
                for (var index = 0; index < drills.Length; index++)
                    maximumFeed[index] = MathF.Max(maximumFeed[index], home[index].Y - spindles[index].GlobalPosition.Y);
                maximumSlide = MathF.Max(maximumSlide, slidePlate.GlobalPosition.DistanceTo(plateHome));
                supported &= HasBearingContact();
                if (runtime.Points["transfer_extend"] is true)
                {
                    transferObserved = true;
                    contactAtTransfer &= ReviewBounds(slidePlate).Grow(0.002f).Intersects(ReviewBounds(subplate));
                }
            }
            var travel = fixture.GlobalPosition.X - fixtureHome.Origin.X;
            GD.Print($"DUAL_SPINDLE_TRAVEL fixtureX={travel} slide={maximumSlide} feedA={maximumFeed[0]} feedB={maximumFeed[1]}");
            Check(maximumFeed.All(feed => feed > 0.001f), "both_declared_position_motions_produce_axial_feed");
            Check(supported, "fixture_has_bearing_contact_through_entire_preview");
            Check(transferObserved && contactAtTransfer, "slide_contacts_fixture_through_transfer");
            Check(MathF.Abs(travel - maximumSlide) <= 0.002f, "fixture_transfer_matches_actual_slide_stroke");
            Check(runtime.Points["cycle_complete"] is true, "timed_reference_reports_completion");
            runtime.ResetSimulation();
            Check(fixture.Transform.IsEqualApprox(fixtureHome), "reset_restores_fixture_home");
        }
        catch (Exception error)
        {
            failures++;
            GD.PushError($"DUAL_SPINDLE_AUDIT_EXCEPTION {error}");
        }
        GD.Print($"DUAL_SPINDLE_AUDIT_RESULT failures={failures}; bounds/contact screen only, no mechanical or controller acceptance");
        GetTree().Quit(failures == 0 ? 0 : 1);
    }
}
