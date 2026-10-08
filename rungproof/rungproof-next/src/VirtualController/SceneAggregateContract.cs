using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text.Json;

namespace RungProof.Next.VirtualController;

/// <summary>Pure scene aggregate boundary validation; call before allocating runtime nodes.</summary>
public static class SceneAggregateContract
{
    public static IReadOnlyDictionary<string, string> Validate(JsonElement definition)
    {
        var aliases = new Dictionary<string, string>(StringComparer.Ordinal);
        if (definition.ValueKind != JsonValueKind.Object) return new ReadOnlyDictionary<string, string>(aliases);
        if (!definition.TryGetProperty("points", out var points)) return new ReadOnlyDictionary<string, string>(aliases);
        if (points.ValueKind != JsonValueKind.Array) throw new ArgumentException("Scene points must be an array.");
        var names = new Dictionary<string, (string Type, string Owner)>(StringComparer.Ordinal);
        var initialValues = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
        var roots = new List<PlcVariable>();
        foreach (var point in points.EnumerateArray())
        {
            static string Text(JsonElement element, string property) => element.TryGetProperty(property, out var text) && text.ValueKind == JsonValueKind.String ? text.GetString() ?? "" : "";
            var name = Text(point, "name"); var type = Text(point, "type").ToUpperInvariant(); var owner = Text(point, "owner").ToUpperInvariant();
            if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("Scene point name is required.");
            if (!names.TryAdd(name, (type, owner))) throw new ArgumentException($"Duplicate scene point '{name}'.");
            if (point.TryGetProperty("initial", out var initialValue)) initialValues.Add(name, initialValue.Clone());
            if (type is not ("STRUCT" or "ARRAY")) continue;
            if (owner is not ("PC" or "PLC")) throw new ArgumentException($"Aggregate '{name}' requires PC or PLC ownership.");
            if (!point.TryGetProperty("initial", out var initial)) throw new ArgumentException($"Aggregate '{name}' requires initial data.");
            var schema = point.TryGetProperty("aggregate", out var metadata) ? PlcAggregates.ParseSchema(metadata) : null;
            roots.Add(new(name, type == "STRUCT" ? PlcVariableType.Struct : PlcVariableType.Array,
                owner == "PC" ? PlcVariableRole.Input : PlcVariableRole.Output, initial.Clone(), Aggregate: schema));
        }
        var leaves = PlcAggregates.Expand(roots).ToDictionary(v => v.Name, StringComparer.Ordinal);
        foreach (var root in roots)
        foreach (var other in names.Keys.Where(name => name != root.Name))
        {
            static bool Descendant(string name, string parent) => name.StartsWith(parent + ".", StringComparison.Ordinal) || name.StartsWith(parent + "[", StringComparison.Ordinal);
            if (Descendant(other, root.Name) || Descendant(root.Name, other)) throw new ArgumentException($"Aggregate root '{root.Name}' overlaps scene declaration '{other}'.");
        }
        if (definition.TryGetProperty("aggregateFeedbackAliases", out var configured))
        {
            if (configured.ValueKind != JsonValueKind.Object) throw new ArgumentException("Aggregate feedback aliases must be an object.");
            foreach (var alias in configured.EnumerateObject())
            {
                var source = alias.Value.ValueKind == JsonValueKind.String ? alias.Value.GetString() ?? "" : "";
                if (!leaves.TryGetValue(alias.Name, out var target) || target.Role != PlcVariableRole.Input
                    || !names.TryGetValue(source, out var declared) || declared.Owner != "PC" || declared.Type != target.Type.ToString().ToUpperInvariant())
                    throw new ArgumentException($"Aggregate feedback alias '{alias.Name}' requires an actual PC-owned scalar leaf and declared PC source of identical type.");
                if (!initialValues.TryGetValue(source, out var sourceInitial)) throw new ArgumentException($"Aggregate alias source '{source}' requires a typed initial value.");
                try
                {
                    // Reuse exactly the aggregate scalar-leaf validator, including ranges and finite REALs.
                    PlcAggregates.Expand([new("aliasSource", PlcVariableType.Struct, PlcVariableRole.Input,
                        new Dictionary<string, object> { ["value"] = sourceInitial }, Aggregate: new([new("value", target.Type)]))]);
                }
                catch (ArgumentException error) { throw new ArgumentException($"Aggregate alias source '{source}' has invalid initial data: {error.Message}", error); }
                if (!aliases.TryAdd(alias.Name, source)) throw new ArgumentException("Duplicate aggregate feedback alias.");
            }
        }
        return new ReadOnlyDictionary<string, string>(aliases);
    }
}
