using System;
using System.Linq;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyPlantMotion()
    {
        var passed = true;
        void Check(bool condition, string label)
        {
            passed &= condition;
            GD.Print($"PLANT_MOTION_CHECK {label}={condition}");
        }
        void Advance(int scans)
        {
            for (var scan = 0; scan < scans; scan++)
                _virtualController!.Advance(0.02, SampleVirtualControllerInputs, SampleVirtualControllerNumericInputs,
                    CommitVirtualControllerOutputs, CommitVirtualControllerNumericOutputs, _sceneRuntime!.AdvanceSimulation);
        }
        var contactId = 0;
        void SaveReviewProject(LadderProgram project, string sceneId, string name)
        {
            var document = new LadderEditorDocument();
            document.ReplaceFromProgram(project);
            document.SourceSceneId = sceneId;
            System.IO.File.WriteAllText(ProjectSettings.GlobalizePath($"res://.tools/plant-review-{name}.rpproj.json"), LadderEditorProjectJson.Save(document));
        }
        LadderNode Contact(string name, bool nc = false) => new($"contact-{++contactId}", LadderNodeKind.Contact, name, nc);
        LadderNode Series(string id, params LadderNode[] nodes) => new(id, LadderNodeKind.Series, Children: nodes);
        try
        {
            AddMigratedScene("scene-2-conveyor-pusher", _candidateCatalog!, _mainCamera!, false, false);
            PlcVariable Tag(string name, PlcVariableRole role, bool initial = false) =>
                new(name, PlcVariableType.Bool, role, initial, name);
            var program = new LadderProgram(1, "review-scene2", "Scene 2 reference sequence", "LD", TimeSpan.FromMilliseconds(20),
                [Tag("part_at_pusher", PlcVariableRole.Input), Tag("pusher_extended", PlcVariableRole.Input),
                    Tag("pusher_retracted", PlcVariableRole.Input, true), Tag("pusher_extend", PlcVariableRole.Output),
                    Tag("conveyor_running", PlcVariableRole.Output)],
                [new("set-extend", "Set at photoeye", Series("extend-permit", Contact("part_at_pusher"), Contact("pusher_retracted")),
                    new("set", "pusher_extend", LadderCoilMode.Set)),
                 new("reset-extend", "Reset wins at extended limit", Contact("pusher_extended"), new("reset", "pusher_extend", LadderCoilMode.Reset)),
                 new("conveyor", "Retracted and photoeye clear", Series("conveyor-permit", Contact("pusher_retracted"), Contact("part_at_pusher", true), Contact("pusher_extend", true)),
                     new("motor", "conveyor_running"))]);
            EnableVirtualControllerProgram(program);
            if (_virtualController is null) throw new InvalidOperationException(string.Join("; ", LadderCompiler.Validate(program).Select(issue => issue.Message)));
            SaveReviewProject(program, "scene-2-conveyor-pusher", "scene2");
            RunActiveController();
            var photoeyeSeen = false;
            var extensionSeen = false;
            var extendedSeen = false;
            for (var scan = 0; scan < 650; scan++)
            {
                Advance(1);
                photoeyeSeen |= _sceneRuntime!.Points["part_at_pusher"] is true;
                extensionSeen |= Convert.ToDouble(_sceneRuntime.Points["pusher_position"]) > 0;
                extendedSeen |= _sceneRuntime.Points["pusher_extended"] is true;
            }
            Check(photoeyeSeen, "scene2_photoeye_from_package_motion");
            Check(extensionSeen && extendedSeen, "scene2_stroke_and_limit_feedback");
            Check(Convert.ToInt64(_sceneRuntime!.Points["parts_completed"]) >= 2, "scene2_repeat_transfer_with_actual_ladder_scans");
            for (var scan = 0; scan < 250 && (Convert.ToDouble(_sceneRuntime.Points["pusher_position"]) <= 0
                || Convert.ToDouble(_sceneRuntime.Points["pusher_position"]) >= 75); scan++) Advance(1);
            Check(Convert.ToDouble(_sceneRuntime.Points["pusher_position"]) is > 0 and < 75, "scene2_stop_fixture_is_mid_stroke");
            StopActiveController();
            var stoppedStroke = _sceneRuntime.Points["pusher_position"];
            Advance(40);
            Check(Equals(stoppedStroke, _sceneRuntime.Points["pusher_position"]), "stopped_controller_holds_plant");
            ResetActiveController();
            Check(_sceneRuntime.Points["pusher_retracted"] is true && _sceneRuntime.Points["part_at_pusher"] is false
                && Convert.ToInt64(_sceneRuntime.Points["parts_completed"]) == 0, "scene2_reset_restores_initial_feedback");

            AddMigratedScene("tank-level", _candidateCatalog!, _mainCamera!, false, false);
            var tankProgram = new LadderProgram(1, "review-tank", "Tank plant exercise", "LD", TimeSpan.FromMilliseconds(20),
                [new("permit", PlcVariableType.Bool, PlcVariableRole.Memory, true), Tag("inlet_pump_run", PlcVariableRole.Output),
                 Tag("drain_valve_open", PlcVariableRole.Output),
                 new("level_transmitter", PlcVariableType.Real, PlcVariableRole.Input, 10.72, "level_transmitter")],
                [new("pump", "Inlet enabled", Contact("permit"), new("pump-coil", "inlet_pump_run"))]);
            EnableVirtualControllerProgram(tankProgram);
            SaveReviewProject(tankProgram, "tank-level", "tank");
            var initial = Convert.ToDouble(_sceneRuntime!.Points["tank_level"]);
            RunActiveController();
            Advance(100);
            var filled = Convert.ToDouble(_sceneRuntime.Points["tank_level"]);
            Check(Math.Abs(filled - (initial + 14)) < 1e-6, "tank_fills_from_ladder_output_without_hidden_local_run");
            Check(Math.Abs(Convert.ToDouble(_sceneRuntime.Points["level_transmitter"]) - (4 + 0.16 * filled)) < 1e-6,
                "tank_analog_feedback_tracks_actual_level");
            ApplyVirtualForce("inlet_pump_run", false);
            ApplyVirtualForce("drain_valve_open", true);
            Advance(100);
            var drained = Convert.ToDouble(_sceneRuntime.Points["tank_level"]);
            Check(Math.Abs(drained - (filled - 9)) < 1e-6, "tank_drain_output_changes_plant");
            StopActiveController();
            Advance(100);
            Check(Math.Abs(Convert.ToDouble(_sceneRuntime.Points["tank_level"]) - drained) < 1e-6,
                "tank_stopped_controller_holds_level");
            RemoveVirtualForce("inlet_pump_run");
            RemoveVirtualForce("drain_valve_open");
            RunActiveController();
            Advance(1000);
            Check(Convert.ToDouble(_sceneRuntime.Points["tank_level"]) == 100 && _sceneRuntime.Points["high_level_switch"] is true,
                "tank_high_limit_and_fill_saturation");
            ApplyVirtualForce("inlet_pump_run", false);
            ApplyVirtualForce("drain_valve_open", true);
            Advance(1500);
            Check(Convert.ToDouble(_sceneRuntime.Points["tank_level"]) == 0 && _sceneRuntime.Points["low_level_switch"] is true,
                "tank_low_limit_and_drain_saturation");
            ResetActiveController();
            Check(Math.Abs(Convert.ToDouble(_sceneRuntime.Points["tank_level"]) - initial) < 1e-6, "tank_reset_restores_level");
            GD.Print($"PLANT_MOTION_VERIFY {(passed ? "PASS" : "FAIL")} offline-only; no PLC transport");
            GetTree().Quit(passed ? 0 : 1);
        }
        catch (Exception exception)
        {
            GD.PushError($"PLANT_MOTION_VERIFY FAIL {exception}");
            GetTree().Quit(1);
        }
    }
}
