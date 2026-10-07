using System;
using System.Linq;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyMultiConveyorControllerWorkflow(Action<bool, string> check)
    {
        AddMigratedScene("lab-11-07-multi-conveyor-pallet-route", _candidateCatalog!, _mainCamera!, false, false);
        var runtime = _sceneRuntime!;
        var root = _sceneCompositionRoot!;
        var pallet = root.GetNode<Node3D>("route_pallet");
        var feed = root.GetNode<Node3D>("conveyor_0");
        var belt = ReviewBounds((MeshInstance3D)feed.FindChild("KIN_belt_surface", true, false));
        var tailX = ReviewBounds((MeshInstance3D)feed.FindChild("KIN_tail_drum", true, false)).GetCenter().X;
        var driveX = ReviewBounds((MeshInstance3D)feed.FindChild("KIN_drive_drum", true, false)).GetCenter().X;
        var runners = ReviewMeshes(pallet).Where(mesh => mesh.Name.ToString().StartsWith("PALLET_BOTTOM_", StringComparison.Ordinal)).ToArray();
        // The curved belt envelope is not the flat carrying span. Check the
        // three actual runner meshes against the drum axes independently.
        check(runners.Length == 3 && runners.All(mesh =>
        {
            var bounds = ReviewBounds(mesh);
            return MathF.Abs(bounds.Position.Y - belt.End.Y) < .001f
                && bounds.Position.X >= tailX && bounds.End.X <= driveX
                && bounds.Position.Z >= belt.Position.Z && bounds.End.Z <= belt.End.Z;
        }), "multi_conveyor_home_pallet_runners_seated_inside_flat_belt");
        GD.Print($"MULTI_CONVEYOR_HOME pallet={ReviewBounds(pallet)} belt={belt} flat={tailX}..{driveX}");
        var document = new LadderEditorDocument();
        document.ResetProject("review-multi-conveyor", "Multi_Conveyor_QA", TimeSpan.FromMilliseconds(20));
        document.SourceSceneId = "lab-11-07-multi-conveyor-pallet-route";
        document.AddTag("common_stop_request", PlcVariableRole.Input, "common_stop_request");
        for (var zone = 1; zone <= 3; zone++)
        {
            var clear = $"zone_{zone}_clear";
            var run = $"zone_{zone}_run";
            document.AddTag(clear, PlcVariableRole.Input, clear);
            document.AddTag(run, PlcVariableRole.Output, run);
            var rung = zone - 1;
            document.AddRung($"Zone {zone}: fresh clear edge, common stop", run);
            // Sample the edge before permissives so releasing Stop with an
            // already-clear zone cannot generate a new start edge.
            document.InsertEdgeContact(rung, 0, 0, clear, LadderEdgeMode.Rising);
            document.AddContact(rung, 0, "common_stop_request", true);
            document.AddParallelBranch(rung);
            document.AddContact(rung, 1, clear, false);
            document.AddContact(rung, 1, "common_stop_request", true);
            document.AddContact(rung, 1, run, false);
        }
        var program = document.BuildProgram();
        var compiled = LadderCompiler.Compile(program);
        check(compiled.IsValid, "multi_conveyor_edge_qa_compiles");
        if (!compiled.IsValid) throw new InvalidOperationException("Multi-conveyor QA compile failed.");
        System.IO.File.WriteAllText(ProjectSettings.GlobalizePath("res://.tools/aaa-multi-conveyor-native-qa.rpproj.json"), LadderEditorProjectJson.Save(document));
        EnableVirtualControllerProgram(program);
        try
        {
            void Tick(int count) { for (var scan = 0; scan < count; scan++) _PhysicsProcess(.02); }
            bool Outputs(bool expected) => Enumerable.Range(1, 3).All(zone => Equals(runtime.Points[$"zone_{zone}_run"], expected));
            void Action(string id) { if (!ExecuteSelectedControllerAction(id)) throw new InvalidOperationException("Rejected action: " + id); }
            RunActiveController(); Tick(5);
            check(Outputs(false), "multi_conveyor_initial_outputs_off");
            for (var zone = 1; zone <= 3; zone++) { Action($"toggle-zone_{zone}_clear"); Tick(2); }
            check(Outputs(true), "multi_conveyor_fresh_edges_start_all_zones");
            Action("toggle-common-stop"); Tick(2);
            check(Outputs(false), "multi_conveyor_common_stop_drops_all_zones");
            Action("toggle-common-stop"); Tick(25);
            check(Outputs(false), "multi_conveyor_stop_release_does_not_restart_clear_zones");
            Action("toggle-zone_2_clear"); Tick(2); Action("toggle-zone_2_clear"); Tick(2);
            check(runtime.Points["zone_2_run"] is true && runtime.Points["zone_1_run"] is false && runtime.Points["zone_3_run"] is false,
                "multi_conveyor_only_fresh_zone_restarts");
            Action("toggle-zone_2_clear"); Tick(2);
            check(Outputs(false), "multi_conveyor_clear_loss_removes_zone_command");
            StopActiveController(); ResetActiveController();
            check(Outputs(false) && runtime.Points["common_stop_request"] is false,
                "multi_conveyor_reset_restores_inputs_and_outputs");
        }
        finally { DisableVirtualController(); }
    }
}
