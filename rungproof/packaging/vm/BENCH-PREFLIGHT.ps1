[CmdletBinding()]
param(
    [string]$OutputDirectory = "",
    [string]$BaselineEvidenceDirectory = ""
)

$ErrorActionPreference = "Stop"
$packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $packageRoot "bench-evidence"
}
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

$requiredFiles = @(
    "RungProof.exe",
    "VERSION",
    "PILOT-CAPABILITIES.json",
    "SHA256.txt",
    "VERIFY-PACKAGE.ps1",
    "plc-profiles\scene-2-db14-pusher-interface.json"
)
foreach ($relative in $requiredFiles) {
    $path = Join-Path $packageRoot $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required package file is missing: $relative"
    }
}

& (Join-Path $packageRoot "VERIFY-PACKAGE.ps1")

$version = (Get-Content -LiteralPath (Join-Path $packageRoot "VERSION") -Raw).Trim()
$capabilityPath = Join-Path $packageRoot "PILOT-CAPABILITIES.json"
$capability = Get-Content -LiteralPath $capabilityPath -Raw | ConvertFrom-Json
if (
    $capability.realPlcWritesEnabled -ne $true -or
    $capability.plcPilotMode -ne "operator-authorized-live-bench"
) {
    throw (
        "This is not the operator-authorized live-bench package. " +
        "Expected realPlcWritesEnabled=true and " +
        "plcPilotMode=operator-authorized-live-bench."
    )
}

$profilePath = Join-Path $packageRoot "plc-profiles\scene-2-db14-pusher-interface.json"
$profile = Get-Content -LiteralPath $profilePath -Raw | ConvertFrom-Json
$expectedTags = [ordered]@{
    simulated_photoeye = @("DB14.DBX0.0", "BOOL", "pc_to_plc")
    simulated_pusher_extended = @("DB14.DBX0.1", "BOOL", "pc_to_plc")
    simulated_pusher_retracted = @("DB14.DBX0.2", "BOOL", "pc_to_plc")
    conveyor_running = @("DB14.DBX1.0", "BOOL", "plc_to_pc")
    pusher_extend = @("DB14.DBX1.1", "BOOL", "plc_to_pc")
    pc_heartbeat = @("DB14.DBD2", "DINT", "pc_to_plc")
    plc_heartbeat_echo = @("DB14.DBD6", "DINT", "plc_to_pc")
    simulation_enable = @("DB14.DBX10.0", "BOOL", "plc_to_pc")
    simulation_comm_ok = @("DB14.DBX10.1", "BOOL", "plc_to_pc")
    simulation_timeout = @("DB14.DBX10.2", "BOOL", "plc_to_pc")
}
if ($profile.version -ne 2 -or $profile.connection.cpu_family -ne "s7-1500") {
    throw "The packaged profile is not the reviewed Scene 2 S7-1500 contract."
}
if (
    $profile.connection.cycle_ms -ne 20 -or
    $profile.connection.connect_timeout_ms -ne 2000 -or
    $profile.heartbeat.timeout_ms -ne 1000
) {
    throw "The packaged profile timing contract is incorrect."
}
$actualTags = @{}
foreach ($tag in $profile.tags) {
    if ($actualTags.ContainsKey($tag.name)) {
        throw "Duplicate profile tag: $($tag.name)"
    }
    $actualTags[$tag.name] = $tag
}
if ($actualTags.Count -ne $expectedTags.Count) {
    throw "The packaged profile does not contain the exact ten-tag contract."
}
foreach ($name in $expectedTags.Keys) {
    if (-not $actualTags.ContainsKey($name)) {
        throw "The packaged profile is missing tag: $name"
    }
    $expected = $expectedTags[$name]
    $tag = $actualTags[$name]
    if (
        $tag.address -ne $expected[0] -or
        $tag.data_type -ne $expected[1] -or
        $tag.direction -ne $expected[2]
    ) {
        throw "The packaged profile mapping is incorrect for tag: $name"
    }
}

$hash = {
    param([string]$Path)
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
$preflight = [ordered]@{
    schemaVersion = 1
    generatedAtUtc = [DateTime]::UtcNow.ToString("o")
    packageVersion = $version
    computerName = $env:COMPUTERNAME
    windows = [ordered]@{
        caption = (Get-CimInstance Win32_OperatingSystem).Caption
        version = [Environment]::OSVersion.Version.ToString()
        architecture = $env:PROCESSOR_ARCHITECTURE
    }
    capability = [ordered]@{
        realPlcWritesEnabled = [bool]$capability.realPlcWritesEnabled
        plcPilotMode = [string]$capability.plcPilotMode
    }
    target = [ordered]@{
        cpuFamily = [string]$profile.connection.cpu_family
        ip = [string]$profile.connection.ip
        rack = [int]$profile.connection.rack
        slot = [int]$profile.connection.slot
        cycleMs = [int]$profile.connection.cycle_ms
        connectTimeoutMs = [int]$profile.connection.connect_timeout_ms
        heartbeatTimeoutMs = [int]$profile.heartbeat.timeout_ms
    }
    writeAddresses = @(
        $profile.tags |
            Where-Object direction -eq "pc_to_plc" |
            ForEach-Object address
    )
    readAddresses = @(
        $profile.tags |
            Where-Object direction -eq "plc_to_pc" |
            ForEach-Object address
    )
    hashes = [ordered]@{
        executableSha256 = &$hash (Join-Path $packageRoot "RungProof.exe")
        capabilitySha256 = &$hash $capabilityPath
        profileSha256 = &$hash $profilePath
        packageManifestSha256 = &$hash (Join-Path $packageRoot "SHA256.txt")
    }
    checks = [ordered]@{
        packageIntegrity = $true
        enabledLiveBenchCapability = $true
        exactScene2Profile = $true
        plcConnectionAttempted = $false
    }
}
$preflightPath = Join-Path $OutputDirectory "BENCH-PREFLIGHT.json"
$preflight | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $preflightPath -Encoding utf8

$resultTemplate = [ordered]@{
    schemaVersion = 1
    preflightSha256 = &$hash $preflightPath
    bench = [ordered]@{
        tiaPortalVersion = ""
        cpuOrderNumber = ""
        cpuFirmware = ""
        vmPlatform = ""
        noPhysicalIoConnected = $null
        db14StandardNonOptimized = $null
        profileEndpointConfirmed = $null
    }
    observations = [ordered]@{
        tiaCompilePassed = $null
        readOnlyZeroWritesObserved = $null
        exactWriteScopeObserved = $null
        twoCyclesPassed = $null
        stopFreshRunPassed = $null
        resetPassed = $null
        heartbeatLossSafe = $null
        networkLossSafe = $null
        reconnectFreshRunPassed = $null
        disconnectSafe = $null
        closeSafe = $null
    }
    approval = [ordered]@{
        result = ""
        approvedBy = ""
        approvedAt = ""
    }
    notes = ""
}
$resultPath = Join-Path $OutputDirectory "BENCH-RESULT.json"
if (-not (Test-Path -LiteralPath $resultPath)) {
    $resultTemplate | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8
}

if ($BaselineEvidenceDirectory) {
    $BaselineEvidenceDirectory = [System.IO.Path]::GetFullPath(
        $BaselineEvidenceDirectory
    )
    $baselineAcceptancePath = Join-Path `
        $BaselineEvidenceDirectory `
        "BENCH-ACCEPTANCE.json"
    if (-not (Test-Path -LiteralPath $baselineAcceptancePath -PathType Leaf)) {
        throw "Baseline BENCH-ACCEPTANCE.json is missing: $baselineAcceptancePath"
    }
    $deltaTemplate = [ordered]@{
        schemaVersion = 1
        changeId = "disconnect-telemetry-truthfulness"
        preflightSha256 = &$hash $preflightPath
        baselineAcceptanceSha256 = &$hash $baselineAcceptancePath
        observations = [ordered]@{
            normalCyclePassed = $null
            exactWriteScopeReconfirmed = $null
            disconnectTelemetryUnavailable = $null
            disconnectWatchdogSafe = $null
            networkLossTelemetryUnavailable = $null
            networkLossPlantSafe = $null
            automaticReconnectPassed = $null
            reconnectFreshRunPassed = $null
            closeSafe = $null
        }
        approval = [ordered]@{
            result = ""
            approvedBy = ""
            approvedAt = ""
        }
        notes = ""
    }
    $deltaPath = Join-Path $OutputDirectory "BENCH-DELTA-RESULT.json"
    if (-not (Test-Path -LiteralPath $deltaPath)) {
        $deltaTemplate |
            ConvertTo-Json -Depth 8 |
            Set-Content -LiteralPath $deltaPath -Encoding utf8
    }
    Write-Host "DELTA_RESULT_TEMPLATE: $deltaPath"
}

Write-Host "RUNGPROOF_BENCH_PREFLIGHT: PASS"
Write-Host "PLC_CONNECTION_ATTEMPTED: FALSE"
Write-Host "PREFLIGHT: $preflightPath"
Write-Host "RESULT_TEMPLATE: $resultPath"
