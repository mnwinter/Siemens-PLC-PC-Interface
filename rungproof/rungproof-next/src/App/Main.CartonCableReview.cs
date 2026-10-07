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
        var receiver = root.GetNode<Node3D>("training_accessory_8");
        var receivingBelt = (MeshInstance3D)receiver.FindChild("KIN_belt_surface", true, false);
        GD.Print($"VISION_SORTER_RECEIVING infeed={belt} platter={ReviewBounds(platter)} bank={ReviewBounds(receivingBelt)}");
        GD.Print($"VISION_SORTER_RECEIVING_GAP x={ReviewBounds(platter).Position.X-belt.End.X} deckDelta={ReviewBounds(platter).End.Y-belt.End.Y} bankBeltCount={receiver.FindChildren("KIN_belt_surface", "MeshInstance3D", true, false).Count}");
        GD.Print($"VISION_SORTER_CARTON_SUPPORT carton={carton} belt={belt}");
        check(MathF.Abs(carton.Position.Y - belt.End.Y) < .001f,
            "vision_sorter_carton_bottom_contacts_actual_delivered_belt_top");
        check(carton.Position.X >= belt.Position.X && carton.End.X <= belt.End.X
            && carton.Position.Z >= belt.Position.Z && carton.End.Z <= belt.End.Z,
            "vision_sorter_initial_carton_full_footprint_is_supported");
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
