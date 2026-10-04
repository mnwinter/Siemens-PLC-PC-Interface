using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json;

namespace RungProof.Next.VirtualController;

public sealed record LadderEditorProjectLoadResult(
    LadderEditorDocument? Document,
    IReadOnlyList<LadderValidationIssue> Issues)
{
    public bool IsReadable => Document is not null && Issues.Count == 0;
}

/// <summary>
/// Persistence for the mutable offline engineering project. Unlike
/// LadderProgramJson, this format deliberately preserves compiler-invalid
/// work in progress. Loading proves only that the editor document is readable;
/// Verify + Load remains the separate executable safety boundary.
/// </summary>
public static class LadderEditorProjectJson
{
    public const int SchemaVersion = 1;
    public const string Kind = "rungproof-ladder-project";

    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
        WriteIndented = true,
    };

    public static string Save(LadderEditorDocument document) => Save(document, contentOnly: false);

    public static bool HasUnsavedChanges(LadderEditorDocument document, string? savedJson)
    {
        if (savedJson is null) return true;
        try
        {
            var saved = JsonSerializer.Deserialize<ProjectDto>(savedJson, Options);
            if (saved is null) return true;
            // Selecting a block is navigation. Preserve it in saved files,
            // but do not confuse it with an edit to the project contents.
            saved.ActiveBlockIndex = 0;
            return !string.Equals(JsonSerializer.Serialize(saved, Options),
                Save(document, contentOnly: true), StringComparison.Ordinal);
        }
        catch (JsonException) { return true; }
    }

    private static string Save(LadderEditorDocument document, bool contentOnly)
    {
        ArgumentNullException.ThrowIfNull(document);
        var snapshot = document.CaptureSnapshot();
        var dto = new ProjectDto
        {
            SchemaVersion = SchemaVersion,
            Kind = Kind,
            Id = snapshot.Id,
            Name = snapshot.Name,
            SourceSceneId = snapshot.SourceSceneId,
            ScanPeriodMs = snapshot.ScanPeriod.TotalMilliseconds,
            ActiveBlockIndex = contentOnly ? 0 : snapshot.ActiveBlockIndex,
            EntryBlockId = snapshot.EntryBlockId,
            NextId = snapshot.NextId,
            Tags = snapshot.Tags.Select(Tag).ToList(),
            Blocks = snapshot.Blocks.Select(Block).ToList(),
            Tasks = snapshot.Tasks.Select(Task).ToList(),
            WatchVariables = snapshot.WatchVariables.ToList(),
        };
        return JsonSerializer.Serialize(dto, Options);
    }

    public static LadderEditorProjectLoadResult Load(string json)
    {
        try
        {
            var dto = JsonSerializer.Deserialize<ProjectDto>(json, Options);
            if (dto is null)
                return Invalid("Project document must be a JSON object.");
            if (dto.SchemaVersion != SchemaVersion)
                return Invalid($"Unsupported editor project schemaVersion '{dto.SchemaVersion}'.");
            if (!string.Equals(dto.Kind, Kind, StringComparison.Ordinal))
                return Invalid($"Unsupported project kind '{dto.Kind}'.");
            if (dto.Tags is null || dto.Blocks is null || dto.Tasks is null || dto.WatchVariables is null)
                return Invalid("Editor project collections must not be null.");
            if (dto.Blocks.Count == 0)
                return Invalid("Editor project must contain at least one block/routine.");
            if (dto.Blocks.Any(block => block.Rungs is null)
                || dto.Blocks.SelectMany(block => block.Rungs).Any(rung => rung.Branches is null)
                || dto.Blocks.SelectMany(block => block.Rungs).SelectMany(rung => rung.Branches)
                    .Any(branch => branch.Contacts is null))
                return Invalid("Editor project block, rung, branch, and contact collections must not be null.");
            if (dto.Blocks.Any(block => block.Rungs.Any(rung => rung.Branches.Count == 0)))
                return Invalid("Every network/rung must retain at least one branch path.");

            var issues = new List<LadderValidationIssue>();
            var tags = dto.Tags.Select((tag, index) => ParseTag(tag, index, issues)).ToArray();
            var blocks = dto.Blocks.Select((block, index) => ParseBlock(block, index, issues)).ToArray();
            var tasks = dto.Tasks.Select((task, index) => ParseTask(task, index, issues)).ToArray();
            if (issues.Count > 0) return new(null, issues);

            var activeBlockIndex = Math.Clamp(dto.ActiveBlockIndex, 0, blocks.Length - 1);
            var nextId = Math.Max(Math.Max(1, dto.NextId), NextAvailableStableId(blocks, tasks));
            var snapshot = new LadderEditorSnapshot(
                dto.Id ?? string.Empty,
                dto.Name ?? string.Empty,
                dto.SourceSceneId ?? string.Empty,
                TimeSpan.FromMilliseconds(dto.ScanPeriodMs),
                tags,
                blocks,
                tasks,
                dto.WatchVariables.ToArray(),
                activeBlockIndex,
                dto.EntryBlockId ?? string.Empty,
                nextId);
            var document = new LadderEditorDocument();
            document.RestoreSnapshot(snapshot);
            return new(document, []);
        }
        catch (JsonException exception)
        {
            return Invalid($"Malformed editor project JSON: {exception.Message}");
        }
        catch (Exception exception) when (exception is InvalidOperationException or OverflowException)
        {
            return Invalid($"Unreadable editor project: {exception.Message}");
        }
    }

    private static int NextAvailableStableId(IEnumerable<EditableBlock> blocks, IEnumerable<EditableTask> tasks)
    {
        var maximum = 0;
        void Include(string id)
        {
            var separator = id.LastIndexOf('-');
            if (separator >= 0 && int.TryParse(id.AsSpan(separator + 1), NumberStyles.None,
                    CultureInfo.InvariantCulture, out var suffix))
                maximum = Math.Max(maximum, suffix);
        }

        foreach (var block in blocks)
        {
            Include(block.Id);
            foreach (var rung in block.Rungs)
            {
                Include(rung.Id);
                foreach (var branch in rung.Branches)
                {
                    Include(branch.Id);
                    foreach (var contact in branch.Contacts) Include(contact.Id);
                }
            }
        }
        foreach (var task in tasks) Include(task.Id);
        return maximum == int.MaxValue ? int.MaxValue : maximum + 1;
    }

    private static TagDto Tag(PlcVariable source) => new()
    {
        Name = source.Name,
        Type = source.Type.ToString(),
        Role = source.Role.ToString(),
        Initial = source.Type == PlcVariableType.Timer && source.InitialValue is TimeSpan time
            ? time.TotalMilliseconds
            : source.InitialValue,
        Binding = source.Binding,
    };

    private static BlockDto Block(EditableBlock source) => new()
    {
        Id = source.Id,
        Name = source.Name,
        BlockType = source.BlockType.ToString(),
        Interface = source.Interface.Select(parameter => new InterfaceDto
        {
            Name = parameter.Name,
            Type = parameter.Type.ToString(),
            Section = parameter.Section.ToString(),
            Initial = parameter.InitialValue is TimeSpan time ? time.TotalMilliseconds : parameter.InitialValue,
            DataType = parameter.DataType,
        }).ToList(),
        Rungs = source.Rungs.Select(Rung).ToList(),
    };

    private static RungDto Rung(EditableRung source) => new()
    {
        Id = source.Id,
        Label = source.Label,
        CoilVariable = source.CoilVariable,
        CoilMode = source.CoilMode.ToString(),
        TimerVariable = source.TimerVariable,
        TimerPresetMs = source.TimerPreset.TotalMilliseconds,
        TimerKind = source.TimerKind.ToString(),
        IsTimer = source.IsTimer,
        IsTimerReset = source.IsTimerReset,
        IsCounter = source.IsCounter,
        IsCounterReset = source.IsCounterReset,
        IsCounterLoad = source.IsCounterLoad,
        CounterKind = source.CounterKind.ToString(),
        CounterVariable = source.CounterVariable,
        CounterPreset = source.CounterPreset,
        IsNumericOperation = source.IsNumericOperation,
        NumericOperationKind = source.NumericOperationKind.ToString(),
        NumericSourceA = source.NumericSourceA,
        NumericSourceB = source.NumericSourceB,
        NumericSourceC = source.NumericSourceC,
        NumericDestination = source.NumericDestination,
        IsCall = source.IsCall,
        CallTarget = source.CallTarget,
        IsReturn = source.IsReturn,
        IsJump = source.IsJump,
        IsLabel = source.IsLabel,
        ProgramControlLabel = source.ProgramControlLabel,
        Branches = source.Branches.Select(branch => new BranchDto
        {
            Id = branch.Id,
            Contacts = branch.Contacts.Select(contact => new ContactDto
            {
                Id = contact.Id,
                Variable = contact.Variable,
                NormallyClosed = contact.NormallyClosed,
                IsComparison = contact.IsComparison,
                CompareOperator = contact.CompareOperator.ToString(),
                RightOperand = contact.RightOperand,
                EdgeMode = contact.EdgeMode.ToString(),
            }).ToList(),
        }).ToList(),
    };

    private static TaskDto Task(EditableTask source) => new()
    {
        Id = source.Id,
        Name = source.Name,
        Kind = source.Kind.ToString(),
        PeriodMs = source.Period.TotalMilliseconds,
        Priority = source.Priority,
        EntryBlock = source.EntryBlock,
    };

    private static PlcVariable ParseTag(TagDto dto, int index, ICollection<LadderValidationIssue> issues)
    {
        var type = ParseEnum(dto.Type, PlcVariableType.Bool, $"$.tags[{index}].type", issues);
        var role = ParseEnum(dto.Role, PlcVariableRole.Memory, $"$.tags[{index}].role", issues);
        var initial = ParseInitial(dto.Initial, type, $"$.tags[{index}].initial", issues);
        return new PlcVariable(dto.Name ?? string.Empty, type, role, initial, dto.Binding ?? string.Empty);
    }

    private static EditableBlock ParseBlock(BlockDto dto, int blockIndex, ICollection<LadderValidationIssue> issues)
    {
        var defaultType = blockIndex == 0 ? LadderBlockType.OrganizationBlock : LadderBlockType.Function;
        var blockType = string.IsNullOrWhiteSpace(dto.BlockType)
            ? defaultType
            : ParseEnum(dto.BlockType, defaultType, $"$.blocks[{blockIndex}].blockType", issues);
        var block = new EditableBlock(dto.Id ?? string.Empty, dto.Name ?? string.Empty, blockType);
        for (var parameterIndex = 0; parameterIndex < dto.Interface.Count; parameterIndex++)
        {
            var source = dto.Interface[parameterIndex];
            var path = $"$.blocks[{blockIndex}].interface[{parameterIndex}]";
            var type = ParseEnum(source.Type, PlcVariableType.Bool, $"{path}.type", issues);
            var section = ParseEnum(source.Section, LadderInterfaceSection.Input, $"{path}.section", issues);
            var initial = ParseInitial(source.Initial, type, $"{path}.initial", issues);
            block.Interface.Add(new LadderInterfaceParameter(source.Name ?? string.Empty, type, section, initial, source.DataType ?? string.Empty));
        }
        for (var rungIndex = 0; rungIndex < dto.Rungs.Count; rungIndex++)
            block.Rungs.Add(ParseRung(dto.Rungs[rungIndex], blockIndex, rungIndex, issues));
        return block;
    }

    private static EditableRung ParseRung(
        RungDto dto,
        int blockIndex,
        int rungIndex,
        ICollection<LadderValidationIssue> issues)
    {
        var path = $"$.blocks[{blockIndex}].rungs[{rungIndex}]";
        var rung = new EditableRung(dto.Id ?? string.Empty, dto.Label ?? string.Empty, dto.CoilVariable ?? string.Empty)
        {
            CoilMode = ParseEnum(dto.CoilMode, LadderCoilMode.Assign, $"{path}.coilMode", issues),
            TimerVariable = dto.TimerVariable ?? string.Empty,
            TimerPreset = TimeSpan.FromMilliseconds(dto.TimerPresetMs),
            TimerKind = ParseEnum(dto.TimerKind, LadderTimerKind.OnDelay, $"{path}.timerKind", issues),
            IsTimer = dto.IsTimer,
            IsTimerReset = dto.IsTimerReset,
            IsCounter = dto.IsCounter,
            IsCounterReset = dto.IsCounterReset,
            IsCounterLoad = dto.IsCounterLoad,
            CounterKind = ParseEnum(dto.CounterKind, LadderCounterKind.CountUp, $"{path}.counterKind", issues),
            CounterVariable = dto.CounterVariable ?? string.Empty,
            CounterPreset = dto.CounterPreset,
            IsNumericOperation = dto.IsNumericOperation,
            NumericOperationKind = ParseEnum(dto.NumericOperationKind, LadderNumericOperationKind.Move,
                $"{path}.numericOperationKind", issues),
            NumericSourceA = dto.NumericSourceA ?? string.Empty,
            NumericSourceB = dto.NumericSourceB ?? string.Empty,
            NumericSourceC = dto.NumericSourceC ?? string.Empty,
            NumericDestination = dto.NumericDestination ?? string.Empty,
            IsCall = dto.IsCall,
            CallTarget = dto.CallTarget ?? string.Empty,
            IsReturn = dto.IsReturn,
            IsJump = dto.IsJump,
            IsLabel = dto.IsLabel,
            ProgramControlLabel = dto.ProgramControlLabel ?? string.Empty,
        };
        for (var branchIndex = 0; branchIndex < dto.Branches.Count; branchIndex++)
        {
            var branchDto = dto.Branches[branchIndex];
            var branch = new EditableBranch(branchDto.Id ?? string.Empty);
            for (var contactIndex = 0; contactIndex < branchDto.Contacts.Count; contactIndex++)
            {
                var contact = branchDto.Contacts[contactIndex];
                var contactPath = $"{path}.branches[{branchIndex}].contacts[{contactIndex}]";
                branch.Contacts.Add(new EditableContact(
                    contact.Id ?? string.Empty,
                    contact.Variable ?? string.Empty,
                    contact.NormallyClosed,
                    contact.IsComparison,
                    ParseEnum(contact.CompareOperator, LadderCompareOperator.Equal,
                        $"{contactPath}.compareOperator", issues),
                    contact.RightOperand ?? string.Empty,
                    ParseEnum(contact.EdgeMode, LadderEdgeMode.None, $"{contactPath}.edgeMode", issues)));
            }
            rung.Branches.Add(branch);
        }
        return rung;
    }

    private static EditableTask ParseTask(TaskDto dto, int index, ICollection<LadderValidationIssue> issues) => new(
        dto.Id ?? string.Empty,
        dto.Name ?? string.Empty,
        ParseEnum(dto.Kind, LadderTaskKind.Continuous, $"$.tasks[{index}].kind", issues),
        TimeSpan.FromMilliseconds(dto.PeriodMs),
        dto.Priority,
        dto.EntryBlock ?? string.Empty);

    private static T ParseEnum<T>(string? value, T fallback, string path, ICollection<LadderValidationIssue> issues)
        where T : struct, Enum
    {
        if (Enum.TryParse<T>(value, true, out var parsed)) return parsed;
        issues.Add(new("EPJ001", path, $"Unknown {typeof(T).Name} value '{value}'."));
        return fallback;
    }

    private static object ParseInitial(
        object? value,
        PlcVariableType type,
        string path,
        ICollection<LadderValidationIssue> issues)
    {
        try
        {
            var element = value is JsonElement json ? json : JsonSerializer.SerializeToElement(value, Options);
            return type switch
            {
                PlcVariableType.Bool => element.GetBoolean(),
                PlcVariableType.Int or PlcVariableType.DInt or PlcVariableType.Counter => element.GetInt64(),
                PlcVariableType.Real => element.GetDouble(),
                PlcVariableType.Timer => TimeSpan.FromMilliseconds(element.GetDouble()),
                _ => false,
            };
        }
        catch (Exception exception) when (exception is InvalidOperationException or FormatException)
        {
            issues.Add(new("EPJ001", path,
                $"Initial value is not valid for {type.ToString().ToUpperInvariant()}."));
            return type switch
            {
                PlcVariableType.Bool => false,
                PlcVariableType.Real => 0.0,
                PlcVariableType.Timer => TimeSpan.Zero,
                _ => 0L,
            };
        }
    }

    private static LadderEditorProjectLoadResult Invalid(string message) =>
        new(null, [new LadderValidationIssue("EPJ001", "$", message)]);

    private sealed class ProjectDto
    {
        public int SchemaVersion { get; set; }
        public string? Kind { get; set; }
        public string? Id { get; set; }
        public string? Name { get; set; }
        public string? SourceSceneId { get; set; }
        public double ScanPeriodMs { get; set; }
        public int ActiveBlockIndex { get; set; }
        public string? EntryBlockId { get; set; }
        public int NextId { get; set; }
        public List<TagDto> Tags { get; set; } = [];
        public List<BlockDto> Blocks { get; set; } = [];
        public List<TaskDto> Tasks { get; set; } = [];
        public List<string> WatchVariables { get; set; } = [];
    }

    private sealed class TagDto
    {
        public string? Name { get; set; }
        public string? Type { get; set; }
        public string? Role { get; set; }
        public object? Initial { get; set; }
        public string? Binding { get; set; }
    }

    private sealed class BlockDto
    {
        public string? Id { get; set; }
        public string? Name { get; set; }
        public string? BlockType { get; set; }
        public List<InterfaceDto> Interface { get; set; } = [];
        public List<RungDto> Rungs { get; set; } = [];
    }

    private sealed class InterfaceDto
    {
        public string? Name { get; set; }
        public string? Type { get; set; }
        public string? Section { get; set; }
        public object? Initial { get; set; }
        public string? DataType { get; set; }
    }

    private sealed class RungDto
    {
        public string? Id { get; set; }
        public string? Label { get; set; }
        public string? CoilVariable { get; set; }
        public string? CoilMode { get; set; }
        public string? TimerVariable { get; set; }
        public double TimerPresetMs { get; set; }
        public string? TimerKind { get; set; }
        public bool IsTimer { get; set; }
        public bool IsTimerReset { get; set; }
        public bool IsCounter { get; set; }
        public bool IsCounterReset { get; set; }
        public bool IsCounterLoad { get; set; }
        public string? CounterKind { get; set; }
        public string? CounterVariable { get; set; }
        public long CounterPreset { get; set; }
        public bool IsNumericOperation { get; set; }
        public string? NumericOperationKind { get; set; }
        public string? NumericSourceA { get; set; }
        public string? NumericSourceB { get; set; }
        public string? NumericSourceC { get; set; }
        public string? NumericDestination { get; set; }
        public bool IsCall { get; set; }
        public string? CallTarget { get; set; }
        public bool IsReturn { get; set; }
        public bool IsJump { get; set; }
        public bool IsLabel { get; set; }
        public string? ProgramControlLabel { get; set; }
        public List<BranchDto> Branches { get; set; } = [];
    }

    private sealed class BranchDto
    {
        public string? Id { get; set; }
        public List<ContactDto> Contacts { get; set; } = [];
    }

    private sealed class ContactDto
    {
        public string? Id { get; set; }
        public string? Variable { get; set; }
        public bool NormallyClosed { get; set; }
        public bool IsComparison { get; set; }
        public string? CompareOperator { get; set; }
        public string? RightOperand { get; set; }
        public string? EdgeMode { get; set; }
    }

    private sealed class TaskDto
    {
        public string? Id { get; set; }
        public string? Name { get; set; }
        public string? Kind { get; set; }
        public double PeriodMs { get; set; }
        public int Priority { get; set; }
        public string? EntryBlock { get; set; }
    }
}
