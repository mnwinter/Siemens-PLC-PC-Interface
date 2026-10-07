using System;
using System.Collections.Generic;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyToteCap(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-21-tote-finishing", _candidateCatalog!, _mainCamera!, false, false);
        var runtime = _sceneRuntime!;
        runtime.UsesExternalClock = true; runtime.SetControllerPlaybackRunning(true);
        void Command(bool travel, bool fill, bool cap) => runtime.CommitVirtualControllerOutputs(
            new Dictionary<string,bool> { ["conveyor_run"]=travel, ["fill_valve_open"]=fill, ["capper_run"]=cap });
        void Tick(int count, double dt=.02) { for(var i=0;i<count;i++) runtime.AdvanceSimulation(dt); }
        bool On(string point) => runtime.Points[point] is true;
        double Number(string point) => Convert.ToDouble(runtime.Points[point]);
        var tote = _sceneCompositionRoot!.GetNode<Node3D>("finishing_tote");
        var cap = (MeshInstance3D)tote.FindChild("IBC_fill_cap",true,false);
        var station = _sceneCompositionRoot.GetNode<Node3D>("capper");
        var held = (MeshInstance3D)station.FindChild("CAP_UNDER_CHUCK",true,false);
        var spindle = (Node3D)station.FindChild("KIN_capper_spindle",true,false);
        var home = spindle.GlobalPosition;
        Command(false,false,true);Tick(20);
        check(On("cap_inhibited") && !On("cap_applied") && Number("cap_extension_percent")==0,
            "off_station_command_cannot_apply");
        Command(true,false,false);Tick(428,.01);Command(false,true,false);Tick(501,.01);
        check(On("fill_complete"),"cap_fixture_has_actual_normalized_fill_complete");
        Command(true,false,false);Tick(345,.01);Command(false,false,true);Tick(10);
        check(On("tote_at_cap") && On("cap_busy") && !On("cap_applied") && spindle.GlobalPosition.Y<home.Y,
            "eligible_cap_command_lowers_actual_spindle_and_attached_chuck");
        var lowered=spindle.GlobalPosition;var extension=Number("cap_extension_percent");
        runtime.SetControllerPlaybackRunning(false);Tick(30);
        check(spindle.GlobalPosition.IsEqualApprox(lowered) && Number("cap_extension_percent")==extension && !On("cap_applied"),
            "stop_holds_actual_partial_cap_stroke");
        runtime.SetControllerPlaybackRunning(true);
        var positionBeforeConflict=Number("tote_position");
        Command(true,false,true);Tick(1);
        check(Number("tote_position")==positionBeforeConflict && On("cap_inhibited") && On("conveyor_run") && !On("cap_applied"),
            "conveyor_request_during_extension_holds_tote_and_aborts_cap_without_rewriting_command");
        Command(false,false,false);Tick(30);
        check(On("cap_home") && !On("cap_applied") && !cap.Visible && held.Visible && spindle.GlobalPosition.IsEqualApprox(home),
            "withdrawal_returns_retained_cap_without_application");
        Command(false,false,true);Tick(80);
        check(On("cap_applied") && On("cap_home") && cap.Visible && !held.Visible && spindle.GlobalPosition.IsEqualApprox(home),
            "accepted_cycle_releases_tote_cap_and_retracts_chuck");
        var capLocal=cap.Transform;Command(true,false,true);Tick(500);
        check(On("tote_at_exit") && On("cap_applied") && cap.Visible && cap.Transform.IsEqualApprox(capLocal) && !held.Visible,
            "applied_cap_remains_with_tote_at_supported_exit");
        runtime.ResetSimulation();
        check(!On("cap_applied") && On("cap_home") && !cap.Visible && held.Visible && spindle.GlobalPosition.IsEqualApprox(home),
            "reset_restores_open_tote_and_held_cap_home");
        runtime.SetControllerPlaybackRunning(false);
    }
}
