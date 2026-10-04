using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json;
using Godot;
using RungProof.Next.App;

namespace RungProof.Next.Scenes;

/// <summary>
/// Executes the simulation contract embedded in a migrated scene. This layer
/// intentionally deals only in symbolic point names. PLC transport and address
/// mapping belong in a separate adapter and must never be invented here.
/// </summary>
public partial class SceneSimulationRuntime : Node
{
    private readonly JsonElement _definition;
    private readonly Node3D _sceneRoot;
    private readonly Dictionary<string, object?> _initialPoints = new(StringComparer.Ordinal);
    private readonly Dictionary<string, object?> _points = new(StringComparer.Ordinal);
    private readonly Dictionary<string, object?> _previousPoints = new(StringComparer.Ordinal);
    private readonly HashSet<string> _outputPoints = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _pointOwners = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _pointTypes = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Vector3> _initialEquipmentPositions = new(StringComparer.Ordinal);
    private readonly Dictionary<Node3D, (Vector3 Scale, Vector3 Position, float Height)> _liquidAuthored = [];
    private JsonElement _activeSteps;
    private int _activeStepIndex = -1;
    private double _stepElapsed;
    // Tank scenes are continuous process simulations, not timed sequences. Keep
    // their running state independently so a stopped tank cannot keep changing
    // level merely because a pump command remains authored in the scene.
    private bool _tankSimulationRunning;
    private readonly HashSet<string> _pulsePoints = new(StringComparer.Ordinal);

    public event Action? StateChanged;

    public string RuntimeType => Text(_definition, "type", "none");
    public IReadOnlyDictionary<string, object?> Points => _points;
    public bool IsRunning => _tankSimulationRunning || _activeStepIndex >= 0 || Controllers().Any(IsControllerRunning);
    public bool UsesExternalClock { get; set; }

    public SceneSimulationRuntime(JsonElement definition, Node3D sceneRoot)
    {
        _definition = definition.Clone();
        _sceneRoot = sceneRoot;
        Name = "SceneSimulationRuntime";
        LoadInitialPoints();
        foreach (Node child in sceneRoot.GetChildren())
        {
            if (child is Node3D equipment)
            {
                _initialEquipmentPositions[equipment.Name.ToString()] = equipment.Position;
            }
        }
    }

    public override void _Ready()
    {
        ResetSimulation();
        GD.Print($"SCENE_RUNTIME_READY type={RuntimeType} points={_points.Count} actions={Actions().Length}");
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!UsesExternalClock) AdvanceSimulation(delta);
    }

    public void AdvanceSimulation(double delta)
    {
        if (_pulsePoints.Count > 0)
        {
            foreach (var point in _pulsePoints)
            {
                SetPoint(point, false);
            }
            _pulsePoints.Clear();
            EvaluateRules();
        }

        if (RuntimeType == "tank" && _tankSimulationRunning)
        {
            AdvanceTank(delta);
        }

        if (RuntimeType == "conveyorStop")
        {
            AdvanceConveyorStop(delta);
        }

        if (RuntimeType == "conveyor")
        {
            AdvanceConveyorCell(delta);
        }

        if (_activeStepIndex < 0 || _activeSteps.ValueKind != JsonValueKind.Array)
        {
            return;
        }

        var steps = _activeSteps.EnumerateArray().ToArray();
        if (_activeStepIndex >= steps.Length)
        {
            _activeStepIndex = -1;
            StopControllers();
            StateChanged?.Invoke();
            GD.Print("SCENE_SEQUENCE_COMPLETE");
            return;
        }

        var step = steps[_activeStepIndex];
        var duration = Math.Max(Number(step, "durationS", 0.0), 0.0001);
        _stepElapsed += delta;
        var progress = (float)Math.Clamp(_stepElapsed / duration, 0.0, 1.0);
        ApplyMotions(step, progress);
        if (_stepElapsed + 1e-9 < duration)
        {
            return;
        }

        ApplyMotions(step, 1.0f);
        _activeStepIndex++;
        _stepElapsed = 0.0;
        if (_activeStepIndex < steps.Length)
        {
            EnterStep(steps[_activeStepIndex]);
        }
    }

    public bool VerifyDeclaredCases(JsonElement verification)
    {
        if (verification.ValueKind != JsonValueKind.Object
            || !verification.TryGetProperty("cases", out var cases)
            || cases.ValueKind != JsonValueKind.Array)
        {
            GD.Print("SCENE_CONTRACT_NO_CASES");
            return true;
        }

        var passed = true;
        foreach (var testCase in cases.EnumerateArray())
        {
            ResetSimulation();
            var caseName = Text(testCase, "name", "unnamed");
            if (testCase.TryGetProperty("actions", out var immediateActions)
                && immediateActions.ValueKind == JsonValueKind.Array)
            {
                foreach (var action in immediateActions.EnumerateArray())
                {
                    ExecuteAction(action.GetString() ?? string.Empty);
                    // Give momentary actions one simulator scan so rising-edge
                    // rules execute and the input can return to false.
                    AdvanceSimulation(1.0 / 120.0);
                }
            }
            if (testCase.TryGetProperty("phases", out var phases) && phases.ValueKind == JsonValueKind.Array)
            {
                foreach (var phase in phases.EnumerateArray())
                {
                    var action = Text(phase, "action", string.Empty);
                    if (action.Length > 0) ExecuteAction(action);
                    var remaining = Math.Max(Number(phase, "runForS", 0.0), 0.0);
                    if (remaining <= 1e-9) AdvanceSimulation(1.0 / 120.0);
                    while (remaining > 1e-9)
                    {
                        var step = Math.Min(remaining, 1.0 / 120.0);
                        AdvanceSimulation(step);
                        remaining -= step;
                    }
                }
            }

            var casePassed = true;
            if (testCase.TryGetProperty("expect", out var expected) && expected.ValueKind == JsonValueKind.Object)
            {
                foreach (var expectation in expected.EnumerateObject())
                {
                    if (!_points.TryGetValue(expectation.Name, out var actual)
                        || !Equivalent(actual, Value(expectation.Value)))
                    {
                        casePassed = false;
                        GD.PushError($"SCENE_CONTRACT_MISMATCH case={caseName} point={expectation.Name} expected={Value(expectation.Value)} actual={actual}");
                    }
                }
            }
            passed &= casePassed;
            GD.Print($"SCENE_CONTRACT_CASE {caseName} {(casePassed ? "PASS" : "FAIL")}");
        }
        GD.Print($"SCENE_CONTRACT_RESULT {(passed ? "PASS" : "FAIL")}");
        return passed;
    }

    public bool RunDefault()
    {
        if (_definition.ValueKind == JsonValueKind.Object
            && _definition.TryGetProperty("defaultSequence", out var sequence)
            && sequence.ValueKind == JsonValueKind.String)
        {
            return StartSequence(sequence.GetString() ?? string.Empty);
        }

        if (RuntimeType == "booleanPanel")
        {
            EvaluateRules();
            GD.Print("SCENE_RUNTIME_BOOLEAN_SCAN");
            return true;
        }

        foreach (var controller in Controllers())
        {
            SetControllerRunning(controller, true);
        }
        if (RuntimeType == "conveyor")
        {
            SetPoint("conveyor_run", true);
            ApplyBindings();
        }
        if (RuntimeType == "tank")
        {
            _tankSimulationRunning = true;
            ProjectTankState();
        }
        StateChanged?.Invoke();
        GD.Print("SCENE_RUNTIME_RUN_DEFAULT");
        return true;
    }

    public void StopSimulation()
    {
        _activeStepIndex = -1;
        _tankSimulationRunning = false;
        if (RuntimeType == "tank")
        {
            // These are symbolic simulator points only. Clearing them here does
            // not write a PLC and mirrors the source simulator's safe stop.
            SetPoint("inlet_pump_run", false);
            SetPoint("drain_valve_open", false);
            ProjectTankState();
        }
        StopControllers();
        if (_definition.ValueKind == JsonValueKind.Object
            && _definition.TryGetProperty("safeState", out var safeState)
            && safeState.ValueKind == JsonValueKind.Object)
        {
            ApplySet(safeState);
        }
        EvaluateRules();
        StateChanged?.Invoke();
        GD.Print("SCENE_RUNTIME_STOP");
    }

    public void ResetSimulation()
    {
        _activeStepIndex = -1;
        _stepElapsed = 0.0;
        _tankSimulationRunning = false;
        _pulsePoints.Clear();
        _points.Clear();
        foreach (var (name, value) in _initialPoints)
        {
            _points[name] = value;
            _previousPoints[name] = value;
        }
        foreach (var (name, position) in _initialEquipmentPositions)
        {
            if (_sceneRoot.GetNodeOrNull<Node3D>(name) is { } equipment)
            {
                equipment.Position = position;
            }
        }
        foreach (var (liquid, authored) in _liquidAuthored)
        {
            liquid.Scale = authored.Scale;
            liquid.Position = authored.Position;
        }
        foreach (var controller in Controllers())
        {
            switch (controller)
            {
                case EquipmentMotionController motion:
                    motion.ResetMotion();
                    break;
                case ConveyorController conveyor:
                    conveyor.RunCommand = false;
                    break;
                case RollerConveyorController rollers:
                    rollers.RunCommand = false;
                    break;
            }
        }
        ApplyInitialTankLevels();
        EvaluateRules();
        ApplyBindings();
        StateChanged?.Invoke();
        GD.Print("SCENE_RUNTIME_RESET");
    }

    public bool ExecuteAction(string actionId)
    {
        var action = Actions().FirstOrDefault(item => Text(item, "id", string.Empty) == actionId);
        if (action.ValueKind != JsonValueKind.Object)
        {
            GD.PushWarning($"Unknown scene action '{actionId}'.");
            return false;
        }
        if (!RequirementsSatisfied(action))
        {
            GD.Print($"SCENE_ACTION_BLOCKED {actionId} {Text(action, "blockedMessage", "requirements not met")}");
            return false;
        }

        var type = Text(action, "type", string.Empty);
        var point = Text(action, "point", string.Empty);
        var result = type switch
        {
            "start" => StartSequence(Text(action, "sequence", string.Empty)),
            "run" => RunDefault(),
            "stop" => StopAction(),
            "emergencyStop" => EmergencyStopAction(action),
            "reset" => ResetAction(),
            "toggle" or "togglePoint" => TogglePoint(point),
            "cycle" => CyclePoint(point, action),
            "pulse" => PulsePoint(point),
            _ => false,
        };
        if (result)
        {
            if (RuntimeType == "tank")
            {
                ProjectTankState();
            }
            GD.Print($"SCENE_ACTION_EXECUTED {actionId}");
        }
        return result;
    }

    public IReadOnlyList<(string Id, string Label)> GetActions() => Actions()
        .Select(action => (Text(action, "id", string.Empty), Text(action, "label", Text(action, "id", "Action"))))
        .Where(action => action.Item1.Length > 0)
        .ToArray();

    /// <summary>
    /// Samples declared simulator-owned BOOL points for a virtual controller.
    /// This is symbolic data only and has no PLC endpoint or address path.
    /// </summary>
    public IReadOnlyDictionary<string, bool> SampleVirtualControllerInputs()
    {
        var result = new Dictionary<string, bool>(StringComparer.Ordinal);
        foreach (var (name, owner) in _pointOwners)
        {
            if (!owner.Equals("PC", StringComparison.OrdinalIgnoreCase)
                || !string.Equals(_pointTypes.GetValueOrDefault(name), "BOOL", StringComparison.OrdinalIgnoreCase))
                continue;
            result[name] = AsBool(_points.GetValueOrDefault(name));
        }
        return result;
    }

    /// <summary>
    /// Samples declared simulator-owned INT, DINT, and REAL points. Values are
    /// returned by symbolic name only; there is no physical PLC address path.
    /// </summary>
    public IReadOnlyDictionary<string, double> SampleVirtualControllerNumericInputs()
    {
        var result = new Dictionary<string, double>(StringComparer.Ordinal);
        foreach (var (name, owner) in _pointOwners)
        {
            var type = _pointTypes.GetValueOrDefault(name);
            if (!owner.Equals("PC", StringComparison.OrdinalIgnoreCase)
                || type is null
                || !IsNumericPointType(type)
                || !TryAsDouble(_points.GetValueOrDefault(name), out var value))
                continue;
            result[name] = value;
        }
        return result;
    }

    /// <summary>
    /// Commits a virtual scan's BOOL outputs only to declared PLC-owned scene
    /// points. Unknown, non-BOOL, or simulator-owned targets fail closed.
    /// </summary>
    public void CommitVirtualControllerOutputs(IReadOnlyDictionary<string, bool> outputs)
    {
        foreach (var (name, value) in outputs)
        {
            if (!_pointOwners.TryGetValue(name, out var owner)
                || !owner.Equals("PLC", StringComparison.OrdinalIgnoreCase)
                || !string.Equals(_pointTypes.GetValueOrDefault(name), "BOOL", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"Virtual controller output '{name}' is not a declared PLC-owned BOOL scene point.");
            }
            _points[name] = value;
        }
        ApplyBindings();
        StateChanged?.Invoke();
    }

    /// <summary>
    /// Commits a virtual scan's finite numeric outputs only to declared
    /// PLC-owned INT, DINT, or REAL scene points. Integer points are truncated
    /// and range-clamped according to their declared scene type.
    /// </summary>
    public void CommitVirtualControllerNumericOutputs(IReadOnlyDictionary<string, double> outputs)
    {
        foreach (var (name, value) in outputs)
        {
            var type = _pointTypes.GetValueOrDefault(name);
            if (!_pointOwners.TryGetValue(name, out var owner)
                || !owner.Equals("PLC", StringComparison.OrdinalIgnoreCase)
                || type is null
                || !IsNumericPointType(type)
                || !double.IsFinite(value))
            {
                throw new InvalidOperationException(
                    $"Virtual controller output '{name}' is not a declared PLC-owned finite numeric scene point.");
            }
            _points[name] = type.ToUpperInvariant() switch
            {
                "INT" => (long)Math.Clamp(Math.Truncate(value), short.MinValue, short.MaxValue),
                "DINT" => (long)Math.Clamp(Math.Truncate(value), int.MinValue, int.MaxValue),
                _ => value,
            };
        }
        ApplyBindings();
        StateChanged?.Invoke();
    }

    private bool StartSequence(string name)
    {
        if (name.Length == 0
            || !_definition.TryGetProperty("sequences", out var sequences)
            || sequences.ValueKind != JsonValueKind.Object
            || !sequences.TryGetProperty(name, out var steps)
            || steps.ValueKind != JsonValueKind.Array
            || steps.GetArrayLength() == 0)
        {
            return false;
        }
        _activeSteps = steps.Clone();
        _activeStepIndex = 0;
        _stepElapsed = 0.0;
        EnterStep(_activeSteps[0]);
        StateChanged?.Invoke();
        GD.Print($"SCENE_SEQUENCE_STARTED {name}");
        return true;
    }

    private void EnterStep(JsonElement step)
    {
        if (step.TryGetProperty("set", out var values) && values.ValueKind == JsonValueKind.Object)
        {
            ApplySet(values);
        }
        EvaluateRules();
        ApplyBindings();
        GD.Print($"SCENE_SEQUENCE_STEP {Text(step, "name", _activeStepIndex.ToString(CultureInfo.InvariantCulture))}");
    }

    private void ApplyMotions(JsonElement step, float progress)
    {
        if (!step.TryGetProperty("motions", out var motions) || motions.ValueKind != JsonValueKind.Array)
        {
            return;
        }
        foreach (var motion in motions.EnumerateArray())
        {
            var equipmentId = SafeNodeName(Text(motion, "equipmentId", string.Empty));
            if (_sceneRoot.GetNodeOrNull<Node3D>(equipmentId) is not { } equipment)
            {
                continue;
            }
            var from = (float)Number(motion, "from", 0.0);
            var to = (float)Number(motion, "to", 0.0);
            var value = Mathf.Lerp(from, to, progress);
            switch (Text(motion, "type", string.Empty))
            {
                case "translate":
                    var position = equipment.Position;
                    position[AxisIndex(Text(motion, "axis", "x"))] = value;
                    equipment.Position = position;
                    break;
                case "position":
                    foreach (var controller in equipment.FindChildren("*", string.Empty, true, false).OfType<EquipmentMotionController>())
                    {
                        controller.SetPositionNormalized(value);
                    }
                    break;
                case "tankLevel":
                    ApplyTankLevel(equipment, value);
                    break;
            }
        }
    }

    private void ApplyTankLevel(Node3D equipment, float normalized)
    {
        if (equipment.FindChild("KIN_liquid", true, false) is not Node3D liquid)
        {
            return;
        }
        if (!_liquidAuthored.TryGetValue(liquid, out var authored))
        {
            var height = liquid is MeshInstance3D mesh ? mesh.GetAabb().Size.Y * liquid.Scale.Y : 1.0f;
            authored = (liquid.Scale, liquid.Position, height);
            _liquidAuthored[liquid] = authored;
        }
        normalized = Mathf.Clamp(normalized, 0.001f, 1.0f);
        var scale = authored.Scale;
        scale.Y = authored.Scale.Y * normalized;
        liquid.Scale = scale;
        var position = authored.Position;
        var bottom = authored.Position.Y - authored.Height * 0.5f;
        position.Y = bottom + authored.Height * normalized * 0.5f;
        liquid.Position = position;
    }

    /// <summary>
    /// Mirrors the source tank simulation using only scene-owned symbolic
    /// points. PLC transport remains outside this class and no address is
    /// accepted or emitted here.
    /// </summary>
    private void AdvanceTank(double delta)
    {
        var level = TankLevelFraction();
        var inletRate = Number(_definition, "inletRatePerSecond", 0.055);
        var outletRate = Number(_definition, "outletRatePerSecond", 0.035);
        var change = (AsBool(_points.GetValueOrDefault("inlet_pump_run")) ? inletRate : 0.0)
            - (AsBool(_points.GetValueOrDefault("drain_valve_open")) ? outletRate : 0.0);
        level = Math.Clamp(level + change * delta, 0.0, 1.0);
        SetPoint("tank_level", level * 100.0);
        ProjectTankState();
    }

    private void AdvanceConveyorStop(double delta)
    {
        var conveyorRunning = AsBool(_points.GetValueOrDefault("conveyor_running"));
        var position = Convert.ToDouble(_points.GetValueOrDefault("object_position") ?? 0.0, CultureInfo.InvariantCulture);
        var speed = Number(_definition, "speedMps", 0.5);
        var sensorPosition = Number(_definition, "photoeyePositionM", 0.5);
        var objectLength = Number(_definition, "objectLengthM", 0.2);
        if (conveyorRunning) position += Math.Max(0.0, speed) * Math.Max(0.0, delta);
        var blocked = position + 1e-9 >= sensorPosition && position <= sensorPosition + objectLength;
        SetExistingPoint("object_position", position);
        SetExistingPoint("simulated_photoeye", blocked);
        SetExistingPoint("component_state", blocked
            ? (conveyorRunning ? "sensor_blocked_running" : "stopped_loaded")
            : conveyorRunning ? "running" : "stopped");

        var productId = SafeNodeName(Text(_definition, "productId", string.Empty));
        var photoeyeId = SafeNodeName(Text(_definition, "photoeyeId", string.Empty));
        if (_sceneRoot.GetNodeOrNull<Node3D>(productId) is { } product
            && _sceneRoot.GetNodeOrNull<Node3D>(photoeyeId) is { } photoeye
            && _initialEquipmentPositions.TryGetValue(productId, out var initial))
        {
            var ratio = sensorPosition <= 1e-9 ? 1.0 : Math.Clamp(position / sensorPosition, 0.0, 1.0);
            var target = initial;
            target.X = Mathf.Lerp(initial.X, photoeye.Position.X, (float)ratio);
            product.Position = target;
        }
        ApplyBindings();
        StateChanged?.Invoke();
    }

    /// <summary>
    /// Applies typed PLC-owned outputs returned by the existing guarded
    /// external PLC session. Physical addresses remain outside the scene
    /// runtime; this method only accepts the declared symbolic scene contract.
    /// </summary>
    public void CommitExternalPlcOutputs(IReadOnlyDictionary<string, object?> outputs)
    {
        foreach (var (name, value) in outputs)
        {
            if (!_pointOwners.TryGetValue(name, out var owner)
                || !owner.Equals("PLC", StringComparison.OrdinalIgnoreCase)
                || value is null)
            {
                throw new InvalidOperationException(
                    $"External PLC output '{name}' is not a declared non-null PLC-owned scene point.");
            }
            _points[name] = value;
        }
        ApplyBindings();
        StateChanged?.Invoke();
    }

    private void AdvanceConveyorCell(double delta)
    {
        var conveyorRunning = AsBool(_points.GetValueOrDefault("conveyor_run"))
            && AsBool(_points.GetValueOrDefault("estop_ok"));
        var speed = Math.Max(0.0, Number(_definition, "speedMps", 0.5));
        var conveyorId = SafeNodeName(Text(_definition, "conveyorId", string.Empty));
        var conveyor = _sceneRoot.GetNodeOrNull<Node3D>(conveyorId);
        var length = Number(_definition, "lengthM", 8.0);
        var startX = (conveyor?.Position.X ?? 0.0f) - (float)length * 0.5f + 0.45f;
        var endX = (conveyor?.Position.X ?? 0.0f) + (float)length * 0.5f - 0.45f;
        var sensorId = SafeNodeName(Text(_definition, "photoeyeId", string.Empty));
        var sensor = _sceneRoot.GetNodeOrNull<Node3D>(sensorId);
        var sensorX = sensor?.Position.X ?? 1.25f;
        var blocked = false;
        var completed = Convert.ToInt32(_points.GetValueOrDefault("parts_completed") ?? 0, CultureInfo.InvariantCulture);

        if (_definition.TryGetProperty("productIds", out var productIds)
            && productIds.ValueKind == JsonValueKind.Array)
        {
            foreach (var productElement in productIds.EnumerateArray())
            {
                var productId = SafeNodeName(productElement.GetString() ?? string.Empty);
                if (_sceneRoot.GetNodeOrNull<Node3D>(productId) is not { } product)
                    continue;

                var position = product.Position;
                if (conveyorRunning)
                {
                    position.X += (float)(speed * Math.Max(0.0, delta));
                    if (position.X > endX)
                    {
                        position.X = startX;
                        completed++;
                    }
                    product.Position = position;
                }

                if (Math.Abs(position.X - sensorX) <= 0.48f)
                    blocked = true;
            }
        }

        SetExistingPoint("conveyor_speed", conveyorRunning ? speed : 0.0);
        SetExistingPoint("photoeye_blocked", blocked);
        SetExistingPoint("parts_completed", completed);
        ApplyBindings();
        StateChanged?.Invoke();
    }

    private double TankLevelFraction()
    {
        if (!_points.TryGetValue("tank_level", out var value))
        {
            return Number(_definition, "initialLevel", 0.0);
        }
        try
        {
            return Math.Clamp(Convert.ToDouble(value, CultureInfo.InvariantCulture) / 100.0, 0.0, 1.0);
        }
        catch (FormatException)
        {
            return Number(_definition, "initialLevel", 0.0);
        }
    }

    private void ProjectTankState()
    {
        var level = TankLevelFraction();
        var lowActive = level <= Number(_definition, "lowThreshold", 0.2);
        var highActive = level >= Number(_definition, "highThreshold", 0.8);
        var pumpRunning = _tankSimulationRunning && AsBool(_points.GetValueOrDefault("inlet_pump_run"));

        var tankId = SafeNodeName(Text(_definition, "tankId", string.Empty));
        var tank = _sceneRoot.GetNodeOrNull<Node3D>(tankId);
        if (tank is not null) ApplyTankLevel(tank, (float)level);

        var pumpId = SafeNodeName(Text(_definition, "pumpId", string.Empty));
        if (_sceneRoot.GetNodeOrNull<Node3D>(pumpId) is { } pump)
        {
            foreach (var controller in Controllers(pump)) SetControllerRunning(controller, pumpRunning);
        }

        SetExistingPoint("low_level_switch", lowActive);
        SetExistingPoint("high_level_switch", highActive);
        SetExistingPoint("level_transmitter", 4.0 + 16.0 * level);
        SetExistingPoint("radar_level", level * 100.0);
        SetExistingPoint("radar_signal", 4.0 + 16.0 * level);
        SetExistingPoint("radar_echo_ok", true);
        SetExistingPoint("radar_distance", RadarDistance(tank));

        var lowId = SafeNodeName(Text(_definition, "lowSensorId", string.Empty));
        if (_sceneRoot.GetNodeOrNull<Node3D>(lowId) is { } lowSensor) SetLevelSensor(lowSensor, lowActive);
        var highId = SafeNodeName(Text(_definition, "highSensorId", string.Empty));
        if (_sceneRoot.GetNodeOrNull<Node3D>(highId) is { } highSensor) SetLevelSensor(highSensor, highActive);

        var indicatorId = SafeNodeName(Text(_definition, "indicatorId", string.Empty));
        if (_sceneRoot.GetNodeOrNull<Node3D>(indicatorId) is { } indicator)
        {
            SetIndicator(indicator, _tankSimulationRunning, !_tankSimulationRunning ? "amber" : (lowActive || highActive ? "red" : "green"));
        }
    }

    private double RadarDistance(Node3D? tank)
    {
        var transmitterId = SafeNodeName(Text(_definition, "transmitterId", string.Empty));
        if (tank?.FindChild("KIN_liquid", true, false) is not Node3D liquid
            || _sceneRoot.GetNodeOrNull<Node3D>(transmitterId) is not Node3D transmitter)
        {
            return _points.TryGetValue("radar_distance", out var existing)
                ? Convert.ToDouble(existing, CultureInfo.InvariantCulture)
                : 0.08;
        }
        var liquidHeight = liquid is MeshInstance3D mesh ? mesh.GetAabb().Size.Y * liquid.Scale.Y : 0.0f;
        var liquidSurfaceY = liquid.GlobalPosition.Y + liquidHeight * 0.5f;
        return Math.Max(0.08, transmitter.GlobalPosition.Y - liquidSurfaceY);
    }

    private void EvaluateRules()
    {
        if (RuntimeType == "booleanPanel")
        {
            // Match the original fake-PLC scan: combinational outputs return
            // to their declared initial state before matching rules execute.
            foreach (var point in _outputPoints) _points[point] = _initialPoints[point];
        }
        if (_definition.TryGetProperty("edgeRules", out var edgeRules) && edgeRules.ValueKind == JsonValueKind.Array)
        {
            foreach (var rule in edgeRules.EnumerateArray())
            {
                var point = Text(rule, "rising", string.Empty);
                if (point.Length > 0 && !AsBool(_previousPoints.GetValueOrDefault(point)) && AsBool(_points.GetValueOrDefault(point)))
                {
                    if (rule.TryGetProperty("set", out var values)) ApplySet(values);
                    if (rule.TryGetProperty("toggle", out var toggles) && toggles.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var toggle in toggles.EnumerateArray()) TogglePoint(toggle.GetString() ?? string.Empty, evaluate: false);
                    }
                }
            }
        }
        if (_definition.TryGetProperty("rules", out var rules) && rules.ValueKind == JsonValueKind.Array)
        {
            foreach (var rule in rules.EnumerateArray())
            {
                if (rule.TryGetProperty("when", out var when) && ConditionsMatch(when)
                    && rule.TryGetProperty("set", out var values))
                {
                    ApplySet(values);
                }
            }
        }
        foreach (var (name, value) in _points) _previousPoints[name] = value;
        ApplyBindings();
        StateChanged?.Invoke();
    }

    private void ApplyBindings()
    {
        if (!_definition.TryGetProperty("pointBindings", out var bindings) || bindings.ValueKind != JsonValueKind.Array)
        {
            return;
        }
        var indicatorStates = new Dictionary<Node3D, (bool Active, string Color)>();
        foreach (var binding in bindings.EnumerateArray())
        {
            var point = Text(binding, "point", string.Empty);
            var equipmentId = SafeNodeName(Text(binding, "equipmentId", string.Empty));
            if (!_points.TryGetValue(point, out var value) || _sceneRoot.GetNodeOrNull<Node3D>(equipmentId) is not { } equipment)
            {
                continue;
            }
            switch (Text(binding, "mode", string.Empty))
            {
                case "running":
                    foreach (var controller in Controllers(equipment)) SetControllerRunning(controller, AsBool(value));
                    break;
                case "estopPermissive":
                    foreach (var controller in Controllers(equipment).OfType<ConveyorController>())
                        controller.EstopOk = AsBool(value);
                    foreach (var controller in Controllers(equipment).OfType<RollerConveyorController>())
                        controller.EstopOk = AsBool(value);
                    break;
                case "switch":
                    foreach (var controller in equipment.FindChildren("*", string.Empty, true, false).OfType<EquipmentMotionController>())
                        controller.SetPositionNormalized(AsBool(value) ? 1.0f : 0.0f);
                    break;
                case "selector":
                    if (equipment.FindChild("KIN_selector_handle", true, false) is Node3D selector)
                        // The four-position selector is drawn on the front (X/Z)
                        // plane.  Its physical axis is vertical in Godot's Y-up
                        // coordinates, so turning Z would swing the handle out of
                        // the dial instead of between its detented positions.
                        selector.RotationDegrees = new Vector3(selector.RotationDegrees.X, -55.0f + Convert.ToSingle(value, CultureInfo.InvariantCulture) * 36.7f, selector.RotationDegrees.Z);
                    break;
                case "indicator":
                    var color = value is string text ? text : Text(binding, "activeColor", "green");
                    var active = value is string || AsBool(value);
                    if (!indicatorStates.ContainsKey(equipment)) indicatorStates[equipment] = (false, color);
                    if (active) indicatorStates[equipment] = (true, color);
                    break;
                case "photoeye":
                    foreach (var beam in equipment.FindChildren("KIN_beam*", string.Empty, true, false).OfType<Node3D>())
                        beam.Visible = !AsBool(value);
                    break;
                case "levelSensor":
                    SetLevelSensor(equipment, AsBool(value));
                    break;
                case "position":
                    var position = value is bool boolean ? (boolean ? 1.0f : 0.0f) : Convert.ToSingle(value, CultureInfo.InvariantCulture);
                    if (position > 1.0f) position /= 100.0f;
                    foreach (var controller in equipment.FindChildren("*", string.Empty, true, false).OfType<EquipmentMotionController>())
                        controller.SetPositionNormalized(position);
                    break;
            }
        }
        foreach (var (equipment, state) in indicatorStates) SetIndicator(equipment, state.Active, state.Color);
    }

    private void ApplyInitialTankLevels()
    {
        var applied = new HashSet<string>(StringComparer.Ordinal);
        if (_definition.ValueKind == JsonValueKind.Object
            && _definition.TryGetProperty("initialLevel", out var initialLevel)
            && initialLevel.TryGetSingle(out var level)
            && _definition.TryGetProperty("tankId", out var tankId)
            && tankId.ValueKind == JsonValueKind.String)
        {
            var id = SafeNodeName(tankId.GetString() ?? string.Empty);
            if (_sceneRoot.GetNodeOrNull<Node3D>(id) is { } tank)
            {
                ApplyTankLevel(tank, level);
                applied.Add(id);
            }
        }
        if (!_definition.TryGetProperty("sequences", out var sequences) || sequences.ValueKind != JsonValueKind.Object) return;
        foreach (var sequence in sequences.EnumerateObject())
        foreach (var step in sequence.Value.EnumerateArray())
        {
            if (!step.TryGetProperty("motions", out var motions) || motions.ValueKind != JsonValueKind.Array) continue;
            foreach (var motion in motions.EnumerateArray())
            {
                if (Text(motion, "type", string.Empty) != "tankLevel") continue;
                var id = SafeNodeName(Text(motion, "equipmentId", string.Empty));
                if (applied.Add(id) && _sceneRoot.GetNodeOrNull<Node3D>(id) is { } tank)
                    ApplyTankLevel(tank, (float)Number(motion, "from", 0.0));
            }
        }
    }

    private static void SetIndicator(Node3D equipment, bool active, string colorName)
    {
        static Color SignalColor(string name) => name.ToLowerInvariant() switch
        {
            "red" => new Color("e03c31"), "amber" => new Color("f2a900"),
            "blue" => new Color("2e8bd1"), "white" => new Color("e9f2f5"),
            _ => new Color("21a366"),
        };
        var lenses = equipment.FindChildren("*", string.Empty, true, false).OfType<MeshInstance3D>()
            .Where(item => item.Name.ToString().Contains("LENS", StringComparison.OrdinalIgnoreCase)).ToArray();
        foreach (var mesh in lenses)
        {
            var name = mesh.Name.ToString().ToLowerInvariant();
            var nativeColor = new[] { "red", "amber", "green", "blue", "white" }
                .FirstOrDefault(name.Contains) ?? colorName;
            var color = SignalColor(nativeColor);
            var lensActive = active && (lenses.Length == 1 || nativeColor.Equals(colorName, StringComparison.OrdinalIgnoreCase));
            mesh.MaterialOverride = new StandardMaterial3D
            {
                AlbedoColor = lensActive ? color : color.Darkened(0.72f),
                Roughness = 0.18f,
                EmissionEnabled = lensActive,
                Emission = color,
                EmissionEnergyMultiplier = lensActive ? 4.0f : 0.0f,
            };
        }
    }

    private static void SetLevelSensor(Node3D equipment, bool active)
    {
        var activeColor = new Color("f2a900");
        foreach (var mesh in equipment.FindChildren("*", string.Empty, true, false).OfType<MeshInstance3D>()
                     .Where(item => item.Name.ToString().Contains("head", StringComparison.OrdinalIgnoreCase)
                         || item.Name.ToString().Contains("tine", StringComparison.OrdinalIgnoreCase)))
        {
            mesh.MaterialOverride = new StandardMaterial3D
            {
                AlbedoColor = active ? activeColor : new Color("536772"),
                Metallic = 0.12f,
                Roughness = 0.42f,
                EmissionEnabled = active,
                Emission = activeColor,
                EmissionEnergyMultiplier = active ? 2.2f : 0.0f,
            };
        }
    }

    private bool RequirementsSatisfied(JsonElement action) =>
        !action.TryGetProperty("requires", out var requires) || ConditionsMatch(requires);

    private bool ConditionsMatch(JsonElement conditions)
    {
        if (conditions.ValueKind != JsonValueKind.Object) return true;
        foreach (var condition in conditions.EnumerateObject())
        {
            if (!_points.TryGetValue(condition.Name, out var current) || !Equivalent(current, Value(condition.Value)))
                return false;
        }
        return true;
    }

    private void ApplySet(JsonElement values)
    {
        if (values.ValueKind != JsonValueKind.Object) return;
        foreach (var property in values.EnumerateObject()) SetPoint(property.Name, Value(property.Value));
    }

    private void SetPoint(string name, object? value)
    {
        if (name.Length > 0) _points[name] = value;
    }

    private void SetExistingPoint(string name, object? value)
    {
        if (_points.ContainsKey(name)) _points[name] = value;
    }

    private bool TogglePoint(string point, bool evaluate = true)
    {
        if (point.Length == 0) return false;
        SetPoint(point, !AsBool(_points.GetValueOrDefault(point)));
        if (evaluate) EvaluateRules();
        return true;
    }

    private bool CyclePoint(string point, JsonElement action)
    {
        if (point.Length == 0 || !action.TryGetProperty("values", out var values) || values.ValueKind != JsonValueKind.Array) return false;
        var available = values.EnumerateArray().Select(Value).ToArray();
        if (available.Length == 0) return false;
        var current = _points.GetValueOrDefault(point);
        var index = Array.FindIndex(available, item => Equivalent(item, current));
        SetPoint(point, available[(index + 1) % available.Length]);
        EvaluateRules();
        return true;
    }

    private bool PulsePoint(string point)
    {
        if (point.Length == 0) return false;
        SetPoint(point, true);
        EvaluateRules();
        _pulsePoints.Add(point);
        return true;
    }

    private bool StopAction() { StopSimulation(); return true; }
    private bool EmergencyStopAction(JsonElement action)
    {
        // This is a scene-local symbolic E-stop model, not safety-rated logic
        // and never a physical I/O command. The action latches its declared
        // permissive false, applies the scene safe state, and requires the
        // normal simulator Reset path before a Start action can run again.
        StopSimulation();
        var point = Text(action, "point", "estop_ok");
        SetExistingPoint(point, false);
        EvaluateRules();
        return true;
    }
    private bool ResetAction() { ResetSimulation(); return true; }

    private void LoadInitialPoints()
    {
        if (_definition.ValueKind != JsonValueKind.Object
            || !_definition.TryGetProperty("points", out var points)
            || points.ValueKind != JsonValueKind.Array) return;
        foreach (var point in points.EnumerateArray())
        {
            var name = Text(point, "name", string.Empty);
            if (name.Length > 0 && point.TryGetProperty("initial", out var initial))
            {
                _initialPoints[name] = Value(initial);
                _pointOwners[name] = Text(point, "owner", string.Empty);
                _pointTypes[name] = Text(point, "type", string.Empty);
                if (Text(point, "role", string.Empty) == "output") _outputPoints.Add(name);
            }
        }
    }

    private JsonElement[] Actions() => _definition.ValueKind == JsonValueKind.Object
        && _definition.TryGetProperty("actions", out var actions) && actions.ValueKind == JsonValueKind.Array
            ? actions.EnumerateArray().Select(item => item.Clone()).ToArray() : [];

    private IEnumerable<Node> Controllers(Node? root = null)
    {
        root ??= _sceneRoot;
        return root.FindChildren("*", string.Empty, true, false).Where(node =>
            node is EquipmentMotionController or ConveyorController or RollerConveyorController);
    }

    private static bool IsControllerRunning(Node controller) => controller switch
    {
        EquipmentMotionController motion => motion.Running,
        ConveyorController conveyor => conveyor.RunCommand,
        RollerConveyorController rollers => rollers.RunCommand,
        _ => false,
    };

    private static void SetControllerRunning(Node controller, bool running)
    {
        switch (controller)
        {
            case EquipmentMotionController motion: if (running) motion.Run(); else motion.Stop(); break;
            case ConveyorController conveyor: conveyor.RunCommand = running; break;
            case RollerConveyorController rollers: rollers.RunCommand = running; break;
        }
    }

    private void StopControllers() { foreach (var controller in Controllers()) SetControllerRunning(controller, false); }
    private static int AxisIndex(string axis) => axis.ToLowerInvariant() switch { "y" => 1, "z" => 2, _ => 0 };
    private static string SafeNodeName(string value) => value.Replace("-", "_", StringComparison.Ordinal);
    private static string Text(JsonElement element, string name, string fallback) => element.ValueKind == JsonValueKind.Object
        && element.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String ? value.GetString() ?? fallback : fallback;
    private static double Number(JsonElement element, string name, double fallback) => element.ValueKind == JsonValueKind.Object
        && element.TryGetProperty(name, out var value) && value.TryGetDouble(out var number) ? number : fallback;
    private static object? Value(JsonElement value) => value.ValueKind switch
    {
        JsonValueKind.True => true, JsonValueKind.False => false,
        JsonValueKind.Number when value.TryGetInt64(out var integer) => integer,
        JsonValueKind.Number => value.GetDouble(), JsonValueKind.String => value.GetString(),
        JsonValueKind.Null => null, _ => value.GetRawText(),
    };
    private static bool AsBool(object? value) => value switch
    {
        bool boolean => boolean, long integer => integer != 0, double number => Math.Abs(number) > 1e-9,
        string text when bool.TryParse(text, out var boolean) => boolean, _ => false,
    };
    private static bool IsNumericPointType(string type) =>
        type.Equals("INT", StringComparison.OrdinalIgnoreCase)
        || type.Equals("DINT", StringComparison.OrdinalIgnoreCase)
        || type.Equals("REAL", StringComparison.OrdinalIgnoreCase);
    private static bool TryAsDouble(object? value, out double result)
    {
        if (value is not (sbyte or byte or short or ushort or int or uint or long or ulong or float or double or decimal))
        {
            result = 0.0;
            return false;
        }
        try
        {
            result = Convert.ToDouble(value, CultureInfo.InvariantCulture);
            return double.IsFinite(result);
        }
        catch (Exception exception) when (exception is FormatException or InvalidCastException or OverflowException)
        {
            result = 0.0;
            return false;
        }
    }
    private static bool Equivalent(object? left, object? right)
    {
        if (left is null || right is null) return left is null && right is null;
        if (left is IConvertible && right is IConvertible && left is not string && right is not string)
        {
            try { return Math.Abs(Convert.ToDouble(left, CultureInfo.InvariantCulture) - Convert.ToDouble(right, CultureInfo.InvariantCulture)) < 1e-9; }
            catch (FormatException) { }
        }
        return Equals(left, right);
    }
}
