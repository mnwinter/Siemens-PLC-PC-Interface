using System;
using System.Linq;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public enum LadderVendorStyle { SiemensTia, RockwellLogix }

/// <summary>Graphical editor surface for a simulator-owned Ladder document.</summary>
public partial class LadderEditorCanvas : Control
{
    private const float FirstRungTop = 55.0f;
    private const float BaseRungHeight = 205.0f;
    private const float BaseRungAdvance = 220.0f;
    private const float MultiBranchGap = 92.0f;
    private const float ContactConductorHalfGap = 20.0f;
    private readonly LadderVendorStyle _style;
    private readonly LadderEditorDocument _document;
    private VirtualControllerSnapshot? _monitorSnapshot;
    public int SelectedRung { get; private set; }
    public int SelectedBranch { get; private set; } = -1;
    public int SelectedContact { get; private set; } = -1;
    public int SelectedInsertionIndex { get; private set; } = -1;
    public bool OutputSelected { get; private set; }
    public bool MonitorActive => _monitorSnapshot is not null;
    public long MonitorScanNumber => _monitorSnapshot?.ScanNumber ?? 0;
    public event Action<int>? RungSelected;
    public event Action<int, int, int, bool>? ElementSelected;
    public event Action<int, int, int>? InsertionPointSelected;
    public event Action<int, int, int, bool>? PropertiesRequested;
    public event Action<int, int, int, bool>? ContextMenuRequested;
    public event Action? CopyRequested;
    public event Action? PasteRequested;
    public event Action? DeleteRequested;
    public event Action<int>? MoveRequested;
    public event Action<string, int, int, int>? InstructionDropRequested;

    public LadderEditorCanvas(LadderVendorStyle style, LadderEditorDocument document)
    {
        _style = style;
        _document = document;
        Name = "GraphicalLadderCanvas";
        CustomMinimumSize = new Vector2(760, 500);
        SizeFlagsHorizontal = SizeFlags.ExpandFill;
        SizeFlagsVertical = SizeFlags.ExpandFill;
        ClipContents = true;
        FocusMode = FocusModeEnum.All;
        MouseDefaultCursorShape = CursorShape.PointingHand;
    }

    public void RefreshDocument()
    {
        CustomMinimumSize = new Vector2(760, Math.Max(500, 76 + TotalRungAdvance()));
        SelectedRung = Math.Clamp(SelectedRung, 0, Math.Max(0, _document.Rungs.Count - 1));
        if (_document.Rungs.Count == 0)
        {
            ClearElementSelection();
        }
        else if (SelectedContact >= 0)
        {
            var rung = _document.Rungs[SelectedRung];
            if (SelectedBranch < 0 || SelectedBranch >= rung.Branches.Count
                || SelectedContact >= rung.Branches[SelectedBranch].Contacts.Count)
                ClearElementSelection();
        }
        else if (SelectedInsertionIndex >= 0)
        {
            var rung = _document.Rungs[SelectedRung];
            if (SelectedBranch < 0 || SelectedBranch >= rung.Branches.Count)
                ClearElementSelection();
            else
                SelectedInsertionIndex = Math.Clamp(
                    SelectedInsertionIndex,
                    0,
                    rung.Branches[SelectedBranch].Contacts.Count);
        }
        QueueRedraw();
    }

    public void SetMonitorSnapshot(VirtualControllerSnapshot? snapshot)
    {
        _monitorSnapshot = snapshot;
        QueueRedraw();
    }

    public bool IsElementEnergized(string id) =>
        _monitorSnapshot?.Elements.TryGetValue(id, out var state) == true && state.Energized;

    public Vector2 GetInsertionPointPosition(int rungIndex, int branchIndex, int insertionIndex)
    {
        if (rungIndex < 0 || rungIndex >= _document.Rungs.Count)
            throw new ArgumentOutOfRangeException(nameof(rungIndex));
        var rung = _document.Rungs[rungIndex];
        if (branchIndex < 0 || branchIndex >= rung.Branches.Count)
            throw new ArgumentOutOfRangeException(nameof(branchIndex));
        var contactCount = rung.Branches[branchIndex].Contacts.Count;
        if (insertionIndex < 0 || insertionIndex > contactCount)
            throw new ArgumentOutOfRangeException(nameof(insertionIndex));
        var rungY = RungTop(rungIndex);
        var logicY = rungY + 102;
        var left = _style == LadderVendorStyle.SiemensTia ? 48.0f : 62.0f;
        var span = Size.X - (_style == LadderVendorStyle.SiemensTia ? 94.0f : 84.0f);
        var branchGap = BranchGap(rung);
        return new Vector2(
            InsertionSlotX(left, span * 0.68f, contactCount, insertionIndex),
            logicY + branchIndex * branchGap);
    }

    public Vector2 GetElementPosition(int rungIndex, int branchIndex, int contactIndex, bool output = false)
    {
        if (rungIndex < 0 || rungIndex >= _document.Rungs.Count)
            throw new ArgumentOutOfRangeException(nameof(rungIndex));
        var rung = _document.Rungs[rungIndex];
        var logicY = RungTop(rungIndex) + 102;
        var left = _style == LadderVendorStyle.SiemensTia ? 48.0f : 62.0f;
        var span = Size.X - (_style == LadderVendorStyle.SiemensTia ? 94.0f : 84.0f);
        if (output) return new Vector2(left + span * 0.86f, logicY);
        if (branchIndex < 0 || branchIndex >= rung.Branches.Count)
            throw new ArgumentOutOfRangeException(nameof(branchIndex));
        var contacts = rung.Branches[branchIndex].Contacts;
        if (contactIndex < 0 || contactIndex >= contacts.Count)
            throw new ArgumentOutOfRangeException(nameof(contactIndex));
        var usable = span * 0.68f;
        return new Vector2(
            left + 36 + usable * (contactIndex + 1) / (contacts.Count + 1),
            logicY + branchIndex * BranchGap(rung));
    }

    public void SelectRung(int index)
    {
        SelectedRung = Math.Clamp(index, 0, Math.Max(0, _document.Rungs.Count - 1));
        ClearElementSelection();
        QueueRedraw();
    }

    public void SelectElement(int rungIndex, int branchIndex, int contactIndex, bool output = false, bool notify = true)
    {
        if (rungIndex < 0 || rungIndex >= _document.Rungs.Count) return;
        if (!output)
        {
            if (branchIndex < 0 || branchIndex >= _document.Rungs[rungIndex].Branches.Count) return;
            if (contactIndex < 0 || contactIndex >= _document.Rungs[rungIndex].Branches[branchIndex].Contacts.Count) return;
        }
        SelectedRung = rungIndex;
        SelectedBranch = output ? -1 : branchIndex;
        SelectedContact = output ? -1 : contactIndex;
        SelectedInsertionIndex = -1;
        OutputSelected = output;
        if (notify)
        {
            RungSelected?.Invoke(rungIndex);
            ElementSelected?.Invoke(rungIndex, SelectedBranch, SelectedContact, output);
        }
        QueueRedraw();
    }

    public void SelectInsertionPoint(
        int rungIndex,
        int branchIndex,
        int insertionIndex,
        bool notify = true)
    {
        if (rungIndex < 0 || rungIndex >= _document.Rungs.Count) return;
        var rung = _document.Rungs[rungIndex];
        if (branchIndex < 0 || branchIndex >= rung.Branches.Count) return;
        if (insertionIndex < 0 || insertionIndex > rung.Branches[branchIndex].Contacts.Count) return;
        SelectedRung = rungIndex;
        SelectedBranch = branchIndex;
        SelectedContact = -1;
        SelectedInsertionIndex = insertionIndex;
        OutputSelected = false;
        if (notify)
        {
            RungSelected?.Invoke(rungIndex);
            InsertionPointSelected?.Invoke(rungIndex, branchIndex, insertionIndex);
        }
        QueueRedraw();
    }

    public void ClearElementSelection()
    {
        SelectedBranch = -1;
        SelectedContact = -1;
        SelectedInsertionIndex = -1;
        OutputSelected = false;
    }

    public bool PreviewInsertionAt(Vector2 position)
    {
        var rungIndex = RungIndexAt(position.Y);
        if (rungIndex < 0) return false;
        if (TryHitElement(rungIndex, position, out var outputBranch, out var outputContact, out var output)
            && output)
        {
            SelectElement(rungIndex, outputBranch, outputContact, output, notify: false);
            return true;
        }
        if (!TryHitInsertionPoint(rungIndex, position, out var branchIndex, out var insertionIndex))
            return false;
        SelectInsertionPoint(rungIndex, branchIndex, insertionIndex, notify: false);
        return true;
    }

    public bool DropInstructionAt(string kind, Vector2 position)
    {
        var rungIndex = RungIndexAt(position.Y);
        if (rungIndex < 0) return false;
        if (TryHitElement(rungIndex, position, out var outputBranch, out var outputContact, out var output)
            && output)
        {
            SelectElement(rungIndex, outputBranch, outputContact, output);
            InstructionDropRequested?.Invoke(kind, rungIndex, outputBranch, -1);
            return true;
        }
        if (!TryHitInsertionPoint(rungIndex, position, out var branchIndex, out var insertionIndex))
            return false;
        SelectInsertionPoint(rungIndex, branchIndex, insertionIndex);
        InstructionDropRequested?.Invoke(kind, rungIndex, branchIndex, insertionIndex);
        return true;
    }

    public override void _GuiInput(InputEvent input)
    {
        // Consume edit keys before Control's directional focus navigation.
        if (input is InputEventKey)
        {
            _ShortcutInput(input);
            return;
        }
        if (input is not InputEventMouseButton { Pressed: true } click
            || click.ButtonIndex is not (MouseButton.Left or MouseButton.Right)) return;
        GrabFocus();
        var index = RungIndexAt(click.Position.Y);
        if (index < 0 || index >= _document.Rungs.Count) return;
        if (TryHitElement(index, click.Position, out var branchIndex, out var contactIndex, out var output))
        {
            SelectElement(index, branchIndex, contactIndex, output);
            if (click.ButtonIndex == MouseButton.Right)
                ContextMenuRequested?.Invoke(index, branchIndex, contactIndex, output);
            else if (click.DoubleClick)
                PropertiesRequested?.Invoke(index, branchIndex, contactIndex, output);
            AcceptEvent();
            return;
        }
        if (click.ButtonIndex == MouseButton.Right)
        {
            SelectedRung = index;
            ClearElementSelection();
            RungSelected?.Invoke(index);
            ContextMenuRequested?.Invoke(index, -1, -1, false);
            QueueRedraw();
            AcceptEvent();
            return;
        }
        if (TryHitInsertionPoint(index, click.Position, out branchIndex, out var insertionIndex))
        {
            SelectInsertionPoint(index, branchIndex, insertionIndex);
            AcceptEvent();
            return;
        }
        SelectedRung = index;
        ClearElementSelection();
        RungSelected?.Invoke(index);
        QueueRedraw();
        AcceptEvent();
    }

    public override void _ShortcutInput(InputEvent input)
    {
        // Shortcut callbacks are global to the viewport, including hidden tabs.
        // Only the surface the user is editing may consume document edit keys.
        if (!IsVisibleInTree() || !HasFocus()) return;
        if (input is not InputEventKey { Pressed: true, Echo: false } key) return;
        if (key.CtrlPressed && key.Keycode == Key.C)
        {
            CopyRequested?.Invoke();
            AcceptEvent();
        }
        else if (key.CtrlPressed && key.Keycode == Key.V)
        {
            PasteRequested?.Invoke();
            AcceptEvent();
        }
        else if (key.Keycode == Key.Delete || key.Keycode == Key.Backspace)
        {
            DeleteRequested?.Invoke();
            AcceptEvent();
        }
        else if (key.Keycode == Key.Left || key.Keycode == Key.Right)
        {
            MoveRequested?.Invoke(key.Keycode == Key.Left ? -1 : 1);
            AcceptEvent();
        }
    }

    private bool TryHitElement(int rungIndex, Vector2 position, out int branchIndex, out int contactIndex, out bool output)
    {
        branchIndex = -1;
        contactIndex = -1;
        output = false;
        var rung = _document.Rungs[rungIndex];
        var rungY = RungTop(rungIndex);
        var logicY = rungY + 102;
        var left = _style == LadderVendorStyle.SiemensTia ? 48.0f : 62.0f;
        var span = Size.X - (_style == LadderVendorStyle.SiemensTia ? 94.0f : 84.0f);
        var outputX = left + span * 0.86f;
        if (new Rect2(outputX - 72, logicY - 48, 144, 96).HasPoint(position))
        {
            output = true;
            return true;
        }
        var branchGap = BranchGap(rung);
        var usable = span * 0.68f;
        for (var currentBranch = 0; currentBranch < rung.Branches.Count; currentBranch++)
        {
            var contacts = rung.Branches[currentBranch].Contacts;
            var branchY = logicY + currentBranch * branchGap;
            for (var currentContact = 0; currentContact < contacts.Count; currentContact++)
            {
                var x = left + 36 + usable * (currentContact + 1) / (contacts.Count + 1);
                var bounds = contacts[currentContact].IsComparison
                    ? new Rect2(x - 64, branchY - 38, 128, 76)
                    : new Rect2(x - 38, branchY - 38, 76, 76);
                if (!bounds.HasPoint(position)) continue;
                branchIndex = currentBranch;
                contactIndex = currentContact;
                return true;
            }
        }
        return false;
    }

    private bool TryHitInsertionPoint(int rungIndex, Vector2 position, out int branchIndex, out int insertionIndex)
    {
        branchIndex = -1;
        insertionIndex = -1;
        var rung = _document.Rungs[rungIndex];
        var rungY = RungTop(rungIndex);
        var logicY = rungY + 102;
        var left = _style == LadderVendorStyle.SiemensTia ? 48.0f : 62.0f;
        var span = Size.X - (_style == LadderVendorStyle.SiemensTia ? 94.0f : 84.0f);
        var branchGap = BranchGap(rung);
        var usable = span * 0.68f;
        for (var currentBranch = 0; currentBranch < rung.Branches.Count; currentBranch++)
        {
            var branchY = logicY + currentBranch * branchGap;
            var contactCount = rung.Branches[currentBranch].Contacts.Count;
            for (var currentInsertion = 0; currentInsertion <= contactCount; currentInsertion++)
            {
                var x = InsertionSlotX(left, usable, contactCount, currentInsertion);
                if (!new Rect2(x - 22, branchY - 24, 44, 48).HasPoint(position)) continue;
                branchIndex = currentBranch;
                insertionIndex = currentInsertion;
                return true;
            }
        }
        return false;
    }

    public Rect2 GetRungBounds(int rungIndex)
    {
        if (rungIndex < 0 || rungIndex >= _document.Rungs.Count)
            throw new ArgumentOutOfRangeException(nameof(rungIndex));
        return new Rect2(0, RungTop(rungIndex), Size.X, RungHeight(_document.Rungs[rungIndex]));
    }

    private float TotalRungAdvance()
    {
        var total = 0.0f;
        foreach (var rung in _document.Rungs) total += RungAdvance(rung);
        return total;
    }

    private float RungTop(int rungIndex)
    {
        var top = FirstRungTop;
        for (var index = 0; index < rungIndex && index < _document.Rungs.Count; index++)
            top += RungAdvance(_document.Rungs[index]);
        return top;
    }

    private int RungIndexAt(float y)
    {
        for (var index = 0; index < _document.Rungs.Count; index++)
        {
            var top = RungTop(index);
            if (y >= top && y < top + RungAdvance(_document.Rungs[index])) return index;
        }
        return -1;
    }

    private static float BranchGap(EditableRung rung) => rung.Branches.Count > 1 ? MultiBranchGap : 0.0f;
    private static float RungHeight(EditableRung rung) =>
        BaseRungHeight + Math.Max(0, rung.Branches.Count - 1) * MultiBranchGap;
    private static float RungAdvance(EditableRung rung) =>
        BaseRungAdvance + Math.Max(0, rung.Branches.Count - 1) * MultiBranchGap;

    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), new Color("f5f6f7"));
        if (_style == LadderVendorStyle.SiemensTia) DrawTia();
        else DrawLogix();
    }

    private void DrawTia()
    {
        DrawRect(new Rect2(0, 0, Size.X, 36), new Color("dfe4e7"));
        var blockName = _document.Blocks.Count > 0 ? _document.Blocks[_document.ActiveBlockIndex].Name : _document.Name;
        DrawString(ThemeDB.FallbackFont, new Vector2(14, 25), $"{blockName}  |  LAD", HorizontalAlignment.Left, -1, 13, new Color("263943"));
        DrawMonitorStatus();
        for (var index = 0; index < _document.Rungs.Count; index++)
        {
            var y = RungTop(index);
            var rungHeight = RungHeight(_document.Rungs[index]);
            var selected = index == SelectedRung;
            DrawRect(new Rect2(22, y, Size.X - 42, rungHeight), selected ? new Color("eef9fb") : new Color("ffffff"));
            DrawRect(new Rect2(22, y, Size.X - 42, 30), selected ? new Color("ccecf2") : new Color("e9edef"));
            DrawRect(new Rect2(22, y, 5, rungHeight), selected ? new Color("0087a8") : new Color("aab6bc"));
            DrawString(ThemeDB.FallbackFont, new Vector2(36, y + 21), $"Network {index + 1}", HorizontalAlignment.Left, -1, 13, new Color("17242c"));
            DrawString(ThemeDB.FallbackFont, new Vector2(130, y + 21), _document.Rungs[index].Label, HorizontalAlignment.Left, -1, 12, new Color("5b6a72"));
            DrawRungLogic(index, _document.Rungs[index], 48, y + 102, Size.X - 94, new Color("203844"));
        }
    }

    private void DrawLogix()
    {
        DrawRect(new Rect2(0, 0, Size.X, 36), new Color("d5d8dd"));
        var blockName = _document.Blocks.Count > 0 ? _document.Blocks[_document.ActiveBlockIndex].Name : _document.Name;
        DrawString(ThemeDB.FallbackFont, new Vector2(14, 25), $"MainProgram — {blockName}  [LAD]", HorizontalAlignment.Left, -1, 13, new Color("20252b"));
        DrawMonitorStatus();
        DrawRect(new Rect2(0, 36, 44, Size.Y - 36), new Color("d9dce1"));
        for (var index = 0; index < _document.Rungs.Count; index++)
        {
            var y = RungTop(index);
            var rungHeight = RungHeight(_document.Rungs[index]);
            var selected = index == SelectedRung;
            DrawRect(new Rect2(44, y, Size.X - 44, rungHeight), selected ? new Color("f1f4fb") : new Color("ffffff"));
            DrawRect(new Rect2(44, y, Size.X - 44, 32), selected ? new Color("dce5f7") : new Color("eceef1"));
            DrawRect(new Rect2(40, y, 4, rungHeight), selected ? new Color("335ea8") : new Color("808996"));
            DrawString(ThemeDB.FallbackFont, new Vector2(14, y + 22), index.ToString(), HorizontalAlignment.Left, -1, 13, new Color("26344a"));
            DrawString(ThemeDB.FallbackFont, new Vector2(56, y + 22), _document.Rungs[index].Label, HorizontalAlignment.Left, -1, 12, new Color("4b5664"));
            DrawRungLogic(index, _document.Rungs[index], 62, y + 102, Size.X - 84, new Color("242d69"));
        }
        DrawString(ThemeDB.FallbackFont, new Vector2(8, FirstRungTop + TotalRungAdvance() + 13), "(End)", HorizontalAlignment.Left, -1, 12, new Color("304f9e"));
    }

    private void DrawRungLogic(int rungIndex, EditableRung rung, float left, float y, float span, Color wire)
    {
        var live = _style == LadderVendorStyle.SiemensTia ? new Color("00a651") : new Color("27a745");
        var networkExecuted = _monitorSnapshot?.Elements.ContainsKey(rung.Id) == true;
        var right = left + span;
        var outputX = left + span * 0.86f;
        var outputGap = OutputConductorHalfGap(rung);
        var outputId = OutputElementId(rung);
        var outputPowered = IsElementEnergized(outputId);
        var branches = Math.Max(1, rung.Branches.Count);
        var branchGap = branches > 1 ? MultiBranchGap : 0.0f;
        var railBottom = y + Math.Max(34, branchGap * (branches - 1) + 34);
        var branchJoinX = outputX - outputGap - 30.0f;
        DrawLine(new Vector2(left, y - 34), new Vector2(left, railBottom), wire, 3);
        // All parallel condition paths rejoin before the single output
        // instruction. Extending the right rail down every branch makes the
        // lower path look like it bypasses the output entirely.
        DrawLine(new Vector2(right, y - 34), new Vector2(right, y + 34), wire, 3);
        if (networkExecuted)
            DrawLine(new Vector2(left, y - 34), new Vector2(left, railBottom), live, 4);
        for (var branchIndex = 0; branchIndex < branches; branchIndex++)
        {
            var branchY = y + branchIndex * branchGap;
            var branch = rung.Branches.Count > branchIndex ? rung.Branches[branchIndex] : null;
            var contacts = branch?.Contacts.Count ?? 0;
            var usable = span * 0.68f;
            if (rungIndex == SelectedRung && branchIndex == SelectedBranch && SelectedInsertionIndex >= 0)
            {
                var insertionX = InsertionSlotX(left, usable, contacts, SelectedInsertionIndex);
                var insertionColor = _style == LadderVendorStyle.SiemensTia
                    ? new Color("0087a8")
                    : new Color("d5222b");
                DrawLine(new Vector2(insertionX, branchY - 25), new Vector2(insertionX, branchY + 25), insertionColor, 3);
                DrawCircle(new Vector2(insertionX, branchY), 9, new Color("ffffff"));
                DrawCircle(new Vector2(insertionX, branchY), 9, insertionColor, false, 2);
                DrawLine(new Vector2(insertionX - 5, branchY), new Vector2(insertionX + 5, branchY), insertionColor, 2);
                DrawLine(new Vector2(insertionX, branchY - 5), new Vector2(insertionX, branchY + 5), insertionColor, 2);
            }
            var flow = networkExecuted;
            var previousX = left;
            for (var contactIndex = 0; contactIndex < contacts; contactIndex++)
            {
                var x = left + 36 + usable * (contactIndex + 1) / (contacts + 1);
                var contact = branch!.Contacts[contactIndex];
                var contactGap = contact.IsComparison ? 58.0f : ContactConductorHalfGap;
                DrawConductor(previousX, x - contactGap, branchY, wire, 2);
                if (flow) DrawConductor(previousX, x - contactGap, branchY, live, 4);
                var contactPowered = flow && IsElementEnergized(contact.Id);
                var elementColor = contactPowered ? live : wire;
                if (contact.IsComparison)
                {
                    DrawRect(new Rect2(x - 58, branchY - 32, 116, 64), new Color("e3e6eb"));
                    DrawRect(new Rect2(x - 58, branchY - 32, 116, 64), elementColor, false, contactPowered ? 4 : 2);
                    var symbol = contact.CompareOperator switch
                    {
                        LadderCompareOperator.Equal => "==",
                        LadderCompareOperator.NotEqual => "<>",
                        LadderCompareOperator.GreaterThan => ">",
                        LadderCompareOperator.GreaterOrEqual => ">=",
                        LadderCompareOperator.LessThan => "<",
                        LadderCompareOperator.LessOrEqual => "<=",
                        _ => "?",
                    };
                    DrawString(ThemeDB.FallbackFont, new Vector2(x - 50, branchY - 10), $"CMP {symbol}", HorizontalAlignment.Left, 100, 12, new Color("17242c"));
                    DrawString(ThemeDB.FallbackFont, new Vector2(x - 50, branchY + 12), $"{contact.Variable} , {contact.RightOperand}", HorizontalAlignment.Left, 100, 10, new Color("536771"));
                }
                else
                {
                    DrawContact(x, branchY, contact.NormallyClosed, elementColor);
                    if (contact.EdgeMode != LadderEdgeMode.None)
                    {
                        var edgeLabel = _style == LadderVendorStyle.SiemensTia
                            ? contact.EdgeMode == LadderEdgeMode.Rising ? "P" : "N"
                            : contact.EdgeMode == LadderEdgeMode.Rising ? "ONS" : "OSF";
                        DrawString(ThemeDB.FallbackFont, new Vector2(x - 24, branchY + 7), edgeLabel,
                            HorizontalAlignment.Center, 48, 11, elementColor);
                    }
                    DrawContactOperand(x, branchY, contact.Variable, Math.Min(136, usable / (contacts + 1) - 8));
                    var contactLabel = contact.EdgeMode switch
                    {
                        LadderEdgeMode.Rising => _style == LadderVendorStyle.SiemensTia ? "P EDGE" : "XIC+ONS",
                        LadderEdgeMode.Falling => _style == LadderVendorStyle.SiemensTia ? "N EDGE" : "XIO+ONS/OSF",
                        _ => _style == LadderVendorStyle.SiemensTia
                            ? contact.NormallyClosed ? "NC" : "NO"
                            : contact.NormallyClosed ? "XIO" : "XIC",
                    };
                    DrawString(ThemeDB.FallbackFont, new Vector2(x - 44, branchY + 39), contactLabel,
                        HorizontalAlignment.Center, 88, 11, new Color("263943"));
                }
                flow = contactPowered;
                previousX = x + contactGap;
                if (rungIndex == SelectedRung && branchIndex == SelectedBranch && contactIndex == SelectedContact)
                {
                    var selectedBounds = contact.IsComparison
                        ? new Rect2(x - 64, branchY - 38, 128, 76)
                        : new Rect2(x - 38, branchY - 38, 76, 76);
                    DrawRect(selectedBounds, _style == LadderVendorStyle.SiemensTia ? new Color("0087a8") : new Color("d5222b"), false, 3);
                }
            }
            if (branches == 1)
            {
                DrawConductor(previousX, outputX - outputGap, branchY, wire, 2);
                DrawConductor(outputX + outputGap, right, branchY, wire, 2);
                if (flow) DrawConductor(previousX, outputX - outputGap, branchY, live, 4);
                if (outputPowered) DrawConductor(outputX + outputGap, right, branchY, live, 4);
            }
            else
            {
                DrawConductor(previousX, branchJoinX, branchY, wire, 2);
                if (flow) DrawConductor(previousX, branchJoinX, branchY, live, 4);
            }
        }
        if (branches > 1)
        {
            var bottomBranchY = y + (branches - 1) * branchGap;
            DrawLine(new Vector2(branchJoinX, y), new Vector2(branchJoinX, bottomBranchY), wire, 2);
            DrawConductor(branchJoinX, outputX - outputGap, y, wire, 2);
            DrawConductor(outputX + outputGap, right, y, wire, 2);
            if (outputPowered)
            {
                DrawLine(new Vector2(branchJoinX, y), new Vector2(branchJoinX, bottomBranchY), live, 4);
                DrawConductor(branchJoinX, outputX - outputGap, y, live, 4);
                DrawConductor(outputX + outputGap, right, y, live, 4);
            }
        }
        var outputColor = outputPowered ? live : wire;
        if (outputPowered)
            DrawLine(new Vector2(right, y - 34), new Vector2(right, y + 34), live, 4);
        if (rung.IsTimer)
        {
            LadderTimerState? timerState = null;
            if (_monitorSnapshot is not null
                && _monitorSnapshot.Timers.TryGetValue(rung.TimerVariable, out var monitorTimer))
                timerState = monitorTimer;
            var hasTimerState = timerState is not null;
            var timerHeight = hasTimerState ? 98.0f : 76.0f;
            DrawRect(new Rect2(outputX - 58, y - timerHeight * 0.5f, 116, timerHeight), new Color("e3e6eb"));
            DrawRect(new Rect2(outputX - 58, y - timerHeight * 0.5f, 116, timerHeight), outputColor, false, outputPowered ? 4 : 2);
            var instruction = rung.TimerKind switch
            {
                LadderTimerKind.OffDelay => "TOF",
                LadderTimerKind.Pulse => "TP",
                LadderTimerKind.RetentiveOnDelay => _style == LadderVendorStyle.SiemensTia ? "TONR" : "RTO",
                _ => "TON",
            };
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y - 18), instruction, HorizontalAlignment.Left, 100, 14, new Color("17242c"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y + 1), rung.TimerVariable, HorizontalAlignment.Left, 100, 11, new Color("17242c"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y + 22), $"PT {rung.TimerPreset.TotalMilliseconds:0} ms", HorizontalAlignment.Left, 100, 10, new Color("536771"));
            if (hasTimerState)
            {
                var elapsed = timerState!.Accumulated.TotalMilliseconds;
                var state = timerState.Done ? "Q/DN" : timerState.Timing ? "TIMING" : "IDLE";
                DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y + 38),
                    $"ET {elapsed:0} ms · {state}", HorizontalAlignment.Left, 108, 9,
                    timerState.Timing ? new Color("0087a8") : new Color("536771"));
            }
        }
        else if (rung.IsTimerReset)
        {
            DrawRect(new Rect2(outputX - 58, y - 34, 116, 68), new Color("e3e6eb"));
            DrawRect(new Rect2(outputX - 58, y - 34, 116, 68), outputColor, false, outputPowered ? 4 : 2);
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y - 10),
                _style == LadderVendorStyle.SiemensTia ? "RT" : "RES",
                HorizontalAlignment.Left, 100, 14, new Color("17242c"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y + 14), rung.TimerVariable,
                HorizontalAlignment.Left, 100, 11, new Color("17242c"));
        }
        else if (rung.IsCounter || rung.IsCounterReset || rung.IsCounterLoad)
        {
            DrawRect(new Rect2(outputX - 58, y - 38, 116, 76), new Color("e3e6eb"));
            DrawRect(new Rect2(outputX - 58, y - 38, 116, 76), outputColor, false, outputPowered ? 4 : 2);
            var instruction = rung.IsCounterReset
                ? "RES"
                : rung.IsCounterLoad
                    ? "LOAD"
                    : rung.CounterKind == LadderCounterKind.CountDown ? "CTD" : "CTU";
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y - 18), instruction, HorizontalAlignment.Left, 100, 14, new Color("17242c"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y + 1), rung.CounterVariable, HorizontalAlignment.Left, 100, 11, new Color("17242c"));
            if (rung.IsCounter || rung.IsCounterLoad)
                DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 50, y + 22), $"PV {rung.CounterPreset}", HorizontalAlignment.Left, 100, 10, new Color("536771"));
        }
        else if (rung.IsNumericOperation)
        {
            DrawRect(new Rect2(outputX - 66, y - 42, 132, 84), new Color("e3e6eb"));
            DrawRect(new Rect2(outputX - 66, y - 42, 132, 84), outputColor, false, outputPowered ? 4 : 2);
            var mnemonic = rung.NumericOperationKind switch
            {
                LadderNumericOperationKind.Move => "MOV",
                LadderNumericOperationKind.Add => "ADD",
                LadderNumericOperationKind.Subtract => "SUB",
                LadderNumericOperationKind.Multiply => "MUL",
                LadderNumericOperationKind.Divide => "DIV",
                LadderNumericOperationKind.Modulo => "MOD",
                LadderNumericOperationKind.Absolute => "ABS",
                LadderNumericOperationKind.Negate => "NEG",
                LadderNumericOperationKind.SquareRoot => "SQRT",
                LadderNumericOperationKind.Exponentiate => "EXPT",
                LadderNumericOperationKind.NaturalLog => "LN",
                LadderNumericOperationKind.Sine => "SIN",
                LadderNumericOperationKind.Cosine => "COS",
                LadderNumericOperationKind.Tangent => "TAN",
                LadderNumericOperationKind.ArcSine => "ASIN",
                LadderNumericOperationKind.ArcCosine => "ACOS",
                LadderNumericOperationKind.ArcTangent => "ATAN",
                LadderNumericOperationKind.Truncate => "TRUNC",
                LadderNumericOperationKind.Normalize => _style == LadderVendorStyle.SiemensTia ? "NORM_X" : "CPT NORM",
                LadderNumericOperationKind.Scale => _style == LadderVendorStyle.SiemensTia ? "SCALE_X" : "CPT SCALE",
                LadderNumericOperationKind.Convert => _style == LadderVendorStyle.SiemensTia ? "CONVERT" : "MOV CONV",
                LadderNumericOperationKind.Round => _style == LadderVendorStyle.SiemensTia ? "ROUND" : "CPT ROUND",
                LadderNumericOperationKind.Ceiling => _style == LadderVendorStyle.SiemensTia ? "CEIL" : "CPT CEIL",
                LadderNumericOperationKind.Floor => _style == LadderVendorStyle.SiemensTia ? "FLOOR" : "CPT FLOOR",
                _ => "NUM",
            };
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y - 22), mnemonic, HorizontalAlignment.Left, 116, 14, new Color("17242c"));
            var sources = LadderNumericOperationRules.RequiresSourceC(rung.NumericOperationKind)
                ? $"{rung.NumericSourceA}, {rung.NumericSourceB}, {rung.NumericSourceC}"
                : !LadderNumericOperationRules.RequiresSourceB(rung.NumericOperationKind)
                    ? rung.NumericSourceA
                    : $"{rung.NumericSourceA}, {rung.NumericSourceB}";
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y), sources, HorizontalAlignment.Left, 116, 10, new Color("536771"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y + 23), $"OUT {rung.NumericDestination}", HorizontalAlignment.Left, 116, 10, new Color("17242c"));
        }
        else if (rung.IsCall)
        {
            DrawRect(new Rect2(outputX - 66, y - 34, 132, 68), new Color("e3e6eb"));
            DrawRect(new Rect2(outputX - 66, y - 34, 132, 68), outputColor, false, outputPowered ? 4 : 2);
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y - 10),
                _style == LadderVendorStyle.SiemensTia ? "CALL" : "JSR",
                HorizontalAlignment.Left, 116, 14, new Color("17242c"));
            // Stable IDs belong to serialization/execution; operators need the
            // current block name, including after a rename. Keep unresolved IDs
            // visible so invalid work in progress remains diagnosable.
            var targetName = _document.Blocks.Find(block => block.Id == rung.CallTarget)?.Name ?? rung.CallTarget;
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y + 14), targetName,
                HorizontalAlignment.Left, 116, 10, new Color("536771"));
        }
        else if (rung.IsReturn)
        {
            DrawRect(new Rect2(outputX - 66, y - 30, 132, 60), new Color("e3e6eb"));
            DrawRect(new Rect2(outputX - 66, y - 30, 132, 60), outputColor, false, outputPowered ? 4 : 2);
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y + 5),
                _style == LadderVendorStyle.SiemensTia ? "RETURN" : "RET",
                HorizontalAlignment.Left, 116, 14, new Color("17242c"));
        }
        else if (rung.IsJump || rung.IsLabel)
        {
            var fill = rung.IsLabel ? new Color("fff4ce") : new Color("e3e6eb");
            var border = rung.IsLabel ? wire : outputColor;
            DrawRect(new Rect2(outputX - 66, y - 34, 132, 68), fill);
            DrawRect(new Rect2(outputX - 66, y - 34, 132, 68), border, false,
                rung.IsJump && outputPowered ? 4 : 2);
            var mnemonic = rung.IsJump
                ? "JMP"
                : _style == LadderVendorStyle.SiemensTia ? "LABEL" : "LBL";
            if (rung.IsLabel)
                DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y - 20),
                    "DESTINATION", HorizontalAlignment.Left, 116, 9, new Color("7a5a00"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y + (rung.IsLabel ? 0 : -10)),
                mnemonic, HorizontalAlignment.Left, 116, 14, new Color("17242c"));
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 58, y + (rung.IsLabel ? 21 : 14)),
                rung.ProgramControlLabel, HorizontalAlignment.Left, 116, 10, new Color("536771"));
        }
        else
        {
            var marker = rung.CoilMode switch
            {
                LadderCoilMode.Set => _style == LadderVendorStyle.SiemensTia ? "S" : "L",
                LadderCoilMode.Reset => _style == LadderVendorStyle.SiemensTia ? "R" : "U",
                _ => string.Empty,
            };
            DrawCoil(outputX, y, outputColor, marker);
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 80, y - 27), rung.CoilVariable,
                HorizontalAlignment.Center, 160, 12, new Color("17242c"));
            var caption = rung.CoilMode switch
            {
                LadderCoilMode.Set => _style == LadderVendorStyle.SiemensTia ? "SET" : "OTL",
                LadderCoilMode.Reset => _style == LadderVendorStyle.SiemensTia ? "RESET" : "OTU",
                _ => _style == LadderVendorStyle.SiemensTia ? "=" : "OTE",
            };
            // Keep the instruction mnemonic readable at high-resolution desktop
            // scales; it is operational context, not decorative metadata.
            DrawString(ThemeDB.FallbackFont, new Vector2(outputX - 32, y + 39), caption,
                HorizontalAlignment.Center, 64, 11, new Color("263943"));
        }
        if (rungIndex == SelectedRung && OutputSelected)
            DrawRect(new Rect2(outputX - 72, y - 48, 144, 96),
                _style == LadderVendorStyle.SiemensTia ? new Color("0087a8") : new Color("d5222b"), false, 3);
    }

    private void DrawMonitorStatus()
    {
        var text = _monitorSnapshot is null
            ? "OFFLINE EDIT"
            : $"MONITOR · {_monitorSnapshot.State.ToString().ToUpperInvariant()} · SCAN {_monitorSnapshot.ScanNumber}";
        var color = _monitorSnapshot is null
            ? new Color("6a7d86")
            : _monitorSnapshot.State == VirtualControllerState.Running
                ? new Color("18864b")
                : new Color("b36c16");
        DrawString(ThemeDB.FallbackFont, new Vector2(Math.Max(360, Size.X - 255), 25), text,
            HorizontalAlignment.Right, 240, 11, color);
    }

    private static string OutputElementId(EditableRung rung) => rung.IsTimer
        ? $"{rung.Id}-timer"
        : rung.IsTimerReset
            ? $"{rung.Id}-timer-reset"
        : rung.IsCounter
            ? $"{rung.Id}-counter"
            : rung.IsCounterReset
                ? $"{rung.Id}-counter-reset"
                : rung.IsCounterLoad
                    ? $"{rung.Id}-counter-load"
                    : rung.IsNumericOperation
                        ? $"{rung.Id}-numeric"
                        : rung.IsCall
                            ? $"{rung.Id}-call"
                            : rung.IsReturn
                                ? $"{rung.Id}-return"
                                : rung.IsJump
                                    ? $"{rung.Id}-jump"
                                    : rung.IsLabel
                                        ? $"{rung.Id}-label"
                                : $"{rung.Id}-coil";

    private static float InsertionSlotX(float left, float usable, int contactCount, int insertionIndex) =>
        left + 36 + usable * (insertionIndex + 0.5f) / (contactCount + 1.0f);

    private static float OutputConductorHalfGap(EditableRung rung) =>
        rung.IsNumericOperation || rung.IsCall || rung.IsReturn || rung.IsJump || rung.IsLabel ? 66.0f
        : rung.IsTimer || rung.IsTimerReset || rung.IsCounter || rung.IsCounterReset || rung.IsCounterLoad ? 58.0f
        : 32.0f;

    private void DrawConductor(float startX, float endX, float y, Color color, float width)
    {
        if (endX <= startX) return;
        DrawLine(new Vector2(startX, y), new Vector2(endX, y), color, width);
    }

    private void DrawContactOperand(float x, float y, string operand, float width)
    {
        width = Math.Max(1, width);
        var font = ThemeDB.FallbackFont;
        string[] lines = [operand];
        if (font.GetStringSize(operand, HorizontalAlignment.Left, -1, 12).X > width)
        {
            // Keep member identity intact: clipping "temperature_valid" to
            // "temperature" would display a different declared symbol.
            var separator = operand.LastIndexOf('.');
            if (separator > 0 && separator < operand.Length - 1)
                lines = [operand[..(separator + 1)], operand[(separator + 1)..]];
            // At narrow contact strides a member alone may exceed the cell.
            // Prefer two complete balanced lines at a readable 9pt minimum.
            if (lines.Length == 1 || lines.Any(line => font.GetStringSize(line, HorizontalAlignment.Left, -1, 9).X > width))
            {
                var split = Enumerable.Range(1, Math.Max(0, operand.Length - 1))
                    .OrderBy(index => Math.Max(font.GetStringSize(operand[..index], HorizontalAlignment.Left, -1, 9).X,
                        font.GetStringSize(operand[index..], HorizontalAlignment.Left, -1, 9).X)).FirstOrDefault();
                if (split > 0) lines = [operand[..split], operand[split..]];
            }
        }
        for (var index = 0; index < lines.Length; index++)
        {
            var fontSize = 12;
            while (fontSize > 9 && font.GetStringSize(lines[index], HorizontalAlignment.Left, -1, fontSize).X > width)
                fontSize--;
            var text = lines[index];
            if (font.GetStringSize(text, HorizontalAlignment.Left, -1, fontSize).X > width)
            {
                // Explicit omission is preferable to displaying a clipped,
                // different symbol or silently shrinking it to one pixel.
                while (text.Length > 0 && font.GetStringSize(text + "…", HorizontalAlignment.Left, -1, fontSize).X > width)
                    text = text[..^1];
                text += "…";
            }
            DrawString(font, new Vector2(x - width / 2, y - 27 - (lines.Length - 1 - index) * 14), text,
                HorizontalAlignment.Center, width, fontSize, new Color("17242c"));
        }
    }

    private void DrawContact(float x, float y, bool normallyClosed, Color color)
    {
        DrawLine(new Vector2(x - 13, y - 18), new Vector2(x - 13, y + 18), color, 3);
        DrawLine(new Vector2(x + 13, y - 18), new Vector2(x + 13, y + 18), color, 3);
        if (normallyClosed) DrawLine(new Vector2(x - 18, y + 22), new Vector2(x + 18, y - 22), color, 2);
    }

    private void DrawCoil(float x, float y, Color color, string marker)
    {
        // IEC/TIA coil notation is two open parentheses, not one closed oval.
        // The left arc bulges left and the right arc bulges right, leaving a
        // visible gap for the assignment/set/reset marker.
        DrawArc(new Vector2(x - 9, y), 18, MathF.PI / 2, MathF.PI * 1.5f, 18, color, 3);
        DrawArc(new Vector2(x + 9, y), 18, -MathF.PI / 2, MathF.PI / 2, 18, color, 3);
        if (!string.IsNullOrEmpty(marker))
            DrawString(ThemeDB.FallbackFont, new Vector2(x - 12, y + 6), marker,
                HorizontalAlignment.Center, 24, 13, color);
    }
}
