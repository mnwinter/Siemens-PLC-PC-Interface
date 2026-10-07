using System;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _auditRadarLayout;
    private void AuditRadarLayout()
    {
        var failures=0;
        void Check(bool ok,string name) {if(!ok)failures++;GD.Print($"RADAR_LAYOUT_CHECK {name}={ok}");}
        try {
            VerifyTankPipingGeometry(Check,"tank-radar");
            VerifyRadarMountAndBeam(Check);
            var tank=_sceneCompositionRoot!.GetNode<Node3D>("water_tank_radar");
            var shell=(MeshInstance3D)tank.FindChild("TANK_shell",true,false);
            var roof=(MeshInstance3D)tank.FindChild("TANK_roof",true,false);
            var original=shell.MaterialOverride;var originalRoof=roof.MaterialOverride;
            var transform=shell.GlobalTransform;var distance=_sceneRuntime!.Points["radar_distance"];
            Check(_sceneRuntime.ExecuteAction("toggle-inspection") && shell.MaterialOverride is StandardMaterial3D material
                && material.Transparency==BaseMaterial3D.TransparencyEnum.Alpha && roof.MaterialOverride==shell.MaterialOverride,
                "inspection_view_ghosts_shell_and_roof");
            Check(shell.GlobalTransform==transform && Equals(_sceneRuntime.Points["radar_distance"],distance),"inspection_view_preserves_geometry_and_range");
            Check(_sceneRuntime.ExecuteAction("toggle-inspection") && shell.MaterialOverride==original && roof.MaterialOverride==originalRoof,
                "inspection_view_restores_authored_opaque_materials");
        } catch(Exception ex) {failures++;GD.PushError(ex.ToString());}
        GD.Print($"RADAR_LAYOUT_VERIFY {(failures==0?"PASS":"FAIL")} bounds and existing feedback only; native piping and radar reference pending");
        GetTree().Quit(failures==0?0:1);
    }
}
