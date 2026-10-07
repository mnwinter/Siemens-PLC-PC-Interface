using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyServiceElevatorInstallation(Action<bool,string> check)
    {
        AddMigratedScene("lab-11-11-service-elevator", _candidateCatalog!, _mainCamera!, false, false);
        var scene = _sceneCompositionRoot!;
        var shaft = scene.GetNode<Node3D>("liftTable_0");
        var car = shaft.GetNode<Node3D>("KIN_service_elevator_car");
        var motion = shaft.GetNode<EquipmentMotionController>("ServiceElevatorPosition");
        var fixedParts = ReviewMeshes(shaft).Except(ReviewMeshes(car)).ToArray();
        bool Penetrates(Aabb a,Aabb b)
        {
            var overlap = a.Intersection(b).Size;
            return overlap.X > .001f && overlap.Y > .001f && overlap.Z > .001f;
        }
        check(LogBoundsCandidates(scene)==0,"elevator_separate_operator_equipment_clear_of_shaft");
        check(fixedParts.Count(p=>p.Name.ToString().StartsWith("ELEVATOR_landing_deck_"))==2,
            "elevator_has_two_distinct_landing_decks");
        var clear=true;
        for(var i=0;i<=100;i++)
        {
            motion.SetPositionNormalized(i/100f);
            foreach(var c in ReviewMeshes(car))
            foreach(var p in fixedParts)
            {
                if (!Penetrates(ReviewBounds(c),ReviewBounds(p))) continue;
                if(clear) GD.Print($"ELEVATOR_INTERFERENCE pose={i} car={c.Name} fixed={p.Name}");
                clear=false;
            }
        }
        check(clear,"elevator_101_car_poses_clear_fixed_shaft_and_landings");
        var deck=car.GetNode<MeshInstance3D>("ELEVATOR_car_floor");
        check(MathF.Abs(ReviewBounds(deck).End.Y-2.7f)<.001f,"elevator_upper_car_floor_matches_upper_landing");
        motion.SetPositionNormalized(0);
        check(MathF.Abs(ReviewBounds(deck).End.Y-.6f)<.001f,"elevator_lower_car_floor_matches_lower_landing");
        motion.Run();motion._PhysicsProcess(1);
        check(motion.InputPositionNormalized==0,"elevator_generic_run_cannot_fabricate_direction_sequence");
        motion.ResetMotion();
        _sceneRuntime!.ResetSimulation();
    }
}
