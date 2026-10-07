using System;
using System.Collections.Generic;
using Godot;
using RungProof.Next.App;

namespace RungProof.Next.Scenes;

public partial class SceneSimulationRuntime
{
    private bool HasServiceElevator => Text(_definition,"installation","")=="serviceElevator";
    private EquipmentMotionController? _elevatorCarMotion;
    private Node3D? _elevatorShaft;
    private float _elevatorPosition;

    private void ResetServiceElevator()
    {
        if(!HasServiceElevator) return;
        _elevatorShaft=_sceneRoot.GetNode<Node3D>("liftTable_0");
        _elevatorCarMotion=_elevatorShaft.GetNode<EquipmentMotionController>("ServiceElevatorPosition");
        _elevatorPosition=0;
        ProjectServiceElevator();
    }

    private void AdvanceServiceElevator(double seconds)
    {
        if(!UsesExternalClock) return;
        if(!double.IsFinite(seconds)||seconds<=0) return;
        var up=AsBool(_points.GetValueOrDefault("lift_up_cmd"));
        var down=AsBool(_points.GetValueOrDefault("lift_down_cmd"));
        // Preserve the controller's output image for diagnostics. Conflicting
        // commands or missing manual permissives inhibit modeled displacement.
        var enabled=AsBool(_points.GetValueOrDefault("call_valid"))
            && AsBool(_points.GetValueOrDefault("doors_closed"))
            && AsBool(_points.GetValueOrDefault("landing_clear"));
        if(enabled && up!=down)
            _elevatorPosition=Math.Clamp(_elevatorPosition+(up?1:-1)*(float)(seconds/6),0,1);
        SetPoint("direction_conflict",up&&down);
        ProjectServiceElevator();
        ApplyBindings();
        StateChanged?.Invoke();
    }

    private void ProjectServiceElevator()
    {
        _elevatorCarMotion!.SetPositionNormalized(_elevatorPosition);
        SetPoint("car_position_pct",(double)_elevatorPosition*100);
        SetPoint("at_lower_landing",_elevatorPosition<=.00001f);
        SetPoint("at_upper_landing",_elevatorPosition>=.99999f);
        // Door poses follow the existing manual fixture input, not a separate
        // pretend sensor. Door travel and protective interlocks remain unmodeled.
        var closed=AsBool(_points.GetValueOrDefault("doors_closed"));
        foreach(var part in _elevatorShaft!.GetChildren())
        {
            if(part is not Node3D leaf || !leaf.Name.ToString().StartsWith("ELEVATOR_open_door_leaf_",StringComparison.Ordinal)) continue;
            var side=MathF.Sign(leaf.Position.X);
            leaf.Position=new Vector3(side*(closed?.55f:1.72f),leaf.Position.Y,leaf.Position.Z);
        }
    }
}
