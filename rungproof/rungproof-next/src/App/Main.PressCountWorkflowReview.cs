using System;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyPressCountWorkflow(Action<bool, string> check)
    {
        AddMigratedScene("lab-4-01-press-count-lamp", _candidateCatalog!, _mainCamera!, false, false);
        check(_sceneCompositionRoot!.GetNode<Node3D>("switch_0")
            .GetNodeOrNull<Label3D>("OperatorFaceLabel")?.Text == "PULSE",
            "press_count_operator_plate_identifies_input_pulse");
        AuthoredDemoLadderPrograms.TryCreate("lab-4-01-press-count-lamp", out var document);
        EnableVirtualControllerProgram(document.BuildProgram());
        try
        {
            var runtime = _sceneRuntime!;
            _virtualController!.Run();
            // Exercise the actual scene action, mapper, fixed scan session and
            // output projection together. A synthetic false/true input loop
            // alone would miss the original scene's persistent toggle defect.
            var oneEdgePerAction = true;
            for (var press = 1; press <= 3; press++)
            {
                runtime.ExecuteAction("toggle-pulse_received");
                _PhysicsProcess(0.040); // one accepted high scan, then a low scan
                oneEdgePerAction &= _virtualController.Snapshot.Counters["press_count"].Accumulated == press
                    && runtime.Points["pulse_received"] is false
                    && Equals(runtime.Points["threshold_lamp"], press == 3);
            }
            check(oneEdgePerAction, "press_count_three_scene_actions_count_three_edges_and_light_only_at_preset");
            _PhysicsProcess(1.0);
            check(_virtualController.Snapshot.Counters["press_count"].Accumulated == 3
                && runtime.Points["threshold_lamp"] is true,
                "press_count_idle_scans_do_not_recount_button_pulses");
            CommitVirtualControllerSnapshot(_virtualController.Stop());
            check(runtime.Points["threshold_lamp"] is false
                && _virtualController.Snapshot.Counters["press_count"].Accumulated == 3,
                "press_count_stop_removes_lamp_command_without_resetting_counter");
            runtime.ResetSimulation();
            CommitVirtualControllerSnapshot(_virtualController.Reset());
            check(runtime.Points["pulse_received"] is false && runtime.Points["threshold_lamp"] is false
                && _virtualController.Snapshot.Counters["press_count"].Accumulated == 0,
                "press_count_reset_clears_input_output_and_counter");
        }
        finally
        {
            DisableVirtualController();
        }
    }
}
