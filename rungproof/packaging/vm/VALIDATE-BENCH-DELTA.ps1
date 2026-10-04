[CmdletBinding()]
param(
    [string]$EvidenceDirectory = "",
    [Parameter(Mandatory = $true)]
    [string]$BaselineEvidenceDirectory
)

$ErrorActionPreference = "Stop"
$packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if (-not $EvidenceDirectory) {
    $EvidenceDirectory = Join-Path $packageRoot "bench-evidence"
}
$EvidenceDirectory = [System.IO.Path]::GetFullPath($EvidenceDirectory)
$BaselineEvidenceDirectory = [System.IO.Path]::GetFullPath(
    $BaselineEvidenceDirectory
)

$paths = [ordered]@{
    currentPreflight = Join-Path $EvidenceDirectory "BENCH-PREFLIGHT.json"
    deltaResult = Join-Path $EvidenceDirectory "BENCH-DELTA-RESULT.json"
    baselinePreflight = Join-Path $BaselineEvidenceDirectory "BENCH-PREFLIGHT.json"
    baselineResult = Join-Path $BaselineEvidenceDirectory "BENCH-RESULT.json"
    baselineAcceptance = Join-Path $BaselineEvidenceDirectory "BENCH-ACCEPTANCE.json"
}
foreach ($name in $paths.Keys) {
    if (-not (Test-Path -LiteralPath $paths[$name] -PathType Leaf)) {
        throw "Required delta evidence file is missing: $($paths[$name])"
    }
}

$hash = {
    param([string]$Path)
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            ([System.BitConverter]::ToString($sha256.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $sha256.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}
$readJson = {
    param([string]$Path)
    Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

$currentPreflight = &$readJson $paths.currentPreflight
$delta = &$readJson $paths.deltaResult
$baselinePreflight = &$readJson $paths.baselinePreflight
$baselineResult = &$readJson $paths.baselineResult
$baselineAcceptance = &$readJson $paths.baselineAcceptance

foreach ($document in @(
    $currentPreflight,
    $delta,
    $baselinePreflight,
    $baselineResult,
    $baselineAcceptance
)) {
    if ($document.schemaVersion -ne 1) {
        throw "Unsupported bench delta evidence schema version."
    }
}
if ($delta.changeId -cne "disconnect-telemetry-truthfulness") {
    throw "Unsupported or missing bench delta changeId."
}

$currentPreflightHash = &$hash $paths.currentPreflight
$baselinePreflightHash = &$hash $paths.baselinePreflight
$baselineResultHash = &$hash $paths.baselineResult
$baselineAcceptanceHash = &$hash $paths.baselineAcceptance

if ($delta.preflightSha256 -ne $currentPreflightHash) {
    throw "BENCH-DELTA-RESULT.json is not tied to the current preflight record."
}
if ($delta.baselineAcceptanceSha256 -ne $baselineAcceptanceHash) {
    throw "BENCH-DELTA-RESULT.json is not tied to the supplied baseline acceptance."
}
if (
    $baselineResult.preflightSha256 -ne $baselinePreflightHash -or
    $baselineAcceptance.preflightSha256 -ne $baselinePreflightHash -or
    $baselineAcceptance.resultSha256 -ne $baselineResultHash
) {
    throw "The baseline preflight/result/acceptance hash chain is invalid."
}
if (
    $baselineAcceptance.result -cne "PASS" -or
    $baselineResult.approval.result -cne "PASS"
) {
    throw "The supplied baseline was not accepted as PASS."
}
if (
    $baselineAcceptance.executableSha256 -ne
        $baselinePreflight.hashes.executableSha256 -or
    $baselineAcceptance.profileSha256 -ne
        $baselinePreflight.hashes.profileSha256
) {
    throw "The baseline acceptance does not identify its preflight artifacts."
}
if (
    $baselinePreflight.packageVersion -ne "0.2.0-pilot.1" -or
    $currentPreflight.packageVersion -ne "0.2.0-pilot.2"
) {
    throw "This delta requires the accepted pilot.1 baseline and pilot.2 candidate."
}
if (
    $currentPreflight.hashes.profileSha256 -ne
        $baselinePreflight.hashes.profileSha256
) {
    throw "The current candidate is not compatible with the accepted baseline."
}
$currentTarget = $currentPreflight.target | ConvertTo-Json -Compress -Depth 8
$baselineTarget = $baselinePreflight.target | ConvertTo-Json -Compress -Depth 8
if ($currentTarget -cne $baselineTarget) {
    throw "The current PLC target/timing contract differs from the baseline."
}
if (
    $currentPreflight.hashes.executableSha256 -eq
        $baselinePreflight.hashes.executableSha256
) {
    throw "Delta qualification requires a changed executable."
}

$requiredTrue = [ordered]@{
    "observations.normalCyclePassed" = $delta.observations.normalCyclePassed
    "observations.exactWriteScopeReconfirmed" = $delta.observations.exactWriteScopeReconfirmed
    "observations.disconnectTelemetryUnavailable" = $delta.observations.disconnectTelemetryUnavailable
    "observations.disconnectWatchdogSafe" = $delta.observations.disconnectWatchdogSafe
    "observations.networkLossTelemetryUnavailable" = $delta.observations.networkLossTelemetryUnavailable
    "observations.networkLossPlantSafe" = $delta.observations.networkLossPlantSafe
    "observations.automaticReconnectPassed" = $delta.observations.automaticReconnectPassed
    "observations.reconnectFreshRunPassed" = $delta.observations.reconnectFreshRunPassed
    "observations.closeSafe" = $delta.observations.closeSafe
}
$failed = @($requiredTrue.Keys | Where-Object { $requiredTrue[$_] -ne $true })
if ($failed.Count -ne 0) {
    throw "Bench delta acceptance is incomplete or failed: $($failed -join ', ')"
}

$requiredText = [ordered]@{
    "approval.approvedBy" = [string]$delta.approval.approvedBy
    "approval.approvedAt" = [string]$delta.approval.approvedAt
}
$missing = @(
    $requiredText.Keys |
        Where-Object { [string]::IsNullOrWhiteSpace($requiredText[$_]) }
)
if ($missing.Count -ne 0) {
    throw "Required bench delta evidence is blank: $($missing -join ', ')"
}
if ($delta.approval.result -cne "PASS") {
    throw "approval.result must be exactly PASS."
}

$deltaResultHash = &$hash $paths.deltaResult
$acceptance = [ordered]@{
    schemaVersion = 1
    qualification = "delta"
    changeId = [string]$delta.changeId
    acceptedAtUtc = [DateTime]::UtcNow.ToString("o")
    packageVersion = [string]$currentPreflight.packageVersion
    preflightSha256 = $currentPreflightHash
    deltaResultSha256 = $deltaResultHash
    executableSha256 = [string]$currentPreflight.hashes.executableSha256
    profileSha256 = [string]$currentPreflight.hashes.profileSha256
    packageManifestSha256 = [string]$currentPreflight.hashes.packageManifestSha256
    baseline = [ordered]@{
        acceptanceSha256 = $baselineAcceptanceHash
        resultSha256 = $baselineResultHash
        executableSha256 = [string]$baselineAcceptance.executableSha256
    }
    target = $currentPreflight.target
    approvedBy = [string]$delta.approval.approvedBy
    approvedAt = [string]$delta.approval.approvedAt
    result = "PASS"
}
$acceptancePath = Join-Path $EvidenceDirectory "BENCH-DELTA-ACCEPTANCE.json"
$acceptance |
    ConvertTo-Json -Depth 8 |
    Set-Content -LiteralPath $acceptancePath -Encoding utf8

Write-Host "RUNGPROOF_BENCH_DELTA_ACCEPTANCE: PASS"
Write-Host "ACCEPTANCE: $acceptancePath"
