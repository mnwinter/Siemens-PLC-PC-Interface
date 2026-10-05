using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using RungProof.Next.App;

namespace RungProof.Next.Scenes;

public partial class SceneSimulationRuntime
{
    // Standalone functional reference only. The current controller seams do
    // not support this legacy scene's STRING motor_direction output. Never
    // manufacture that command when a controller is selected.
    private bool HasBottleShuttleReference => _definition.TryGetProperty("bottleShuttleReference", out _);
    private bool _bottleShuttleReferenceActive;
    private int _bottleShuttleLeg = 1;
    private Node3D? _bottleShuttle;
    private MeshInstance3D? _bottleShuttleBody;
    private MeshInstance3D[] _bottleShuttleTx = [], _bottleShuttleRx = [];
    private Vector3[] _bottleShuttleFaces = [];
    private ConveyorController? _bottleShuttleConveyor;
    private double _bottleShuttleX, _bottleShuttleLeftTripX, _bottleShuttleRightTripX, _bottleShuttleSpeed;

    private void ResetBottleShuttleReference()
    {
        _bottleShuttleReferenceActive = false;
        _bottleShuttleLeg = 1;
        if (!HasBottleShuttleReference) return;
        var config = _definition.GetProperty("bottleShuttleReference");
        _bottleShuttle = _sceneRoot.GetNode<Node3D>(SafeNodeName(Text(config, "productId", "")));
        _bottleShuttleBody = (MeshInstance3D)_bottleShuttle.FindChild("BOTTLE_BODY", true, false);
        _bottleShuttleFaces = _bottleShuttleBody.Mesh.GetFaces();
        var sensors = new[] { "leftPhotoeyeId", "rightPhotoeyeId" }
            .Select(key => _sceneRoot.GetNode<Node3D>(SafeNodeName(Text(config, key, "")))).ToArray();
        _bottleShuttleTx = sensors.Select(sensor => (MeshInstance3D)sensor.FindChild("TX_lens", true, false)).ToArray();
        _bottleShuttleRx = sensors.Select(sensor => (MeshInstance3D)sensor.FindChild("RX_lens", true, false)).ToArray();
        _bottleShuttleConveyor = _sceneRoot.GetNode<Node3D>(SafeNodeName(Text(config, "conveyorId", "")))
            .FindChildren("*", string.Empty, true, false).OfType<ConveyorController>().Single();
        _bottleShuttleSpeed = Number(_definition, "conveyorSpeedMps", 0);
        var minimum = Number(config, "minimumX", double.NaN);
        var maximum = Number(config, "maximumX", double.NaN);
        if (!double.IsFinite(minimum) || !double.IsFinite(maximum) || minimum >= maximum
            || !double.IsFinite(_bottleShuttleSpeed) || _bottleShuttleSpeed <= 0 || _bottleShuttleSpeed > 2
            || _bottleShuttleFaces.Length == 0)
            throw new InvalidOperationException("Bottle shuttle requires finite ordered bounds, a body mesh and a positive speed up to 2 m/s.");
        foreach (var (point, owner, type) in new[] { ("left_sensor_active", "PC", "BOOL"), ("right_sensor_active", "PC", "BOOL"),
            ("motor_run", "PLC", "BOOL"), ("motor_direction", "PLC", "STRING"), ("cycle_complete", "SIM", "BOOL") })
            if (_pointOwners.GetValueOrDefault(point) != owner || _pointTypes.GetValueOrDefault(point) != type)
                throw new InvalidOperationException($"Bottle shuttle has an invalid {point} ownership/type contract.");

        var home = _bottleShuttle.Position;
        try
        {
            // This specific convex body crosses each horizontal beam once on
            // its approach. Keep an inside endpoint during bisection, so the
            // transition pose really intersects triangles despite float rounding.
            MoveBottleShuttle(minimum);
            if (!BottleShuttleBlocksBeam(0) || BottleShuttleBlocksBeam(1))
                throw new InvalidOperationException("Bottle shuttle minimum must block only the left beam.");
            MoveBottleShuttle(maximum);
            if (!BottleShuttleBlocksBeam(1) || BottleShuttleBlocksBeam(0))
                throw new InvalidOperationException("Bottle shuttle maximum must block only the right beam.");
            double FirstInside(int sensor, double inside, double outside)
            {
                for (var iteration = 0; iteration < 32; iteration++)
                {
                    var middle = (inside + outside) / 2;
                    MoveBottleShuttle(middle);
                    if (BottleShuttleBlocksBeam(sensor)) inside = middle; else outside = middle;
                }
                return inside;
            }
            _bottleShuttleRightTripX = FirstInside(1, maximum, minimum);
            _bottleShuttleLeftTripX = FirstInside(0, minimum, maximum);
        }
        finally { _bottleShuttle.Position = home; }
        if (home.X < minimum || home.X > _bottleShuttleLeftTripX || _bottleShuttleLeftTripX >= _bottleShuttleRightTripX)
            throw new InvalidOperationException("Bottle shuttle home must be supported inside its left sensor region.");
        _bottleShuttleX = home.X;
        _bottleShuttleConveyor.SetPhysicsProcess(false);
        _bottleShuttleConveyor.ApplyPlantTravel(0, 0);
        ProjectBottleShuttleFeedback();
        GD.Print($"BOTTLE_SHUTTLE_REFERENCE_DATUM home={home.X} leftTrip={_bottleShuttleLeftTripX} rightTrip={_bottleShuttleRightTripX} speed={_bottleShuttleSpeed}");
    }

    private bool StartBottleShuttleReference(string sequence)
    {
        if (UsesExternalClock || _externalPlaybackSelected || _bottleShuttleReferenceActive
            || _bottleShuttle is null || sequence != "round-trip") return false;
        // Stop retains the leg and exact held pose; a completed round trip can
        // start again from that left crossing without teleporting to home.
        if (AsBool(_points["cycle_complete"])) _bottleShuttleLeg = 1;
        if (Math.Abs(_bottleShuttle.Position.X - _bottleShuttleX) > 0.001) return false;
        _bottleShuttleReferenceActive = true;
        SetPoint("motor_run", true);
        SetPoint("motor_direction", _bottleShuttleLeg > 0 ? "right" : "left");
        SetPoint("cycle_complete", false); SetPoint("status_color", "green");
        ProjectBottleShuttleFeedback(); ApplyBindings(); StateChanged?.Invoke();
        GD.Print($"BOTTLE_SHUTTLE_REFERENCE_START x={_bottleShuttleX} leg={_bottleShuttleLeg}");
        return true;
    }

    private void AdvanceBottleShuttleReference(double seconds)
    {
        if (!double.IsFinite(seconds) || seconds < 0) throw new ArgumentException("Bottle shuttle time must be finite and non-negative.");
        if (UsesExternalClock || _externalPlaybackSelected)
        {
            _bottleShuttleReferenceActive = false;
            _bottleShuttleConveyor?.ApplyPlantTravel(0, 0);
            ProjectBottleShuttleFeedback(); ApplyBindings(); StateChanged?.Invoke();
            return;
        }
        var remaining = seconds;
        while (_bottleShuttleReferenceActive && remaining > 0)
        {
            var target = _bottleShuttleLeg > 0 ? _bottleShuttleRightTripX : _bottleShuttleLeftTripX;
            var distance = Math.Abs(target - _bottleShuttleX);
            var duration = distance / _bottleShuttleSpeed;
            var reachesSensor = remaining + 1e-9 >= duration;
            var travel = reachesSensor ? distance : _bottleShuttleSpeed * remaining;
            var signedTravel = _bottleShuttleLeg * travel;
            _bottleShuttleX = reachesSensor ? target : _bottleShuttleX + signedTravel;
            MoveBottleShuttle(_bottleShuttleX);
            _bottleShuttleConveyor!.ApplyPlantTravel((float)signedTravel, (float)(_bottleShuttleLeg * _bottleShuttleSpeed));
            ProjectBottleShuttleFeedback();
            remaining = reachesSensor ? Math.Max(0, remaining - duration) : 0;
            if (!reachesSensor) break;
            if (_bottleShuttleLeg > 0)
            {
                _bottleShuttleLeg = -1;
                SetPoint("motor_direction", "left");
                // Reverse the displayed belt velocity at this event; no extra
                // displacement is added until simulation time advances again.
                _bottleShuttleConveyor.ApplyPlantTravel(0, (float)-_bottleShuttleSpeed);
                GD.Print($"BOTTLE_SHUTTLE_REFERENCE_REVERSE x={_bottleShuttleX} right={_points["right_sensor_active"]}");
            }
            else
            {
                _bottleShuttleReferenceActive = false;
                SetPoint("motor_run", false); SetPoint("motor_direction", "stopped");
                SetPoint("cycle_complete", true); SetPoint("status_color", "amber");
                _bottleShuttleConveyor.ApplyPlantTravel(0, 0);
                GD.Print($"BOTTLE_SHUTTLE_REFERENCE_COMPLETE x={_bottleShuttleX} left={_points["left_sensor_active"]}");
            }
        }
        ProjectBottleShuttleFeedback(); ApplyBindings(); StateChanged?.Invoke();
    }

    private void MoveBottleShuttle(double x)
    {
        var position = _bottleShuttle!.Position;
        position.X = (float)x;
        _bottleShuttle.Position = position;
    }

    private void ProjectBottleShuttleFeedback()
    {
        if (_bottleShuttleBody is null) return;
        SetPoint("left_sensor_active", BottleShuttleBlocksBeam(0));
        SetPoint("right_sensor_active", BottleShuttleBlocksBeam(1));
    }

    private bool BottleShuttleBlocksBeam(int sensor)
    {
        var inverse = _bottleShuttleBody!.GlobalTransform.AffineInverse();
        var tx = _bottleShuttleTx[sensor]; var rx = _bottleShuttleRx[sensor];
        var from = inverse * (tx.GlobalTransform * tx.GetAabb().GetCenter());
        var to = inverse * (rx.GlobalTransform * rx.GetAabb().GetCenter());
        var direction = to - from;
        // Double-sided finite segment/triangle test. A bounding box alone can
        // report the curved shoulder or cylinder corner as blocked incorrectly.
        for (var index = 0; index < _bottleShuttleFaces.Length; index += 3)
        {
            var edge1 = _bottleShuttleFaces[index + 1] - _bottleShuttleFaces[index];
            var edge2 = _bottleShuttleFaces[index + 2] - _bottleShuttleFaces[index];
            var cross = direction.Cross(edge2); var determinant = edge1.Dot(cross);
            if (MathF.Abs(determinant) < 1e-8f) continue;
            var offset = from - _bottleShuttleFaces[index]; var u = offset.Dot(cross) / determinant;
            if (u < -1e-6f || u > 1.000001f) continue;
            var q = offset.Cross(edge1); var v = direction.Dot(q) / determinant;
            if (v < -1e-6f || u + v > 1.000001f) continue;
            var t = edge2.Dot(q) / determinant;
            if (t >= 0 && t <= 1) return true;
        }
        return false;
    }
}
