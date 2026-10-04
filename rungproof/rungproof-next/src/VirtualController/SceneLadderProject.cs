using System;
using System.Collections.Generic;

namespace RungProof.Next.VirtualController;

/// <summary>
/// Creates an exercise project from declared symbolic I/O. It does not invent
/// a solution, translate scene reference rules into PLC code, or coerce types
/// that the offline controller cannot execute.
/// </summary>
public static class SceneLadderProject
{
    public static LadderEditorDocument Create(string sceneId, string sceneName,
        IReadOnlyList<SceneIoPoint> points, IReadOnlyDictionary<string, object?> initialValues,
        out IReadOnlyList<SceneIoPoint> unsupportedPoints)
    {
        var document = new LadderEditorDocument();
        document.ResetProject("exercise-" + sceneId, "Main", TimeSpan.FromMilliseconds(20));
        document.Name = sceneName;
        document.SourceSceneId = sceneId;
        var unsupported = new List<SceneIoPoint>();
        foreach (var point in points)
        {
            var input = point.Owner.Equals("PC", StringComparison.OrdinalIgnoreCase);
            var output = point.Owner.Equals("PLC", StringComparison.OrdinalIgnoreCase);
            if (!input && !output) continue; // Internal plant state has no PLC binding.
            var type = point.Type.ToUpperInvariant() switch
            {
                "BOOL" => (PlcVariableType?)PlcVariableType.Bool,
                "INT" => PlcVariableType.Int,
                "DINT" => PlcVariableType.DInt,
                "REAL" => PlcVariableType.Real,
                _ => null,
            };
            if (type is null)
            {
                unsupported.Add(point);
                continue;
            }
            var initial = initialValues.GetValueOrDefault(point.Name);
            // JSON `0` is read by the plant as a long. Its declared REAL type
            // requires a double in the editor. Normalize this numeric token
            // at the scene boundary; retain strict validation for other values.
            if (type == PlcVariableType.Real && initial is long integer)
                initial = (double)integer;
            document.AddTag(point.Name, input ? PlcVariableRole.Input : PlcVariableRole.Output,
                point.Name, type.Value, initial);
            document.WatchVariables.Add(point.Name);
        }
        unsupportedPoints = unsupported;
        return document;
    }
}
