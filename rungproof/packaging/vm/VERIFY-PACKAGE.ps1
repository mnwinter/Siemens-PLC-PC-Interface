[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$manifestPath = Join-Path $packageRoot "SHA256.txt"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Package hash manifest is missing: $manifestPath"
}

$checked = 0
foreach ($line in Get-Content -LiteralPath $manifestPath) {
    if (-not $line.Trim()) {
        continue
    }
    if ($line -notmatch '^([0-9a-fA-F]{64})  (.+)$') {
        throw "Invalid SHA256.txt entry: $line"
    }
    $expected = $Matches[1].ToLowerInvariant()
    $relative = $Matches[2].Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $candidate = [System.IO.Path]::GetFullPath((Join-Path $packageRoot $relative))
    if (-not $candidate.StartsWith(
        $packageRoot + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Unsafe package hash path: $relative"
    }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "Package file is missing: $relative"
    }
    $actual = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) {
        throw "Package file hash mismatch: $relative"
    }
    $checked++
}

Write-Host "RUNGPROOF_PACKAGE_INTEGRITY: PASS ($checked files)"
