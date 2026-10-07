using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _auditLuggageLayout;
    private void AuditLuggageLayout()
    {
        var failures=0;
        void Check(bool ok,string name) {if(!ok)failures++;GD.Print($"LUGGAGE_LAYOUT_CHECK {name}={ok}");}
        try {
            AddMigratedScene("lab-6-07-luggage-weight-sort",_candidateCatalog!,_mainCamera!,false,false);
            var root=_sceneCompositionRoot!;
            var bag=root.GetNode<Node3D>("training_accessory_5");
            var belt=(MeshInstance3D)root.GetNode<Node3D>("conveyor_0").FindChild("KIN_belt_surface",true,false);
            var receiver=(MeshInstance3D)root.GetNode<Node3D>("reject_outfeed").FindChild("KIN_belt_surface",true,false);
            var scale=root.GetNode<Node3D>("training_accessory_4");
            var deck=(MeshInstance3D)scale.FindChild("SCALE_DECK_surface",true,false);
            var baseMesh=(MeshInstance3D)bag.FindChild("LUGGAGE_base",true,false);
            Check(bag.FindChild("LUGGAGE_BODY",true,false) is MeshInstance3D && root.GetNodeOrNull<Node3D>("machine_2") is null && root.GetNodeOrNull<Node3D>("box_1") is null,"actual_suitcase_and_no_cnc_or_extra_carton");
            bool Borne(Aabb load,Aabb surface)=>Math.Abs(load.Position.Y-surface.End.Y)<.005 && load.Position.X>=surface.Position.X-.001 && load.End.X<=surface.End.X+.001 && load.Position.Z>=surface.Position.Z-.001 && load.End.Z<=surface.End.Z+.001;
            Check(Borne(ReviewBounds(baseMesh),ReviewBounds(belt)),"home_base_bears_within_infeed_belt");
            var home=bag.Position;bag.Position=new(0,.9f,0);
            Check(Borne(ReviewBounds(baseMesh),ReviewBounds(deck)),"station_pose_base_bears_within_actual_weigh_deck");bag.Position=home;
            var cells=ReviewMeshes(scale).Where(m=>m.Name.ToString().StartsWith("LOAD_CELL_body_")).Select(ReviewBounds).ToArray();
            Check(cells.Length==4 && cells.All(cell=>Math.Abs(cell.End.Y-ReviewBounds(deck).Position.Y)<.005),"weigh_deck_bears_on_four_cell_bodies");
            var diverter=root.GetNode<Node3D>("training_accessory_7");
            var rollers=ReviewMeshes(diverter).Where(m=>m.Name.ToString().StartsWith("ROLLER_")).Select(ReviewBounds).ToArray();
            Check(rollers.Length==12 && rollers.All(roller=>Math.Abs(roller.End.Y-.9)<.005) && Math.Abs(ReviewBounds(receiver).End.Y-.9)<.005,"retained_roller_crowns_and_receiver_match_point_nine_plane");
            var bridge=ReviewBounds((MeshInstance3D)root.GetNode<Node3D>("luggage_transfer_bridge").FindChild("LUGGAGE_reject_bridge_surface",true,false));
            Check(Math.Abs(bridge.End.Y-.9)<.005 && bridge.Position.Z<=ReviewBounds(receiver).End.Z && bridge.End.Z<=-.43,"reject_receiving_bridge_reaches_outfeed_at_matching_height");
            var arm=(MeshInstance3D)diverter.FindChild("KIN_DIVERTER_ARM",true,false);
            var gate=diverter.GetNode<Node3D>("LuggageGatePivot");
            var solids=ReviewMeshes(root).Where(m=>!ReviewMeshes(bag).Contains(m)).ToArray();
            bool Clear() => ReviewMeshes(bag).All(m=>solids.All(f=> {
                var overlap=ReviewBounds(m).Intersection(ReviewBounds(f)).Size;
                return overlap.X<=.002 || overlap.Y<=.002 || overlap.Z<=.002 || !OrientedBoxesPenetrate(m,f);
            }));
            bool directClear=true;
            for(var i=0;i<=300;i++) {
                bag.Position=new(-3.2f+5.85f*i/300,.9f,0);directClear &= Clear();
            }
            Check(directClear,"301_prescribed_normal_route_poses_clear_visible_fixed_solids");
            gate.Rotation=new(0,Mathf.DegToRad(55),0);
            // Conservatively place the entire suitcase behind the arm plane.
            // Use actual delivered mesh corners, including the tag and handles,
            // rather than only the nominal rectangular body dimensions.
            var normal=gate.GlobalBasis.Z.Normalized();
            var pivot=gate.GlobalPosition;
            bag.Position=Vector3.Zero;
            var localProjection=ReviewMeshes(bag).SelectMany(m=> {
                var bounds=m.GetAabb();return Enumerable.Range(0,8).Select(i=>m.GlobalTransform*new Vector3(
                    (i&1)==0?bounds.Position.X:bounds.End.X,
                    (i&2)==0?bounds.Position.Y:bounds.End.Y,
                    (i&4)==0?bounds.Position.Z:bounds.End.Z));
            }).Max(v=>v.Dot(normal));
            float GuidedZ(float x)=>Math.Min(0,(pivot.Dot(normal)-.055f-localProjection-x*normal.X)/normal.Z);
            bool rejectClear=true;
            for(var i=0;i<=300;i++) {
                var x=-3.2f+5.5f*i/300;
                bag.Position=new(x,.9f,GuidedZ(x));rejectClear &= Clear();
            }
            var branchStart=GuidedZ(2.3f);
            for(var i=0;i<=150;i++) {
                bag.Position=new(2.3f,.9f,branchStart+(-3.03f-branchStart)*i/150);rejectClear &= Clear();
            }
            Check(rejectClear,"452_prescribed_reject_route_poses_clear_visible_fixed_solids");
            Check(Borne(ReviewBounds(baseMesh),ReviewBounds(receiver)),"reject_end_pose_is_retained_on_actual_receiving_belt");
            GD.Print($"LUGGAGE_GUIDE_GEOMETRY branchStartZ={branchStart} marginM=.005 prescribed-only");
            bag.Position=home;gate.Rotation=Vector3.Zero;

        } catch(Exception e) {failures++;GD.PushError(e.ToString());}
        GD.Print($"LUGGAGE_LAYOUT_VERIFY {(failures==0?"PASS":"FAIL")} static-bearing-only numeric/process/controller review pending");GetTree().Quit(failures==0?0:1);
    }
}
