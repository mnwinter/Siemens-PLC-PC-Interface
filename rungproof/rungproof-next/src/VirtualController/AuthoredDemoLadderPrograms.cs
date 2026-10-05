using System;

namespace RungProof.Next.VirtualController;

/// <summary>
/// The five authored demonstrations are paired with real ladder documents.
/// Keeping these documents as code makes the demo selector deterministic and
/// ensures the ladder shown in the editor matches the selected plant contract.
/// </summary>
public static class AuthoredDemoLadderPrograms
{
    public static bool TryCreate(string sceneId, out LadderEditorDocument document)
    {
        document = sceneId switch
        {
            "lab-4-01-press-count-lamp" => CreatePressCount(),
            "lab-5-01-delayed-lamp" => CreateDelayedLamp(),
            "scene-1-conveyor-stop" => CreateConveyorSequence(),
            "lab-9-11-pallet-counting" => CreateBatchCounter(),
            "lab-11-13-xy-palletizing" => CreateIntegratedPalletizer(),
            _ => null!,
        };
        return document is not null;
    }

    private static LadderEditorDocument CreatePressCount()
    {
        var document = New("demo-1-press-count", "Press_Count_Main", "lab-4-01-press-count-lamp");
        document.AddTag("pulse_received", PlcVariableRole.Input, "pulse_received");
        document.AddTag("threshold_lamp", PlcVariableRole.Output, "threshold_lamp");
        document.AddTag("press_count", PlcVariableRole.Memory, type: PlcVariableType.Counter);
        document.AddTag("lamp_enable", PlcVariableRole.Memory);
        document.WatchVariables.AddRange(["pulse_received", "press_count", "threshold_lamp"]);

        document.AddCounterRung("Count press pulses", "press_count", 3);
        document.AddContact(0, 0, "pulse_received", false);
        document.AddRung("Turn on threshold lamp", "threshold_lamp");
        document.AddContact(1, 0, "press_count.DN", false);
        return document;
    }

    private static LadderEditorDocument CreateDelayedLamp()
    {
        var document = New("demo-2-delayed-lamp", "Delayed_Lamp_Main", "lab-5-01-delayed-lamp");
        document.AddTag("timer_request", PlcVariableRole.Input, "timer_request");
        document.AddTag("delayed_lamp", PlcVariableRole.Output, "delayed_lamp");
        document.AddTag("delay_timer", PlcVariableRole.Memory, type: PlcVariableType.Timer);
        document.WatchVariables.AddRange(["timer_request", "delay_timer", "delayed_lamp"]);

        document.AddTimerRung("Delay lamp request", "delay_timer", TimeSpan.FromSeconds(2));
        document.AddContact(0, 0, "timer_request", false);
        document.AddRung("Delayed lamp output", "delayed_lamp");
        document.AddContact(1, 0, "delay_timer.Q", false);
        return document;
    }

    private static LadderEditorDocument CreateConveyorSequence()
    {
        var document = New("demo-3-conveyor-sequence", "Conveyor_Sequence_Main", "scene-1-conveyor-stop");
        document.AddTag("start_command", PlcVariableRole.Input, "operator.start");
        document.AddTag("stop_command", PlcVariableRole.Input, "operator.stop");
        document.AddTag("simulated_photoeye", PlcVariableRole.Input, "simulated_photoeye");
        document.AddTag("seal_in", PlcVariableRole.Memory);
        document.AddTag("conveyor_running", PlcVariableRole.Output, "conveyor_running");
        document.WatchVariables.AddRange(["start_command", "stop_command", "simulated_photoeye", "seal_in", "conveyor_running"]);

        document.AddRung("Start/stop conveyor sequence", "seal_in");
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

    private static LadderEditorDocument CreateBatchCounter()
    {
        var document = New("demo-4-batch-process", "Batch_Process_Main", "lab-9-11-pallet-counting");
        document.AddTag("pallet_detected", PlcVariableRole.Input, "pallet_detected");
        document.AddTag("pallet_type_valid", PlcVariableRole.Input, "pallet_type_valid");
        document.AddTag("count_request", PlcVariableRole.Input, "count_request");
        document.AddTag("pallet_count_valid", PlcVariableRole.Output, "pallet_count_valid");
        document.AddTag("pallet_count", PlcVariableRole.Output, "pallet_count", type: PlcVariableType.DInt);
        document.AddTag("batch_count", PlcVariableRole.Memory, type: PlcVariableType.Counter);
        document.AddTag("batch_ready", PlcVariableRole.Memory);
        document.AddTag("always_scan", PlcVariableRole.Memory, initialValue: true);
        document.WatchVariables.AddRange(["pallet_detected", "pallet_type_valid", "count_request", "batch_count", "pallet_count", "pallet_count_valid"]);

        var counter = document.AddBlock("FB_ValidPalletCounter", LadderBlockType.FunctionBlock);
        var validation = document.AddBlock("FC_BatchValidation", LadderBlockType.Function);
        document.SelectBlock(1);
        document.AddCounterRung("Count valid pallets", "batch_count", 5);
        // Count the detection edge only when that event has both permissives.
        // Gating a held detection with a newly enabled permissive must not
        // manufacture a new pallet event.
        document.InsertEdgeContact(0, 0, 0, "pallet_detected", LadderEdgeMode.Rising);
        document.AddContact(0, 0, "pallet_type_valid", false);
        document.AddContact(0, 0, "count_request", false);
        document.SelectBlock(2);
        document.AddRung("Batch ready permissive", "batch_ready");
        document.AddContact(0, 0, "pallet_type_valid", false);
        document.AddContact(0, 0, "count_request", false);
        document.AddRung("Validate pallet count", "pallet_count_valid");
        document.AddContact(1, 0, "batch_count.DN", false);
        document.AddContact(1, 0, "batch_ready", false);
        document.SelectBlock(0);
        AddAlwaysScannedCall(document, "Count valid pallet events", counter.Id);
        AddAlwaysScannedCall(document, "Validate batch completion", validation.Id);
        // Publish after the counter call so the scene sees this scan's count.
        // Keep the standard Stop policy: output image zero, counter retained.
        document.AddNumericOperationRung("Publish current pallet count", LadderNumericOperationKind.Move,
            "batch_count.ACC", string.Empty, "pallet_count");
        document.AddContact(2, 0, "always_scan", false);
        return document;
    }

    private static LadderEditorDocument CreateIntegratedPalletizer()
    {
        var document = New("demo-5-integrated-palletizer", "Palletizing_Cell_Main", "lab-11-13-xy-palletizing");
        document.AddTag("carton_at_pick", PlcVariableRole.Input, "carton_at_pick");
        document.AddTag("gantry_home", PlcVariableRole.Input, "gantry_home");
        document.AddTag("pallet_position_valid", PlcVariableRole.Input, "pallet_position_valid");
        document.AddTag("vacuum_pick", PlcVariableRole.Output, "vacuum_pick");
        document.AddTag("gantry_cycle", PlcVariableRole.Output, "gantry_cycle");
        document.AddTag("layer_complete", PlcVariableRole.Output, "layer_complete");
        document.AddTag("cell_permissive", PlcVariableRole.Memory);
        document.AddTag("pick_permissive", PlcVariableRole.Memory);
        document.AddTag("sequence_ready", PlcVariableRole.Memory);
        document.AddTag("cell_active", PlcVariableRole.Memory);
        document.AddTag("always_scan", PlcVariableRole.Memory, initialValue: true);
        document.AddTag("layer_count", PlcVariableRole.Memory, type: PlcVariableType.DInt);
        document.AddTag("position_sum", PlcVariableRole.Memory, type: PlcVariableType.DInt);
        document.AddTag("pick_timer", PlcVariableRole.Memory, type: PlcVariableType.Timer);
        document.AddTag("cycle_count", PlcVariableRole.Memory, type: PlcVariableType.Counter);
        document.WatchVariables.AddRange(["carton_at_pick", "gantry_home", "pallet_position_valid", "vacuum_pick", "gantry_cycle", "layer_complete", "layer_count", "cycle_count", "cell_active", "position_sum"]);

        var safety = document.AddBlock("FB_SafetyInterlock", LadderBlockType.FunctionBlock);
        document.AddInterfaceParameter(safety.Id, "GantryHome", PlcVariableType.Bool, LadderInterfaceSection.Input);
        document.AddInterfaceParameter(safety.Id, "PalletValid", PlcVariableType.Bool, LadderInterfaceSection.Input);
        document.AddInterfaceParameter(safety.Id, "Permissive", PlcVariableType.Bool, LadderInterfaceSection.Output);
        document.AddInterfaceParameter(safety.Id, "TripLatched", PlcVariableType.Bool, LadderInterfaceSection.Static);

        var pick = document.AddBlock("FB_PickAndPlace", LadderBlockType.FunctionBlock);
        document.AddInterfaceParameter(pick.Id, "Enable", PlcVariableType.Bool, LadderInterfaceSection.Input);
        document.AddInterfaceParameter(pick.Id, "CartonPresent", PlcVariableType.Bool, LadderInterfaceSection.Input);
        document.AddInterfaceParameter(pick.Id, "VacuumCommand", PlcVariableType.Bool, LadderInterfaceSection.Output);
        document.AddInterfaceParameter(pick.Id, "CycleActive", PlcVariableType.Bool, LadderInterfaceSection.Output);
        document.AddInterfaceParameter(pick.Id, "PickTimer", PlcVariableType.Timer, LadderInterfaceSection.Static);

        var sequence = document.AddBlock("FC_SequenceSupervisor", LadderBlockType.Function);
        document.AddInterfaceParameter(sequence.Id, "Permissive", PlcVariableType.Bool, LadderInterfaceSection.Input);
        document.AddInterfaceParameter(sequence.Id, "Ready", PlcVariableType.Bool, LadderInterfaceSection.Output);

        var math = document.AddBlock("FC_InspectionMath", LadderBlockType.Function);
        document.AddInterfaceParameter(math.Id, "LayerCount", PlcVariableType.DInt, LadderInterfaceSection.Input);
        document.AddInterfaceParameter(math.Id, "PositionSum", PlcVariableType.DInt, LadderInterfaceSection.Output);

        // DB members are presentation declarations in this simulator. Runtime
        // values remain the matching project tags, as the workbench explains.
        var data = document.AddBlock("DB_CellData", LadderBlockType.DataBlock);
        document.AddInterfaceParameter(data.Id, "layer_count", PlcVariableType.DInt, LadderInterfaceSection.Static);
        document.AddInterfaceParameter(data.Id, "position_sum", PlcVariableType.DInt, LadderInterfaceSection.Static);
        var diagnostics = document.AddBlock("DB_CellStatus", LadderBlockType.DataBlock);
        document.AddInterfaceParameter(diagnostics.Id, "cell_active", PlcVariableType.Bool, LadderInterfaceSection.Static);
        document.AddInterfaceParameter(diagnostics.Id, "layer_complete", PlcVariableType.Bool, LadderInterfaceSection.Static);

        document.SelectBlock(1);
        document.AddRung("Home and pallet permissive", "cell_permissive");
        document.AddContact(0, 0, "gantry_home", false);
        document.AddContact(0, 0, "pallet_position_valid", false);

        document.SelectBlock(2);
        document.AddRung("Pick command", "pick_permissive");
        document.AddContact(0, 0, "cell_permissive", false);
        document.AddContact(0, 0, "carton_at_pick", false);
        // Finish one four-carton layer and require Reset before another layer.
        // Held carton feedback must not issue a fifth pick after completion.
        document.AddComparison(0, 0, "cycle_count.ACC", LadderCompareOperator.LessThan, "4");

        document.SelectBlock(3);
        document.AddRung("Sequence ready", "sequence_ready");
        document.AddContact(0, 0, "cell_permissive", false);

        document.SelectBlock(4);
        document.AddNumericOperationRung("Add layer position", LadderNumericOperationKind.Add, "layer_count", "1", "position_sum");
        document.AddContact(0, 0, "sequence_ready", false);

        document.SelectBlock(0);
        // Scan permissive-producing blocks even when their inputs are false.
        // Skipping a call retains its previous memory and can leave commands on.
        document.AddRung("Safety interlock block call", string.Empty);
        document.AddContact(0, 0, "always_scan", false);
        document.Rungs[0].IsCall = true;
        document.Rungs[0].CallTarget = safety.Id;
        document.AddRung("Pick and place block call", string.Empty);
        document.AddContact(1, 0, "always_scan", false);
        document.Rungs[1].IsCall = true;
        document.Rungs[1].CallTarget = pick.Id;
        document.AddRung("Sequence supervisor function call", string.Empty);
        document.AddContact(2, 0, "always_scan", false);
        document.Rungs[2].IsCall = true;
        document.Rungs[2].CallTarget = sequence.Id;
        document.AddRung("Inspection math function call", string.Empty);
        document.AddContact(3, 0, "always_scan", false);
        document.Rungs[3].IsCall = true;
        document.Rungs[3].CallTarget = math.Id;
        document.AddRung("Gantry cycle command", "gantry_cycle");
        document.AddContact(4, 0, "pick_permissive", false);
        document.AddRung("Vacuum pick command", "vacuum_pick");
        document.AddContact(5, 0, "pick_permissive", false);
        document.AddRung("Layer completion output", "layer_complete");
        document.AddComparison(6, 0, "cycle_count.ACC", LadderCompareOperator.GreaterOrEqual, "4");
        document.AddTimerRung("Pick dwell timer", "pick_timer", TimeSpan.FromMilliseconds(750));
        document.AddContact(7, 0, "pick_permissive", false);
        document.AddCounterRung("Count completed picks", "cycle_count", 4);
        document.AddContact(8, 0, "pick_timer.Q", false);
        document.AddNumericOperationRung("Advance layer count", LadderNumericOperationKind.Add, "layer_count", "1", "layer_count");
        document.InsertEdgeContact(9, 0, 0, "layer_complete", LadderEdgeMode.Rising);
        document.AddRung("Cell active status: either commanded actuator", "cell_active");
        document.AddContact(10, 0, "vacuum_pick", false);
        document.AddParallelBranch(10);
        document.AddContact(10, 1, "gantry_cycle", false);

        document.SelectBlock(0);
        return document;
    }

    private static void AddAlwaysScannedCall(LadderEditorDocument document, string label, string target)
    {
        var index = document.Rungs.Count;
        document.AddRung(label, string.Empty);
        document.AddContact(index, 0, "always_scan", false);
        document.Rungs[index].IsCall = true;
        document.Rungs[index].CallTarget = target;
    }

    private static LadderEditorDocument New(string id, string name, string sceneId)
    {
        var document = new LadderEditorDocument();
        document.ResetProject(id, name, TimeSpan.FromMilliseconds(20));
        document.SourceSceneId = sceneId;
        return document;
    }
}
