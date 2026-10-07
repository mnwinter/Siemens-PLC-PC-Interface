using System;
using System.Collections.Generic;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyToteStartCommand(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-21-tote-finishing", _candidateCatalog!, _mainCamera!, false, false);
        var document = new LadderEditorDocument();
        document.ResetProject("review-tote-start-binding", "Tote_Start_Binding_Probe", TimeSpan.FromMilliseconds(20));
        document.SourceSceneId = "lab-2-21-tote-finishing";
        document.AddTag("start_request", PlcVariableRole.Input, "operator.start");
        document.AddTag("start_seen", PlcVariableRole.Memory);
        foreach (var name in new[] { "conveyor_run", "fill_valve_open", "capper_run", "labeler_run", "inspection_run" })
            document.AddTag(name, PlcVariableRole.Output, name);
        var rung = document.Rungs.Count;
        document.AddRung("Capture the operator Start pulse without commanding actuators", "start_seen").CoilMode = LadderCoilMode.Set;
        document.AddContact(rung, 0, "start_request", false);
        EnableVirtualControllerProgram(document.BuildProgram());
        try
        {
            RunActiveController();
            _PhysicsProcess(.02);
            check(!_virtualController!.Snapshot.Variables.GetValueOrDefault("start_seen"), "tote_start_run_alone_does_not_pulse_start");
            var accepted = ExecuteSelectedControllerAction("start-line");
            _PhysicsProcess(.02);
            check(accepted && _virtualController.Snapshot.Variables.GetValueOrDefault("start_seen"),
                "tote_start_3d_action_reaches_declared_ladder_start_input");
            _PhysicsProcess(.02);
            check(!_virtualController.Snapshot.Variables.GetValueOrDefault("start_request"), "tote_start_command_is_a_single_scan_pulse");
            ResetActiveController();
            check(!_virtualController.Snapshot.Variables.GetValueOrDefault("start_seen"), "tote_start_reset_clears_probe_state");
            check(!ExecuteSelectedControllerAction("start-line"), "tote_start_stopped_controller_rejects_command");
        }
        finally { DisableVirtualController(); }
    }
}
