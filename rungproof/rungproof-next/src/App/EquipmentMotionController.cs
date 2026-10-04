using System;
using System.Collections.Generic;
using Godot;

namespace RungProof.Next.App;

/// <summary>
/// Reusable simulator-side motion adapter for catalog assets.  It exposes only
/// symbolic playback state and never owns PLC transport, addresses, or I/O.
/// Run advances the configured motion, Stop freezes it, and Reset restores the
/// authored transform.
/// </summary>
public partial class EquipmentMotionController : Node
{
    public enum MotionKind
    {
        ContinuousRotation,
        OscillatingRotation,
        PositionRotation,
        LinearX,
        LinearY,
        PneumaticPusher,
        FanRotor,
        ScissorLift,
        RollerShutter,
        CartesianGantry,
    }

    [Export] public MotionKind Kind { get; set; }
    [Export] public string TargetPrefix { get; set; } = string.Empty;
    [Export] public bool RunCommand { get; set; }
    [Export(PropertyHint.Range, "0.05,5,0.05,suffix:s")]
    public float TravelTimeSeconds { get; set; } = 1.0f;
    [Export(PropertyHint.Range, "0,3600,10,suffix:rpm")]
    public float SpeedRpm { get; set; } = 90.0f;
    [Export]
    public Vector3 RotationAxis { get; set; } = Vector3.Up;
    [Export(PropertyHint.Range, "-5,5,0.01,suffix:m")]
    public float TravelM { get; set; } = 0.35f;
    [Export(PropertyHint.Range, "-360,360,1,suffix:deg")]
    public float TravelDegrees { get; set; } = 90.0f;
    [Export] public bool PositionInputInverted { get; set; }

    public bool Running => RunCommand;
    public float PositionPercent => _position * 100.0f;

    private readonly List<Node3D> _targets = [];
    private readonly Dictionary<Node3D, Transform3D> _authoredTransforms = [];
    private readonly Dictionary<Node3D, Vector3> _authoredScales = [];
    private Vector3 _fanCenter;
    private float _position;
    private float _angleRadians;

    public override void _Ready()
    {
        BindTargets(GetParent());
        if (Kind == MotionKind.FanRotor)
        {
            var hub = _targets.Find(node => node.Name.ToString().StartsWith("KIN_fan_hub", StringComparison.Ordinal));
            _fanCenter = hub is null ? Vector3.Zero : _authoredTransforms[hub].Origin;
        }
        GD.Print($"Equipment motion controller {Kind} bound {_targets.Count} nodes for '{TargetPrefix}'.");
    }

    public override void _PhysicsProcess(double delta)
    {
        var seconds = (float)delta;
        switch (Kind)
        {
            case MotionKind.ContinuousRotation:
                if (RunCommand)
                {
                    RotateContinuously(seconds);
                }
                break;
            case MotionKind.FanRotor:
                if (RunCommand)
                {
                    _angleRadians += RpmToRadiansPerSecond(SpeedRpm) * seconds;
                    ApplyFanRotation(_angleRadians);
                }
                break;
            case MotionKind.OscillatingRotation:
                if (RunCommand)
                {
                    _angleRadians += seconds * 0.8f;
                    ApplyRotation(MathF.Sin(_angleRadians) * Mathf.DegToRad(TravelDegrees));
                }
                break;
            case MotionKind.CartesianGantry:
                if (RunCommand)
                {
                    // Illustrative command sweep only. No fabricated home or
                    // pick-complete feedback is sent to the controller.
                    _angleRadians = (_angleRadians + seconds * MathF.PI / MathF.Max(TravelTimeSeconds, 0.05f)) % MathF.Tau;
                    _position = (1.0f - MathF.Cos(_angleRadians)) * 0.5f;
                    ApplyGantryPosition();
                }
                break;
            case MotionKind.PositionRotation:
            case MotionKind.LinearX:
            case MotionKind.LinearY:
            case MotionKind.PneumaticPusher:
            case MotionKind.ScissorLift:
            case MotionKind.RollerShutter:
                if (RunCommand)
                {
                    _position = Mathf.MoveToward(_position, 1.0f, seconds / MathF.Max(TravelTimeSeconds, 0.05f));
                    ApplyPosition();
                }
                break;
        }
    }

    public void Run() => RunCommand = true;

    public void Stop() => RunCommand = false;

    public void SetPositionNormalized(float position)
    {
        _position = Mathf.Clamp(PositionInputInverted ? 1.0f - position : position, 0.0f, 1.0f);
        if (Kind is MotionKind.PositionRotation
            or MotionKind.LinearX
            or MotionKind.LinearY
            or MotionKind.PneumaticPusher
            or MotionKind.ScissorLift
            or MotionKind.RollerShutter)
        {
            ApplyPosition();
        }
    }

    public void ResetMotion()
    {
        RunCommand = false;
        _position = 0.0f;
        _angleRadians = 0.0f;
        foreach (var (node, transform) in _authoredTransforms)
        {
            node.Transform = transform;
            node.Scale = _authoredScales[node];
        }
    }

    private void RotateContinuously(float delta)
    {
        var radians = RpmToRadiansPerSecond(SpeedRpm) * delta;
        var axis = RotationAxis.LengthSquared() > 0.0001f
            ? RotationAxis.Normalized()
            : Vector3.Up;
        foreach (var target in _targets)
        {
            target.RotateObjectLocal(axis, radians);
        }
    }

    private void ApplyPosition()
    {
        if (Kind == MotionKind.PositionRotation)
        {
            ApplyRotation(Mathf.DegToRad(TravelDegrees) * _position);
            return;
        }

        if (Kind == MotionKind.ScissorLift)
        {
            ApplyScissorLift();
            return;
        }
        if (Kind == MotionKind.RollerShutter)
        {
            ApplyRollerShutter();
            return;
        }
        if (Kind == MotionKind.PneumaticPusher)
        {
            ApplyPneumaticPusher();
            return;
        }

        var offset = Kind == MotionKind.LinearY
            ? Vector3.Up * (TravelM * _position)
            : Vector3.Right * (TravelM * _position);
        foreach (var target in _targets)
        {
            target.Transform = _authoredTransforms[target].TranslatedLocal(offset);
        }
    }

    private void ApplyGantryPosition()
    {
        // The delivered gantry's three KIN nodes are siblings, rather than a
        // transform hierarchy. Move carriage and Z axis with the X bridge.
        foreach (var target in _targets)
        {
            var name = target.Name.ToString();
            var offset = Vector3.Right * (TravelM * _position);
            if (name.StartsWith("KIN_Y_CARRIAGE", StringComparison.Ordinal)
                || name.StartsWith("KIN_Z_AXIS", StringComparison.Ordinal))
                offset += Vector3.Back * (0.45f * _position);
            if (name.StartsWith("KIN_Z_AXIS", StringComparison.Ordinal))
                // Keep this delivered solid rod inside the carriage housing.
                // It is not a modeled telescoping actuator.
                offset += Vector3.Down * (0.12f * _position);
            var authored = _authoredTransforms[target];
            target.Transform = new Transform3D(authored.Basis, authored.Origin + offset);
        }
    }

    private void ApplyRotation(float radians)
    {
        foreach (var target in _targets)
        {
            var authored = _authoredTransforms[target];
            target.Transform = new Transform3D(
                authored.Basis.Rotated(Vector3.Up, radians),
                authored.Origin
            );
        }
    }

    private void BindTargets(Node root)
    {
        foreach (Node child in root.GetChildren())
        {
            if (child is Node3D node && IsTarget(node.Name.ToString()))
            {
                _targets.Add(node);
                _authoredTransforms[node] = node.Transform;
                _authoredScales[node] = node.Scale;
            }
            BindTargets(child);
        }
    }

    private bool IsTarget(string name)
    {
        if (Kind == MotionKind.CartesianGantry)
            return name.StartsWith("KIN_X_BRIDGE", StringComparison.Ordinal)
                || name.StartsWith("KIN_Y_CARRIAGE", StringComparison.Ordinal)
                || name.StartsWith("KIN_Z_AXIS", StringComparison.Ordinal);
        if (Kind == MotionKind.ScissorLift)
        {
            return name.StartsWith("KIN_platform", StringComparison.Ordinal)
                || name.StartsWith("KIN_scissor_", StringComparison.Ordinal)
                || name.StartsWith("KIN_stage_pivot_", StringComparison.Ordinal)
                || name.StartsWith("KIN_mid_pivot_", StringComparison.Ordinal)
                || name.StartsWith("KIN_lift_rod", StringComparison.Ordinal)
                || name.StartsWith("KIN_lift_bellows_", StringComparison.Ordinal)
                || name.StartsWith("LIFT_top_pivot_", StringComparison.Ordinal)
                || name.StartsWith("LIFT_bottom_pivot_", StringComparison.Ordinal)
                || name.StartsWith("LIFT_upper_track_", StringComparison.Ordinal);
        }
        if (Kind == MotionKind.RollerShutter)
        {
            return name.StartsWith("KIN_slat_", StringComparison.Ordinal)
                || name.StartsWith("KIN_bottom_bar", StringComparison.Ordinal);
        }
        return name.StartsWith(TargetPrefix, StringComparison.Ordinal);
    }

    private void ApplyScissorLift()
    {
        const float armLength = 2.0f;
        const float initialStageHeight = 0.60f;
        var totalRise = TravelM * _position;
        var stageHeight = initialStageHeight + totalRise * 0.5f;
        var initialAngle = MathF.Asin(initialStageHeight / armLength);
        var targetAngle = MathF.Asin(Math.Clamp(stageHeight / armLength, -0.999f, 0.999f));
        var armRotation = targetAngle - initialAngle;
        var targetHalfRun = MathF.Sqrt(MathF.Max(0.0f,
            MathF.Pow(armLength * 0.5f, 2) - MathF.Pow(stageHeight * 0.5f, 2)));
        foreach (var target in _targets)
        {
            var authored = _authoredTransforms[target];
            var name = target.Name.ToString();
            if (name.StartsWith("KIN_platform", StringComparison.Ordinal)
                || name.StartsWith("LIFT_top_pivot_", StringComparison.Ordinal)
                || name.StartsWith("LIFT_upper_track_", StringComparison.Ordinal))
            {
                var origin = authored.Origin + Vector3.Up * totalRise;
                if (name.StartsWith("LIFT_top_pivot_", StringComparison.Ordinal))
                    origin.X = MathF.CopySign(targetHalfRun, authored.Origin.X);
                target.Transform = new Transform3D(authored.Basis, origin);
            }
            else if (name.StartsWith("KIN_scissor_", StringComparison.Ordinal))
            {
                // Blender's positive Y rotation imports as negative Godot Z
                // rotation, so the name suffix and runtime delta have opposite signs.
                var sign = name.EndsWith("_-1", StringComparison.Ordinal) ? 1.0f : -1.0f;
                var stage = name.StartsWith("KIN_scissor_1_", StringComparison.Ordinal) ? 1 : 0;
                var centerRise = totalRise * (stage == 0 ? 0.25f : 0.75f);
                target.Transform = new Transform3D(
                    authored.Basis.Rotated(Vector3.Back, sign * armRotation),
                    authored.Origin + Vector3.Up * centerRise
                );
            }
            else if (name.StartsWith("KIN_stage_pivot_", StringComparison.Ordinal))
            {
                var stage = name.StartsWith("KIN_stage_pivot_1_", StringComparison.Ordinal) ? 1 : 0;
                var centerRise = totalRise * (stage == 0 ? 0.25f : 0.75f);
                target.Transform = new Transform3D(authored.Basis, authored.Origin + Vector3.Up * centerRise);
            }
            else if (name.StartsWith("KIN_mid_pivot_", StringComparison.Ordinal))
            {
                var origin = authored.Origin + Vector3.Up * (totalRise * 0.5f);
                origin.X = MathF.CopySign(targetHalfRun, authored.Origin.X);
                target.Transform = new Transform3D(authored.Basis, origin);
            }
            else if (name.StartsWith("LIFT_bottom_pivot_", StringComparison.Ordinal))
            {
                var origin = authored.Origin;
                origin.X = MathF.CopySign(targetHalfRun, authored.Origin.X);
                target.Transform = new Transform3D(authored.Basis, origin);
            }
            else if (name.StartsWith("KIN_lift_rod", StringComparison.Ordinal))
            {
                target.Transform = authored;
            }
            else if (name.StartsWith("KIN_lift_bellows_", StringComparison.Ordinal))
            {
                // The bellows spans from the fixed base envelope to the
                // travelling platform.  Scale around its centre and move the
                // centre by half the platform travel so both ends stay seated.
                var scale = _authoredScales[target];
                scale.Y *= 1.0f + totalRise / 1.22f;
                target.Transform = new Transform3D(
                    authored.Basis,
                    authored.Origin + Vector3.Up * (totalRise * 0.5f)
                );
                target.Scale = scale;
            }
        }
    }

    private void ApplyRollerShutter()
    {
        var top = float.MinValue;
        foreach (var target in _targets)
        {
            if (target.Name.ToString().StartsWith("KIN_slat_", StringComparison.Ordinal))
            {
                top = MathF.Max(top, _authoredTransforms[target].Origin.Y);
            }
        }
        var stackTop = top + 0.10f;
        foreach (var target in _targets)
        {
            var authored = _authoredTransforms[target];
            var name = target.Name.ToString();
            float targetY;
            if (name.StartsWith("KIN_slat_", StringComparison.Ordinal))
            {
                var suffix = name["KIN_slat_".Length..];
                var index = int.TryParse(suffix, out var parsed) ? parsed : 0;
                targetY = stackTop - index * 0.025f;
            }
            else
            {
                targetY = stackTop - 0.50f;
            }
            var origin = authored.Origin;
            origin.Y = Mathf.Lerp(authored.Origin.Y, targetY, _position);
            target.Transform = new Transform3D(authored.Basis, origin);
        }
    }

    private void ApplyPneumaticPusher()
    {
        var extension = TravelM * _position;
        foreach (var target in _targets)
        {
            var authored = _authoredTransforms[target];
            if (target.Name.ToString().StartsWith("KIN_pusher_rod", StringComparison.Ordinal))
            {
                // The rod remains seated in the front cap while its free end
                // follows the carriage. Scaling and shifting half the added
                // length models extension instead of translating a loose rod.
                // Use the authored parent-space travel axis. TranslatedLocal
                // would apply the rod's own imported basis; this asset's rod
                // basis rotates its local X into vertical Y, which makes the
                // pusher appear to move up/down instead of in/out.
                target.Transform = new Transform3D(
                    authored.Basis,
                    authored.Origin + Vector3.Right * (extension * 0.5f));
                var scale = _authoredScales[target];
                scale.X *= 1.0f + extension / MathF.Max(TravelM, 0.01f);
                target.Scale = scale;
            }
            else
            {
                // Keep the authored basis and move the part in the asset's
                // parent-space longitudinal direction.
                target.Transform = new Transform3D(
                    authored.Basis,
                    authored.Origin + Vector3.Right * extension);
            }
        }
    }

    private void ApplyFanRotation(float radians)
    {
        var rotation = new Basis(Vector3.Back, radians);
        foreach (var target in _targets)
        {
            var authored = _authoredTransforms[target];
            var offset = authored.Origin - _fanCenter;
            target.Transform = new Transform3D(
                rotation * authored.Basis,
                _fanCenter + rotation * offset
            );
        }
    }

    private static float RpmToRadiansPerSecond(float rpm) => rpm * Mathf.Tau / 60.0f;
}
