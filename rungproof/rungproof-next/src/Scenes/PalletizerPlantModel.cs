using System;

namespace RungProof.Next.Scenes;

/// <summary>Fixed four-carton kinematic lesson. PLC owns cycle/vacuum; the
/// plant owns position, attachment and placement feedback. No force physics.</summary>
public sealed class PalletizerPlantModel
{
    public enum Phase { Idle, PickDown, VacuumDwell, PickUp, Transfer, PlaceDown, Release, PlaceUp, Return }
    public const double PickX = -.95, PickZ = -.4, DeckY = 1.055, PalletY = .4505, CartonHeight = .4, CarryY = 1.66;
    public Phase State { get; private set; }
    public double X { get; private set; }
    public double Z { get; private set; }
    public double ToolY { get; private set; }
    public int Placed { get; private set; }
    public bool CartonAtPick { get; private set; }
    public bool Attached { get; private set; }
    public bool PickComplete { get; private set; }
    public bool Home => State == Phase.Idle;
    public bool AtPickup => State == Phase.VacuumDwell;
    public bool AtPlace => State == Phase.Release;
    public bool InProgress => !Home;
    public bool Faulted { get; private set; }
    public string FaultReason { get; private set; } = "";
    public static (double X, double Z) Slot(int index) => ((index % 2 == 0 ? -.26 : .26), (index < 2 ? -.23 : .23));
    public PalletizerPlantModel() => Reset();
    public void Reset()
    { State = Phase.Idle; X = PickX; Z = PickZ; ToolY = CarryY; Placed = 0; CartonAtPick = true; Attached = PickComplete = Faulted = false; FaultReason = ""; }
    // This operator action stages a new carton on the supported pick table.
    // It cannot replace a carried carton, erase a placement, or refill a layer.
    public bool CanLoadCarton => Home && !CartonAtPick && !Attached && Placed < 4 && !Faulted;
    public bool LoadCarton()
    {
        if (!CanLoadCarton) return false;
        // Keep completion latched across operator Load. The PLC must observe
        // this event even if Load arrives between home return and the next scan.
        CartonAtPick = true; return true;
    }
    public void Step(double seconds, bool cycle, bool vacuum, bool palletValid)
    {
        if (!double.IsFinite(seconds) || seconds < 0) throw new ArgumentException("Elapsed time must be finite and nonnegative.");
        if (!cycle || Faulted || seconds == 0) return;
        if (!palletValid) { Fault("Cycle without pallet permissive."); return; }
        if (Attached && !vacuum && State != Phase.Release) { Fault("Vacuum lost while carrying carton."); return; }
        if (Home && (!CartonAtPick || Placed >= 4)) { Fault("Cycle without an available carton."); return; }
        if (Home) { PickComplete = false; State = Phase.PickDown; }
        for (var remaining = seconds; remaining > 1e-9;)
        {
            var dt = Math.Min(.01, remaining); remaining -= dt;
            switch (State)
            {
                case Phase.PickDown:
                    if (MoveY(DeckY + CartonHeight, dt)) State = Phase.VacuumDwell;
                    break;
                case Phase.VacuumDwell:
                    if (vacuum) { Attached = true; CartonAtPick = false; State = Phase.PickUp; }
                    break;
                case Phase.PickUp:
                    if (MoveY(CarryY, dt)) State = Phase.Transfer;
                    break;
                case Phase.Transfer:
                    var slot = Slot(Placed);
                    var distance = Math.Sqrt(Math.Pow(slot.X - X, 2) + Math.Pow(slot.Z - Z, 2));
                    var fraction = distance < 1e-9 ? 1 : Math.Min(1, .4 * dt / distance);
                    X += (slot.X - X) * fraction; Z += (slot.Z - Z) * fraction;
                    if (fraction == 1) State = Phase.PlaceDown;
                    break;
                case Phase.PlaceDown:
                    if (MoveY(PalletY + CartonHeight, dt)) State = Phase.Release;
                    break;
                case Phase.Release:
                    if (!vacuum) { Attached = false; Placed++; State = Phase.PlaceUp; }
                    break;
                case Phase.PlaceUp:
                    if (MoveY(CarryY, dt)) State = Phase.Return;
                    break;
                case Phase.Return:
                    var homeDistance = Math.Sqrt(Math.Pow(PickX - X, 2) + Math.Pow(PickZ - Z, 2));
                    var homeFraction = homeDistance < 1e-9 ? 1 : Math.Min(1, .4 * dt / homeDistance);
                    X += (PickX - X) * homeFraction; Z += (PickZ - Z) * homeFraction;
                    if (homeFraction == 1) { State = Phase.Idle; PickComplete = true; return; }
                    break;
                default: return;
            }
        }
    }
    private bool MoveY(double target, double dt)
    { ToolY += Math.Clamp(target - ToolY, -.3 * dt, .3 * dt); return Math.Abs(ToolY - target) < 1e-9; }
    private void Fault(string reason) { Faulted = true; FaultReason = reason; }
}
