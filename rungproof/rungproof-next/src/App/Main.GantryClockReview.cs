using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using RungProof.Next.Scenes;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private HBoxContainer? _gantryReviewClockBar;
    private CheckButton? _gantryReviewHold;
    private Button? _gantryReviewStep;
    private Label? _gantryReviewClockLabel;
    private Node3D? _gantryReviewHeldRoot;
    private SceneSimulationRuntime? _gantryReviewHeldRuntime;
    private ProcessModeEnum _gantryReviewRootMode;
    private ProcessModeEnum _gantryReviewRuntimeMode;
    private bool _gantryReviewStepping;
    private bool _gantryReviewOperatorView = true;

    // Scoped to reviewed offline clock implementations: the autonomous
    // gantry adapter and the single-clock chain lift / cookie / barrel / cable plants. Other scenes may
    // have separate callbacks; this is not a general external PLC step.
    private bool CanReviewGantryClock => _visualSceneReview && !_visualPlantReview
        && _currentSceneId is "lab-11-13-xy-palletizing" or "lab-4-09-chain-drive-lift" or "lab-4-10-cookie-packaging" or "lab-4-11-barrel-fill-station" or "lab-4-12-cable-cut-length"
        && _simulatorShell?.IsExternalMode != true;

    private bool GantryReviewClockHeld => _gantryReviewHeldRoot is not null
        && ReferenceEquals(_gantryReviewHeldRoot, _sceneCompositionRoot);

    private void AddGantryReviewClockControls(CanvasLayer layer)
    {
        _gantryReviewClockBar = new HBoxContainer { Position = new Vector2(310, 162) };
        layer.AddChild(_gantryReviewClockBar);
        _gantryReviewHold = new CheckButton { Text = "Hold offline plant clock" };
        _gantryReviewStep = new Button { Text = "Step 0.5 s", Disabled = true };
        _gantryReviewClockLabel = new Label();
        _gantryReviewClockBar.AddChild(_gantryReviewHold);
        _gantryReviewClockBar.AddChild(_gantryReviewStep);
        _gantryReviewClockBar.AddChild(_gantryReviewClockLabel);
        _gantryReviewHold.Toggled += SetGantryReviewClockHeld;
        _gantryReviewStep.Pressed += StepGantryReviewClock;
        _simulatorShell!.ProductViewChanged += view =>
        {
            _gantryReviewOperatorView = view == "operator";
            if (!_gantryReviewOperatorView) ReleaseGantryReviewClock();
            RefreshGantryReviewClockControls();
        };
        RefreshGantryReviewClockControls();
    }

    private void RefreshGantryReviewClockControls()
    {
        if (!CanReviewGantryClock) ReleaseGantryReviewClock();
        if (_gantryReviewClockBar is not null)
            _gantryReviewClockBar.Visible = CanReviewGantryClock && _gantryReviewOperatorView;
        if (_gantryReviewStep is not null)
            _gantryReviewStep.Text = _currentSceneId is "lab-4-09-chain-drive-lift" or "lab-4-10-cookie-packaging" or "lab-4-11-barrel-fill-station" ? "Step 2.0 s" : "Step 0.5 s";
        UpdateGantryReviewClockLabel();
    }

    private void SetGantryReviewClockHeld(bool held)
    {
        if (!held) { ReleaseGantryReviewClock(); return; }
        if (!CanReviewGantryClock || _sceneCompositionRoot is null || _sceneRuntime is null)
        {
            _gantryReviewHold?.SetPressedNoSignal(false);
            return;
        }
        if (GantryReviewClockHeld) return;
        _gantryReviewHeldRoot = _sceneCompositionRoot;
        _gantryReviewHeldRuntime = _sceneRuntime;
        _gantryReviewRootMode = _sceneCompositionRoot.ProcessMode;
        _gantryReviewRuntimeMode = _sceneRuntime.ProcessMode;
        _sceneCompositionRoot.ProcessMode = ProcessModeEnum.Disabled;
        _sceneRuntime.ProcessMode = ProcessModeEnum.Disabled;
        GD.Print("GANTRY_REVIEW_CLOCK held=True offline-only");
        UpdateGantryReviewClockLabel();
    }

    private void ReleaseGantryReviewClock()
    {
        if (_gantryReviewHeldRoot is not null && GodotObject.IsInstanceValid(_gantryReviewHeldRoot))
            _gantryReviewHeldRoot.ProcessMode = _gantryReviewRootMode;
        if (_gantryReviewHeldRuntime is not null && GodotObject.IsInstanceValid(_gantryReviewHeldRuntime))
            _gantryReviewHeldRuntime.ProcessMode = _gantryReviewRuntimeMode;
        _gantryReviewHeldRoot = null;
        _gantryReviewHeldRuntime = null;
        _gantryReviewHold?.SetPressedNoSignal(false);
        UpdateGantryReviewClockLabel();
    }

    private void StepGantryReviewClock()
    {
        if (!CanReviewGantryClock || !GantryReviewClockHeld
            || _virtualController?.Snapshot.State != VirtualControllerState.Running) return;
        var chainLift = _currentSceneId == "lab-4-09-chain-drive-lift";
        var indexedPlant = _currentSceneId is "lab-4-10-cookie-packaging" or "lab-4-11-barrel-fill-station" or "lab-4-12-cable-cut-length";
        var motion = indexedPlant ? null : chainLift ? _sceneCompositionRoot!.GetNode<Node3D>("liftTable_1").GetNode<EquipmentMotionController>("ChainLiftMotion")
            : _sceneCompositionRoot!.GetNode<Node3D>("training_accessory_4").GetNode<EquipmentMotionController>("GantryCommandMotion");
        _gantryReviewStepping = true;
        try
        {
            // Preserve the existing input -> ladder -> output -> plant path,
            // at the authored 20 ms scan cadence. The disabled parent prevents
            // Godot from also advancing autonomous equipment during inspection.
            for (var tick = 0; tick < (_currentSceneId == "lab-4-12-cable-cut-length" ? 25 : chainLift || indexedPlant ? 100 : 25); tick++)
            {
                _PhysicsProcess(0.02);
                if (!chainLift && !indexedPlant && motion!.IsPhysicsProcessing()) motion._PhysicsProcess(0.02);
            }
        }
        finally { _gantryReviewStepping = false; }
        UpdateGantryReviewClockLabel();
        GD.Print($"GANTRY_REVIEW_STEP time={_virtualController.Snapshot.SimulatedTime.TotalSeconds:F2} scan={_virtualController.Snapshot.ScanNumber} position={motion?.PositionPercent ?? 0:F3}%");
    }

    private void UpdateGantryReviewClockLabel()
    {
        if (_gantryReviewStep is not null)
            _gantryReviewStep.Disabled = !GantryReviewClockHeld
                || _virtualController?.Snapshot.State != VirtualControllerState.Running;
        if (_gantryReviewClockLabel is null) return;
        var motion = _sceneCompositionRoot?.FindChildren("*", string.Empty, true, false)
            .OfType<EquipmentMotionController>().FirstOrDefault(item => item is ChainLiftDriveVisual || item.Kind == EquipmentMotionController.MotionKind.CartesianGantry);
        if (_currentSceneId == "lab-4-12-cable-cut-length")
        {
            _gantryReviewClockLabel.Text = $"QA | {(_virtualController?.Snapshot.SimulatedTime.TotalSeconds ?? 0):F2} s | length {_sceneRuntime?.Points.GetValueOrDefault("measured_length_m") ?? 0:0.00} m | blade {_sceneRuntime?.Points.GetValueOrDefault("cutter_position") ?? 0:0.00}";
            return;
        }
        if (_currentSceneId == "lab-4-11-barrel-fill-station")
        {
            _gantryReviewClockLabel.Text = $"QA | {(_virtualController?.Snapshot.SimulatedTime.TotalSeconds ?? 0):F2} s | barrel {_sceneRuntime?.Points.GetValueOrDefault("barrel_litres") ?? 0:0.0} L | source {_sceneRuntime?.Points.GetValueOrDefault("source_litres") ?? 0:0.0} L";
            return;
        }
        if (_currentSceneId == "lab-4-10-cookie-packaging")
        {
            _gantryReviewClockLabel.Text = $"QA | {(_virtualController?.Snapshot.SimulatedTime.TotalSeconds ?? 0):F2} s | cookies {_sceneRuntime?.Points.GetValueOrDefault("cookie_count") ?? 0} | sealed {_sceneRuntime?.Points.GetValueOrDefault("wrapped_count") ?? 0}";
            return;
        }
        _gantryReviewClockLabel.Text = $"QA · {(_virtualController?.Snapshot.SimulatedTime.TotalSeconds ?? 0):F2} s · stroke {motion?.PositionPercent ?? 0:F1}%";
    }

    private void VerifyGantryReviewClock(Action<bool, string> check)
    {
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        var rootMode = root.ProcessMode;
        var runtimeMode = runtime.ProcessMode;
        var motion = root.GetNode<Node3D>("training_accessory_4").GetNode<EquipmentMotionController>("GantryCommandMotion");
        var axes = root.GetNode<Node3D>("training_accessory_4").FindChildren("KIN_*", string.Empty, true, false)
            .OfType<Node3D>().ToArray();
        var home = axes.Select(axis => axis.Transform).ToArray();
        SetGantryReviewClockHeld(true);
        runtime.ExecuteAction("toggle-gantry_home");
        runtime.ExecuteAction("toggle-pallet_position_valid");
        runtime.ExecuteAction("toggle-carton_at_pick");
        RunActiveController();
        var scans = _virtualController!.Snapshot.ScanNumber;
        _PhysicsProcess(5);
        check(GantryReviewClockHeld && !motion.CanProcess()
            && _virtualController.Snapshot.ScanNumber == scans
            && axes.Select((axis, index) => axis.Transform == home[index]).All(held => held),
            "demo5_review_hold_freezes_controller_and_native_equipment_clock");
        var matches = true;
        foreach (var expected in new[] { 25f, 75f, 100f, 75f, 25f, 0f })
        {
            StepGantryReviewClock();
            matches &= Math.Abs(motion.PositionPercent - expected) < 0.01f;
        }
        check(matches && _virtualController.Snapshot.ScanNumber == scans + 150
            && Math.Abs(_virtualController.Snapshot.SimulatedTime.TotalSeconds - 3) < 1e-6,
            "demo5_review_steps_actual_ladder_and_complete_gantry_sweep_at_twenty_ms_cadence");
        StepGantryReviewClock();
        StopActiveController();
        var stopped = axes.Select(axis => axis.Transform).ToArray();
        scans = _virtualController.Snapshot.ScanNumber;
        StepGantryReviewClock();
        check(_virtualController.Snapshot.ScanNumber == scans
            && axes.Select((axis, index) => axis.Transform == stopped[index]).All(held => held),
            "demo5_review_step_cannot_move_stopped_controller");
        RunActiveController();
        runtime.ExecuteAction("toggle-gantry_home");
        StepGantryReviewClock();
        check(!motion.RunCommand && axes.Select((axis, index) => axis.Transform == stopped[index]).All(held => held),
            "demo5_review_step_respects_actual_ladder_permissive");
        ResetActiveController();
        check(GantryReviewClockHeld && _virtualController.Snapshot.ScanNumber == 0
            && runtime.Points["gantry_home"] is false
            && axes.Select((axis, index) => axis.Transform == home[index]).All(reset => reset),
            "demo5_review_reset_restores_home_and_feedback_while_clock_held");
        ReleaseGantryReviewClock();
        runtime.ExecuteAction("toggle-gantry_home");
        runtime.ExecuteAction("toggle-pallet_position_valid");
        runtime.ExecuteAction("toggle-carton_at_pick");
        RunActiveController();
        _PhysicsProcess(0.02);
        check(!GantryReviewClockHeld && root.ProcessMode == rootMode && runtime.ProcessMode == runtimeMode
            && motion.CanProcess() && _virtualController.Snapshot.ScanNumber == 1,
            "demo5_review_release_restores_native_processing_and_controller_cadence");
        SetGantryReviewClockHeld(true);
        AddMigratedScene("scene-2-conveyor-pusher", _candidateCatalog!, _mainCamera!, false, false);
        check(!GantryReviewClockHeld && root.ProcessMode == rootMode && runtime.ProcessMode == runtimeMode
            && _gantryReviewClockBar?.Visible == false,
            "demo5_review_scene_change_releases_old_clock_and_hides_gantry_controls");
    }
}
