[CmdletBinding()]
param(
    [string]$EvidenceDirectory = ""
)

$ErrorActionPreference = "Stop"

# Keep the packaged validator independent of PowerShell module auto-loading.
# Some locked-down VM/test hosts expose the core language and .NET runtime but
# do not auto-import Microsoft.PowerShell.Utility, where Get-FileHash lives.
function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $stream = [System.IO.File]::OpenRead($LiteralPath)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            return ([System.BitConverter]::ToString($sha256.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $sha256.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

$packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if (-not $EvidenceDirectory) {
    $EvidenceDirectory = Join-Path $packageRoot "bench-evidence"
}
$EvidenceDirectory = [System.IO.Path]::GetFullPath($EvidenceDirectory)
$preflightPath = Join-Path $EvidenceDirectory "BENCH-PREFLIGHT.json"
$resultPath = Join-Path $EvidenceDirectory "BENCH-RESULT.json"
foreach ($path in @($preflightPath, $resultPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required bench evidence file is missing: $path"
    }
}

$preflight = Get-Content -LiteralPath $preflightPath -Raw | ConvertFrom-Json
$result = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
if ($preflight.schemaVersion -ne 1 -or $result.schemaVersion -ne 1) {
    throw "Unsupported bench evidence schema version."
}
$preflightHash = Get-Sha256Hex -LiteralPath $preflightPath
if ($result.preflightSha256 -ne $preflightHash) {
    throw "BENCH-RESULT.json is not tied to the current preflight record."
}

$requiredText = [ordered]@{
    "bench.tiaPortalVersion" = [string]$result.bench.tiaPortalVersion
    "bench.cpuOrderNumber" = [string]$result.bench.cpuOrderNumber
    "bench.cpuFirmware" = [string]$result.bench.cpuFirmware
    "bench.vmPlatform" = [string]$result.bench.vmPlatform
    "approval.approvedBy" = [string]$result.approval.approvedBy
    "approval.approvedAt" = [string]$result.approval.approvedAt
}
$missing = @(
    $requiredText.Keys | Where-Object { [string]::IsNullOrWhiteSpace($requiredText[$_]) }
)
if ($missing.Count -ne 0) {
    throw "Required bench evidence is blank: $($missing -join ', ')"
}

$requiredTrue = [ordered]@{
    "bench.noPhysicalIoConnected" = $result.bench.noPhysicalIoConnected
    "bench.db14StandardNonOptimized" = $result.bench.db14StandardNonOptimized
    "bench.profileEndpointConfirmed" = $result.bench.profileEndpointConfirmed
    "observations.tiaCompilePassed" = $result.observations.tiaCompilePassed
    "observations.readOnlyZeroWritesObserved" = $result.observations.readOnlyZeroWritesObserved
    "observations.exactWriteScopeObserved" = $result.observations.exactWriteScopeObserved
    "observations.twoCyclesPassed" = $result.observations.twoCyclesPassed
    "observations.stopFreshRunPassed" = $result.observations.stopFreshRunPassed
    "observations.resetPassed" = $result.observations.resetPassed
    "observations.heartbeatLossSafe" = $result.observations.heartbeatLossSafe
    "observations.networkLossSafe" = $result.observations.networkLossSafe
    "observations.reconnectFreshRunPassed" = $result.observations.reconnectFreshRunPassed
    "observations.disconnectSafe" = $result.observations.disconnectSafe
    "observations.closeSafe" = $result.observations.closeSafe
}
$failed = @($requiredTrue.Keys | Where-Object { $requiredTrue[$_] -ne $true })
if ($failed.Count -ne 0) {
    throw "Bench acceptance is incomplete or failed: $($failed -join ', ')"
}
if ([string]$result.approval.result -cne "PASS") {
    throw "approval.result must be exactly PASS."
}

$resultHash = Get-Sha256Hex -LiteralPath $resultPath
$acceptance = [ordered]@{
    schemaVersion = 1
    acceptedAtUtc = [DateTime]::UtcNow.ToString("o")
    packageVersion = [string]$preflight.packageVersion
    preflightSha256 = $preflightHash
    resultSha256 = $resultHash
    executableSha256 = [string]$preflight.hashes.executableSha256
    profileSha256 = [string]$preflight.hashes.profileSha256
    target = $preflight.target
    approvedBy = [string]$result.approval.approvedBy
    approvedAt = [string]$result.approval.approvedAt
    result = "PASS"
}
$acceptancePath = Join-Path $EvidenceDirectory "BENCH-ACCEPTANCE.json"
$acceptance | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $acceptancePath -Encoding utf8

Write-Host "RUNGPROOF_BENCH_ACCEPTANCE: PASS"
Write-Host "ACCEPTANCE: $acceptancePath"
