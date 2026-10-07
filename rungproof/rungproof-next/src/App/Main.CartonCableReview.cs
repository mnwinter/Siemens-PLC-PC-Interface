using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _verifyCartonStaticRoutes;

    private void VerifyCartonStaticRoutesOnly()
    {
        var passed = true;
        void Check(bool condition, string label)
        {
            passed &= condition;
            GD.Print($"CARTON_STATIC_CHECK {label}={condition}");
        }
        try
        {
            VerifyCartonStaticCableRoutes(Check);
            VerifyInclinedPhotoeyeGeometry(Check);
            VerifyVisionSorterCartonSupport(Check);
        }
        catch (Exception error)
        {
            passed = false;
            GD.PushError($"CARTON_STATIC_CHECK exception: {error}");
        }
        GetTree().Quit(passed ? 0 : 1);
    }

    private void VerifyVisionSorterCartonSupport(Action<bool, string> check)
    {
        AddMigratedScene("lab-10-03-vision-package-sorter", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var display = root.GetNode<Node3D>("training_accessory_6");
        check(display.FindChild("COUNT_DISPLAY_screen", true, false) is MeshInstance3D
            && display.FindChild("COUNT_DISPLAY_base", true, false) is MeshInstance3D,
            "vision_sorter_class_display_has_actual_supported_display_mesh_identity");
        var foot = (MeshInstance3D)display.FindChild("COUNT_DISPLAY_base", true, false);
        var mast = (MeshInstance3D)display.FindChild("COUNT_DISPLAY_mast", true, false);
        var housing = (MeshInstance3D)display.FindChild("COUNT_DISPLAY_housing", true, false);
        check(MathF.Abs(ReviewBounds(foot).Position.Y) < .001f
            && ReviewBounds(foot).Grow(.001f).Intersects(ReviewBounds(mast))
            && ReviewBounds(mast).Grow(.001f).Intersects(ReviewBounds(housing)),
            "vision_sorter_display_has_grounded_base_and_attached_mast_housing");
        check(display.FindChild("StaticReadout", true, false) is Label3D label && label.Text == "CLASS\nNO RESULT"
            && display.FindChild("COUNT_DISPLAY_static_legend", true, false) is MeshInstance3D legend && !legend.Visible,
            "vision_sorter_display_states_no_result_and_hides_stale_count_legend");
        var carton = ReviewBounds(root.GetNode<Node3D>("box_1"));
        var surface = (MeshInstance3D)root.GetNode<Node3D>("conveyor_0").FindChild("KIN_belt_surface", true, false);
        var belt = ReviewBounds(surface);
        var table = root.GetNode<Node3D>("rotaryTable_3");
        var platter = (MeshInstance3D)table.FindChild("TABLE_rotating_platter", true, false);
        check(!ReviewMeshes(table).Any(mesh => mesh.Name.ToString().StartsWith("TABLE_fixture_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("TABLE_index_", StringComparison.Ordinal) || mesh.Name == "TABLE_center_register"),
            "vision_sorter_parcel_platter_has_no_visible_machining_fixture_or_raised_index_markers");
        check(MathF.Abs(ReviewBounds(platter).End.Y - belt.End.Y) < .001f,
            "vision_sorter_parcel_platter_matches_actual_infeed_bearing_plane");
        var receiver = root.GetNode<Node3D>("training_accessory_8");
        var receivingBelt = (MeshInstance3D)receiver.FindChild("KIN_belt_surface", true, false);
        GD.Print($"VISION_SORTER_RECEIVING infeed={belt} platter={ReviewBounds(platter)} bank={ReviewBounds(receivingBelt)}");
        GD.Print($"VISION_SORTER_RECEIVING_GAP x={ReviewBounds(platter).Position.X-belt.End.X} deckDelta={ReviewBounds(platter).End.Y-belt.End.Y} bankBeltCount={receiver.FindChildren("KIN_belt_surface", "MeshInstance3D", true, false).Count}");
        var bridge = root.GetNode<Node3D>("sorter_handoff_bridge");
        var deck = (MeshInstance3D)bridge.FindChild("SORTER_handoff_deck", true, false);
        check(MathF.Abs(ReviewBounds(deck).End.Y-belt.End.Y)<.001f,
            "vision_sorter_handoff_bridge_matches_infeed_and_platter_height");
        var feet=ReviewMeshes(bridge).Where(m=>m.Name.ToString().StartsWith("SORTER_bridge_foot_",StringComparison.Ordinal)).ToArray();
        var legs=ReviewMeshes(bridge).Where(m=>m.Name.ToString().StartsWith("SORTER_bridge_leg_",StringComparison.Ordinal)).ToArray();
        check(feet.Length==4 && legs.Length==4 && feet.All(f=>MathF.Abs(ReviewBounds(f).Position.Y)<.001f)
            && legs.All(l=>feet.Any(f=>ReviewBounds(f).Grow(.001f).Intersects(ReviewBounds(l)))
                && ReviewBounds(l).Grow(.001f).Intersects(ReviewBounds(deck))),
            "vision_sorter_handoff_has_four_grounded_attached_supports");
        var bridgeClear=true;var candidates=0;
        foreach(var part in ReviewMeshes(bridge))
        foreach(var peer in root.GetChildren().OfType<Node3D>().Where(node=>node!=bridge))
        foreach(var other in ReviewMeshes(peer))
        {
            // These two interfaces need a separate shaped-nose/contact test;
            // their enclosing boxes deliberately overlap the handoff boundary.
            if(part==deck && (other==surface || other==platter))continue;
            var overlap=ReviewBounds(part).Intersection(ReviewBounds(other)).Size;
            if(overlap.X<=.001f || overlap.Y<=.001f || overlap.Z<=.001f || !OrientedBoxesPenetrate(part,other))continue;
            if(part==deck && other.Name=="KIN_drive_drum" && VisionSorterDrumProfileClear(deck,other))continue;
            candidates++;
            if(candidates<=8) GD.Print($"VISION_SORTER_BRIDGE_INTERFERENCE {part.Name}/{peer.Name}/{other.Name} overlap={overlap}");
            bridgeClear=false;
        }
        check(bridgeClear,"vision_sorter_bridge_other_equipment_clear_at_one_mm_obb_screen_excluding_two_mating_surfaces");
        var drum=(MeshInstance3D)root.GetNode<Node3D>("conveyor_0").FindChild("KIN_drive_drum",true,false);
        var deckHome=deck.Transform;
        var detected=false;
        GD.Print("VISION_SORTER_DRUM_PROFILE_NEGATIVE_CONTROL_BEGIN lowered_deck_mm=50");
        try { deck.Position+=Vector3.Down*.05f;detected=!VisionSorterDrumProfileClear(deck,drum); }
        finally { deck.Transform=deckHome; }
        GD.Print("VISION_SORTER_DRUM_PROFILE_NEGATIVE_CONTROL_END restored=True");
        check(detected,"vision_sorter_drum_profile_screen_detects_deliberately_lowered_deck");
        var beltBearingEnd=surface.Mesh.GetFaces().Select(v=>surface.GlobalTransform*v)
            .Where(v=>MathF.Abs(v.Y-belt.End.Y)<.002f).Max(v=>v.X);
        GD.Print($"VISION_SORTER_BELT_BEARING_END {beltBearingEnd}");
        var topTriangles = new[] {surface,deck,platter}.SelectMany(mesh=>
        {
            var vertices=mesh.Mesh.GetFaces().Select(v=>mesh.GlobalTransform*v).ToArray();
            return Enumerable.Range(0,vertices.Length/3).Select(i=>new[]{vertices[i*3],vertices[i*3+1],vertices[i*3+2]})
                .Where(t=>t.All(v=>MathF.Abs(v.Y-belt.End.Y)<.002f));
        }).ToArray();
        bool Supported(Vector2 p)
        {
            foreach(var t in topTriangles)
            {
                var x0=t[0].X;var z0=t[0].Z;var x1=t[1].X;var z1=t[1].Z;var x2=t[2].X;var z2=t[2].Z;
                var denominator=(z1-z2)*(x0-x2)+(x2-x1)*(z0-z2);
                if(MathF.Abs(denominator)<1e-9f)continue;
                var u=((z1-z2)*(p.X-x2)+(x2-x1)*(p.Y-z2))/denominator;
                var v=((z2-z0)*(p.X-x2)+(x0-x2)*(p.Y-z2))/denominator;
                if(u>=-.00001f && v>=-.00001f && u+v<=1.00001f)return true;
            }
            return false;
        }
        var routeSupported=true;var samples=0;
        for(var step=0;step<=88;step++)
        for(var along=0;along<=4;along++)
        for(var across=0;across<=4;across++)
        {
            var x=-1.1f+step*.05f-carton.Size.X/2+carton.Size.X*along/4;
            var z=carton.Position.Z+carton.Size.Z*across/4;
            if(!Supported(new Vector2(x,z)))
            {
                if(routeSupported) GD.Print($"VISION_SORTER_UNSUPPORTED x={x} z={z}");
                routeSupported=false;
            }
            samples++;
        }
        GD.Print($"VISION_SORTER_SUPPORT_SAMPLES {samples}");
        check(routeSupported,"vision_sorter_infeed_bridge_and_platter_support_sampled_full_carton_footprint");
        GD.Print($"VISION_SORTER_CARTON_SUPPORT carton={carton} belt={belt}");
        check(MathF.Abs(carton.Position.Y - belt.End.Y) < .001f,
            "vision_sorter_carton_bottom_contacts_actual_delivered_belt_top");
        check(carton.Position.X >= belt.Position.X && carton.End.X <= belt.End.X
            && carton.Position.Z >= belt.Position.Z && carton.End.Z <= belt.End.Z,
            "vision_sorter_initial_carton_full_footprint_is_supported");
    }

    // Conservative drum silhouette test for this installation: clip every
    // bridge triangle's XY projection against the actual drum vertex hull,
    // eroded by a declared 1 mm allowance. No blanket drum exclusion.
    private static bool VisionSorterDrumProfileClear(MeshInstance3D deck, MeshInstance3D drum)
    {
        var points=drum.Mesh.GetFaces().Select(v=>drum.GlobalTransform*v)
            .Select(v=>new Vector2(v.X,v.Y)).Distinct().OrderBy(v=>v.X).ThenBy(v=>v.Y).ToArray();
        float Cross(Vector2 a,Vector2 b)=>a.X*b.Y-a.Y*b.X;
        var hull=new System.Collections.Generic.List<Vector2>();
        foreach(var p in points)
        {
            while(hull.Count>=2 && Cross(hull[^1]-hull[^2],p-hull[^1])<=0)hull.RemoveAt(hull.Count-1);
            hull.Add(p);
        }
        var lower=hull.Count;
        for(var i=points.Length-2;i>=0;i--)
        {
            var p=points[i];
            while(hull.Count>lower && Cross(hull[^1]-hull[^2],p-hull[^1])<=0)hull.RemoveAt(hull.Count-1);
            hull.Add(p);
        }
        if(hull.Count>1)hull.RemoveAt(hull.Count-1);
        if(hull.Count<3)return false;
        var faces=deck.Mesh.GetFaces();var drumBounds=ReviewBounds(drum);
        for(var i=0;i<faces.Length;i+=3)
        {
            var triangle=new[]{deck.GlobalTransform*faces[i],deck.GlobalTransform*faces[i+1],deck.GlobalTransform*faces[i+2]};
            if(triangle.All(v=>v.Z<drumBounds.Position.Z) || triangle.All(v=>v.Z>drumBounds.End.Z))continue;
            var clipped=triangle.Select(v=>new Vector2(v.X,v.Y)).ToList();
            for(var edge=0;edge<hull.Count && clipped.Count>0;edge++)
            {
                var origin=hull[edge];var direction=hull[(edge+1)%hull.Count]-origin;
                float Distance(Vector2 v)=>Cross(direction,v-origin)-.001f*direction.Length();
                var next=new System.Collections.Generic.List<Vector2>();
                var previous=clipped[^1];var before=Distance(previous);
                foreach(var current in clipped)
                {
                    var after=Distance(current);
                    if((before>=0)!=(after>=0))next.Add(previous+(current-previous)*(before/(before-after)));
                    if(after>=0)next.Add(current);
                    previous=current;before=after;
                }
                clipped=next;
            }
            if(clipped.Count>0)
            {
                GD.Print($"VISION_SORTER_DRUM_PROFILE_INTERFERENCE triangle={i/3}");return false;
            }
        }
        GD.Print("VISION_SORTER_DRUM_PROFILE_CLEAR declared_allowance_mm=1");
        return true;
    }

    private void VerifyCartonStaticCableRoutes(Action<bool, string> check,
        string sceneId = "scene-2-conveyor-pusher", string checkPrefix = "scene2")
    {
        AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
        var equipment = _sceneCompositionRoot!.GetChildren().OfType<Node3D>()
            .Select(node => (Node: node, Meshes: ReviewMeshes(node))).ToArray();
        var candidates = 0; var unresolved = 0;
        bool Cable(MeshInstance3D mesh) => mesh.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase);
        for (var a = 0; a < equipment.Length; a++)
        for (var b = a + 1; b < equipment.Length; b++)
        foreach (var left in equipment[a].Meshes)
        foreach (var right in equipment[b].Meshes)
        {
            var overlap = ReviewBounds(left).Intersection(ReviewBounds(right)).Size;
            if (overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f) continue;
            candidates++;
            var cable = Cable(left) ? left : Cable(right) ? right : null;
            var other = cable == left ? right : left;
            var surfaceCandidate = cable is null;
            if (cable is not null)
            {
                // Screen each actual cable triangle in the other component's
                // local frame. This excludes empty route bounds. A remaining
                // candidate still needs inspection: the other mesh's local box
                // can contain empty space. Cable pairs also screen against
                // individual triangles rather than the entire second route.
                var transform = other.GlobalTransform.AffineInverse() * cable.GlobalTransform;
                // Convert a 1 mm world allowance into each local axis; authored
                // equipment scales must not silently change the tolerance.
                var basis = other.GlobalTransform.Basis;
                var padding = new Vector3(0.001f / basis.X.Length(),
                    0.001f / basis.Y.Length(), 0.001f / basis.Z.Length());
                var authored = other.GetAabb();
                var bounds = new Aabb(authored.Position + padding, authored.Size - padding * 2);
                var otherFaces = Cable(other) ? other.Mesh.GetFaces() : System.Array.Empty<Vector3>();
                var otherTriangles = Enumerable.Range(0, otherFaces.Length / 3).Select(index =>
                    new Aabb(otherFaces[index * 3], Vector3.Zero)
                        .Expand(otherFaces[index * 3 + 1]).Expand(otherFaces[index * 3 + 2])).ToArray();
                var faces = cable.Mesh.GetFaces();
                for (var index = 0; index < faces.Length && !surfaceCandidate; index += 3)
                {
                    var triangle = new Aabb(transform * faces[index], Vector3.Zero)
                        .Expand(transform * faces[index + 1]).Expand(transform * faces[index + 2]);
                    surfaceCandidate = triangle.Grow(0.0001f).Intersects(bounds)
                        && (otherTriangles.Length == 0 || otherTriangles.Any(otherTriangle =>
                            triangle.Grow(0.0001f).Intersects(otherTriangle)));
                }
            }
            if (surfaceCandidate)
            {
                unresolved++;
                GD.Print($"CARTON_STATIC_ROUTE_BOUNDS left={ReviewBounds(left)} right={ReviewBounds(right)}");
            }
            GD.Print($"CARTON_STATIC_ROUTE {equipment[a].Node.Name}/{left.Name} {equipment[b].Node.Name}/{right.Name} surfaceCandidate={surfaceCandidate}");
        }
        GD.Print($"CARTON_STATIC_ROUTE_TOTAL broad={candidates} unresolved={unresolved}");
        check(unresolved == 0, $"{checkPrefix}_static_routes_clear_other_equipment_local_bounds_at_one_mm_tolerance");
    }
}
