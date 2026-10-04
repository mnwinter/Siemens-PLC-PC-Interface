using System;
using System.Collections.Generic;

namespace RungProof.Next.VirtualController;

/// <summary>
/// Converts between scene-owned symbolic point names and controller-owned tag
/// names. This is deliberately a pure mapping boundary: it has no PLC
/// transport dependency and cannot resolve physical addresses.
/// </summary>
public static class SceneIoImageMapper
{
    public static IReadOnlyDictionary<string, bool> SampleBoolInputs(
        LadderProgram program,
        IReadOnlyDictionary<string, bool> sceneInputs)
    {
        ArgumentNullException.ThrowIfNull(program);
        ArgumentNullException.ThrowIfNull(sceneInputs);
        var mapped = new Dictionary<string, bool>(StringComparer.Ordinal);
        foreach (var variable in program.Variables)
        {
            if (variable.Role != PlcVariableRole.Input
                || variable.Type != PlcVariableType.Bool
                || string.IsNullOrWhiteSpace(variable.Binding)) continue;
            if (sceneInputs.TryGetValue(variable.Binding, out var value)) mapped[variable.Name] = value;
        }
        return mapped;
    }

    public static IReadOnlyDictionary<string, double> SampleNumericInputs(
        LadderProgram program,
        IReadOnlyDictionary<string, double> sceneInputs)
    {
        ArgumentNullException.ThrowIfNull(program);
        ArgumentNullException.ThrowIfNull(sceneInputs);
        var mapped = new Dictionary<string, double>(StringComparer.Ordinal);
        foreach (var variable in program.Variables)
        {
            if (variable.Role != PlcVariableRole.Input
                || variable.Type is not (PlcVariableType.Int or PlcVariableType.DInt or PlcVariableType.Real)
                || string.IsNullOrWhiteSpace(variable.Binding)) continue;
            if (sceneInputs.TryGetValue(variable.Binding, out var value)) mapped[variable.Name] = value;
        }
        return mapped;
    }

    public static IReadOnlyDictionary<string, bool> CommitBoolOutputs(
        LadderProgram program,
        IReadOnlyDictionary<string, bool> controllerOutputs)
    {
        ArgumentNullException.ThrowIfNull(program);
        ArgumentNullException.ThrowIfNull(controllerOutputs);
        var mapped = new Dictionary<string, bool>(StringComparer.Ordinal);
        foreach (var variable in program.Variables)
        {
            if (variable.Role != PlcVariableRole.Output
                || variable.Type != PlcVariableType.Bool
                || string.IsNullOrWhiteSpace(variable.Binding)
                || !controllerOutputs.TryGetValue(variable.Name, out var value)) continue;
            mapped[variable.Binding] = value;
        }
        return mapped;
    }

    public static IReadOnlyDictionary<string, double> CommitNumericOutputs(
        LadderProgram program,
        IReadOnlyDictionary<string, double> controllerOutputs)
    {
        ArgumentNullException.ThrowIfNull(program);
        ArgumentNullException.ThrowIfNull(controllerOutputs);
        var mapped = new Dictionary<string, double>(StringComparer.Ordinal);
        foreach (var variable in program.Variables)
        {
            if (variable.Role != PlcVariableRole.Output
                || variable.Type is not (PlcVariableType.Int or PlcVariableType.DInt or PlcVariableType.Real)
                || string.IsNullOrWhiteSpace(variable.Binding)
                || !controllerOutputs.TryGetValue(variable.Name, out var value)) continue;
            mapped[variable.Binding] = value;
        }
        return mapped;
    }
}
