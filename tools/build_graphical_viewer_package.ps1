[CmdletBinding()]
param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$buildRoot = Join-Path $repoRoot "build"
$packageDir = Join-Path $buildRoot "graphical-viewer-vm-package"
$workDir = Join-Path $buildRoot "graphical-viewer-pyinstaller-work"
$specDir = Join-Path $buildRoot "graphical-viewer-pyinstaller-spec"
$zipPath = Join-Path $buildRoot "SiemensPlcPcInterface-GraphicalViewer-VM.zip"

function Assert-BuildPath {
    param([Parameter(Mandatory)][string]$Path)

    $resolvedParent = [System.IO.Path]::GetFullPath(
        (Split-Path -Parent $Path)
    )
    $resolvedBuild = [System.IO.Path]::GetFullPath($buildRoot)
    if (-not $resolvedParent.StartsWith(
        $resolvedBuild,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Refusing to modify a path outside $resolvedBuild`: $Path"
    }
}

Assert-BuildPath -Path $packageDir
Assert-BuildPath -Path $workDir
Assert-BuildPath -Path $specDir
Assert-BuildPath -Path $zipPath

if (-not $SkipBuild) {
    & py -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --name SiemensPlcPcInterface `
        --paths (Join-Path $repoRoot "src") `
        --collect-all snap7 `
        --distpath $packageDir `
        --workpath $workDir `
        --specpath $specDir `
        (Join-Path $repoRoot "tools\runtime_entrypoint.py")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
}

$executable = Join-Path $packageDir "SiemensPlcPcInterface.exe"
if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "Packaged executable is missing: $executable"
}

$packageFiles = @{
    (Join-Path $repoRoot "examples\db14-conveyor-interface.json") =
        "db14-conveyor-interface.json"
    (Join-Path $repoRoot "examples\conveyor-scene-fast.json") =
        "conveyor-scene-fast.json"
    (Join-Path $repoRoot "docs\GRAPHICAL_VIEWER.md") =
        "GRAPHICAL_VIEWER.md"
    (Join-Path $repoRoot "docs\FIRST_SCENE.md") =
        "FIRST_SCENE.md"
    (Join-Path $repoRoot "docs\USER_SETUP.md") =
        "USER_SETUP.md"
    (Join-Path $repoRoot "packaging\graphical-viewer\1-VALIDATE-GRAPHICAL-VIEWER.cmd") =
        "1-VALIDATE-GRAPHICAL-VIEWER.cmd"
    (Join-Path $repoRoot "packaging\graphical-viewer\2-LIVE-GRAPHICAL-VIEWER.cmd") =
        "2-LIVE-GRAPHICAL-VIEWER.cmd"
    (Join-Path $repoRoot "packaging\graphical-viewer\README-GRAPHICAL-VIEWER.txt") =
        "README-GRAPHICAL-VIEWER.txt"
}

foreach ($entry in $packageFiles.GetEnumerator()) {
    Copy-Item -LiteralPath $entry.Key `
        -Destination (Join-Path $packageDir $entry.Value) `
        -Force
}

$hashLines = Get-ChildItem -LiteralPath $packageDir -File |
    Where-Object Name -ne "SHA256.txt" |
    Sort-Object Name |
    ForEach-Object {
        $hash = Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256
        "$($hash.Hash.ToLowerInvariant())  $($_.Name)"
    }
Set-Content -LiteralPath (Join-Path $packageDir "SHA256.txt") `
    -Value $hashLines `
    -Encoding ascii

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -Path (Join-Path $packageDir "*") `
    -DestinationPath $zipPath `
    -CompressionLevel Optimal

Write-Host "PACKAGE_DIR: $packageDir"
Write-Host "ZIP: $zipPath"
