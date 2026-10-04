using System;
using System.IO;
using System.Linq;
using Godot;
using RungProof.Next.Workspace;

namespace RungProof.Next.App;

public partial class Main
{
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
