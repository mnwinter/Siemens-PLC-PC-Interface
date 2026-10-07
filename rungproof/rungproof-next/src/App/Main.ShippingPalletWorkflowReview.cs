using System;
using Godot;
using RungProof.Next.VirtualController;

namespace RungProof.Next.App;

public partial class Main
{
    private void VerifyShippingPalletControllerWorkflow(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-18-pallet-pickup", _candidateCatalog!, _mainCamera!, false, false);
        var runtime = _sceneRuntime!;
        var pallet = _sceneCompositionRoot!.GetNode<Node3D>("shipping_pallet");
        var home = pallet.Position;
        var document = new LadderEditorDocument();
        document.ResetProject("review-shipping-pallet", "Shipping_Pallet_QA", TimeSpan.FromMilliseconds(20));
        document.SourceSceneId = "lab-2-18-pallet-pickup";
        document.AddTag("auto_mode", PlcVariableRole.Input, "auto_mode");
        document.AddTag("pickup_sensor", PlcVariableRole.Input, "pickup_sensor");
        document.AddTag("auto_start_request", PlcVariableRole.Input, "auto_start_request");
        document.AddTag("manual_jog_request", PlcVariableRole.Input, "manual_jog_request");
        document.AddTag("conveyor_run", PlcVariableRole.Output, "conveyor_run");
        document.AddRung("Automatic travel until actual pickup beam", "conveyor_run");
        document.AddContact(0, 0, "auto_mode", false);
        document.AddContact(0, 0, "pickup_sensor", true);
        document.AddContact(0, 0, "auto_start_request", false);
        document.AddParallelBranch(0);
        document.AddContact(0, 1, "auto_mode", false);
        document.AddContact(0, 1, "pickup_sensor", true);
        document.AddContact(0, 1, "conveyor_run", false);
        var program = document.BuildProgram();
        var compiled = LadderCompiler.Compile(program);
        check(compiled.IsValid, "shipping_pallet_qa_compiles");
        if (!compiled.IsValid) throw new InvalidOperationException("Shipping QA compile failed.");
        System.IO.File.WriteAllText(ProjectSettings.GlobalizePath("res://.tools/aaa-shipping-pallet-native-qa.rpproj.json"), LadderEditorProjectJson.Save(document));
        EnableVirtualControllerProgram(program);
        try
        {
            void Tick(int count) { for (var scan = 0; scan < count; scan++) _PhysicsProcess(.02); }
            RunActiveController(); Tick(50);
            check(pallet.Position.IsEqualApprox(home) && runtime.Points["conveyor_run"] is false,
                "shipping_pallet_loaded_run_waits_for_start");
            check(ExecuteSelectedControllerAction("start-auto"), "shipping_pallet_start_button_accepted");
            Tick(50);
            check(MathF.Abs(pallet.Position.X - home.X - .75f) < .001f && runtime.Points["conveyor_run"] is true,
                "shipping_pallet_loaded_ladder_moves_at_configured_speed");
            StopActiveController(); var stopped = pallet.Position; Tick(50);
            check(pallet.Position.IsEqualApprox(stopped) && runtime.Points["conveyor_run"] is false,
                "shipping_pallet_loaded_ladder_stop_holds");
            check(Equals(runtime.Points["status_color"], "red"), "shipping_pallet_stop_tower_refreshes_without_motion_tick");
            RunActiveController(); Tick(10);
            check(pallet.Position.IsEqualApprox(stopped), "shipping_pallet_restart_requires_new_start");
            check(ExecuteSelectedControllerAction("start-auto"), "shipping_pallet_restart_start_button_accepted");
            Tick(400);
            check(runtime.Points["pickup_sensor"] is true && runtime.Points["conveyor_run"] is false
                && runtime.Points["cycle_complete"] is true,
                "shipping_pallet_loaded_ladder_stops_on_geometric_sensor");
            var endpoint = pallet.Position; Tick(50);
            check(pallet.Position.IsEqualApprox(endpoint), "shipping_pallet_loaded_ladder_endpoint_remains_held");
            ResetActiveController();
            check(pallet.Position.IsEqualApprox(home) && runtime.Points["pickup_sensor"] is false,
                "shipping_pallet_loaded_ladder_reset_restores_home");
        }
        finally { DisableVirtualController(); }
    }
}
