using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using RungProof.Next.Connections;

internal static class Program
{
    private static readonly JsonElement OfflineDescriptor = JsonSerializer.SerializeToElement(new { id = "offline.json" });
    private static string _python = "";
    private static int _passed;

    private static async Task Main(string[] args)
    {
        if (args.Length != 1 || !File.Exists(args[0])) throw new ArgumentException("Pass the local Python executable.");
        _python = args[0];
        await Test("stderr flood is drained without blocking JSON", async () =>
        {
            using var channel = Channel();
            var result = await channel.SendAsync(new { command = "flood", value = 7 }, TimeSpan.FromSeconds(3));
            Require(result.GetProperty("result").GetProperty("value").GetInt32() == 7);
        });
        await Test("missing response times out, kills process, and recovers on a fresh process", async () =>
        {
            using var channel = Channel();
            var pid = Pid(await channel.SendAsync(new { command = "echo" }, TimeSpan.FromSeconds(3)));
            var clock = Stopwatch.StartNew();
            await Reject<TimeoutException>(() => channel.SendAsync(new { command = "hang" }, TimeSpan.FromMilliseconds(120)));
            Require(clock.Elapsed < TimeSpan.FromSeconds(2));
            RequireExited(pid);
            var recovered = await channel.SendAsync(new { command = "echo", value = 9 }, TimeSpan.FromSeconds(3));
            Require(Pid(recovered) != pid && recovered.GetProperty("result").GetProperty("value").GetInt32() == 9);
        });
        await Test("malformed, rejected, and EOF replies close the channel", async () =>
        {
            foreach (var command in new[] { "malformed", "reject", "close" })
            {
                using var channel = Channel();
                var pid = Pid(await channel.SendAsync(new { command = "echo" }, TimeSpan.FromSeconds(3)));
                await Reject<Exception>(() => channel.SendAsync(new { command }, TimeSpan.FromSeconds(3)));
                RequireExited(pid);
            }
        });
        await Test("queued requests are serialized and preserve reply identity", async () =>
        {
            using var channel = Channel();
            var first = channel.SendAsync(new { command = "delay", value = 1 }, TimeSpan.FromSeconds(3));
            var second = channel.SendAsync(new { command = "echo", value = 2 }, TimeSpan.FromSeconds(3));
            Require((await first).GetProperty("result").GetProperty("value").GetInt32() == 1);
            Require((await second).GetProperty("result").GetProperty("value").GetInt32() == 2);
        });
        await Test("cancel before startup never creates a process", async () =>
        {
            using var channel = Channel();
            using var cancelled = new CancellationTokenSource();
            cancelled.Cancel();
            await Reject<OperationCanceledException>(() => channel.SendAsync(new { command = "connect" }, TimeSpan.FromSeconds(3), cancelled.Token));
        });
        await Test("Dispose cancels a pending read and refuses restart", async () =>
        {
            var channel = Channel();
            var pid = Pid(await channel.SendAsync(new { command = "echo" }, TimeSpan.FromSeconds(3)));
            var pending = channel.SendAsync(new { command = "hang" }, TimeSpan.FromSeconds(3));
            channel.Dispose();
            await Reject<Exception>(() => pending);
            RequireExited(pid);
            await Reject<ObjectDisposedException>(() => channel.SendAsync(new { command = "echo" }, TimeSpan.FromSeconds(3)));
        });
        await Test("controller completion runs only on the polling caller", async () =>
        {
            using var client = Client();
            var completed = false;
            var callbackThread = 0;
            client.Connect("offline.json", "offline-scene", [], _ => { completed = true; callbackThread = Environment.CurrentManagedThreadId; }, Fail, 100, OfflineDescriptor);
            await Task.Delay(300);
            Require(!completed && client.State == ConnectionState.Connecting);
            var pollThread = Environment.CurrentManagedThreadId;
            client.Poll();
            Require(completed && callbackThread == pollThread && client.State == ConnectionState.Connected);
        });
        await Test("disconnect invalidates an in-flight connect and permits a fresh session", async () =>
        {
            using var client = Client();
            var staleApplied = false;
            client.Connect("offline.json", "old-scene", [], _ => staleApplied = true, Fail, 100, OfflineDescriptor);
            client.Disconnect();
            await Task.Delay(100);
            client.Poll();
            Require(!staleApplied && client.State == ConnectionState.Disconnected && client.ActiveDescriptor is null);
            client.Connect("offline.json", "new-scene", [], _ => { }, Fail, 100, OfflineDescriptor);
            await Pump(client);
            Require(client.State == ConnectionState.Connected && client.ActiveDescriptor!.Value.GetProperty("sceneId").GetString() == "new-scene");
        });
        foreach (var mode in new[] { "stale", "bad_status", "hang" })
        {
            await Test($"cycle {mode} cannot publish and closes session", async () =>
            {
                using var client = Client();
                client.Connect("offline.json", "offline-scene", [], _ => { }, Fail, 100, OfflineDescriptor);
                await Pump(client);
                var published = false;
                var failed = false;
                client.Cycle("offline-scene", new Dictionary<string, object?> { ["mode"] = mode }, _ => published = true, _ => failed = true);
                await Pump(client);
                Require(!published && failed && client.State == ConnectionState.Disconnected && client.ActiveDescriptor is null);
            });
        }
        await Test("healthy and fault cycles retain actual guarded health metadata", async () =>
        {
            using var client = Client();
            client.Connect("offline.json", "offline-scene", [], _ => { }, Fail, 100, OfflineDescriptor);
            await Pump(client);
            client.Cycle("offline-scene", new Dictionary<string, object?>(), _ => { }, Fail);
            await Pump(client);
            Require(client.LatestCycle!.Value.GetProperty("health").GetString() == "healthy");
            client.Cycle("offline-scene", new Dictionary<string, object?> { ["mode"] = "fault" }, _ => { }, Fail);
            await Pump(client);
            Require(client.State == ConnectionState.Disconnected && client.LatestCycle!.Value.GetProperty("health").GetString() == "fault");
        });
        await Test("symbolic ownership, exact scope, types and numeric bounds are enforced", () =>
        {
            using var simulation = JsonDocument.Parse("""{"points":[{"name":"sensor","owner":"PC","type":"BOOL"},{"name":"motor","owner":"PLC","type":"BOOL"}]}""");
            using var descriptor = JsonDocument.Parse("""{"cycleMs":20,"heartbeatTimeoutMs":1000,"pcPointScope":[{"name":"sensor","dataType":"BOOL"}],"plcPointScope":[{"name":"motor","dataType":"BOOL"}]}""");
            ExternalSceneContract.Validate(simulation.RootElement, descriptor.RootElement);
            Require(ExternalSceneContract.SamplePcPoints(descriptor.RootElement, new Dictionary<string, object?> { ["sensor"] = true })["sensor"] is true);
            foreach (var json in new[] { "{}", "{\"motor\":1}", "{\"motor\":null}", "{\"motor\":true,\"extra\":false}" })
            {
                using var outputs = JsonDocument.Parse(json);
                ExpectRejected(() => ExternalSceneContract.ReadPlcPoints(descriptor.RootElement, outputs.RootElement));
            }
            using var wrongOwner = JsonDocument.Parse("""{"points":[{"name":"sensor","owner":"PLC","type":"BOOL"},{"name":"motor","owner":"PLC","type":"BOOL"}]}""");
            ExpectRejected(() => ExternalSceneContract.Validate(wrongOwner.RootElement, descriptor.RootElement));
            ExpectRejected(() => ExternalSceneContract.TypedValue("BOOL", 1, "x"));
            ExpectRejected(() => ExternalSceneContract.TypedValue("INT", 32768, "x"));
            ExpectRejected(() => ExternalSceneContract.TypedValue("DINT", 1.5, "x"));
            ExpectRejected(() => ExternalSceneContract.TypedValue("REAL", double.NaN, "x"));
            Require((long)ExternalSceneContract.TypedValue("INT", -32768, "x") == -32768);
            Require((long)ExternalSceneContract.TypedValue("DINT", int.MaxValue, "x") == int.MaxValue);
            return Task.CompletedTask;
        });
        Console.WriteLine($"CONNECTION_TESTS_PASS {_passed}; offline child processes only, no PLC transport or network.");
    }

    private static ProcessBridgeChannel Channel()
    {
        var info = new ProcessStartInfo(_python) { UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardInput = true, RedirectStandardOutput = true, RedirectStandardError = true };
        info.ArgumentList.Add(Path.GetFullPath("tests/Connections/fake_bridge.py"));
        return new ProcessBridgeChannel(info);
    }
    private static ExternalPlcRuntimeClient Client() => new(Channel);
    private static int Pid(JsonElement response) => response.GetProperty("result").GetProperty("pid").GetInt32();
    private static void Fail(Exception exception) => throw new Exception("Unexpected bridge error", exception);
    private static void Require(bool condition) { if (!condition) throw new Exception("Assertion failed."); }
    private static void RequireExited(int pid)
    {
        try { using var process = Process.GetProcessById(pid); Require(process.WaitForExit(1000)); }
        catch (ArgumentException) { /* Already reaped. */ }
    }
    private static async Task Pump(ExternalPlcRuntimeClient client)
    {
        var deadline = Stopwatch.StartNew();
        while (client.IsBusy && deadline.Elapsed < TimeSpan.FromSeconds(5)) { client.Poll(); await Task.Delay(5); }
        Require(!client.IsBusy);
    }
    private static async Task Reject<T>(Func<Task> action) where T : Exception
    {
        try { await action(); } catch (T) { return; }
        throw new Exception($"Expected {typeof(T).Name}.");
    }
    private static void ExpectRejected(Action action)
    {
        try { action(); } catch (InvalidOperationException) { return; }
        throw new Exception("Invalid symbolic contract was accepted.");
    }
    private static async Task Test(string name, Func<Task> action)
    {
        await action(); _passed++; Console.WriteLine($"PASS {name}");
    }
}
