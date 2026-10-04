using System;
using System.Collections.Generic;
using System.Linq;

namespace RungProof.Next.VirtualController;

public sealed record SceneIoPoint(
    string Name,
    string Type,
    string Owner,
    string Role,
    string Purpose);

/// <summary>
/// Validates the symbolic seam between an offline Ladder program and the
/// currently loaded simulator scene. It has no PLC transport or address model.
/// </summary>
public static class SceneIoBindingValidator
{
    private static readonly HashSet<string> OperatorPulseBindings = new(StringComparer.Ordinal)
    {
        "operator.start",
        "operator.stop",
    };

    public static IReadOnlyList<LadderValidationIssue> Validate(
        LadderProgram program,
        IReadOnlyList<SceneIoPoint> points)
    {
        var issues = new List<LadderValidationIssue>();
        var pointsByName = points.ToDictionary(point => point.Name, StringComparer.Ordinal);
        var outputBindings = new HashSet<string>(StringComparer.Ordinal);
        for (var index = 0; index < program.Variables.Count; index++)
        {
            var variable = program.Variables[index];
            if (string.IsNullOrWhiteSpace(variable.Binding)) continue;
            var path = $"$.variables[{index}].binding";
            if (OperatorPulseBindings.Contains(variable.Binding))
            {
                if (variable.Type != PlcVariableType.Bool || variable.Role != PlcVariableRole.Input)
                    issues.Add(new("IO002", path,
                        $"Operator pulse binding '{variable.Binding}' requires a BOOL Input tag."));
                continue;
            }
            if (!pointsByName.TryGetValue(variable.Binding, out var point))
            {
                issues.Add(new("IO001", path,
                    $"Scene point '{variable.Binding}' is not declared by the active scene."));
                continue;
            }
            if (!TypesCompatible(variable.Type, point.Type))
            {
                issues.Add(new("IO002", path,
                    $"Tag '{variable.Name}' is {variable.Type.ToString().ToUpperInvariant()} but scene point '{point.Name}' is {point.Type}; BOOL, INT, DINT, and REAL bindings require matching types."));
                continue;
            }
            if (variable.Role == PlcVariableRole.Input
                && !point.Owner.Equals("PC", StringComparison.OrdinalIgnoreCase))
            {
                issues.Add(new("IO003", path,
                    $"Input tag '{variable.Name}' must bind to a simulator-owned (PC) scene point; '{point.Name}' is owned by {point.Owner}."));
            }
            else if (variable.Role == PlcVariableRole.Output)
            {
                if (!point.Owner.Equals("PLC", StringComparison.OrdinalIgnoreCase))
                    issues.Add(new("IO003", path,
                        $"Output tag '{variable.Name}' must bind to a PLC-owned scene point; '{point.Name}' is owned by {point.Owner}."));
                else if (!outputBindings.Add(point.Name))
                    issues.Add(new("IO004", path,
                        $"PLC-owned scene point '{point.Name}' is already driven by another output tag."));
            }
            else if (variable.Role == PlcVariableRole.Memory)
            {
                issues.Add(new("IO003", path,
                    $"Memory tag '{variable.Name}' cannot bind to scene I/O."));
            }
        }
        return issues;
    }

    public static bool TypesCompatible(PlcVariableType variableType, string pointType) => variableType switch
    {
        PlcVariableType.Bool => pointType.Equals("BOOL", StringComparison.OrdinalIgnoreCase),
        PlcVariableType.Int => pointType.Equals("INT", StringComparison.OrdinalIgnoreCase),
        PlcVariableType.DInt => pointType.Equals("DINT", StringComparison.OrdinalIgnoreCase),
        PlcVariableType.Real => pointType.Equals("REAL", StringComparison.OrdinalIgnoreCase),
        _ => false,
    };
}
