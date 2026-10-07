using System;
using System.Collections.Generic;

namespace RungProof.Next.VirtualController;

/// <summary>
/// Fixed-time scan coordinator. Each completed scan samples inputs, executes
/// LD, commits outputs, advances the plant by exactly one scan period, and
/// publishes an immutable snapshot in that order.
/// </summary>
public sealed class VirtualControllerSession
{
    private readonly VirtualControllerRuntime _runtime;
    private readonly Dictionary<string, bool> _operatorInputs = new(StringComparer.Ordinal);
    private readonly HashSet<string> _pulseInputs = new(StringComparer.Ordinal);
    private double _accumulatorSeconds;

    public event Action<VirtualControllerSnapshot>? SnapshotPublished;
    public VirtualControllerSnapshot Snapshot => _runtime.Snapshot;
    public TimeSpan ScanPeriod => _runtime.ScanPeriod;

    public VirtualControllerSession(VirtualControllerRuntime runtime)
    {
        _runtime = runtime;
    }

    public void Run()
    {
        _runtime.Run();
        SnapshotPublished?.Invoke(_runtime.Snapshot);
    }

    public VirtualControllerSnapshot Stop()
    {
        // A momentary command that was not scanned before Stop must not fire
        // during a later Run. Held inputs retain their separate semantics.
        foreach (var name in _pulseInputs) _operatorInputs[name] = false;
        _pulseInputs.Clear();
        _accumulatorSeconds = 0.0;
        var snapshot = _runtime.Stop();
        SnapshotPublished?.Invoke(snapshot);
        return snapshot;
    }

    public VirtualControllerSnapshot Reset()
    {
        _accumulatorSeconds = 0.0;
        _operatorInputs.Clear();
        _pulseInputs.Clear();
        var snapshot = _runtime.Reset();
        SnapshotPublished?.Invoke(snapshot);
        return snapshot;
    }

    public void SetInput(string name, bool value) => _operatorInputs[name] = value;

    public void PulseInput(string name)
    {
        if (!_operatorInputs.GetValueOrDefault(name, _runtime.Snapshot.Variables.GetValueOrDefault(name)))
            _runtime.PrepareExplicitInputPulse(name);
        _operatorInputs[name] = true;
        _pulseInputs.Add(name);
    }

    public void PrepareExplicitInputPulse(string name) => _runtime.PrepareExplicitInputPulse(name);

    public VirtualControllerSnapshot SetBoolForce(string variableName, bool value)
    {
        var snapshot = _runtime.SetBoolForce(variableName, value);
        SnapshotPublished?.Invoke(snapshot);
        return snapshot;
    }

    public VirtualControllerSnapshot RemoveForce(string variableName)
    {
        var snapshot = _runtime.RemoveForce(variableName);
        SnapshotPublished?.Invoke(snapshot);
        return snapshot;
    }

    public VirtualControllerSnapshot ClearForces()
    {
        var snapshot = _runtime.ClearForces();
        SnapshotPublished?.Invoke(snapshot);
        return snapshot;
    }

    public int Advance(
        double elapsedSeconds,
        Func<IReadOnlyDictionary<string, bool>> samplePlantInputs,
        Action<IReadOnlyDictionary<string, bool>> commitOutputs,
        Action<double> advancePlant)
        => Advance(
            elapsedSeconds,
            samplePlantInputs,
            static () => new Dictionary<string, double>(),
            commitOutputs,
            static _ => { },
            advancePlant);

    public int Advance(
        double elapsedSeconds,
        Func<IReadOnlyDictionary<string, bool>> samplePlantInputs,
        Func<IReadOnlyDictionary<string, double>> sampleNumericPlantInputs,
        Action<IReadOnlyDictionary<string, bool>> commitOutputs,
        Action<IReadOnlyDictionary<string, double>> commitNumericOutputs,
        Action<double> advancePlant)
    {
        _accumulatorSeconds += Math.Max(0.0, elapsedSeconds);
        var cycleSeconds = ScanPeriod.TotalSeconds;
        var scans = 0;
        while (_accumulatorSeconds + 1e-12 >= cycleSeconds)
        {
            _accumulatorSeconds -= cycleSeconds;
            var inputs = new Dictionary<string, bool>(samplePlantInputs(), StringComparer.Ordinal);
            var numericInputs = new Dictionary<string, double>(sampleNumericPlantInputs(), StringComparer.Ordinal);
            foreach (var (name, value) in _operatorInputs) inputs[name] = value;
            var snapshot = _runtime.Scan(inputs, numericInputs);
            commitOutputs(snapshot.Outputs);
            commitNumericOutputs(snapshot.NumericOutputs);
            advancePlant(cycleSeconds);
            foreach (var name in _pulseInputs) _operatorInputs[name] = false;
            _pulseInputs.Clear();
            SnapshotPublished?.Invoke(snapshot);
            scans++;
        }
        return scans;
    }
}
