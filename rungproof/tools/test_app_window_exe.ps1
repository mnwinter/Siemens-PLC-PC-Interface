[CmdletBinding()]
param(
    [string]$Executable
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
    throw "App-window test executable must be under $buildRoot"
}
if (-not (Test-Path -LiteralPath $resolvedExecutable -PathType Leaf)) {
    throw "Executable not found: $resolvedExecutable"
}

$existing = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -eq "RungProof.exe" -and
            $_.ExecutablePath -eq $resolvedExecutable
        }
)
if ($existing.Count -ne 0) {
    throw "A packaged RungProof process is already running."
}

$browserProcessesBefore = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @("msedge.exe", "chrome.exe") -and
            $_.CommandLine -match "RungProof"
        } |
        Select-Object -ExpandProperty ProcessId
)

$launched = $null
$windowProcess = $null
$previousQpaPlatform = $env:QT_QPA_PLATFORM
try {
    # This is deliberately a visible-window test. A preceding headless Qt test
    # must not leak its offscreen platform setting into the packaged process.
    $env:QT_QPA_PLATFORM = $null
    $launched = Start-Process `
        -FilePath $resolvedExecutable `
        -WorkingDirectory (Split-Path -Parent $resolvedExecutable) `
        -PassThru

    for ($attempt = 0; $attempt -lt 120; $attempt += 1) {
        Start-Sleep -Milliseconds 250
        $windowProcess = @(
            Get-Process -Name RungProof -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.MainWindowTitle -eq (
                        "RungProof - PLC Visual Simulator"
                    )
                }
        ) | Select-Object -First 1
        if ($null -ne $windowProcess) {
            break
        }
        if ($launched.HasExited -and $null -eq $windowProcess) {
            throw "Packaged RungProof exited before opening its native window."
        }
    }
    if ($null -eq $windowProcess) {
        throw "Packaged RungProof did not open a native window in 30 seconds."
    }

    $packageProcesses = @(
        Get-CimInstance Win32_Process |
            Where-Object {
                $_.Name -eq "RungProof.exe" -and
                $_.ExecutablePath -eq $resolvedExecutable
            }
    )
    $packageProcessIds = @(
        $packageProcesses | Select-Object -ExpandProperty ProcessId
    )
    $listeners = @(
        Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
            Where-Object {
                $_.OwningProcess -in $packageProcessIds
            }
    )
    if ($listeners.Count -ne 0) {
        throw "Native RungProof unexpectedly opened a listening HTTP port."
    }

    $browserProcessesAfter = @(
        Get-CimInstance Win32_Process |
            Where-Object {
                $_.Name -in @("msedge.exe", "chrome.exe") -and
                $_.CommandLine -match "RungProof"
            } |
            Select-Object -ExpandProperty ProcessId
    )
    $newBrowserProcesses = @(
        Compare-Object `
            -ReferenceObject $browserProcessesBefore `
            -DifferenceObject $browserProcessesAfter |
            Where-Object SideIndicator -eq "=>" |
            Select-Object -ExpandProperty InputObject
    )
    if ($newBrowserProcesses.Count -ne 0) {
        throw "Native RungProof launched a browser process."
    }

    Write-Host "NATIVE_APP_WINDOW: PASS"
    Write-Host "WINDOW_TITLE: $($windowProcess.MainWindowTitle)"
    Write-Host "PACKAGE_PROCESS_COUNT: $($packageProcesses.Count)"
    Write-Host "LISTENING_PORT_COUNT: $($listeners.Count)"
    Write-Host "NEW_BROWSER_PROCESS_COUNT: $($newBrowserProcesses.Count)"

    [void]$windowProcess.CloseMainWindow()
    for ($attempt = 0; $attempt -lt 80; $attempt += 1) {
        Start-Sleep -Milliseconds 250
        $remaining = @(
            Get-CimInstance Win32_Process |
                Where-Object {
                    $_.Name -eq "RungProof.exe" -and
                    $_.ExecutablePath -eq $resolvedExecutable
                }
        )
        if ($remaining.Count -eq 0) {
            break
        }
    }
    if ($remaining.Count -ne 0) {
        throw "Native RungProof did not exit cleanly after WM_CLOSE."
    }
    Write-Host "NATIVE_APP_EXIT: PASS"
}
finally {
    $env:QT_QPA_PLATFORM = $previousQpaPlatform
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -eq "RungProof.exe" -and
            $_.ExecutablePath -eq $resolvedExecutable
        } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
        }
    if ($null -ne $launched -and -not $launched.HasExited) {
        Stop-Process -Id $launched.Id -ErrorAction SilentlyContinue
    }
}
