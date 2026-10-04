[CmdletBinding()]
param(
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$executable = Join-Path $packageRoot "RungProof.exe"
if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "RungProof executable is missing: $executable"
}
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $packageRoot "visual-evidence"
}
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)

$argumentLine = '--capture-view-dir "' + $OutputDirectory + '"'
$process = Start-Process `
    -FilePath $executable `
    -WorkingDirectory $packageRoot `
    -ArgumentList $argumentLine `
    -PassThru `
    -Wait
if ($process.ExitCode -ne 0) {
    throw "RungProof view capture exited with code $($process.ExitCode)."
}

$report = Join-Path $OutputDirectory "CAPTURE-REPORT.json"
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) {
    throw "RungProof did not create its view-capture report."
}
Write-Host "RUNGPROOF_VIEW_CAPTURE: PASS"
Write-Host "OUTPUT: $OutputDirectory"
