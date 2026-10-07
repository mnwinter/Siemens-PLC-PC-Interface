using System.Collections.Generic;
using Godot;

namespace RungProof.Next.Scenes;

public partial class SceneSimulationRuntime
{
    private readonly Dictionary<MeshInstance3D,Material?> _radarOpaqueMaterials=[];
    private StandardMaterial3D? _radarInspectionMaterial;
    private void ProjectRadarInspectionView(Node3D? tank)
    {
        if(tank is null || !_points.ContainsKey("tank_inspection_view"))return;
        // Explicit presentation-only inspection: retain the real shell/roof
        // meshes and their transforms, but reveal internal beam/surface geometry.
        // This SIM point is never a PLC command or simulated physical opening.
        _radarInspectionMaterial ??= new StandardMaterial3D {
            AlbedoColor=new Color(.55f,.68f,.75f,.12f),
            Transparency=BaseMaterial3D.TransparencyEnum.Alpha,
            CullMode=BaseMaterial3D.CullModeEnum.Disabled,
            ShadingMode=BaseMaterial3D.ShadingModeEnum.Unshaded,
        };
        foreach(var name in new[]{"TANK_shell","TANK_roof"}) {
            if(tank.FindChild(name,true,false) is not MeshInstance3D mesh)continue;
            if(!_radarOpaqueMaterials.ContainsKey(mesh))_radarOpaqueMaterials[mesh]=mesh.MaterialOverride;
            mesh.MaterialOverride=AsBool(_points["tank_inspection_view"]) ? _radarInspectionMaterial : _radarOpaqueMaterials[mesh];
        }
    }
}
