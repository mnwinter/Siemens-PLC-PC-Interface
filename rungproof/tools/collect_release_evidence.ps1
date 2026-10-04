[CmdletBinding()]
param(
    [string[]]$VerificationLog = @()
)

$ErrorActionPreference = "Stop"
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$version = (Get-Content -LiteralPath (Join-Path $repoRoot "VERSION") -Raw).Trim()
$buildRoot = Join-Path $repoRoot "build"
$zipPath = Join-Path $buildRoot "RungProof-VM-v$version.zip"
$packageDir = Join-Path $buildRoot "RungProof-VM-v$version"
$evidenceDir = Join-Path $buildRoot "release-evidence\v$version"

if (-not (Test-Path -LiteralPath $zipPath -PathType Leaf)) {
    throw "Versioned release ZIP is missing: $zipPath"
}
if (-not (Test-Path -LiteralPath $packageDir -PathType Container)) {
    throw "Versioned package directory is missing: $packageDir"
}

New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
$evidenceDir = [System.IO.Path]::GetFullPath($evidenceDir)
if (-not $evidenceDir.StartsWith(
    [System.IO.Path]::GetFullPath($buildRoot) + [System.IO.Path]::DirectorySeparatorChar,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Refusing to write evidence outside the build directory."
}

$filesToCopy = @(
    "BUILD-VERSIONS.txt",
    "PILOT-CAPABILITIES.json",
    "RungProof.cdx.json",
    "SHA256.txt",
    "VERSION"
)
foreach ($name in $filesToCopy) {
    $source = Join-Path $packageDir $name
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Required release evidence is missing: $source"
    }
    Copy-Item -LiteralPath $source -Destination $evidenceDir -Force
}

$copiedLogs = @()
foreach ($log in $VerificationLog) {
    $resolved = [System.IO.Path]::GetFullPath($log)
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        throw "Verification log is missing: $resolved"
    }
    $destination = Join-Path $evidenceDir ([System.IO.Path]::GetFileName($resolved))
    Copy-Item -LiteralPath $resolved -Destination $destination -Force
    $copiedLogs += [System.IO.Path]::GetFileName($resolved)
}

$gitHead = (& git -C $repoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the Git revision."
}
$gitStatus = @(& git -C $repoRoot status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the Git working-tree status."
}
$record = [ordered]@{
    schemaVersion = 1
    product = "RungProof"
    version = $version
    collectedUtc = [DateTime]::UtcNow.ToString("o")
    gitRevision = $gitHead
    gitWorkingTreeClean = ($gitStatus.Count -eq 0)
    artifact = [ordered]@{
        file = [System.IO.Path]::GetFileName($zipPath)
        sha256 = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
        bytes = (Get-Item -LiteralPath $zipPath).Length
    }
    verificationLogs = $copiedLogs
}
$record | ConvertTo-Json -Depth 5 | Set-Content `
    -LiteralPath (Join-Path $evidenceDir "RELEASE-EVIDENCE.json") `
    -Encoding utf8

Write-Host "RELEASE_EVIDENCE: $evidenceDir"
Write-Host "ZIP_SHA256: $($record.artifact.sha256)"
Write-Host "GIT_WORKTREE_CLEAN: $($record.gitWorkingTreeClean)"
