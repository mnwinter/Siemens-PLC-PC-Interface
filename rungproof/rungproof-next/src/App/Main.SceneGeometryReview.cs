using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using RungProof.Next.Scenes;

namespace RungProof.Next.App;

public partial class Main
{
    private bool _verifySceneGeometry;
    private bool _reportSceneGeometry;
    private bool _visualSceneReview;
    private bool _visualPlantReview;
    private Label? _visualReviewLabel;
    private bool _visualReviewClose;
    private OptionButton? _visualReviewFocus;
    private string? _visualReviewFocusId;
    private HBoxContainer? _visualReviewBar;

    // This opt-in inspection bar uses the real shell, scene composer, meshes
    // and camera. It does not execute scene actions or open a PLC connection.
    private void AddVisualSceneReviewControls()
    {
        var layer = new CanvasLayer { Name = "VisualSceneReview", Layer = 20 };
        AddChild(layer);
        var bar = new HBoxContainer { Position = _visualPlantReview ? new Vector2(400, 18) : new Vector2(310, 126) };
        _visualReviewBar = bar;
        layer.AddChild(bar);
        if (_simulatorShell is not null)
            _simulatorShell.ProductViewChanged += view => bar.Visible = view == "operator";
        void Button(string text, Action action)
        {
            var button = new Godot.Button { Text = text };
            button.Pressed += action;
            bar.AddChild(button);
        }
        if (!_visualPlantReview)
        {
            Button("Previous", () => ChangeVisualReviewScene(-1));
            Button("Next", () => ChangeVisualReviewScene(1));
        }
        else bar.AddChild(new Label { Text = "PLANT PREVIEW · NO PLC CONTROLLER" });
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
        _visualReviewFocus = new OptionButton { CustomMinimumSize = new Vector2(180, 0) };
        _visualReviewFocus.ItemSelected += index =>
        {
            _visualReviewFocusId = index == 0 ? null : _visualReviewFocus.GetItemText((int)index);
            _visualReviewClose = false;
            SetVisualReviewAngle(_sceneCameraDirection, $"focus-{_visualReviewFocusId ?? "scene"}");
        };
        bar.AddChild(_visualReviewFocus);
        UpdateVisualReviewLabel();
        if (_visualPlantReview && _sceneRuntime is not null)
        {
            // Standalone QA must expose both directions/actions, not only the
            // default sequence. Keep this out of the controller-owned shell.
            var runtime = _sceneRuntime;
            var actions = runtime.GetActions();
            var actionBar = new HBoxContainer { Position = new Vector2(18, 240) };
            layer.AddChild(actionBar);
            var choice = new OptionButton { CustomMinimumSize = new Vector2(280, 0) };
            foreach (var action in actions) choice.AddItem(action.Label);
            actionBar.AddChild(choice);
            var execute = new Godot.Button { Text = "Preview action", Disabled = actions.Count == 0 };
            execute.Pressed += () => runtime.ExecuteAction(actions[choice.Selected].Id);
            actionBar.AddChild(execute);
        }
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
        _visualReviewFocusId = null;
        _visualReviewFocus?.Clear();
        _visualReviewFocus?.AddItem("Full scene");
        if (_sceneCompositionRoot is not null)
            foreach (var node in _sceneCompositionRoot.GetChildren().OfType<Node3D>().Where(node => ReviewMeshes(node).Length > 0))
                _visualReviewFocus?.AddItem(node.Name);
        GD.Print($"VISUAL_REVIEW_SCENE {_currentSceneId} index={index + 1}");
        if (_sceneCompositionRoot is not null) LogBoundsCandidates(_sceneCompositionRoot);
    }

    private void SetVisualReviewAngle(Vector3 direction, string label)
    {
        if (_mainCamera is null || _sceneCompositionRoot is null) return;
        var focus = _visualReviewFocusId is null ? _sceneCompositionRoot
            : _sceneCompositionRoot.GetNodeOrNull<Node3D>(_visualReviewFocusId) ?? _sceneCompositionRoot;
        FrameComposition(_mainCamera, focus, direction);
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

            AddMigratedScene("lab-11-19-powder-batch-mixer", _candidateCatalog!, _mainCamera!, false, false);
            var mixer = _sceneCompositionRoot!;
            Check(LogBoundsCandidates(mixer) == 0, "mixer_static_equipment_clearance_screen");
            var tankShells = ReviewMeshes(mixer).Where(mesh => mesh.Name == "TANK_shell").ToArray();
            Check(tankShells.Length == 3 && tankShells.All(shell =>
            {
                var size = ReviewBounds(shell).Size;
                return MathF.Abs(size.X - 2.6f) < 0.01f && MathF.Abs(size.Y - 2.5f) < 0.01f
                    && MathF.Abs(size.Z - 2.6f) < 0.01f;
            }), "mixer_tank_shells_match_authored_dimensions");
            var chute = mixer.GetNode<Node3D>("training_accessory_10");
            var chuteMeshes = ReviewMeshes(chute);
            Check(chuteMeshes.Any(mesh => mesh.Name == "CHUTE_bottom")
                && chuteMeshes.Count(mesh => mesh.Name.ToString().StartsWith("CHUTE_side_", StringComparison.Ordinal)) == 2
                && !chuteMeshes.Any(mesh => mesh.Name.ToString().Contains("SHUTTER", StringComparison.Ordinal)),
                "mixer_chute_is_open_channel_without_door_geometry");
            Check(MathF.Abs(ReviewBounds(chute).Position.Y) < 0.01f
                && MathF.Abs(ReviewBounds(mixer.GetNode<Node3D>("valve_4")).Position.Y) < 0.01f,
                "mixer_chute_and_valve_supports_rest_on_floor");

            VerifyParcelGeometry(Check);
            VerifyInspectionConveyorGeometry(Check);
            VerifyGalleryGeometry(Check);
            VerifyDriveAlarmGeometry(Check);
            VerifyMotorStateProjection(Check);
            VerifyLabelPrintGeometry(Check);
            VerifySelectorProjection(Check);
            VerifyInboundToteGeometry(Check);
            VerifyAssemblyLiftGeometry(Check);

            AddMigratedScene("tank-radar", _candidateCatalog!, _mainCamera!, false, false);
            // Exercise an authored parent scale as well as configured sizing.
            var radarTank = _sceneCompositionRoot!.GetNode<Node3D>("water_tank_radar");
            radarTank.Scale = new Vector3(0.7f, 0.6f, 0.7f);
            _sceneRuntime!.ResetSimulation();
            var liquid = radarTank.FindChild("KIN_liquid", true, false) as MeshInstance3D;
            var transmitter = _sceneCompositionRoot.GetNode<Node3D>("radar_transmitter");
            var expectedDistance = Math.Max(0.08, transmitter.GlobalPosition.Y - ReviewBounds(liquid!).End.Y);
            var actualDistance = Convert.ToDouble(_sceneRuntime.Points["radar_distance"]);
            GD.Print($"RADAR_GEOMETRY expected={expectedDistance} actual={actualDistance}");
            Check(Math.Abs(actualDistance - expectedDistance) < 0.001, "radar_distance_uses_world_scaled_liquid_surface");
            GD.Print($"SCENE_GEOMETRY_VERIFY {(passed ? "PASS" : "FAIL")} bounds screen only; no mechanical or live acceptance");
            GetTree().Quit(passed ? 0 : 1);
        }
        catch (Exception exception)
        {
            GD.PushError($"SCENE_GEOMETRY_VERIFY FAIL {exception}");
            GetTree().Quit(1);
        }
    }

    private void VerifyParcelGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-23-parcel-sorter", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        var definition = SceneCatalogLoader.LoadScene(_sceneCatalog!.Scenes.First(scene => scene.Id == "lab-2-23-parcel-sorter"));
        var equipment = root.GetChildren().OfType<Node3D>().ToArray();
        var cartons = equipment.Where(node => node.Name.ToString().EndsWith("_parcel", StringComparison.Ordinal)).ToArray();
        var authored = cartons.ToDictionary(node => node, node => node.Transform);
        var tables = equipment.Where(node => node.Name.ToString().StartsWith("sort_turntable_", StringComparison.Ordinal)).ToArray();
        var motions = tables.SelectMany(node => node.FindChildren("*", string.Empty, true, false)
            .OfType<EquipmentMotionController>()).ToArray();
        check(tables.Length == 2 && motions.Length == 2 && tables.All(table => !ReviewMeshes(table).Any(mesh =>
            mesh.Name.ToString().StartsWith("TABLE_fixture_", StringComparison.Ordinal))), "parcel_tables_have_no_machining_jaws_in_load_path");
        check(equipment.Where(node => definition.Equipment.Any(item => item.Id == node.Name && item.Type == "conveyor"))
            .All(node => MathF.Abs(ReviewBounds(node).Position.Y) < 0.01f), "parcel_conveyor_feet_grounded");
        var deck = root.GetNode<Node3D>("sort_infeed").FindChild("KIN_belt_surface", true, false) as MeshInstance3D;
        var deckBounds = ReviewBounds(deck!);
        check(MathF.Abs(deckBounds.Size.Z - 1.2f) < 0.01f && MathF.Abs(deckBounds.End.Y - 1.055f) < 0.01f,
            "parcel_infeed_honors_belt_width_and_deck_height");
        var portal = root.GetNode<Node3D>("size_sensor_bank");
        var beamHeights = Enumerable.Range(1, 3).Select(channel =>
            ReviewBounds((MeshInstance3D)portal.FindChild($"KIN_beam_size_{channel}", true, false)).GetCenter().Y).ToArray();
        var parcelTops = new[] { "small_parcel", "medium_parcel", "large_parcel" }
            .Select(id => ReviewBounds(root.GetNode<Node3D>(id)).End.Y).ToArray();
        check(beamHeights[0] > deckBounds.End.Y && beamHeights[0] < parcelTops[0]
            && beamHeights[1] > parcelTops[0] && beamHeights[1] < parcelTops[1]
            && beamHeights[2] > parcelTops[1] && beamHeights[2] < parcelTops[2],
            "parcel_optical_beams_clear_deck_and_distinguish_three_carton_heights");

        var cartonSizes = cartons.ToDictionary(node => node, node => definition.Equipment.First(item => item.Id == node.Name)
            .Config.GetProperty("size").EnumerateArray().Select(value => value.GetSingle()).ToArray());
        var supports = definition.Equipment.Where(item => item.Type is "conveyor" or "rotaryTable").Select(item =>
        {
            var node = root.GetNode<Node3D>(item.Id);
            return (Inverse: node.GlobalTransform.AffineInverse(), Height: item.Config.GetProperty("deckHeight").GetSingle(),
                Circle: item.Type == "rotaryTable", HalfLength: item.Type == "conveyor" ? item.Config.GetProperty("length").GetSingle() * 2.935f / 6f : 0,
                HalfWidth: item.Type == "conveyor" ? item.Config.GetProperty("width").GetSingle() / 2f : 0,
                Radius: item.Type == "rotaryTable" ? item.Config.GetProperty("radius").GetSingle() : 0);
        }).ToArray();
        // These supports/frames stay fixed throughout the declared path. The
        // only rotating table surfaces are below the cartons' bottom plane.
        // Cache their bounds rather than making millions of Godot interop calls.
        var solids = equipment.Except(cartons).SelectMany(node => ReviewMeshes(node).Where(mesh =>
            !mesh.Name.ToString().Contains("beam", StringComparison.OrdinalIgnoreCase))
            .Select(mesh => (Equipment: node.Name, Mesh: mesh.Name, Node: mesh, Bounds: ReviewBounds(mesh))))
            .Where(solid => solid.Bounds.End.Y > 1.061f).ToArray();
        var cartonMeshes = cartons.ToDictionary(node => node, ReviewMeshes);

        bool Supported(Node3D carton)
        {
            var size = cartonSizes[carton];
            var transform = carton.GlobalTransform;
            var contacts = new List<Vector2>();
            // Sample actual oriented bottom footprints, including transitions
            // across the small nose gaps. A support hull containing the center
            // checks balanced geometry; it is not a dynamics/load calculation.
            for (var ix = 0; ix < 7; ix++)
            for (var iz = 0; iz < 7; iz++)
            {
                var point = transform * new Vector3(size[0] * (ix / 6f - 0.5f), 0, size[2] * (iz / 6f - 0.5f));
                foreach (var support in supports)
                {
                    var local = support.Inverse * point;
                    if (MathF.Abs(local.Y - support.Height) > 0.015f) continue;
                    var covered = !support.Circle
                        ? MathF.Abs(local.X) <= support.HalfLength && MathF.Abs(local.Z) <= support.HalfWidth
                        : new Vector2(local.X, local.Z).Length() <= support.Radius;
                    if (!covered) continue;
                    contacts.Add(new Vector2(point.X, point.Z));
                    break;
                }
            }
            if (contacts.Count < 18) return false;
            var hull = ContactHull(contacts);
            var center = new Vector2(carton.GlobalPosition.X, carton.GlobalPosition.Z);
            return hull.Count >= 3 && Enumerable.Range(0, hull.Count).All(index =>
                (hull[(index + 1) % hull.Count] - hull[index]).Cross(center - hull[index]) >= -0.001f);
        }

        var supported = cartons.Length == 3 && cartons.All(Supported);
        var clear = true;
        var reported = false;
        runtime.UsesExternalClock = false; // Declared plant preview only, no controller/PLC seam.
        runtime.ExecuteAction("start-sort");
        for (var frame = 0; frame < 2300; frame++)
        {
            runtime.AdvanceSimulation(0.02);
            foreach (var motion in motions) motion._PhysicsProcess(0.02);
            supported &= cartons.All(Supported);
            var cartonBounds = cartons.ToDictionary(node => node, ReviewBounds);
            foreach (var carton in cartons)
            foreach (var solid in solids.Concat(cartons.Where(node => node != carton).SelectMany(node =>
                cartonMeshes[node].Select(mesh => (Equipment: node.Name, Mesh: mesh.Name, Node: mesh, Bounds: cartonBounds[node])))))
            {
                var overlap = cartonBounds[carton].Intersection(solid.Bounds).Size;
                if (overlap.X <= 0.005f || overlap.Y <= 0.005f || overlap.Z <= 0.005f) continue;
                if (!cartonMeshes[carton].Any(mesh => OrientedBoxesPenetrate(mesh, solid.Node))) continue;
                clear = false;
                if (!reported)
                {
                    GD.Print($"PARCEL_PATH_INTERFERENCE frame={frame} {carton.Name}/{solid.Equipment} mesh={solid.Mesh} overlap={overlap}");
                    reported = true;
                }
            }
        }
        check(supported, "parcel_full_path_has_balanced_surface_contacts");
        check(clear, "parcel_full_path_clear_of_other_cartons_and_solid_equipment");
        check(Convert.ToInt64(runtime.Points["sorted_count"]) == 3 && runtime.Points["cycle_complete"] is true,
            "parcel_supported_path_finishes_three_way_batch");

        runtime.ResetSimulation();
        runtime.ExecuteAction("start-sort");
        for (var frame = 0; frame < 870; frame++)
        {
            runtime.AdvanceSimulation(0.02);
            foreach (var motion in motions) motion._PhysicsProcess(0.02);
        }
        runtime.StopSimulation();
        var held = cartons.ToDictionary(node => node, node => node.Transform);
        var heldPlates = tables.Select(table => table.FindChild("KIN_table", true, false) as Node3D).ToArray();
        var heldTransforms = heldPlates.Select(plate => plate!.Transform).ToArray();
        runtime.AdvanceSimulation(0.4);
        foreach (var motion in motions) motion._PhysicsProcess(0.4);
        check(cartons.All(node => node.Transform == held[node]) && heldPlates.Select((plate, index) =>
            plate!.Transform == heldTransforms[index]).All(value => value), "parcel_stop_holds_cartons_and_indexing_tables");
        runtime.ResetSimulation();
        check(cartons.All(node => node.Transform == authored[node]) && motions.All(motion => motion.PositionPercent == 0),
            "parcel_reset_restores_cartons_and_table_pose");
    }

    private void VerifyInspectionConveyorGeometry(Action<bool, string> check)
    {
        AddMigratedScene("conveyor-cell", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        var conveyor = root.GetNode<Node3D>("main_conveyor");
        var cartons = Enumerable.Range(1, 3).Select(index => root.GetNode<Node3D>($"carton_{index}")).ToArray();
        var authored = cartons.Select(carton => carton.Transform).ToArray();
        var deck = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
        var sensor = root.GetNode<Node3D>("inspection_photoeye");
        var stands = ReviewMeshes(sensor).Where(mesh => mesh.Name.ToString() is "TX_post" or "RX_post").ToArray();
        var feet = ReviewMeshes(sensor).Where(mesh => mesh.Name.ToString() is "TX_foot" or "RX_foot").ToArray();
        var beams = sensor.FindChildren("KIN_beam*", string.Empty, true, false).OfType<MeshInstance3D>().ToArray();
        foreach (var mesh in stands.Concat(feet)) GD.Print($"INSPECTION_SENSOR_GEOMETRY {mesh.Name} position={mesh.GlobalPosition} bounds={ReviewBounds(mesh)}");
        LogBoundsCandidates(root); // Curved cable boxes can overlap diagonal frame boxes.
        var sensorSolids = ReviewMeshes(sensor).Where(mesh => !mesh.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase)
            && !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)).ToArray();
        var conveyorSolids = ReviewMeshes(conveyor).Where(mesh => !mesh.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase)).ToArray();
        foreach (var sensorMesh in sensorSolids)
        foreach (var conveyorMesh in conveyorSolids)
            if (OrientedBoxesPenetrate(sensorMesh, conveyorMesh))
                GD.Print($"INSPECTION_SOLID_INTERFERENCE {sensorMesh.Name}/{conveyorMesh.Name}");
        check(sensorSolids.All(sensorMesh => conveyorSolids.All(conveyorMesh => !OrientedBoxesPenetrate(sensorMesh, conveyorMesh))),
            "inspection_sensor_solid_parts_clear_conveyor_frames");
        check(cartons.All(carton => MathF.Abs(ReviewBounds(carton).Position.Y - deck.End.Y) < 0.01f),
            "inspection_cartons_rest_on_actual_belt_surface");
        check(stands.Length == 2 && MathF.Abs(MathF.Abs(stands[0].GlobalPosition.Z - stands[1].GlobalPosition.Z) - 2.6f) < 0.01f
            && feet.Length == 2 && feet.All(foot => MathF.Abs(ReviewBounds(foot).Position.Y) < 0.01f),
            "inspection_photoeye_stands_honor_span_and_grounding");
        check(beams.Length > 0 && beams.All(beam => ReviewBounds(beam).GetCenter().Y > deck.End.Y
            && ReviewBounds(beam).GetCenter().Y < cartons.Min(carton => ReviewBounds(carton).End.Y)),
            "inspection_optical_path_crosses_carton_height_above_deck");
        runtime.UsesExternalClock = false; // Bounded declared plant preview, no PLC transport.
        runtime.ExecuteAction("conveyor_run");
        var support = true;
        var sawBlocked = false;
        var sawClear = false;
        var beamMatches = true;
        for (var frame = 0; frame < 1200; frame++)
        {
            runtime.AdvanceSimulation(0.02);
            support &= cartons.All(carton => MathF.Abs(ReviewBounds(carton).Position.Y - deck.End.Y) < 0.01f
                && carton.GlobalPosition.X > deck.Position.X && carton.GlobalPosition.X < deck.End.X);
            var blocked = runtime.Points["photoeye_blocked"] is true;
            sawBlocked |= blocked; sawClear |= !blocked;
            beamMatches &= beams.All(beam => beam.Visible == !blocked);
        }
        check(support && sawBlocked && sawClear && beamMatches && Convert.ToInt64(runtime.Points["parts_completed"]) > 0,
            "inspection_circulation_holds_height_and_projects_beam_feedback");
        runtime.StopSimulation();
        var held = cartons.Select(carton => carton.Transform).ToArray();
        runtime.AdvanceSimulation(0.4);
        var stopped = cartons.Select((carton, index) => carton.Transform == held[index]).All(value => value);
        runtime.ResetSimulation();
        check(stopped && cartons.Select((carton, index) => carton.Transform == authored[index]).All(value => value),
            "inspection_stop_holds_and_reset_restores_cartons");
    }

    private void VerifyDriveAlarmGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-10-01-drive-alarm-code-string", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        check(root.GetChildren().OfType<Node3D>().Where(node => ReviewMeshes(node).Length > 0)
            .All(node => ReviewBounds(node).Position.Y >= -0.005f),
            "drive_alarm_equipment_above_finished_floor");
        check(LogBoundsCandidates(root) == 0, "drive_alarm_separate_equipment_clear");
        check(Enumerable.Range(3, 3).All(index =>
        {
            var prop = root.GetNode<Node3D>($"training_accessory_{index}");
            var foot = ReviewBounds((MeshInstance3D)prop.FindChild("STAND_base", true, false));
            var mast = ReviewBounds((MeshInstance3D)prop.FindChild("STAND_mast", true, false));
            return mast.Position.X >= foot.Position.X && mast.End.X <= foot.End.X
                && mast.Position.Z >= foot.Position.Z && mast.End.Z <= foot.End.Z
                && MathF.Abs(mast.Position.Y - foot.End.Y) < 0.005f;
        }), "drive_alarm_masts_land_on_base_plates");
        // Guard the observed identity failures. This checks geometry families,
        // not manufacturer equivalence or independent asset acceptance.
        check(root.GetNode("training_accessory_3").FindChild("VFD_BODY", true, false) is not null
            && root.GetNode("training_accessory_4").FindChild("ALARM_DISPLAY_screen", true, false) is not null
            && root.GetNode("training_accessory_5").FindChild("LENS_red", true, false) is not null
            && !ReviewMeshes(root).Any(mesh => mesh.Name.ToString().StartsWith("SHUTTER_", StringComparison.Ordinal)
                || mesh.Name.ToString().StartsWith("PANEL_edge_post", StringComparison.Ordinal)
                || mesh.Name == "SERVO_DRIVE"), "drive_alarm_correct_prop_families_replace_inherited_copies");
        var labels = new[] { "MESSAGE VALID", "CODE FOUND", "RESET" };
        check(Enumerable.Range(6, 3).All(index =>
            root.GetNode<Node3D>($"switch_{index}").FindChild("OperatorFaceLabel", true, false) is Label3D label
            && label.Text == labels[index - 6]), "drive_alarm_operator_plates_match_input_functions");
        var alarmLens = (MeshInstance3D)root.GetNode("training_accessory_5").FindChild("LENS_red", true, false);
        // Exercise only the symbolic image boundary; this does not connect to a PLC.
        _sceneRuntime!.CommitExternalPlcOutputs(new Dictionary<string, object?> { ["drive_alarm_active"] = true });
        check(alarmLens.MaterialOverride is StandardMaterial3D { EmissionEnabled: true },
            "drive_alarm_bound_status_lens_projects_true");
        _sceneRuntime.ResetSimulation();
        check(alarmLens.MaterialOverride is StandardMaterial3D { EmissionEnabled: false }
            && _sceneRuntime.Points["drive_alarm_active"] is false, "drive_alarm_reset_clears_status_lens");
    }

    private void VerifyLabelPrintGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-10-02-chicken-label-print", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        check(root.GetChildren().OfType<Node3D>().Where(node => ReviewMeshes(node).Length > 0)
            .All(node => ReviewBounds(node).Position.Y >= -0.005f), "label_print_visible_equipment_above_finished_floor");
        check(LogBoundsCandidates(root) == 0, "label_print_separate_solid_equipment_clear");
        var weigh = root.GetNode<Node3D>("training_accessory_5");
        var deck = ReviewBounds((MeshInstance3D)weigh.FindChild("WEIGH_DECK_surface", true, false));
        var food = ReviewBounds(root.GetNode<Node3D>("training_accessory_4"));
        check(MathF.Abs(deck.End.Y - 0.9f) < 0.005f && MathF.Abs(food.Position.Y - deck.End.Y) < 0.005f
            && food.Position.X >= deck.Position.X && food.End.X <= deck.End.X
            && food.Position.Z >= deck.Position.Z && food.End.Z <= deck.End.Z,
            "label_print_food_tray_supported_by_actual_weigh_deck");
        var carton = ReviewBounds(root.GetNode<Node3D>("box_2"));
        check(ReviewMeshes(root.GetNode("conveyor_0")).Where(mesh => mesh.Name == "KIN_belt_surface").Any(mesh =>
        {
            var belt = ReviewBounds(mesh);
            return MathF.Abs(carton.Position.Y - belt.End.Y) < 0.005f
                && carton.Position.X >= belt.Position.X && carton.End.X <= belt.End.X
                && carton.Position.Z >= belt.Position.Z && carton.End.Z <= belt.End.Z;
        }), "label_print_carton_supported_by_actual_input_belt");
        check(root.GetNode("training_accessory_4").FindChild("FOOD_TRAY_bottom", true, false) is not null
            && weigh.FindChild("WEIGH_DECK_surface", true, false) is not null
            && root.GetNode("training_accessory_6").FindChild("PRINTER_exit_slot", true, false) is not null
            && root.GetNode("training_accessory_7").FindChild("LABEL_DISPLAY_screen", true, false) is not null
            && !ReviewMeshes(root).Any(mesh => mesh.Name.ToString().StartsWith("SHUTTER_", StringComparison.Ordinal)
                || mesh.Name.ToString().StartsWith("PUSHER_", StringComparison.Ordinal)),
            "label_print_correct_training_prop_families");
        var foot = ReviewBounds((MeshInstance3D)weigh.FindChild("WEIGH_readout_foot", true, false));
        var mast = ReviewBounds((MeshInstance3D)weigh.FindChild("WEIGH_readout_mast", true, false));
        check(MathF.Abs(foot.Position.Y) < 0.005f && MathF.Abs(mast.Position.Y - foot.End.Y) < 0.005f
            && mast.Position.X >= foot.Position.X && mast.End.X <= foot.End.X
            && mast.Position.Z >= foot.Position.Z && mast.End.Z <= foot.End.Z,
            "label_print_readout_mast_supported_on_grounded_foot");
        var printer = root.GetNode<Node3D>("training_accessory_6");
        var paper = ReviewBounds((MeshInstance3D)printer.FindChild("PRINTER_demo_paper", true, false));
        var tray = ReviewBounds((MeshInstance3D)printer.FindChild("PRINTER_output_tray", true, false));
        check(MathF.Abs(paper.Position.Y - tray.End.Y) < 0.002f
            && paper.Position.X >= tray.Position.X && paper.End.X <= tray.End.X
            && paper.Position.Z >= tray.Position.Z && paper.End.Z <= tray.End.Z,
            "label_print_demo_paper_rests_on_output_tray");
    }

    private void VerifyMotorStateProjection(Action<bool, string> check)
    {
        AddMigratedScene("lab-10-04-motor-enum-state", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        var labels = new Dictionary<string, string>
        {
            ["switch_1"] = "START REQUEST", ["switch_3"] = "STOP REQUEST", ["switch_4"] = "FAULT ACTIVE",
        };
        check(labels.All(pair => root.GetNode(pair.Key).FindChild("OperatorFaceLabel", true, false)
            is Label3D label && label.Text == pair.Value), "motor_state_operator_plates_identify_distinct_inputs");
        var motor = root.GetNode<Node3D>("motor_0");
        var motion = motor.FindChildren("*", string.Empty, true, false).OfType<EquipmentMotionController>().Single();
        var shaft = motor.FindChildren("KIN_motor_*", string.Empty, true, false).OfType<Node3D>().First();
        var authored = shaft.Transform;
        // Supply the declared symbolic output image only. No controller logic,
        // enum state transitions, or physical PLC behavior is inferred here.
        runtime.CommitExternalPlcOutputs(new Dictionary<string, object?> { ["motor_running"] = true });
        motion._PhysicsProcess(0.137);
        check(motion.Running && shaft.Transform != authored, "motor_state_true_output_turns_actual_shaft");
        runtime.CommitExternalPlcOutputs(new Dictionary<string, object?> { ["motor_running"] = false });
        var held = shaft.Transform;
        motion._PhysicsProcess(0.137);
        check(!motion.Running && shaft.Transform == held, "motor_state_false_output_holds_actual_shaft");
        runtime.ResetSimulation();
        check(!motion.Running && shaft.Transform == authored && runtime.Points["motor_running"] is false,
            "motor_state_reset_restores_shaft_and_output");
    }

    private void VerifyAssemblyLiftGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-12-assembly-lift", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        var lift = root.GetNode<Node3D>("assembly_lift");
        var fixture = root.GetNode<Node3D>("lift_fixture");
        var deck = (MeshInstance3D)lift.FindChild("KIN_platform", true, false);
        var meshes = ReviewMeshes(lift);
        var driveArm = meshes.Single(mesh => mesh.Name == "KIN_scissor_0_-0_65_-1");
        var basePin = meshes.Single(mesh => mesh.Name == "LIFT_cylinder_base_clevis_pin");
        var tipPin = meshes.Single(mesh => mesh.Name == "LIFT_rod_end_clevis_pin");
        var cylinder = meshes.Single(mesh => mesh.Name == "LIFT_cylinder");
        var rod = meshes.Single(mesh => mesh.Name == "KIN_lift_rod");
        var hydraulicParts = meshes.Where(mesh => mesh == cylinder || mesh == rod
            || mesh.Name.ToString().StartsWith("LIFT_rod_end_clevis", StringComparison.Ordinal)
            || mesh.Name == "LIFT_drive_lug").ToArray();
        var hydraulicRest = hydraulicParts.Select(mesh => mesh.Transform).ToArray();
        var tipOnArm = driveArm.ToLocal(tipPin.GlobalPosition);
        // Check the delivered mesh caps, not a controller-owned state variable.
        // The imported cylinders' longest mesh axis defines their centreline.
        (Vector3 A, Vector3 B) Caps(MeshInstance3D member)
        {
            var bounds = member.GetAabb();
            var axis = (int)bounds.Size.MaxAxisIndex();
            var half = Vector3.Zero;
            half[axis] = bounds.Size[axis] * 0.5f;
            return (member.ToGlobal(bounds.GetCenter() - half), member.ToGlobal(bounds.GetCenter() + half));
        }
        var cylinderCaps = Caps(cylinder);
        var cylinderLength = cylinderCaps.A.DistanceTo(cylinderCaps.B);
        var glandRest = cylinderCaps.A.DistanceTo(basePin.GlobalPosition) > cylinderCaps.B.DistanceTo(basePin.GlobalPosition)
            ? cylinderCaps.A : cylinderCaps.B;
        GD.Print($"LIFT_HYDRAULIC_IMPORT arm={driveArm.Transform} body={cylinder.Transform} bodyBounds={cylinder.GetAabb()} rod={rod.Transform} rodBounds={rod.GetAabb()} base={basePin.GlobalPosition} tip={tipPin.GlobalPosition} gland={glandRest}");
        var pivots = meshes.Where(mesh => mesh.Name.ToString().StartsWith("LIFT_top_pivot_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("LIFT_bottom_pivot_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("KIN_mid_pivot_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("KIN_stage_pivot_", StringComparison.Ordinal)).ToArray();
        var followers = meshes.Where(mesh => mesh.Name.ToString().StartsWith("LIFT_retaining_washer_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("LIFT_lower_guide_roller_", StringComparison.Ordinal)
            || mesh.Name.ToString().StartsWith("LIFT_upper_guide_roller_", StringComparison.Ordinal))
            .Select(mesh => (Mesh: mesh, Pivot: pivots.OrderBy(pivot => pivot.GlobalPosition.DistanceSquaredTo(mesh.GlobalPosition)).First()))
            .Select(pair => (pair.Mesh, pair.Pivot, Offset: pair.Mesh.GlobalPosition - pair.Pivot.GlobalPosition)).ToArray();
        bool Supported()
        {
            var load = ReviewBounds(fixture);
            var platform = ReviewBounds(deck);
            return MathF.Abs(load.Position.Y - platform.End.Y) < 0.001f
                && load.Position.X >= platform.Position.X && load.End.X <= platform.End.X
                && load.Position.Z >= platform.Position.Z && load.End.Z <= platform.End.Z;
        }
        GD.Print($"ASSEMBLY_LIFT_GEOMETRY deck={ReviewBounds(deck)} fixture={ReviewBounds(fixture)} followers={followers.Length}");
        check(Supported(), "assembly_fixture_supported_at_initial_deck");
        runtime.UsesExternalClock = false;
        FrameComposition(_mainCamera!, root, new Vector3(-11, 7, 12));
        var framed = true;
        var support = true;
        var attachments = followers.Length == 16;
        var hydraulicAttachment = true;
        var hydraulicCaps = true;
        foreach (var action in new[] { "raise-lift", "lower-lift" })
        {
            runtime.ExecuteAction(action);
            for (var sample = 0; sample < 120; sample++)
            {
                runtime.AdvanceSimulation(0.02);
                support &= Supported();
                var expectedTip = driveArm.ToGlobal(tipOnArm);
                hydraulicAttachment &= hydraulicParts.Where(mesh => mesh != cylinder && mesh != rod)
                    .All(mesh => mesh.GlobalPosition.DistanceTo(expectedTip) < 0.001f);
                var expectedGland = basePin.GlobalPosition
                    + (expectedTip - basePin.GlobalPosition).Normalized() * cylinderLength;
                bool MatchesCaps(MeshInstance3D member, Vector3 a, Vector3 b)
                {
                    var caps = Caps(member);
                    return (caps.A.DistanceTo(a) < 0.001f && caps.B.DistanceTo(b) < 0.001f)
                        || (caps.B.DistanceTo(a) < 0.001f && caps.A.DistanceTo(b) < 0.001f);
                }
                // Require actual barrel/rod cap contact at both named pins and
                // the gland throughout motion, rather than accepting loose rods.
                hydraulicCaps &= MatchesCaps(cylinder, basePin.GlobalPosition, expectedGland)
                    && MatchesCaps(rod, expectedGland, expectedTip);
                foreach (var mesh in ReviewMeshes(root))
                {
                    var bounds = ReviewBounds(mesh);
                    for (var corner = 0; corner < 8; corner++)
                        framed &= _mainCamera!.IsPositionInFrustum(bounds.Position + bounds.Size * new Vector3(
                            (corner & 1) == 0 ? 0 : 1, (corner & 2) == 0 ? 0 : 1, (corner & 4) == 0 ? 0 : 1));
                }
                attachments &= followers.All(pair => (pair.Mesh.GlobalPosition - pair.Pivot.GlobalPosition)
                    .DistanceTo(pair.Offset) < 0.001f);
            }
        }
        check(support, "assembly_fixture_supported_through_raise_and_lower");
        check(attachments, "assembly_guide_rollers_and_washers_follow_pins");
        check(framed, "assembly_full_travel_fits_initial_camera_frustum");
        check(hydraulicAttachment, "assembly_hydraulic_clevis_and_lug_follow_driven_arm");
        check(hydraulicCaps, "assembly_hydraulic_mesh_caps_stay_seated_through_travel");
        runtime.ResetSimulation();
        runtime.ExecuteAction("raise-lift");
        runtime.AdvanceSimulation(0.7);
        runtime.StopSimulation();
        var stoppedDeck = deck.Transform;
        var stoppedFixture = fixture.Transform;
        var stoppedHydraulics = hydraulicParts.Select(mesh => mesh.Transform).ToArray();
        runtime.AdvanceSimulation(0.5);
        check(deck.Transform.IsEqualApprox(stoppedDeck) && fixture.Transform.IsEqualApprox(stoppedFixture),
            "assembly_stop_holds_deck_and_fixture");
        check(hydraulicParts.Select((mesh, index) => mesh.Transform.IsEqualApprox(stoppedHydraulics[index])).All(held => held),
            "assembly_stop_holds_hydraulic_chain");
        runtime.ResetSimulation();
        check(Supported() && runtime.Points["bottom_limit"] is true && runtime.Points["top_limit"] is false,
            "assembly_reset_restores_supported_bottom_state");
        check(hydraulicParts.Select((mesh, index) => mesh.Transform.IsEqualApprox(hydraulicRest[index])).All(restored => restored),
            "assembly_reset_restores_hydraulic_authored_pose");
    }

    private void VerifyInboundToteGeometry(Action<bool, string> check)
    {
        AddMigratedScene("lab-2-11-inbound-tote-stop", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        var runtime = _sceneRuntime!;
        var conveyor = root.GetNode<Node3D>("inbound_conveyor");
        var tote = root.GetNode<Node3D>("inbound_tote");
        var sensor = root.GetNode<Node3D>("scan_photoeye");
        var initial = tote.Transform;
        var belt = ReviewBounds((MeshInstance3D)conveyor.FindChild("KIN_belt_surface", true, false));
        bool Supported()
        {
            var load = ReviewBounds(tote);
            return MathF.Abs(load.Position.Y - belt.End.Y) < 0.001f
                && load.Position.X >= belt.Position.X && load.End.X <= belt.End.X
                && load.Position.Z >= belt.Position.Z && load.End.Z <= belt.End.Z;
        }
        check(Supported(), "inbound_tote_rests_on_actual_belt_with_full_footprint");
        var sensorSolids = ReviewMeshes(sensor).Where(mesh => !mesh.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase)
            && !mesh.Name.ToString().StartsWith("KIN_beam", StringComparison.Ordinal)).ToArray();
        var conveyorSolids = ReviewMeshes(conveyor).Where(mesh => !mesh.Name.ToString().Contains("cable", StringComparison.OrdinalIgnoreCase)).ToArray();
        check(sensorSolids.All(head => conveyorSolids.All(frame => !OrientedBoxesPenetrate(head, frame))),
            "inbound_sensor_solids_clear_conveyor_frame");
        var feet = ReviewMeshes(sensor).Where(mesh => mesh.Name.ToString() is "TX_foot" or "RX_foot").ToArray();
        check(feet.Length == 2 && feet.All(foot => MathF.Abs(ReviewBounds(foot).Position.Y) < 0.001f),
            "inbound_photoeye_feet_grounded");
        runtime.UsesExternalClock = false; // Declared plant preview only, no PLC controller.
        runtime.ExecuteAction("start-cycle");
        runtime.AdvanceSimulation(0.7);
        runtime.StopSimulation();
        var stopped = tote.Transform;
        runtime.AdvanceSimulation(0.4);
        var holds = tote.Transform.IsEqualApprox(stopped);
        runtime.ResetSimulation();
        check(holds && tote.Transform.IsEqualApprox(initial), "inbound_stop_holds_and_reset_restores_tote");
        runtime.ExecuteAction("start-cycle");
        var support = true;
        var scanEnvelope = true;
        var sawScan = false;
        var beam = (MeshInstance3D)sensor.FindChild("KIN_beam*", true, false);
        for (var sample = 0; sample < 300; sample++)
        {
            runtime.AdvanceSimulation(0.02);
            support &= Supported();
            if (runtime.Points["tote_at_scanner"] is true)
            {
                sawScan = true;
                var load = ReviewBounds(tote);
                var center = ReviewBounds(beam).GetCenter();
                scanEnvelope &= center.X >= load.Position.X && center.X <= load.End.X
                    && center.Y > load.Position.Y && center.Y < load.End.Y;
            }
        }
        check(support && runtime.Points["cycle_complete"] is true, "inbound_full_cycle_keeps_tote_on_belt");
        check(sawScan && scanEnvelope, "inbound_scan_dwell_places_tote_in_optical_envelope");
        runtime.ResetSimulation();
    }

    private void VerifySelectorProjection(Action<bool, string> check)
    {
        // Inspect actual imported pointer/tick geometry through each declared
        // action, including the BOOL mode selector and a four-position dial.
        foreach (var sceneId in new[] { "lab-2-05-bay-light-selector", "lab-2-09-maintenance-beacon",
            "lab-2-15-fume-extractor", "lab-2-18-pallet-pickup" })
        {
            AddMigratedScene(sceneId, _candidateCatalog!, _mainCamera!, false, false);
            var equipment = _sceneCompositionRoot!.GetChildren().OfType<Node3D>()
                .Single(node => node.FindChild("KIN_selector_handle", true, false) is not null);
            var runtime = _sceneRuntime!;
            var definition = SceneCatalogLoader.LoadScene(_sceneCatalog!.Scenes.Single(scene => scene.Id == sceneId));
            var config = definition.Equipment.Single(item => item.Type == "rotarySwitch").Config;
            var count = config.GetProperty("positionCount").GetInt32();
            var action = config.GetProperty("action").GetString()!;
            var binding = definition.Simulation.GetProperty("pointBindings").EnumerateArray()
                .Single(item => item.GetProperty("mode").GetString() == "selector");
            var point = binding.GetProperty("point").GetString()!;
            var pivot = (Node3D)equipment.FindChild("KIN_selector_handle", true, false)!;
            var inlay = (Node3D)equipment.FindChild("SELECTOR_direction_inlay", true, false)!;
            var ticks = ReviewMeshes(equipment).Where(mesh => mesh.Name.ToString().StartsWith("POSITION_tick_", StringComparison.Ordinal)).ToArray();
            check(ticks.Length == count, $"{sceneId}_only_configured_detents_visible");
            var dialFace = ReviewBounds((MeshInstance3D)equipment.FindChild("SELECTOR_dial_plate", true, false)!).End.Z;
            check(ticks.All(tick => MathF.Abs(ReviewBounds(tick).Position.Z - dialFace) < 0.001f),
                $"{sceneId}_tick_solids_rest_on_dial_face");
            var initial = inlay.GlobalTransform;
            var aligned = true;
            var onFace = true;
            var actionsAccepted = true;
            for (var step = 0; step <= count; step++)
            {
                var ordinal = Convert.ToInt32(runtime.Points[point]);
                var center = equipment.ToLocal(pivot.GlobalPosition);
                var tip = equipment.ToLocal(inlay.GlobalPosition);
                var direction = new Vector2(tip.X - center.X, tip.Y - center.Y).Normalized();
                var tick = ticks.SingleOrDefault(mesh => mesh.Name == $"POSITION_tick_{ordinal}");
                if (tick is null) aligned = false;
                else
                {
                    var target = equipment.ToLocal(tick.GlobalPosition) - center;
                    aligned &= direction.Dot(new Vector2(target.X, target.Y).Normalized()) > 0.999f;
                }
                // Authored inlay lies 51 mm forward of the pivot. The old Y
                // rotation changed this depth and swung the handle off the face.
                onFace &= MathF.Abs(tip.Z - center.Z - 0.051f) < 0.001f;
                actionsAccepted &= runtime.ExecuteAction(action);
            }
            check(actionsAccepted && aligned, $"{sceneId}_pointer_aligns_with_current_input_detent");
            check(onFace, $"{sceneId}_pointer_stays_in_dial_plane");
            runtime.ResetSimulation();
            check(inlay.GlobalTransform.IsEqualApprox(initial), $"{sceneId}_reset_restores_initial_pointer");
        }
    }

    private void VerifyGalleryGeometry(Action<bool, string> check)
    {
        AddMigratedScene("equipment-gallery", _candidateCatalog!, _mainCamera!, false, false);
        var root = _sceneCompositionRoot!;
        check(root.GetChildren().OfType<Node3D>().Where(node => ReviewMeshes(node).Length > 0)
            .All(node => ReviewBounds(node).Position.Y >= -0.005f), "gallery_equipment_clear_finished_floor");
        check(LogBoundsCandidates(root) == 0, "gallery_separate_equipment_bounds_clear");
        var instruments = new[] { "gallery_low_sensor", "gallery_transmitter" }.Select(id => root.GetNode<Node3D>(id)).ToArray();
        check(instruments.All(instrument =>
        {
            var standBase = instrument.FindChild("DISPLAY_STAND_base", true, false) as MeshInstance3D;
            var tips = ReviewMeshes(instrument).Where(mesh => mesh.Name.ToString().StartsWith("FORK_tip", StringComparison.Ordinal)
                || mesh.Name == "PROBE_tip_weight").ToArray();
            return standBase is not null && MathF.Abs(ReviewBounds(standBase).Position.Y) < 0.005f
                && tips.Length > 0 && tips.All(tip => ReviewBounds(tip).Position.Y >= 0.13f);
        }), "gallery_display_stands_grounded_and_probe_tips_clear");
        check(new[] { "gallery_pipe", "gallery_valve" }.All(id => MathF.Abs(ReviewBounds(root.GetNode<Node3D>(id)).Position.Y) < 0.005f),
            "gallery_pipe_and_valve_supports_grounded");
    }

    private static List<Vector2> ContactHull(IEnumerable<Vector2> contacts)
    {
        var points = contacts.Distinct().OrderBy(point => point.X).ThenBy(point => point.Y).ToArray();
        var hull = new List<Vector2>();
        foreach (var point in points)
        {
            while (hull.Count >= 2 && (hull[^1] - hull[^2]).Cross(point - hull[^1]) <= 0) hull.RemoveAt(hull.Count - 1);
            hull.Add(point);
        }
        var lower = hull.Count;
        foreach (var point in points.Reverse().Skip(1))
        {
            while (hull.Count > lower && (hull[^1] - hull[^2]).Cross(point - hull[^1]) <= 0) hull.RemoveAt(hull.Count - 1);
            hull.Add(point);
        }
        if (hull.Count > 1) hull.RemoveAt(hull.Count - 1);
        return hull;
    }

    // Separating axes for transformed mesh boxes. Unlike world AABBs, this
    // keeps the diagonal belt motor separate from a carton centered on it.
    // It still bounds meshes rather than testing triangles or certifying fit.
    private static bool OrientedBoxesPenetrate(MeshInstance3D left, MeshInstance3D right)
    {
        (Vector3 Center, Vector3[] Edges) Box(MeshInstance3D mesh)
        {
            var bounds = mesh.GetAabb();
            var transform = mesh.GlobalTransform;
            return (transform * bounds.GetCenter(), new[] {
                transform.Basis.X * bounds.Size.X / 2,
                transform.Basis.Y * bounds.Size.Y / 2,
                transform.Basis.Z * bounds.Size.Z / 2 });
        }
        var a = Box(left); var b = Box(right);
        var axes = new List<Vector3>();
        foreach (var box in new[] { a, b })
        {
            axes.Add(box.Edges[0].Cross(box.Edges[1]));
            axes.Add(box.Edges[1].Cross(box.Edges[2]));
            axes.Add(box.Edges[2].Cross(box.Edges[0]));
        }
        foreach (var edgeA in a.Edges)
        foreach (var edgeB in b.Edges) axes.Add(edgeA.Cross(edgeB));
        foreach (var axis in axes.Where(axis => axis.LengthSquared() > 1e-10f).Select(axis => axis.Normalized()))
        {
            var radius = a.Edges.Sum(edge => MathF.Abs(axis.Dot(edge))) + b.Edges.Sum(edge => MathF.Abs(axis.Dot(edge)));
            if (radius - MathF.Abs(axis.Dot(a.Center - b.Center)) <= 0.005f) return false;
        }
        return true;
    }
}
