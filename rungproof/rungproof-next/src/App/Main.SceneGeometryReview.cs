using System;
using System.Linq;
using Godot;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _verifySceneGeometry;
    private bool _reportSceneGeometry;
    private bool _visualSceneReview;
    private Label? _visualReviewLabel;
    private bool _visualReviewClose;

    // This opt-in inspection bar uses the real shell, scene composer, meshes
    // and camera. It does not execute scene actions or open a PLC connection.
    private void AddVisualSceneReviewControls()
    {
        var layer = new CanvasLayer { Name = "VisualSceneReview", Layer = 20 };
        AddChild(layer);
        var bar = new HBoxContainer { Position = new Vector2(310, 126) };
        layer.AddChild(bar);
        if (_simulatorShell is not null)
            _simulatorShell.ProductViewChanged += view => bar.Visible = view == "operator";
        void Button(string text, Action action)
        {
            var button = new Godot.Button { Text = text };
            button.Pressed += action;
            bar.AddChild(button);
        }
        Button("Previous", () => ChangeVisualReviewScene(-1));
        Button("Next", () => ChangeVisualReviewScene(1));
        Button("Front right", () => SetVisualReviewAngle(new Vector3(11, 7, 12), "front-right"));
        Button("Front left", () => SetVisualReviewAngle(new Vector3(-11, 7, 12), "front-left"));
        Button("Rear left", () => SetVisualReviewAngle(new Vector3(-11, 7, -12), "rear-left"));
        Button("Rear right", () => SetVisualReviewAngle(new Vector3(11, 7, -12), "rear-right"));
        Button("Top", () => SetVisualReviewAngle(new Vector3(0.01f, 20, 0.01f), "top"));
        Button("Wide / close", () =>
        {
            _visualReviewClose = !_visualReviewClose;
            SetVisualReviewAngle(_sceneCameraDirection, _visualReviewClose ? "close-up" : "wide");
        });
        _visualReviewLabel = new Label();
        bar.AddChild(_visualReviewLabel);
        UpdateVisualReviewLabel();
    }

    private void ChangeVisualReviewScene(int step)
    {
        if (_sceneCatalog is null || _candidateCatalog is null || _mainCamera is null) return;
        var scenes = _sceneCatalog.Scenes;
        var index = scenes.ToList().FindIndex(scene => scene.Id == _currentSceneId);
        var next = scenes[(index + step + scenes.Count) % scenes.Count];
        // Use the same request path as the browser, including workspace and
        // ladder replacement guards, rather than bypassing them in QA mode.
        _simulatorShell?.RequestSceneChange(next.Id);
    }

    private void UpdateVisualReviewLabel()
    {
        if (_sceneCatalog is null || _visualReviewLabel is null) return;
        var index = _sceneCatalog.Scenes.ToList().FindIndex(scene => scene.Id == _currentSceneId);
        _visualReviewLabel.Text = $"{index + 1}/{_sceneCatalog.Scenes.Count}";
        GD.Print($"VISUAL_REVIEW_SCENE {_currentSceneId} index={index + 1}");
        if (_sceneCompositionRoot is not null) LogBoundsCandidates(_sceneCompositionRoot);
    }

    private void SetVisualReviewAngle(Vector3 direction, string label)
    {
        if (_mainCamera is null || _sceneCompositionRoot is null) return;
        FrameComposition(_mainCamera, _sceneCompositionRoot, direction);
        if (_visualReviewClose && _cameraController is not null)
        {
            var target = _cameraController.ViewTarget;
            _cameraController.FocusOn(target, _mainCamera.Position.DistanceTo(target) * 0.58f / 2.6f);
        }
        _sceneCameraDirection = direction;
        GD.Print($"VISUAL_REVIEW_ANGLE {_currentSceneId} {label}");
    }

    private static MeshInstance3D[] ReviewMeshes(Node root) =>
        root.FindChildren("*", "MeshInstance3D", true, false).OfType<MeshInstance3D>()
            .Where(mesh => mesh.Mesh is not null && mesh.IsVisibleInTree()).ToArray();

    private static Aabb ReviewBounds(MeshInstance3D mesh)
    {
        var local = mesh.GetAabb();
        var minimum = new Vector3(float.PositiveInfinity, float.PositiveInfinity, float.PositiveInfinity);
        var maximum = new Vector3(float.NegativeInfinity, float.NegativeInfinity, float.NegativeInfinity);
        for (var corner = 0; corner < 8; corner++)
        {
            var point = mesh.GlobalTransform * (local.Position + local.Size * new Vector3(
                (corner & 1) == 0 ? 0 : 1, (corner & 2) == 0 ? 0 : 1, (corner & 4) == 0 ? 0 : 1));
            minimum = new Vector3(MathF.Min(minimum.X, point.X), MathF.Min(minimum.Y, point.Y), MathF.Min(minimum.Z, point.Z));
            maximum = new Vector3(MathF.Max(maximum.X, point.X), MathF.Max(maximum.Y, point.Y), MathF.Max(maximum.Z, point.Z));
        }
        return new Aabb(minimum, maximum - minimum);
    }

    private static Aabb ReviewBounds(Node root) => root is MeshInstance3D mesh
        ? ReviewBounds(mesh)
        : ReviewMeshes(root).Select(ReviewBounds).Aggregate((a, b) => a.Merge(b));

    // Broad-phase candidates guide visual inspection; overlapping bounds on
    // curved/rotated meshes are not proof of solid interference. Intentional
    // machine connections can also intersect and require interpretation.
    private int LogBoundsCandidates(Node3D root)
    {
        var total = 0;
        var equipment = root.GetChildren().OfType<Node3D>()
            .Select(node => (Node: node, Meshes: ReviewMeshes(node)
                .Select(mesh => (Name: mesh.Name.ToString(), Bounds: ReviewBounds(mesh))).ToArray())).ToArray();
        for (var a = 0; a < equipment.Length; a++)
        for (var b = a + 1; b < equipment.Length; b++)
        {
            var candidates = 0;
            var example = string.Empty;
            foreach (var left in equipment[a].Meshes)
            foreach (var right in equipment[b].Meshes)
            {
                var overlap = left.Bounds.Intersection(right.Bounds).Size;
                if (overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f) continue;
                candidates++;
                if (example.Length == 0) example = $"{left.Name}/{right.Name}";
            }
            if (candidates > 0)
            {
                total += candidates;
                GD.Print($"BOUNDS_CANDIDATE {_currentSceneId} {equipment[a].Node.Name}/{equipment[b].Node.Name} count={candidates} example={example}");
            }
        }
        return total;
    }

    // This inventory only identifies candidates for a human camera review.
    // A successful report means the inventory ran, not that scenes are clear.
    private async void ReportSceneGeometry()
    {
        try
        {
            foreach (var scene in _sceneCatalog!.Scenes)
            {
                AddMigratedScene(scene.Id, _candidateCatalog!, _mainCamera!, false, false);
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                var root = _sceneCompositionRoot!;
                foreach (var equipment in root.GetChildren().OfType<Node3D>())
                {
                    if (ReviewMeshes(equipment).Length > 0)
                        GD.Print($"GEOMETRY_EQUIPMENT {scene.Id} {equipment.Name} {ReviewBounds(equipment)}");
                }
                GD.Print($"GEOMETRY_INVENTORY {scene.Id} candidates={LogBoundsCandidates(root)}");
            }
            GD.Print($"GEOMETRY_INVENTORY_COMPLETE scenes={_sceneCatalog.Scenes.Count} visual acceptance pending");
            GetTree().Quit();
        }
        catch (Exception exception)
        {
            GD.PushError($"GEOMETRY_INVENTORY_ERROR {exception}");
            GetTree().Quit(1);
        }
    }

    private void VerifySceneGeometry()
    {
        try
        {
            AddMigratedScene("lab-11-13-xy-palletizing", _candidateCatalog!, _mainCamera!, false, false);
            var root = _sceneCompositionRoot!;
            var gantry = root.GetNode<Node3D>("training_accessory_4");
            var pallet = root.GetNode<Node3D>("training_accessory_6");
            var carton = root.GetNode<Node3D>("box_2");
            var conveyor = root.GetNode<Node3D>("conveyor_1");
            var staticCandidates = LogBoundsCandidates(root);
            var palletBounds = ReviewBounds(pallet);
            var cartonBounds = ReviewBounds(carton);
            foreach (var mesh in ReviewMeshes(gantry))
                GD.Print($"GEOMETRY_MESH {mesh.Name} {ReviewBounds(mesh)}");
            GD.Print($"GEOMETRY_PALLET {palletBounds}");
            GD.Print($"GEOMETRY_CARTON {cartonBounds}");
            var passed = true;
            void Check(bool condition, string label)
            {
                passed &= condition;
                GD.Print($"SCENE_GEOMETRY_CHECK {label}={condition}");
            }
            Check(staticCandidates == 0, "demo5_static_equipment_clearance_screen");
            var posts = ReviewMeshes(gantry).Where(mesh => mesh.Name.ToString().StartsWith("GANTRY_POST", StringComparison.Ordinal)).ToArray();
            Check(posts.Length == 4 && posts.All(post => !ReviewBounds(post).Intersects(palletBounds)), "pallet_clear_of_all_four_gantry_posts");
            var deck = ReviewMeshes(conveyor).Where(mesh => mesh.Name.ToString().Contains("belt_surface", StringComparison.OrdinalIgnoreCase)).ToArray();
            foreach (var mesh in ReviewMeshes(conveyor)) GD.Print($"GEOMETRY_CONVEYOR {mesh.Name} {ReviewBounds(mesh)}");
            Check(deck.Length > 0 && deck.Any(mesh =>
            {
                var bounds = ReviewBounds(mesh);
                return cartonBounds.Position.X >= bounds.Position.X && cartonBounds.End.X <= bounds.End.X
                    && cartonBounds.Position.Z >= bounds.Position.Z && cartonBounds.End.Z <= bounds.End.Z
                    && MathF.Abs(cartonBounds.Position.Y - bounds.End.Y) < 0.015f;
            }), "carton_supported_on_conveyor_deck");
            var rod = gantry.FindChildren("KIN_Z_AXIS*", "Node3D", true, false).OfType<Node3D>().First();
            var tool = gantry.FindChildren("GANTRY_GRIPPER*", "Node3D", true, false).OfType<Node3D>().First();
            var relative = tool.GlobalPosition - rod.GlobalPosition;
            var authoredTool = tool.Transform;
            var motion = gantry.GetNode<EquipmentMotionController>("GantryCommandMotion");
            motion.Run();
            var sweepClear = true;
            var attached = true;
            var toolMoved = false;
            for (var step = 0; step < 150; step++)
            {
                motion._PhysicsProcess(0.02);
                attached &= (tool.GlobalPosition - rod.GlobalPosition).IsEqualApprox(relative);
                toolMoved |= tool.Transform != authoredTool;
                sweepClear &= posts.All(post => !ReviewBounds(post).Intersects(ReviewBounds(tool)));
            }
            Check(attached && toolMoved, "gripper_follows_z_axis_through_complete_sweep");
            Check(sweepClear, "gripper_sweep_clear_of_posts");
            motion._PhysicsProcess(0.37);
            motion.Stop();
            var heldTool = tool.Transform;
            motion._PhysicsProcess(0.4);
            Check(tool.Transform == heldTool, "gripper_holds_with_stopped_axes");
            motion.ResetMotion();
            Check(tool.Transform == authoredTool, "gripper_reset_restores_attached_authored_pose");
            GD.Print($"SCENE_GEOMETRY_VERIFY {(passed ? "PASS" : "FAIL")} bounds screen only; no mechanical or live acceptance");
            GetTree().Quit(passed ? 0 : 1);
        }
        catch (Exception exception)
        {
            GD.PushError($"SCENE_GEOMETRY_VERIFY FAIL {exception}");
            GetTree().Quit(1);
        }
    }
}
