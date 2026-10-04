using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using Godot;

namespace RungProof.Next.Connections;

public enum ConnectionState
{
    Disconnected,
    Connecting,
    Connected,
    Reconnecting,
}

public interface IGuardedRuntimeClient
{
    ConnectionState State { get; }
    string EndpointDescription { get; }
    string StatusDetail { get; }
    event Action? StateChanged;
}

/// <summary>
/// Safe default used until an explicitly configured guarded PLC runtime exists.
/// This is deliberately not a fake PLC and never invents an endpoint or address.
/// Local scene simulation remains available independently of this connection.
/// </summary>
public sealed class DisconnectedRuntimeClient : IGuardedRuntimeClient
{
    public ConnectionState State => ConnectionState.Disconnected;
    public string EndpointDescription => "No guarded PLC endpoint configured";
    public string StatusDetail => "Local simulation only; physical PLC I/O is disabled.";
    public event Action? StateChanged;

    public void Refresh() => StateChanged?.Invoke();
}

/// <summary>
/// Adapter for the repository's existing guarded Python PLC runtime. The
/// Godot process owns no S7 socket; it exchanges typed JSON commands with the
/// existing tools/plc_live.py controller through plc_bridge.py.
/// </summary>
public sealed class ExternalPlcRuntimeClient : IGuardedRuntimeClient, IDisposable
{
    private readonly object _gate = new();
    private Process? _bridge;
    private string? _sessionId;
    private string? _sceneId;
    private string _endpoint = "No external profile selected";

    public ConnectionState State { get; private set; } = ConnectionState.Disconnected;
    public JsonElement? ActiveDescriptor { get; private set; }
    public string EndpointDescription => _endpoint;
    public string StatusDetail { get; private set; } = "External PLC bridge is disconnected.";
    public event Action? StateChanged;

    public JsonElement DescribeProfile(string profileId)
    {
        var response = Send(new { command = "describe", profileId });
        return response.GetProperty("descriptor").Clone();
    }

    public JsonElement RunReadOnlyDiagnostic(string profileId)
    {
        var response = Send(new { command = "diagnostic", profileId });
        return response.GetProperty("result").Clone();
    }

    public JsonElement Connect(
        string profileId,
        string sceneId,
        IReadOnlyList<Dictionary<string, string>> authorizedWriteScope)
    {
        SetState(ConnectionState.Connecting, "Opening guarded PLC session…");
        try
        {
            var response = Send(new
            {
                command = "connect",
                profileId,
                sceneId,
                execute = true,
                authorizedWriteScope,
            });
            var result = response.GetProperty("result").Clone();
            ActiveDescriptor = result.Clone();
            _sessionId = result.GetProperty("sessionId").GetString();
            _sceneId = sceneId;
            _endpoint = $"{result.GetProperty("ip").GetString()} rack {result.GetProperty("rack").GetInt32()} slot {result.GetProperty("slot").GetInt32()}";
            SetState(ConnectionState.Connected, "Guarded PLC session connected; waiting for healthy readiness.");
            return result;
        }
        catch
        {
            SetState(ConnectionState.Disconnected, "External PLC connection failed; no active session.");
            throw;
        }
    }

    public JsonElement Cycle(string sceneId, IReadOnlyDictionary<string, object?> pcPoints)
    {
        if (_sessionId is null || _sceneId != sceneId)
            throw new InvalidOperationException("No active external PLC session for the current scene.");
        var response = Send(new
        {
            command = "cycle",
            sessionId = _sessionId,
            sceneId,
            pcPoints,
        });
        var result = response.GetProperty("result").Clone();
        if (!result.GetProperty("connected").GetBoolean())
        {
            _sessionId = null;
            ActiveDescriptor = null;
            SetState(ConnectionState.Disconnected, "PLC cycle health fault closed the guarded session.");
        }
        return result;
    }

    public void Disconnect()
    {
        if (_sessionId is not null)
        {
            try { Send(new { command = "disconnect", sessionId = _sessionId }); }
            finally { _sessionId = null; }
        }
        ActiveDescriptor = null;
        SetState(ConnectionState.Disconnected, "External PLC disconnected.");
    }

    private JsonElement Send(object request)
    {
        lock (_gate)
        {
            EnsureBridge();
            var line = JsonSerializer.Serialize(request);
            _bridge!.StandardInput.WriteLine(line);
            _bridge.StandardInput.Flush();
            var output = _bridge.StandardOutput.ReadLine();
            if (string.IsNullOrWhiteSpace(output))
                throw new InvalidOperationException("PLC bridge stopped without a response.");
            using var document = JsonDocument.Parse(output);
            var root = document.RootElement.Clone();
            if (!root.GetProperty("ok").GetBoolean())
                throw new InvalidOperationException(root.GetProperty("error").GetString() ?? "PLC bridge rejected the request.");
            return root;
        }
    }

    private void EnsureBridge()
    {
        if (_bridge is { HasExited: false }) return;
        var projectRoot = ProjectSettings.GlobalizePath("res://..");
        var python = Path.Combine(projectRoot, "build", ".venv-rungproof", "Scripts", "python.exe");
        var bridge = Path.Combine(projectRoot, "tools", "plc_bridge.py");
        var profiles = Path.Combine(projectRoot, "prototype", "plc-profiles");
        var info = new ProcessStartInfo
        {
            FileName = File.Exists(python) ? python : "py",
            UseShellExecute = false,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };
        if (File.Exists(python)) info.ArgumentList.Add(bridge);
        else { info.ArgumentList.Add("-3"); info.ArgumentList.Add(bridge); }
        info.ArgumentList.Add(profiles);
        _bridge = Process.Start(info) ?? throw new InvalidOperationException("Unable to start the guarded PLC bridge.");
    }

    private void SetState(ConnectionState state, string detail)
    {
        State = state;
        StatusDetail = detail;
        StateChanged?.Invoke();
    }

    public void Dispose()
    {
        try { Disconnect(); } catch { }
        lock (_gate)
        {
            if (_bridge is { HasExited: false }) _bridge.Kill(entireProcessTree: true);
            _bridge?.Dispose();
            _bridge = null;
        }
    }
}
