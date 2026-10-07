using System;
using System.Collections.Generic;
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
        var runtime=_sceneRuntime;
        runtime.UsesExternalClock=true;
        runtime.SetControllerPlaybackRunning(true);
        void Command(bool up,bool down) => runtime.CommitVirtualControllerOutputs(new Dictionary<string,bool>
            { ["lift_up_cmd"]=up,["lift_down_cmd"]=down });
        void Tick(int n) { for(var i=0;i<n;i++) runtime.AdvanceSimulation(.02); }
        foreach(var name in new[]{"call_valid","doors_closed","landing_clear"}) runtime.ExecuteAction("toggle-"+name);
        Command(true,false);Tick(150);
        check(Math.Abs(Convert.ToDouble(runtime.Points["car_position_pct"])-50)<.001
            && runtime.Points["at_lower_landing"] is false && runtime.Points["at_upper_landing"] is false,
            "elevator_single_up_command_reaches_mid_travel_with_matching_floor_flags");
        var held=car.Transform;
        Command(true,true);Tick(20);
        check(car.Transform==held && runtime.Points["direction_conflict"] is true
            && runtime.Points["lift_up_cmd"] is true && runtime.Points["lift_down_cmd"] is true,
            "elevator_opposing_commands_hold_and_remain_visible_for_diagnosis");
        Command(true,false);
        foreach(var name in new[]{"call_valid","doors_closed","landing_clear"})
        {
            runtime.ExecuteAction("toggle-"+name);Tick(20);
            check(car.Transform==held,"elevator_missing_"+name+"_holds_position");
            runtime.ExecuteAction("toggle-"+name);
        }
        runtime.SetControllerPlaybackRunning(false);Tick(20);
        check(car.Transform==held,"elevator_stopped_controller_clock_holds_position");
        runtime.SetControllerPlaybackRunning(true);Tick(200);
        check(runtime.Points["at_upper_landing"] is true && Math.Abs(Convert.ToDouble(runtime.Points["car_position_pct"])-100)<.001,
            "elevator_upper_endpoint_clamps_and_projects_feedback");
        Command(false,true);Tick(350);
        check(runtime.Points["at_lower_landing"] is true && Math.Abs(Convert.ToDouble(runtime.Points["car_position_pct"]))<.001,
            "elevator_down_command_returns_and_clamps_lower_endpoint");
        runtime.ResetSimulation();
        check(runtime.Points["at_lower_landing"] is true && runtime.Points["direction_conflict"] is false
            && runtime.Points["lift_up_cmd"] is false && runtime.Points["lift_down_cmd"] is false,
            "elevator_reset_restores_home_and_command_image");
    }
}
