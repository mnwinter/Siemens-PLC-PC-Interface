using System;
using System.Collections.Generic;
using Godot;

namespace RungProof.Next.App;

/// <summary>
/// Symbolic simulator behavior for a chain-driven pallet roller conveyor.
/// This class owns no PLC transport or physical I/O addressing.
/// </summary>
public partial class RollerConveyorController : Node
{
    [Export] public bool RunCommand { get; set; }
    [Export] public bool EstopOk { get; set; } = true;
    [Export(PropertyHint.Range, "-1,1,0.01,suffix:m/s")]
    public float SpeedSetpointMps { get; set; } = 0.45f;
    [Export(PropertyHint.Range, "0.05,2,0.05,suffix:m/s²")]
    public float AccelerationMps2 { get; set; } = 0.60f;

    public bool Running => MathF.Abs(ActualSpeedMps) > 0.01f;
    public float ActualSpeedMps { get; private set; }

    private readonly List<Node3D> _rollers = [];
    private const float RollerRadiusM = 0.038f;

    public override void _Ready()
    {
        RegisterRollers(GetParent());
        GD.Print($"Roller conveyor controller bound {_rollers.Count} powered rollers.");
    }

    public override void _PhysicsProcess(double delta)
    {
        var target = RunCommand && EstopOk
            ? Math.Clamp(SpeedSetpointMps, -1.0f, 1.0f)
            : 0.0f;
        ActualSpeedMps = Mathf.MoveToward(
            ActualSpeedMps,
            target,
            AccelerationMps2 * (float)delta
        );

        var radians = ActualSpeedMps / RollerRadiusM * (float)delta;
        foreach (var roller in _rollers)
        {
            roller.RotateObjectLocal(Vector3.Up, radians);
        }
    }

    private void RegisterRollers(Node root)
    {
        foreach (Node child in root.GetChildren())
        {
            if (child is Node3D node
                && node.Name.ToString().StartsWith("KIN_roller_", StringComparison.Ordinal))
            {
                _rollers.Add(node);
            }
            RegisterRollers(child);
        }
    }
}
