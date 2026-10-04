using System;
using System.IO;
using System.Linq;
using Godot;
using RungProof.Next.Workspace;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyWorkspaceDirtyUndo()
    {
        var original = CreateWorkspaceDocument();
        var originalBaseline = _workspaceSavedSnapshotJson;
        var path = ProjectSettings.GlobalizePath($"res://.tools/workspace-baseline-review-{Guid.NewGuid():N}.json");
        try
        {
            PlaceAsset(_candidateCatalog!.Assets.First(item => item.Id == "material-handling.belt-conveyor.600x6000.v1"));
            var editedDirty = _simulatorShell!.IsWorkspaceDirty;
            UndoWorkspace();
            var undoClean = !_simulatorShell.IsWorkspaceDirty;
            RedoWorkspace();
            var redoDirty = _simulatorShell.IsWorkspaceDirty;
            SaveWorkspaceToPath(path);
            var savedClean = !_simulatorShell.IsWorkspaceDirty && File.Exists(path);
            PlaceAsset(_candidateCatalog.Assets.First(item => item.Id == "sensing.photoelectric.through-beam.v1"));
            var savedEditDirty = _simulatorShell.IsWorkspaceDirty;
            UndoWorkspace();
            var savedUndoClean = !_simulatorShell.IsWorkspaceDirty;
            RedoWorkspace();
            var savedRedoDirty = _simulatorShell.IsWorkspaceDirty;
            var passed = editedDirty && undoClean && redoDirty && savedClean && savedEditDirty && savedUndoClean && savedRedoDirty;
            GD.Print($"WORKSPACE_DIRTY_VERIFY {(passed ? "PASS" : "FAIL")} edited={editedDirty} undoClean={undoClean} redoDirty={redoDirty} savedClean={savedClean} savedEdit={savedEditDirty} savedUndo={savedUndoClean} savedRedo={savedRedoDirty}");
            if (!passed) throw new InvalidOperationException("Workspace dirty state does not reflect Undo/Redo to its saved baseline.");
        }
        finally
        {
            ApplyWorkspaceSnapshot(original);
            _undoHistory.Clear();
            _redoHistory.Clear();
            _workspaceSavedSnapshotJson = originalBaseline;
            RefreshWorkspaceDirty();
            if (File.Exists(path)) File.Delete(path);
        }
    }

    private static void VerifyWorkspaceWriteFailure(WorkspaceDocument document)
    {
        // Windows file sharing blocks replacement while this reader owns the
        // destination. Only this verifier's uniquely named disposable file is used.
        if (!OperatingSystem.IsWindows()) return;
        var path = ProjectSettings.GlobalizePath($"res://.tools/workspace-write-review-{Guid.NewGuid():N}.json");
        try
        {
            WorkspaceRepository.Save(document, path);
            var original = File.ReadAllText(path);
            var updated = document with { Placements = document.Placements.Select((placement, index) => index == 0
                ? placement with { Position = [placement.Position[0] + 0.1, placement.Position[1], placement.Position[2]] }
                : placement).ToArray() };
            var blocked = false;
            using (var reader = new FileStream(path, FileMode.Open, System.IO.FileAccess.Read, FileShare.Read))
            {
                try { WorkspaceRepository.Save(updated, path); }
                catch (Exception exception) when (exception is IOException or UnauthorizedAccessException) { blocked = true; }
            }
            var preserved = blocked && File.ReadAllText(path) == original;
            var cleaned = !Directory.EnumerateFiles(Path.GetDirectoryName(path)!, Path.GetFileName(path) + ".*.tmp").Any();
            WorkspaceRepository.Save(updated, path);
            var retry = File.ReadAllText(path) != original;
            var passed = preserved && cleaned && retry;
            GD.Print($"WORKSPACE_WRITE_GUARD_VERIFY {(passed ? "PASS" : "FAIL")} preserved={preserved} cleaned={cleaned} retry={retry}");
            if (!passed) throw new InvalidOperationException("Workspace write failure did not preserve its previous saved contents.");
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
