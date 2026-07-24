# User setup: Siemens processor and DB

This guide prepares a Siemens S7-1200 or S7-1500 for this project's PC
interface and proves the connection before any larger simulation is added.

## Proven and planned support

| Item | Status |
|---|---|
| CPU 1512SP-1 PN, TIA Portal V17 | Proven on real hardware |
| Windows Server 2019 VM | Proven |
| `python-snap7 3.1.0` | Proven |
| S7-1200 | Planned; not yet hardware-proven by this project |
| Other S7-1500 models/firmware | Expected to use the same S7 mechanism, but must be verified |

The proven controller used PLC address `10.70.9.201`, PC address
`10.70.9.242`, and rack/slot `0/1`. These are examples, not required site
addresses.

## Before changing the PLC

Changing CPU security settings or data-block access is a PLC configuration
change. Make an offline project backup and follow the site's change-control
and commissioning procedure.

If this is an operating machine:

- establish a safe machine state;
- account for motion, stored energy, and product damage;
- do not bypass safety logic or operating permissives;
- determine whether the required hardware/software download can interrupt the
  process;
- have a qualified controls person review the final mapping.

Do not expose TCP port 102 to an untrusted or Internet-routed network.
PUT/GET does not provide authentication or encryption.

## 1. Configure the processor network

In TIA Portal:

1. Open **Devices & networks**.
2. Select the CPU's PROFINET interface.
3. Open **Properties > General > Ethernet addresses**.
4. Assign a unique PLC IPv4 address and subnet mask.
5. Compile the hardware configuration.
6. Download the required hardware configuration to the CPU.

On the PC, configure the selected Ethernet adapter with a unique address in
the same subnet.

Example isolated test network:

| Device | Address | Subnet mask |
|---|---|---|
| PLC | `10.70.9.201` | Site-specific |
| PC/VM | `10.70.9.242` | Same as PLC |

A default gateway is normally unnecessary for a direct, isolated PLC test
network.

For a VM, prefer one dedicated USB Ethernet adapter passed directly into the
VM. If bridged networking is used, bind the VM adapter to the specific
physical PLC-network adapter instead of relying on automatic bridging.

From PowerShell on the PC or inside the VM, prove the TCP path:

```powershell
Test-NetConnection 10.70.9.201 -Port 102
```

Required result:

```text
TcpTestSucceeded : True
```

Ping alone is not sufficient proof because ICMP can be blocked while S7
communication still works.

## 2. Permit client-side S7 PUT/GET access

The Snap7 client used by this project connects as an external S7 client. The
CPU must permit client-side PUT/GET access.

In TIA Portal, select the CPU and open:

```text
Properties
  > General
  > Protection & Security
  > Connection mechanisms
```

Enable:

```text
Permit access with PUT/GET communication from remote partner
```

### If the checkbox is available

For S7-1500 CPUs through firmware V3.0, the configured CPU access level must
allow at least HMI access, read access, or full access. Complete protection
prevents enabling PUT/GET.

Use only the access level needed for the test. A write test requires the CPU
to permit the intended write access.

### If the checkbox is greyed out

First go offline in TIA Portal and reopen the CPU properties. Configuration
fields can be locked while editing an online view.

For S7-1500 firmware V3.1 and later, Siemens uses user management for this
permission:

1. Open the CPU's **Protection & Security > Access control** configuration.
2. Enable access control.
3. Activate the `Anonymous` runtime user.
4. Grant that user the minimum CPU runtime right that allows the required
   access: HMI access, read access, or full access.
5. Return to **Connection mechanisms** and enable PUT/GET access.

S7-1200 firmware V4.7 and later uses the same newer user/role concept. Exact
labels can vary with TIA Portal and firmware, so use the CPU's installed
firmware documentation when the project view differs.

### Secure PG/PC setting

Do not disable this option merely to make this interface work:

```text
Only allow secure PG/PC and HMI communication
```

Siemens states that secure PG/HMI communication and PUT/GET are separate. The
secure PG/PC option can remain enabled while PUT/GET is used. PUT/GET itself
is still unencrypted, which is why network isolation is required.

After changing processor protection or connection settings:

1. Compile the hardware configuration.
2. Review the download preview.
3. Download the required configuration to the CPU.
4. Return the CPU to the approved operating state if the download procedure
   required a transition.

## 3. Create the communication data block

Under the PLC's **Program blocks** folder:

1. Select **Add new block**.
2. Choose **Data block**.
3. Create a global DB named `DB_SimulationProof`.
4. Assign DB number `14` for the current proof utilities.
5. Open the DB properties.
6. Select **Attributes**.
7. Clear **Optimized block access**.

The PC client uses absolute DB addresses. Siemens optimized DBs do not expose
fixed byte offsets, so this communication DB must use standard/non-optimized
access.

The DB attributes for OPC UA and the Web server are separate services. They do
not enable this Snap7/PUT/GET path and should not be enabled solely for this
test. Likewise, HMI accessibility columns should follow the project's HMI
requirements rather than being opened unnecessarily.

Changing an existing DB from optimized to standard access can reorganize or
reinitialize data. Do not convert a production DB for this test. Create a
separate communication DB.

Enter the variables in this exact order:

| Name | Type | Expected offset | Writer |
|---|---|---:|---|
| `PC_To_PLC` | `Bool` | `0.0` | PC |
| `PLC_To_PC` | `Bool` | `0.1` | PLC |
| `PC_Heartbeat` | `DInt` | `2.0` | PC |
| `PLC_Heartbeat_Echo` | `DInt` | `6.0` | PLC |

Confirm that TIA shows these absolute addresses:

```text
DB14.DBX0.0  PC_To_PLC
DB14.DBX0.1  PLC_To_PC
DB14.DBD2    PC_Heartbeat
DB14.DBD6    PLC_Heartbeat_Echo
```

Do not add fields ahead of these four variables without updating and
revalidating the PC address mapping.

## 4. Add the PLC proof logic

Call the following logic cyclically, such as from OB1.

### Boolean echo

In LAD:

```text
|----[ DB_SimulationProof.PC_To_PLC ]----( DB_SimulationProof.PLC_To_PC )----|
```

Equivalent assignment:

```text
DB_SimulationProof.PLC_To_PC := DB_SimulationProof.PC_To_PLC
```

### Heartbeat echo

Use a `MOVE` instruction:

```text
IN:   DB_SimulationProof.PC_Heartbeat
OUT:  DB_SimulationProof.PLC_Heartbeat_Echo
```

Each field has one writer:

- The PC writes only `PC_To_PLC` and `PC_Heartbeat`.
- The PLC writes only `PLC_To_PC` and `PLC_Heartbeat_Echo`.

Compile and download the DB and PLC logic. Confirm that the echo networks are
called cyclically.

## 5. Create a TIA watch table

Add these four symbolic tags to a watch table:

```text
"DB_SimulationProof".PC_To_PLC
"DB_SimulationProof".PLC_To_PC
"DB_SimulationProof".PC_Heartbeat
"DB_SimulationProof".PLC_Heartbeat_Echo
```

Go online and select **Monitor all**. The monitor values should initially show
the current PLC values without question marks or access errors.

Do not force these tags during the PC round-trip test. A force or competing
write invalidates the result.

## 6. Prepare the PC software

Install Python on a supported engineering computer and create a virtual
environment:

```powershell
git clone https://github.com/mnwinter/Siemens-PLC-PC-Interface.git
cd Siemens-PLC-PC-Interface
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If company policy blocks Python installation, do not bypass that policy.
Use an approved computer to build a standalone executable or have IT approve
the runtime.

## 7. Run the read-only proof

Run this before authorizing any PLC write:

```powershell
.\.venv\Scripts\python.exe .\tools\prove_s7_connection.py `
    --ip 10.70.9.201
```

Required result:

```text
S7_SESSION_CONNECTED: True
```

Some optional controller-information queries may report `UNAVAILABLE` on
certain firmware. The S7 session result and later DB test determine whether
the required interface works.

## 8. Run the guarded DB14 round trip

Keep the TIA watch table monitoring, then run:

```powershell
.\.venv\Scripts\python.exe .\tools\round_trip_db14.py `
    --ip 10.70.9.201 `
    --execute `
    --hold-seconds 5
```

Expected watch-table sequence:

1. Five seconds: `TRUE` and heartbeat `24072401`.
2. Five seconds: `FALSE` and heartbeat `24072402`.
3. Original PC-owned values restored.

Required terminal results:

```text
TEST_A: ... PASS=True
TEST_B: ... PASS=True
RESTORE_CONFIRMED: True
ROUND_TRIP_PROOF: PASS
```

The test writes only `DB14.DBX0.0` and `DB14.DBD2`.

## Troubleshooting

| Symptom | First check |
|---|---|
| `TcpTestSucceeded : False` | PC adapter, subnet, cabling, VM adapter ownership, firewall, PLC power |
| TCP 102 works but S7 connection fails | Correct PLC IP, rack/slot `0/1`, CPU protection, PUT/GET permission |
| PUT/GET checkbox is greyed out | Work offline; then check access level or `Anonymous` runtime rights for the installed firmware |
| DB read reports object/address unavailable | DB number, downloaded DB, optimized access disabled, exact offsets |
| Read works but write fails | Write-capable access level, PUT/GET permission, DB write protection |
| PC fields change but echoes do not | Echo logic downloaded, called from OB1, PLC in RUN |
| Proof passes but TIA does not visibly change | Watch table monitoring active and `--hold-seconds 5` used |
| Restore fails | Stop testing; inspect competing writes and manually return the two PC-owned tags to approved values |

## Siemens references

- [Restriction of communication services for S7-1500](https://docs.tia.siemens.cloud/r/en-us/v21/functional-description-of-s7-1500-cpus-s7-1500/setting-the-operating-behavior-s7-1500/protection-security-s7-1500/connection-mechanisms-s7-1500/restriction-of-communication-services-s7-1500)
- [Basics of optimized and standard block access](https://docs.tia.siemens.cloud/r/en-us/v20/programming-basics/blocks-in-the-user-program/blocks-with-optimized-access/basics-of-block-access)
- [Siemens FAQ: activating PUT/GET on newer CPU firmware](https://support.industry.siemens.com/cs/ww/en/view/109925755)
- [Siemens S7 communication example and configuration](https://support.industry.siemens.com/cs/ww/en/view/92269951)
- [Siemens technical note: PUT/GET with secure PG/PC communication](https://support.industry.siemens.com/forum/ng/en/post/1072043/)
