[CmdletBinding()]
param(
    [string]$Executable,
    [switch]$ExpectRealPlcWritesEnabled
)

$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$buildRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "build"))
if ([string]::IsNullOrWhiteSpace($Executable)) {
    $Executable = Join-Path $buildRoot "RungProof-VM\RungProof.exe"
}
$resolvedExecutable = [System.IO.Path]::GetFullPath($Executable)
if (-not $resolvedExecutable.StartsWith(
    $buildRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Smoke-test executable must be under $buildRoot"
}
if (-not (Test-Path -LiteralPath $resolvedExecutable -PathType Leaf)) {
    throw "Executable not found: $resolvedExecutable"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$testDir = Join-Path $buildRoot "native-exe-smoke-$stamp"
New-Item -ItemType Directory -Path $testDir | Out-Null
$sourcePackage = Split-Path -Parent $resolvedExecutable
$testPackage = Join-Path $testDir "RungProof-VM"
Copy-Item `
    -LiteralPath $sourcePackage `
    -Destination $testPackage `
    -Recurse
$testExe = Join-Path $testPackage "RungProof.exe"
if (-not (Test-Path -LiteralPath $testExe -PathType Leaf)) {
    throw "Copied one-folder package is missing its executable."
}
if (
    -not (Test-Path `
        -LiteralPath (Join-Path $testPackage "plc-profiles") `
        -PathType Container)
) {
    throw "Copied one-folder package is missing its PLC profiles."
}
$qtCore = @(
    Get-ChildItem `
        -LiteralPath $testPackage `
        -Recurse `
        -File `
        -Filter "Qt6Core.dll"
)
if ($qtCore.Count -ne 1) {
    throw "Copied one-folder package does not contain one Qt6Core.dll."
}

$reportPath = Join-Path $testDir "native-self-test.json"
# Deliberately launch outside the package directory. Frozen resource lookup
# must follow RungProof.exe, not the caller's working directory.
$process = Start-Process `
    -FilePath $testExe `
    -ArgumentList @("--self-test-report", "`"$reportPath`"") `
    -WorkingDirectory $testDir `
    -WindowStyle Hidden `
    -PassThru

$netTcpCommand = Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue
if ($null -eq $netTcpCommand) {
    throw "Get-NetTCPConnection is required for packaged listener proof."
}
$selfTestDeadline = [DateTime]::UtcNow.AddSeconds(30)
$listenerDetected = $false
do {
    $process.Refresh()
    if ([DateTime]::UtcNow -ge $selfTestDeadline) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Packaged native self-test exceeded the 30 second limit."
    }
    try {
        $processListeners = @(
            Get-NetTCPConnection `
                -State Listen `
                -ErrorAction Stop |
                Where-Object OwningProcess -eq $process.Id
        )
    }
    catch {
        $process.Refresh()
        if ($process.HasExited) {
            $processListeners = @()
        }
        else {
            throw (
                "Could not inspect packaged self-test listeners: " +
                $_.Exception.Message
            )
        }
    }
    if ($processListeners.Count -ne 0) {
        $listenerDetected = $true
    }
    if (-not $process.HasExited) {
        Start-Sleep -Milliseconds 20
    }
} while (-not $process.HasExited)
$process.WaitForExit()

if ($process.ExitCode -ne 0) {
    throw "Packaged native self-test exited with code $($process.ExitCode)."
}
if ($listenerDetected) {
    throw "Native packaged self-test opened a listening port."
}
if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
    throw "Packaged native self-test did not create $reportPath"
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if (
    -not $report.ok -or
    $report.entrypoint -ne "native-qt" -or
    $report.defaultRenderer -ne "software" -or
    $report.rendererId -ne "isometric-3d" -or
    $report.nativeChildWindow -ne $false -or
    $report.readOnlyPlcTestAvailable -ne $true -or
    $report.realPlcWritesEnabled -ne [bool]$ExpectRealPlcWritesEnabled -or
    $report.browserEngine -ne $false -or
    $report.httpServer -ne $false -or
    $report.plcConnectionAttempted -ne $false
) {
    throw "Packaged native self-test contract failed."
}
if (
    $report.target.ip -ne "10.70.9.201" -or
    $report.target.rack -ne 0 -or
    $report.target.slot -ne 1 -or
    $report.target.cycleMs -ne 20
) {
    throw "Packaged native DB14 target contract is incorrect."
}
$expectedWrites = @(
    "DB14.DBX0.0",
    "DB14.DBX0.1",
    "DB14.DBX0.2",
    "DB14.DBD2"
)
if (
    (Compare-Object `
        -ReferenceObject $expectedWrites `
        -DifferenceObject @($report.writeAddresses)).Count -ne 0
) {
    throw "Packaged native write scope is incorrect."
}

$analysisFiles = @(
    Get-ChildItem `
        -LiteralPath (Join-Path $buildRoot "pyinstaller-work\RungProof") `
        -Recurse `
        -File `
        -Include *.toc,*.txt `
        -ErrorAction SilentlyContinue
)
$analysisTocs = @(
    Get-ChildItem `
        -LiteralPath (Join-Path $buildRoot "pyinstaller-work\RungProof") `
        -File `
        -Filter "Analysis-*.toc" `
        -ErrorAction SilentlyContinue
)
if ($analysisTocs.Count -ne 1) {
    throw (
        "Expected one current PyInstaller Analysis-*.toc; found " +
        "$($analysisTocs.Count)."
    )
}
$currentAnalysis = (
    $analysisTocs |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
)
$sourceExe = Get-Item -LiteralPath $resolvedExecutable
$analysisAgeMinutes = [Math]::Abs(
    (
        $sourceExe.LastWriteTimeUtc -
        $currentAnalysis.LastWriteTimeUtc
    ).TotalMinutes
)
if ($analysisAgeMinutes -gt 15) {
    throw "PyInstaller Analysis TOC does not match the current package."
}
$analysisText = ($analysisFiles | ForEach-Object {
    Get-Content -LiteralPath $_.FullName -Raw -ErrorAction SilentlyContinue
}) -join "`n"
foreach ($forbidden in @(
    "QtWebEngine",
    "serve_player.py",
    "webbrowser.py",
    "http.server"
)) {
    if ($analysisText -match [regex]::Escape($forbidden)) {
        throw "Packaged analysis contains forbidden browser stack: $forbidden"
    }
}
$packageEntries = @(
    Get-ChildItem -LiteralPath $testPackage -Recurse -Force
)
foreach ($forbiddenName in @(
    "QtWebEngine",
    "serve_player",
    "player.html",
    "three.module",
    "webbrowser.py"
)) {
    if (
        $packageEntries.FullName -match [regex]::Escape($forbiddenName)
    ) {
        throw "Copied package contains forbidden browser asset: $forbiddenName"
    }
}

Write-Host "NATIVE_EXE_SMOKE_TEST: PASS"
Write-Host "ENTRYPOINT: $($report.entrypoint)"
Write-Host "DEFAULT_RENDERER: $($report.defaultRenderer)"
Write-Host "RENDERER_ID: $($report.rendererId)"
Write-Host "NATIVE_CHILD_WINDOW: $($report.nativeChildWindow)"
Write-Host "READ_ONLY_PLC_TEST: $($report.readOnlyPlcTestAvailable)"
Write-Host "REAL_PLC_WRITES_ENABLED: $($report.realPlcWritesEnabled)"
Write-Host "BROWSER_ENGINE: $($report.browserEngine)"
Write-Host "HTTP_SERVER: $($report.httpServer)"
Write-Host "PLC_CONNECTION_ATTEMPTED: $($report.plcConnectionAttempted)"
Write-Host "TARGET: $($report.target.ip) rack=$($report.target.rack) slot=$($report.target.slot)"
Write-Host "CYCLE_MS: $($report.target.cycleMs)"
Write-Host "WRITE_SCOPE: $($report.writeAddresses -join ', ')"
Write-Host "TEST_DIR: $testDir"
