using System;
using System.Collections.Generic;
using System.Linq;

namespace RungProof.Next.VirtualController;

public sealed record EditableContact(
    string Id,
    string Variable,
    bool NormallyClosed,
    bool IsComparison = false,
    LadderCompareOperator CompareOperator = LadderCompareOperator.Equal,
    string RightOperand = "",
    LadderEdgeMode EdgeMode = LadderEdgeMode.None);

public sealed class EditableBranch
{
    public string Id { get; }
    public List<EditableContact> Contacts { get; } = [];

    public EditableBranch(string id) => Id = id;
}

public sealed class EditableRung
{
    public string Id { get; }
    public string Label { get; set; }
    public string CoilVariable { get; set; }
    public LadderCoilMode CoilMode { get; set; } = LadderCoilMode.Assign;
    public string TimerVariable { get; set; } = string.Empty;
    public TimeSpan TimerPreset { get; set; } = TimeSpan.FromSeconds(1);
    public LadderTimerKind TimerKind { get; set; } = LadderTimerKind.OnDelay;
    public bool IsTimer { get; set; }
    public bool IsTimerReset { get; set; }
    public bool IsCounter { get; set; }
    public bool IsCounterReset { get; set; }
    public bool IsCounterLoad { get; set; }
    public LadderCounterKind CounterKind { get; set; } = LadderCounterKind.CountUp;
    public string CounterVariable { get; set; } = string.Empty;
    public long CounterPreset { get; set; } = 10;
    public bool IsNumericOperation { get; set; }
    public LadderNumericOperationKind NumericOperationKind { get; set; } = LadderNumericOperationKind.Move;
    public string NumericSourceA { get; set; } = "0";
    public string NumericSourceB { get; set; } = "0";
    public string NumericSourceC { get; set; } = "0";
    public string NumericDestination { get; set; } = string.Empty;
    public bool IsCall { get; set; }
    public string CallTarget { get; set; } = string.Empty;
    public bool IsReturn { get; set; }
    public bool IsJump { get; set; }
    public bool IsLabel { get; set; }
    public string ProgramControlLabel { get; set; } = string.Empty;
    public List<EditableBranch> Branches { get; } = [];

    public EditableRung(string id, string label, string coilVariable)
    {
        Id = id;
        Label = label;
        CoilVariable = coilVariable;
    }
}

public sealed class EditableBlock
{
    public string Id { get; }
    public string Name { get; set; }
    public LadderBlockType BlockType { get; set; }
    public List<LadderInterfaceParameter> Interface { get; } = [];
    public List<EditableRung> Rungs { get; } = [];

    public EditableBlock(string id, string name, LadderBlockType blockType = LadderBlockType.Function)
    {
        Id = id;
        Name = name;
        BlockType = blockType;
    }
}

public sealed class EditableTask
{
    public string Id { get; }
    public string Name { get; set; }
    public LadderTaskKind Kind { get; set; }
    public TimeSpan Period { get; set; }
    public int Priority { get; set; }
    public string EntryBlock { get; set; }

    public EditableTask(string id, string name, LadderTaskKind kind, TimeSpan period, int priority, string entryBlock)
    {
        Id = id;
        Name = name;
        Kind = kind;
        Period = period;
        Priority = priority;
        EntryBlock = entryBlock;
    }
}

/// <summary>
/// Mutable editor document for the offline Ladder workbench. The execution
/// runtime remains immutable: BuildProgram creates and validates a fresh IR
/// snapshot before a program can be loaded or scanned.
/// </summary>
public sealed partial class LadderEditorDocument
{
    private int _nextId = 1;
    public string Id { get; set; } = "offline-controller";
    public string Name { get; set; } = "Main";
    public string SourceSceneId { get; set; } = string.Empty;
    public TimeSpan ScanPeriod { get; set; } = TimeSpan.FromMilliseconds(20);
    public List<PlcVariable> Tags { get; } = [];
    public List<EditableBlock> Blocks { get; } = [];
    public List<EditableTask> Tasks { get; } = [];
    public List<string> WatchVariables { get; } = [];
    public int ActiveBlockIndex { get; private set; }
    public string EntryBlockId { get; set; } = string.Empty;
    public List<EditableRung> Rungs => EnsureActiveBlock().Rungs;

    /// <summary>
    /// Resets every project-owned authoring field. Runtime state is deliberately
    /// outside this document and is invalidated by the shell after this call.
    /// </summary>
    public void ResetProject(string id, string name, TimeSpan scanPeriod)
    {
        if (string.IsNullOrWhiteSpace(id)) throw new ArgumentException("Project ID cannot be empty.", nameof(id));
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("Project name cannot be empty.", nameof(name));
        if (scanPeriod <= TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(scanPeriod));
        Id = id.Trim();
        Name = name.Trim();
        SourceSceneId = string.Empty;
        ScanPeriod = scanPeriod;
        Tags.Clear();
        Blocks.Clear();
        Tasks.Clear();
        WatchVariables.Clear();
        ActiveBlockIndex = 0;
        EntryBlockId = string.Empty;
        _nextId = 1;
        AddBlock(Name);
    }

    public EditableBlock AddBlock(string name, LadderBlockType? blockType = null)
    {
        var normalizedName = ValidateUniqueName(name, Blocks.Select(block => block.Name), "Block/routine");
        var type = blockType ?? (Blocks.Count == 0 ? LadderBlockType.OrganizationBlock : LadderBlockType.Function);
        var block = new EditableBlock(NewId("block"), normalizedName, type);
        Blocks.Add(block);
        if (Blocks.Count == 1)
        {
            ActiveBlockIndex = 0;
            EntryBlockId = block.Id;
            if (Tasks.Count == 0)
                Tasks.Add(new EditableTask(NewId("task"), "MainTask", LadderTaskKind.Continuous, ScanPeriod, 10, block.Id));
        }
        return block;
    }

    public LadderInterfaceParameter AddInterfaceParameter(
        string blockId,
        string name,
        PlcVariableType type,
        LadderInterfaceSection section,
        object? initialValue = null,
        string dataType = "")
    {
        var block = Blocks.FirstOrDefault(candidate => candidate.Id.Equals(blockId, StringComparison.Ordinal))
            ?? throw new InvalidOperationException($"Block '{blockId}' does not exist.");
        var normalizedName = ValidateUniqueName(name, block.Interface.Select(parameter => parameter.Name), "Interface parameter");
        var value = initialValue ?? type switch
        {
            PlcVariableType.Bool => false,
            PlcVariableType.Real => 0.0,
            PlcVariableType.Timer => TimeSpan.Zero,
            _ => 0L,
        };
        var parameter = new LadderInterfaceParameter(normalizedName, type, section, value, dataType);
        block.Interface.Add(parameter);
        return parameter;
    }

    public bool RemoveInterfaceParameter(string blockId, int index)
    {
        var block = Blocks.FirstOrDefault(candidate => candidate.Id.Equals(blockId, StringComparison.Ordinal));
        if (block is null || index < 0 || index >= block.Interface.Count) return false;
        block.Interface.RemoveAt(index);
        return true;
    }

    public EditableBlock RenameBlock(string blockId, string name)
    {
        var block = Blocks.FirstOrDefault(candidate => candidate.Id.Equals(blockId, StringComparison.Ordinal))
            ?? throw new InvalidOperationException($"Block/routine '{blockId}' does not exist.");
        block.Name = ValidateUniqueName(
            name,
            Blocks.Where(candidate => !ReferenceEquals(candidate, block)).Select(candidate => candidate.Name),
            "Block/routine");
        return block;
    }

    public bool CanRemoveBlock(string blockId, out string reason)
    {
        var index = Blocks.FindIndex(block => block.Id.Equals(blockId, StringComparison.Ordinal));
        if (index < 0)
        {
            reason = $"Block/routine '{blockId}' does not exist.";
            return false;
        }
        var block = Blocks[index];
        if (Blocks.Count == 1)
        {
            reason = "The controller must retain at least one block/routine.";
            return false;
        }
        if (EntryBlockId.Equals(blockId, StringComparison.Ordinal))
        {
            reason = $"'{block.Name}' is the controller entry block and cannot be removed.";
            return false;
        }
        var owningTasks = Tasks.Where(task => task.EntryBlock.Equals(blockId, StringComparison.Ordinal))
            .Select(task => task.Name).ToArray();
        if (owningTasks.Length > 0)
        {
            reason = $"'{block.Name}' is assigned to {string.Join(", ", owningTasks)}. Reassign those tasks/OBs first.";
            return false;
        }
        var callers = Blocks.SelectMany(owner => owner.Rungs
                .Where(rung => rung.IsCall && rung.CallTarget.Equals(blockId, StringComparison.Ordinal))
                .Select(rung => $"{owner.Name}/{rung.Label}"))
            .ToArray();
        if (callers.Length > 0)
        {
            reason = $"'{block.Name}' is referenced by CALL/JSR at {string.Join(", ", callers)}. Remove those calls first.";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public bool TryRemoveBlock(string blockId, out string reason)
    {
        if (!CanRemoveBlock(blockId, out reason)) return false;
        var index = Blocks.FindIndex(block => block.Id.Equals(blockId, StringComparison.Ordinal));
        Blocks.RemoveAt(index);
        if (ActiveBlockIndex > index) ActiveBlockIndex--;
        else if (ActiveBlockIndex == index) ActiveBlockIndex = Math.Min(index, Blocks.Count - 1);
        return true;
    }

    public EditableTask AddTask(
        string name,
        LadderTaskKind kind,
        TimeSpan period,
        int priority,
        string entryBlock)
    {
        var normalizedName = ValidateUniqueName(name, Tasks.Select(task => task.Name), "Task/OB");
        if (!Blocks.Any(block => block.Id.Equals(entryBlock, StringComparison.Ordinal)))
            throw new InvalidOperationException($"Task/OB entry block '{entryBlock}' does not exist.");
        var task = new EditableTask(NewId("task"), normalizedName, kind, period, priority, entryBlock);
        Tasks.Add(task);
        return task;
    }

    public EditableTask RenameTask(string taskId, string name)
    {
        var task = Tasks.FirstOrDefault(candidate => candidate.Id.Equals(taskId, StringComparison.Ordinal))
            ?? throw new InvalidOperationException($"Task/OB '{taskId}' does not exist.");
        task.Name = ValidateUniqueName(
            name,
            Tasks.Where(candidate => !ReferenceEquals(candidate, task)).Select(candidate => candidate.Name),
            "Task/OB");
        return task;
    }

    public bool CanRemoveTask(string taskId, out string reason)
    {
        var index = Tasks.FindIndex(task => task.Id.Equals(taskId, StringComparison.Ordinal));
        if (index < 0)
        {
            reason = $"Task/OB '{taskId}' does not exist.";
            return false;
        }
        if (Tasks.Count == 1)
        {
            reason = "The controller must retain at least one task/OB schedule.";
            return false;
        }
        reason = string.Empty;
        return true;
    }

    public bool TryRemoveTask(string taskId, out string reason)
    {
        if (!CanRemoveTask(taskId, out reason)) return false;
        var index = Tasks.FindIndex(task => task.Id.Equals(taskId, StringComparison.Ordinal));
        Tasks.RemoveAt(index);
        return true;
    }

    public void SelectBlock(int index)
    {
        if (index < 0 || index >= Blocks.Count) throw new ArgumentOutOfRangeException(nameof(index));
        ActiveBlockIndex = index;
    }

    public PlcVariable AddAggregateTag(string name, PlcVariableRole role, PlcVariableType type, PlcAggregateSchema schema, object initialValue, string binding = "")
    {
        if (!PlcAggregates.IsAggregate(type)) throw new ArgumentException("Aggregate tag requires STRUCT or ARRAY.");
        var tag = new PlcVariable(name.Trim(), type, role, initialValue, binding.Trim(), schema);
        PlcAggregates.Expand(Tags.Append(tag).ToArray());
        Tags.Add(tag); return tag;
    }

    public PlcVariable AddTag(
        string name,
        PlcVariableRole role,
        string binding = "",
        PlcVariableType type = PlcVariableType.Bool,
        object? initialValue = null)
    {
        var normalizedInitialValue = initialValue ?? InitialValue(type);
        ValidateInitialValue(type, normalizedInitialValue);
        var tag = new PlcVariable(name.Trim(), type, role, normalizedInitialValue, binding.Trim());
        Tags.Add(tag);
        return tag;
    }

    public PlcVariable UpdateTag(
        string currentName,
        string newName,
        PlcVariableType type,
        PlcVariableRole role,
        string binding = "",
        object? initialValue = null,
        PlcAggregateSchema? aggregate = null)
    {
        var index = Tags.FindIndex(tag => tag.Name.Equals(currentName, StringComparison.Ordinal));
        if (index < 0) throw new InvalidOperationException($"Tag '{currentName}' does not exist.");
        var normalizedName = newName.Trim();
        if (normalizedName.Length == 0) throw new InvalidOperationException("Tag name cannot be empty.");
        if (Tags.Where((_, tagIndex) => tagIndex != index)
            .Any(tag => tag.Name.Equals(normalizedName, StringComparison.Ordinal)))
            throw new InvalidOperationException($"Tag '{normalizedName}' already exists.");
        if (type is PlcVariableType.Timer or PlcVariableType.Counter)
        {
            role = PlcVariableRole.Memory;
            binding = string.Empty;
        }
        var current = Tags[index];
        var normalizedInitialValue = initialValue ?? (current.Type == type ? current.InitialValue : InitialValue(type));
        var updatedSchema = PlcAggregates.IsAggregate(type) ? aggregate ?? (current.Type == type ? current.Aggregate : null) : null;
        if (PlcAggregates.IsAggregate(type)) PlcAggregates.Expand([current with { Name = normalizedName, Type = type, InitialValue = normalizedInitialValue, Aggregate = updatedSchema }]);
        else ValidateInitialValue(type, normalizedInitialValue);
        var updated = new PlcVariable(normalizedName, type, role, normalizedInitialValue, binding.Trim(), updatedSchema);
        if (PlcAggregates.IsAggregate(type) || Tags.Any(tag => PlcAggregates.IsAggregate(tag.Type)))
            PlcAggregates.Expand(Tags.Where((_, tagIndex) => tagIndex != index).Append(updated).ToArray());
        if (!current.Name.Equals(normalizedName, StringComparison.Ordinal))
        {
            RenameTagReferences(current.Name, normalizedName);
            for (var watchIndex = 0; watchIndex < WatchVariables.Count; watchIndex++)
                if (WatchVariables[watchIndex].Equals(current.Name, StringComparison.Ordinal)
                    || WatchVariables[watchIndex].StartsWith(current.Name + ".", StringComparison.Ordinal)
                    || WatchVariables[watchIndex].StartsWith(current.Name + "[", StringComparison.Ordinal))
                    WatchVariables[watchIndex] = normalizedName + WatchVariables[watchIndex][current.Name.Length..];
        }
        Tags[index] = updated;
        return updated;
    }

    public int CountTagReferences(string name)
    {
        var count = 0;
        bool Matches(string operand) => operand.Equals(name, StringComparison.Ordinal)
            || operand.StartsWith(name + ".", StringComparison.Ordinal)
            || operand.StartsWith(name + "[", StringComparison.Ordinal);
        foreach (var block in Blocks)
        foreach (var rung in block.Rungs)
        {
            foreach (var contact in rung.Branches.SelectMany(branch => branch.Contacts))
            {
                if (Matches(contact.Variable)) count++;
                if (contact.IsComparison && Matches(contact.RightOperand)) count++;
            }
            if ((rung.IsTimer || rung.IsTimerReset) && Matches(rung.TimerVariable)) count++;
            else if ((rung.IsCounter || rung.IsCounterReset || rung.IsCounterLoad) && Matches(rung.CounterVariable)) count++;
            else if (rung.IsNumericOperation)
            {
                if (Matches(rung.NumericSourceA)) count++;
                if (LadderNumericOperationRules.RequiresSourceB(rung.NumericOperationKind) && Matches(rung.NumericSourceB)) count++;
                if (LadderNumericOperationRules.RequiresSourceC(rung.NumericOperationKind) && Matches(rung.NumericSourceC)) count++;
                if (Matches(rung.NumericDestination)) count++;
            }
            else if (!rung.IsCall && !rung.IsReturn && !rung.IsJump && !rung.IsLabel && Matches(rung.CoilVariable)) count++;
        }
        return count;
    }

    public bool TryRemoveTag(string name, out int referenceCount)
    {
        referenceCount = CountTagReferences(name);
        if (referenceCount > 0) return false;
        var index = Tags.FindIndex(tag => tag.Name.Equals(name, StringComparison.Ordinal));
        if (index < 0) return false;
        Tags.RemoveAt(index);
        WatchVariables.RemoveAll(item => item.Equals(name, StringComparison.Ordinal) || item.StartsWith(name + ".", StringComparison.Ordinal) || item.StartsWith(name + "[", StringComparison.Ordinal));
        return true;
    }

    private void RenameTagReferences(string oldName, string newName)
    {
        string RenameOperand(string operand)
        {
            if (operand.Equals(oldName, StringComparison.Ordinal)) return newName;
            return operand.StartsWith(oldName + ".", StringComparison.Ordinal) || operand.StartsWith(oldName + "[", StringComparison.Ordinal)
                ? newName + operand[oldName.Length..]
                : operand;
        }
        foreach (var block in Blocks)
        foreach (var rung in block.Rungs)
        {
            foreach (var branch in rung.Branches)
            for (var index = 0; index < branch.Contacts.Count; index++)
            {
                var contact = branch.Contacts[index];
                branch.Contacts[index] = contact with
                {
                    Variable = RenameOperand(contact.Variable),
                    RightOperand = RenameOperand(contact.RightOperand),
                };
            }
            rung.CoilVariable = RenameOperand(rung.CoilVariable);
            rung.TimerVariable = RenameOperand(rung.TimerVariable);
            rung.CounterVariable = RenameOperand(rung.CounterVariable);
            rung.NumericSourceA = RenameOperand(rung.NumericSourceA);
            rung.NumericSourceB = RenameOperand(rung.NumericSourceB);
            rung.NumericSourceC = RenameOperand(rung.NumericSourceC);
            rung.NumericDestination = RenameOperand(rung.NumericDestination);
        }
    }

    private static object InitialValue(PlcVariableType type) => type switch
    {
        PlcVariableType.Timer => TimeSpan.Zero,
        PlcVariableType.Counter => 0L,
        PlcVariableType.Int => 0L,
        PlcVariableType.DInt => 0L,
        PlcVariableType.Real => 0.0,
        _ => false,
    };

    public static bool TryParseInitialValue(
        PlcVariableType type,
        string text,
        out object value,
        out string error)
    {
        var normalized = text.Trim();
        error = string.Empty;
        switch (type)
        {
            case PlcVariableType.Bool:
                if (normalized.Equals("TRUE", StringComparison.OrdinalIgnoreCase) || normalized == "1")
                {
                    value = true;
                    return true;
                }
                if (normalized.Equals("FALSE", StringComparison.OrdinalIgnoreCase) || normalized == "0")
                {
                    value = false;
                    return true;
                }
                error = "BOOL initial value must be TRUE, FALSE, 1, or 0.";
                break;
            case PlcVariableType.Int:
                if (short.TryParse(normalized, System.Globalization.NumberStyles.Integer,
                        System.Globalization.CultureInfo.InvariantCulture, out var intValue))
                {
                    value = (long)intValue;
                    return true;
                }
                error = $"INT initial value must be an integer from {short.MinValue} to {short.MaxValue}.";
                break;
            case PlcVariableType.DInt:
                if (int.TryParse(normalized, System.Globalization.NumberStyles.Integer,
                        System.Globalization.CultureInfo.InvariantCulture, out var dIntValue))
                {
                    value = (long)dIntValue;
                    return true;
                }
                error = $"DINT initial value must be an integer from {int.MinValue} to {int.MaxValue}.";
                break;
            case PlcVariableType.Real:
                if (double.TryParse(normalized, System.Globalization.NumberStyles.Float,
                        System.Globalization.CultureInfo.InvariantCulture, out var realValue)
                    && double.IsFinite(realValue))
                {
                    value = realValue;
                    return true;
                }
                error = "REAL initial value must be a finite invariant-culture number.";
                break;
            case PlcVariableType.Timer:
            case PlcVariableType.Counter:
                value = type == PlcVariableType.Timer ? TimeSpan.Zero : 0L;
                return true;
            default:
                error = $"Unsupported tag type '{type}'.";
                break;
        }
        value = InitialValue(type);
        return false;
    }

    private static void ValidateInitialValue(PlcVariableType type, object value)
    {
        var valid = type switch
        {
            PlcVariableType.Bool => value is bool,
            PlcVariableType.Int => value is long intValue && intValue is >= short.MinValue and <= short.MaxValue,
            PlcVariableType.DInt => value is long dIntValue && dIntValue is >= int.MinValue and <= int.MaxValue,
            PlcVariableType.Real => value is double realValue && double.IsFinite(realValue),
            PlcVariableType.Timer => value is TimeSpan,
            PlcVariableType.Counter => value is long,
            _ => false,
        };
        if (!valid) throw new InvalidOperationException($"Invalid {type.ToString().ToUpperInvariant()} initial value '{value}'.");
    }

    public EditableRung AddRung(string label, string coilVariable)
    {
        var rung = new EditableRung(NewId("rung"), label, coilVariable);
        rung.Branches.Add(new EditableBranch(NewId("branch")));
        Rungs.Add(rung);
        return rung;
    }

    public EditableRung AddTimerRung(
        string label,
        string timerVariable,
        TimeSpan preset,
        LadderTimerKind kind = LadderTimerKind.OnDelay)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsTimer = true;
        rung.TimerVariable = timerVariable;
        rung.TimerPreset = preset;
        rung.TimerKind = kind;
        return rung;
    }

    public EditableRung AddTimerResetRung(string label, string timerVariable)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsTimerReset = true;
        rung.TimerVariable = timerVariable;
        return rung;
    }

    public EditableRung AddCounterRung(
        string label,
        string counterVariable,
        long preset,
        bool reset = false,
        LadderCounterKind kind = LadderCounterKind.CountUp,
        bool load = false)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsCounter = !reset && !load;
        rung.IsCounterReset = reset;
        rung.IsCounterLoad = load;
        rung.CounterKind = kind;
        rung.CounterVariable = counterVariable;
        rung.CounterPreset = preset;
        return rung;
    }

    public EditableRung AddNumericOperationRung(
        string label,
        LadderNumericOperationKind kind,
        string sourceA,
        string sourceB,
        string destination,
        string sourceC = "0")
    {
        var rung = AddRung(label, string.Empty);
        rung.IsNumericOperation = true;
        rung.NumericOperationKind = kind;
        rung.NumericSourceA = sourceA;
        rung.NumericSourceB = sourceB;
        rung.NumericSourceC = sourceC;
        rung.NumericDestination = destination;
        return rung;
    }

    public EditableRung AddCallRung(string label, string targetBlock)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsCall = true;
        rung.CallTarget = targetBlock;
        return rung;
    }

    public EditableRung AddReturnRung(string label)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsReturn = true;
        return rung;
    }

    public EditableRung AddJumpRung(string label, string targetLabel)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsJump = true;
        rung.ProgramControlLabel = targetLabel.Trim();
        return rung;
    }

    public EditableRung AddLabelRung(string label, string name)
    {
        var rung = AddRung(label, string.Empty);
        rung.IsLabel = true;
        rung.ProgramControlLabel = name.Trim();
        return rung;
    }

    public EditableContact AddContact(int rungIndex, int branchIndex, string variable, bool normallyClosed)
    {
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        return InsertContact(rungIndex, branchIndex, contacts.Count, variable, normallyClosed);
    }

    public EditableContact InsertContact(
        int rungIndex,
        int branchIndex,
        int contactIndex,
        string variable,
        bool normallyClosed)
    {
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        if (contactIndex < 0 || contactIndex > contacts.Count)
            throw new ArgumentOutOfRangeException(nameof(contactIndex));
        var contact = new EditableContact(NewId("contact"), variable, normallyClosed);
        contacts.Insert(contactIndex, contact);
        return contact;
    }

    public EditableContact InsertEdgeContact(
        int rungIndex,
        int branchIndex,
        int contactIndex,
        string variable,
        LadderEdgeMode edgeMode)
    {
        if (edgeMode == LadderEdgeMode.None)
            throw new ArgumentException("An edge contact requires Rising or Falling mode.", nameof(edgeMode));
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        if (contactIndex < 0 || contactIndex > contacts.Count)
            throw new ArgumentOutOfRangeException(nameof(contactIndex));
        var contact = new EditableContact(
            NewId("edge"), variable, false, EdgeMode: edgeMode);
        contacts.Insert(contactIndex, contact);
        return contact;
    }

    public EditableContact AddComparison(
        int rungIndex,
        int branchIndex,
        string leftOperand,
        LadderCompareOperator comparison,
        string rightOperand)
    {
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        return InsertComparison(rungIndex, branchIndex, contacts.Count, leftOperand, comparison, rightOperand);
    }

    public EditableContact InsertComparison(
        int rungIndex,
        int branchIndex,
        int contactIndex,
        string leftOperand,
        LadderCompareOperator comparison,
        string rightOperand)
    {
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        if (contactIndex < 0 || contactIndex > contacts.Count)
            throw new ArgumentOutOfRangeException(nameof(contactIndex));
        var element = new EditableContact(
            NewId("compare"), leftOperand, false, true, comparison, rightOperand.Trim());
        contacts.Insert(contactIndex, element);
        return element;
    }

    public EditableBranch AddParallelBranch(int rungIndex)
    {
        var branch = new EditableBranch(NewId("branch"));
        Rungs[rungIndex].Branches.Add(branch);
        return branch;
    }

    /// <summary>
    /// Captures an isolated rung/network template for the editor clipboard.
    /// Stable IDs are intentionally retained in the template so Copy itself
    /// cannot mutate the document. PasteRung regenerates every identity.
    /// </summary>
    public EditableRung CaptureRung(int rungIndex)
    {
        if (rungIndex < 0 || rungIndex >= Rungs.Count)
            throw new ArgumentOutOfRangeException(nameof(rungIndex));
        return CloneRungTemplate(Rungs[rungIndex], preserveIds: true);
    }

    /// <summary>
    /// Inserts a copied rung/network and assigns new rung, branch, and contact
    /// IDs. This prevents clipboard operations from creating duplicate stable
    /// identities in the compiler/runtime monitor index.
    /// </summary>
    public EditableRung PasteRung(EditableRung template, int insertionIndex)
    {
        ArgumentNullException.ThrowIfNull(template);
        if (insertionIndex < 0 || insertionIndex > Rungs.Count)
            throw new ArgumentOutOfRangeException(nameof(insertionIndex));
        var pasted = CloneRungTemplate(template, preserveIds: false);
        Rungs.Insert(insertionIndex, pasted);
        return pasted;
    }

    /// <summary>Copies one condition instruction into an exact series slot.</summary>
    public EditableContact PasteContact(
        EditableContact template,
        int rungIndex,
        int branchIndex,
        int insertionIndex)
    {
        ArgumentNullException.ThrowIfNull(template);
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        if (insertionIndex < 0 || insertionIndex > contacts.Count)
            throw new ArgumentOutOfRangeException(nameof(insertionIndex));
        var prefix = template.IsComparison
            ? "compare"
            : template.EdgeMode == LadderEdgeMode.None ? "contact" : "edge";
        var pasted = template with { Id = NewId(prefix) };
        contacts.Insert(insertionIndex, pasted);
        return pasted;
    }

    private EditableRung CloneRungTemplate(EditableRung source, bool preserveIds)
    {
        var rung = new EditableRung(preserveIds ? source.Id : NewId("rung"), source.Label, source.CoilVariable)
        {
            CoilMode = source.CoilMode,
            TimerVariable = source.TimerVariable,
            TimerPreset = source.TimerPreset,
            TimerKind = source.TimerKind,
            IsTimer = source.IsTimer,
            IsTimerReset = source.IsTimerReset,
            IsCounter = source.IsCounter,
            IsCounterReset = source.IsCounterReset,
            IsCounterLoad = source.IsCounterLoad,
            CounterKind = source.CounterKind,
            CounterVariable = source.CounterVariable,
            CounterPreset = source.CounterPreset,
            IsNumericOperation = source.IsNumericOperation,
            NumericOperationKind = source.NumericOperationKind,
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
        };
        foreach (var sourceBranch in source.Branches)
        {
            var branch = new EditableBranch(preserveIds ? sourceBranch.Id : NewId("branch"));
            foreach (var sourceContact in sourceBranch.Contacts)
            {
                var prefix = sourceContact.IsComparison
                    ? "compare"
                    : sourceContact.EdgeMode == LadderEdgeMode.None ? "contact" : "edge";
                branch.Contacts.Add(preserveIds
                    ? sourceContact with { }
                    : sourceContact with { Id = NewId(prefix) });
            }
            rung.Branches.Add(branch);
        }
        // Older or hand-built templates must still produce a structurally
        // editable rung even if they contain no explicit branch objects.
        if (rung.Branches.Count == 0)
            rung.Branches.Add(new EditableBranch(preserveIds ? source.Id + "-clipboard-branch" : NewId("branch")));
        return rung;
    }

    public void RemoveParallelBranch(int rungIndex, int branchIndex)
    {
        var branches = Rungs[rungIndex].Branches;
        if (branches.Count <= 1)
            throw new InvalidOperationException("A rung/network must retain at least one branch path.");
        branches.RemoveAt(branchIndex);
    }

    public void RemoveContact(int rungIndex, int branchIndex, int contactIndex) =>
        Rungs[rungIndex].Branches[branchIndex].Contacts.RemoveAt(contactIndex);

    public void ReplaceContact(int rungIndex, int branchIndex, int contactIndex, EditableContact replacement)
    {
        var current = Rungs[rungIndex].Branches[branchIndex].Contacts[contactIndex];
        if (!string.Equals(current.Id, replacement.Id, StringComparison.Ordinal))
            throw new InvalidOperationException("Replacing a contact must preserve its stable element ID.");
        Rungs[rungIndex].Branches[branchIndex].Contacts[contactIndex] = replacement;
    }

    public int MoveContact(int rungIndex, int branchIndex, int contactIndex, int offset)
    {
        var contacts = Rungs[rungIndex].Branches[branchIndex].Contacts;
        if (contactIndex < 0 || contactIndex >= contacts.Count)
            throw new ArgumentOutOfRangeException(nameof(contactIndex));
        var destination = Math.Clamp(contactIndex + offset, 0, contacts.Count - 1);
        if (destination == contactIndex) return contactIndex;
        var contact = contacts[contactIndex];
        contacts.RemoveAt(contactIndex);
        contacts.Insert(destination, contact);
        return destination;
    }

    public void RemoveRung(int rungIndex) => Rungs.RemoveAt(rungIndex);

    public LadderProgram BuildProgram()
    {
        EnsureActiveBlock();
        LadderNetwork BuildNetwork(EditableRung rung)
        {
            var branchNodes = rung.Branches
                .Where(branch => branch.Contacts.Count > 0)
                .Select(branch => new LadderNode(
                    branch.Id,
                    LadderNodeKind.Series,
                    Children: branch.Contacts.Select(contact => new LadderNode(
                        contact.Id,
                        contact.IsComparison ? LadderNodeKind.Compare : LadderNodeKind.Contact,
                        contact.Variable,
                        contact.NormallyClosed,
                        CompareOperator: contact.CompareOperator,
                        RightOperand: contact.RightOperand,
                        EdgeMode: contact.EdgeMode)).ToArray()))
                .ToArray();
            LadderNode logic = branchNodes.Length == 1
                ? branchNodes[0]
                : new LadderNode(NewStableId(rung.Id, "parallel"), LadderNodeKind.Parallel, Children: branchNodes);
            var usesCoil = !rung.IsTimer && !rung.IsTimerReset && !rung.IsCounter && !rung.IsCounterReset && !rung.IsCounterLoad
                && !rung.IsNumericOperation && !rung.IsCall && !rung.IsReturn && !rung.IsJump && !rung.IsLabel;
            return new LadderNetwork(
                rung.Id,
                rung.Label,
                logic,
                usesCoil ? new LadderCoil(NewStableId(rung.Id, "coil"), rung.CoilVariable, rung.CoilMode) : null,
                rung.IsTimer ? new LadderTimer(NewStableId(rung.Id, "timer"), rung.TimerVariable, rung.TimerPreset, rung.TimerKind) : null,
                rung.IsCounter ? new LadderCounter(NewStableId(rung.Id, "counter"), rung.CounterVariable, rung.CounterPreset, rung.CounterKind) : null,
                rung.IsCounterReset ? new LadderCounterReset(NewStableId(rung.Id, "counter-reset"), rung.CounterVariable) : null,
                rung.IsNumericOperation ? new LadderNumericOperation(
                    NewStableId(rung.Id, "numeric"),
                    rung.NumericOperationKind,
                    rung.NumericSourceA,
                    rung.NumericSourceB,
                    rung.NumericDestination,
                    rung.NumericSourceC) : null,
                rung.IsCall ? new LadderCall(NewStableId(rung.Id, "call"), rung.CallTarget) : null,
                rung.IsReturn ? new LadderReturn(NewStableId(rung.Id, "return")) : null,
                rung.IsCounterLoad ? new LadderCounterLoad(NewStableId(rung.Id, "counter-load"), rung.CounterVariable, rung.CounterPreset) : null,
                rung.IsTimerReset ? new LadderTimerReset(NewStableId(rung.Id, "timer-reset"), rung.TimerVariable) : null,
                rung.IsJump ? new LadderJump(NewStableId(rung.Id, "jump"), rung.ProgramControlLabel) : null,
                rung.IsLabel ? new LadderLabel(NewStableId(rung.Id, "label"), rung.ProgramControlLabel) : null);
        }
        var blocks = Blocks.Select(block => new LadderBlock(
            block.Id,
            block.Name,
            block.Rungs.Select(BuildNetwork).ToArray(),
            block.BlockType,
            block.Interface.ToArray())).ToArray();
        var tasks = Tasks.Select(task => new LadderTask(
            task.Id,
            task.Name,
            task.Kind,
            task.Kind == LadderTaskKind.Continuous ? ScanPeriod : task.Period,
            task.Priority,
            task.EntryBlock)).ToArray();
        return new LadderProgram(
            1,
            Id,
            Name,
            "LD",
            ScanPeriod,
            Tags.ToArray(),
            blocks[0].Networks,
            blocks,
            string.IsNullOrWhiteSpace(EntryBlockId) ? blocks[0].Id : EntryBlockId,
            tasks,
            WatchVariables.ToArray());
    }

    public void ReplaceFromProgram(LadderProgram program)
    {
        Id = program.Id;
        Name = program.Name;
        ScanPeriod = program.ScanPeriod;
        Tags.Clear();
        Tags.AddRange(program.Variables);
        WatchVariables.Clear();
        WatchVariables.AddRange(program.WatchVariables ?? []);
        Blocks.Clear();
        Tasks.Clear();
        _nextId = 1;
        var sourceBlocks = program.Blocks is { Count: > 0 }
            ? program.Blocks
            : [new LadderBlock("main", program.Name, program.Networks)];
        foreach (var sourceBlock in sourceBlocks)
        {
            var editableBlock = new EditableBlock(sourceBlock.Id, sourceBlock.Name, sourceBlock.BlockType);
            editableBlock.Interface.AddRange(sourceBlock.Interface ?? []);
            Blocks.Add(editableBlock);
            ActiveBlockIndex = Blocks.Count - 1;
            foreach (var network in sourceBlock.Networks)
            {
                var rung = network.Timer is not null
                    ? AddTimerRung(network.Label, network.Timer.Variable, network.Timer.Preset, network.Timer.Kind)
                    : network.TimerReset is not null
                        ? AddTimerResetRung(network.Label, network.TimerReset.Variable)
                    : network.Counter is not null
                        ? AddCounterRung(network.Label, network.Counter.Variable, network.Counter.Preset)
                        : network.CounterReset is not null
                            ? AddCounterRung(network.Label, network.CounterReset.Variable, 1, reset: true)
                            : network.CounterLoad is not null
                                ? AddCounterRung(network.Label, network.CounterLoad.Variable,
                                    network.CounterLoad.Preset, load: true)
                            : network.NumericOperation is not null
                                ? AddNumericOperationRung(
                                    network.Label,
                                    network.NumericOperation.Kind,
                                    network.NumericOperation.SourceA,
                                    network.NumericOperation.SourceB,
                                    network.NumericOperation.Destination,
                                    network.NumericOperation.SourceC)
                                : network.Call is not null
                                    ? AddCallRung(network.Label, network.Call.TargetBlock)
                                    : network.Return is not null
                                        ? AddReturnRung(network.Label)
                                        : network.Jump is not null
                                            ? AddJumpRung(network.Label, network.Jump.TargetLabel)
                                            : network.LabelInstruction is not null
                                                ? AddLabelRung(network.Label, network.LabelInstruction.Name)
                                        : AddRung(network.Label, network.Coil?.Variable ?? string.Empty);
                if (network.Counter is not null) rung.CounterKind = network.Counter.Kind;
                if (network.Coil is not null) rung.CoilMode = network.Coil.Mode;
                rung.Branches.Clear();
                foreach (var path in ExpandPaths(network.Logic))
                {
                    var branch = AddParallelBranch(Rungs.Count - 1);
                    foreach (var contact in path)
                        branch.Contacts.Add(new EditableContact(
                            contact.Id,
                            contact.Variable,
                            contact.NormallyClosed,
                            contact.Kind == LadderNodeKind.Compare,
                            contact.CompareOperator,
                            contact.RightOperand,
                            contact.EdgeMode));
                }
            }
        }
        EntryBlockId = string.IsNullOrWhiteSpace(program.EntryBlock) ? Blocks[0].Id : program.EntryBlock;
        if (program.Tasks is { Count: > 0 })
        {
            foreach (var task in program.Tasks)
                Tasks.Add(new EditableTask(task.Id, task.Name, task.Kind, task.Period, task.Priority, task.EntryBlock));
        }
        else
        {
            Tasks.Add(new EditableTask(NewId("task"), "MainTask", LadderTaskKind.Continuous, ScanPeriod, 10, EntryBlockId));
        }
        ActiveBlockIndex = Math.Max(0, Blocks.FindIndex(block => block.Id == EntryBlockId));
    }

    public static LadderEditorDocument CreateConveyorExample()
    {
        var document = new LadderEditorDocument { Id = "offline-conveyor", Name = "Conveyor_Main" };
        document.AddTag("start_command", PlcVariableRole.Input, "operator.start");
        document.AddTag("stop_command", PlcVariableRole.Input, "operator.stop");
        document.AddTag("simulated_photoeye", PlcVariableRole.Input, "simulated_photoeye");
        document.AddTag("seal_in", PlcVariableRole.Memory);
        document.AddTag("conveyor_running", PlcVariableRole.Output, "conveyor_running");
        document.WatchVariables.AddRange(document.Tags.Select(tag => tag.Name));

        document.AddRung("Start/Stop seal-in and photoeye permissive", "seal_in");
        document.AddContact(0, 0, "start_command", false);
        document.AddContact(0, 0, "stop_command", true);
        document.AddContact(0, 0, "simulated_photoeye", true);
        document.AddParallelBranch(0);
        document.AddContact(0, 1, "seal_in", false);
        document.AddContact(0, 1, "stop_command", true);
        document.AddContact(0, 1, "simulated_photoeye", true);

        document.AddRung("Conveyor output command", "conveyor_running");
        document.AddContact(1, 0, "seal_in", false);
        document.AddContact(1, 0, "simulated_photoeye", true);
        return document;
    }

    private string NewId(string prefix) => $"{prefix}-{_nextId++}";
    private static string NewStableId(string owner, string suffix) => $"{owner}-{suffix}";

    private static string ValidateUniqueName(string name, IEnumerable<string> existingNames, string objectKind)
    {
        var normalized = name.Trim();
        if (normalized.Length == 0) throw new InvalidOperationException($"{objectKind} name cannot be empty.");
        if (existingNames.Any(existing => existing.Equals(normalized, StringComparison.Ordinal)))
            throw new InvalidOperationException($"{objectKind} name '{normalized}' already exists.");
        return normalized;
    }

    private EditableBlock EnsureActiveBlock()
    {
        if (Blocks.Count == 0) AddBlock(string.IsNullOrWhiteSpace(Name) ? "Main" : Name);
        ActiveBlockIndex = Math.Clamp(ActiveBlockIndex, 0, Blocks.Count - 1);
        return Blocks[ActiveBlockIndex];
    }

    private static IReadOnlyList<IReadOnlyList<LadderNode>> ExpandPaths(LadderNode node)
    {
        if (node.Kind is LadderNodeKind.Contact or LadderNodeKind.Compare) return [[node]];
        var children = node.Children ?? [];
        if (node.Kind == LadderNodeKind.Parallel)
            return children.SelectMany(ExpandPaths).ToArray();
        IReadOnlyList<IReadOnlyList<LadderNode>> paths = [Array.Empty<LadderNode>()];
        foreach (var child in children)
        {
            var childPaths = ExpandPaths(child);
            paths = paths.SelectMany(left => childPaths.Select(right =>
                (IReadOnlyList<LadderNode>)left.Concat(right).ToArray())).ToArray();
        }
        return paths;
    }
}
