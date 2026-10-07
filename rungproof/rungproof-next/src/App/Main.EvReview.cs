using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _auditEvLayout;
    private void AuditEvLayout()
    {
        var failures=0;
        void Check(bool ok,string name) { if(!ok)failures++; GD.Print($"EV_LAYOUT_CHECK {name}={ok}"); }
        try {
            AddMigratedScene("lab-9-12-ev-charging-manager",_candidateCatalog!,_mainCamera!,false,false);
            var root=_sceneCompositionRoot!;
            foreach(var ids in new[]{new[]{"training_accessory_3","training_accessory_4","training_accessory_5","training_accessory_6","training_accessory_7"},new[]{"ev_bay_b","ev_connector_b","ev_meter_b","ev_pulse_b","ev_reader_b"}}) {
                var bay=root.GetNode<Node3D>(ids[0]);
                MeshInstance3D Mesh(Node3D n,string name)=>(MeshInstance3D)n.FindChild(name,true,false);
                var pad=ReviewBounds(Mesh(bay,"EV_BAY_ground_pad"));
                var tires=ReviewMeshes(bay).Where(m=>m.Name.ToString().StartsWith("EV_tire_")).ToArray();
                Check(tires.Length==4 && tires.All(t=>Math.Abs(ReviewBounds(t).Position.Y-pad.End.Y)<.003),ids[0]+"_four_tires_bear_on_pad");
                var pedestal=ReviewBounds(Mesh(bay,"EVSE_base"));
                Check(Math.Abs(pedestal.Position.Y-pad.End.Y)<.003,ids[0]+"_charger_base_bears_on_pad");
                var plug=root.GetNode<Node3D>(ids[1]);
                var nose=ReviewBounds(Mesh(plug,"CONNECTOR_nose"));
                var inlet=ReviewBounds(Mesh(bay,"EV_INLET"));
                Check(Math.Abs(nose.GetCenter().X-inlet.GetCenter().X)<.003 && Math.Abs(nose.GetCenter().Y-inlet.GetCenter().Y)<.003 && nose.Intersects(inlet),ids[0]+"_plug_nose_engages_inlet");
                var cable=ReviewBounds(Mesh(bay,"EVSE_CABLE_4"));
                var gland=ReviewBounds(Mesh(plug,"CONNECTOR_cable_gland"));
                Check(cable.Intersects(gland),ids[0]+"_cable_reaches_plug_gland");
                var meter=root.GetNode<Node3D>(ids[2]);
                var meterBase=ReviewBounds(Mesh(meter,"METER_base"));
                Check(Math.Abs(meterBase.Position.Y)<.003,ids[0]+"_meter_grounded");
                var pulse=root.GetNode<Node3D>(ids[3]);
                var module=ReviewBounds(Mesh(pulse,"PULSE_module"));
                var housing=ReviewBounds(Mesh(meter,"METER_enclosure"));
                Check(Math.Abs(module.Position.Z-housing.End.Z)<.003 && module.Position.Y>=housing.Position.Y && module.End.Y<=housing.End.Y,ids[0]+"_pulse_module_backs_onto_meter");
                Check(Math.Abs(ReviewBounds(Mesh(root.GetNode<Node3D>(ids[4]),"READER_base")).Position.Y)<.003,ids[0]+"_reader_grounded");
            }
            Check(!ReviewMeshes(root).Any(m=>m.Name.ToString().StartsWith("KIN_slat_") || m.Name.ToString().StartsWith("PROCESS_flange")),"no_inherited_shutter_or_fluid_identity");
            Check(!root.HasNode("machine_0"),"unrelated_cabinet_removed");
        } catch(Exception ex) { failures++;GD.PushError(ex.ToString()); }
        GD.Print($"EV_LAYOUT_VERIFY {(failures==0?"PASS":"FAIL")} installation bounds only; charging and energy behavior unfinished");
        GetTree().Quit(failures==0?0:1);
    }
}
