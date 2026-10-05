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
        }
        catch (Exception error)
        {
            passed = false;
            GD.PushError($"CARTON_STATIC_CHECK exception: {error}");
        }
        GetTree().Quit(passed ? 0 : 1);
    }

    private void VerifyCartonStaticCableRoutes(Action<bool, string> check)
    {
        AddMigratedScene("scene-2-conveyor-pusher", _candidateCatalog!, _mainCamera!, false, false);
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
        check(unresolved == 0, "scene2_static_routes_clear_other_equipment_local_bounds_at_one_mm_tolerance");
    }
}
