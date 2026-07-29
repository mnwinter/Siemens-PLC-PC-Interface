[CmdletBinding()]
param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$buildRoot = Join-Path $repoRoot "build"
$packageDir = Join-Path $buildRoot "scene-2-pusher-vm-package"
$workDir = Join-Path $buildRoot "scene-2-pusher-pyinstaller-work"
$specDir = Join-Path $buildRoot "scene-2-pusher-pyinstaller-spec"
$zipPath = Join-Path $buildRoot "SiemensPlcPcInterface-Scene-2-Pusher-VM.zip"

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
    (Join-Path $repoRoot "examples\scene-2-db14-pusher-interface.json") =
        "scene-2-db14-pusher-interface.json"
    (Join-Path $repoRoot "examples\scene-2-conveyor-pusher.json") =
        "scene-2-conveyor-pusher.json"
    (Join-Path $repoRoot "docs\SCENE_2_PUSHER.md") =
        "SCENE_2_PUSHER.md"
    (Join-Path $repoRoot "docs\USER_SETUP.md") =
        "USER_SETUP.md"
    (Join-Path $repoRoot "packaging\scene-2-pusher\1-VALIDATE-SCENE-2.cmd") =
        "1-VALIDATE-SCENE-2.cmd"
    (Join-Path $repoRoot "packaging\scene-2-pusher\2-PREVIEW-SCENE-2.cmd") =
        "2-PREVIEW-SCENE-2.cmd"
    (Join-Path $repoRoot "packaging\scene-2-pusher\3-LIVE-SCENE-2.cmd") =
        "3-LIVE-SCENE-2.cmd"
    (Join-Path $repoRoot "packaging\scene-2-pusher\README-SCENE-2.txt") =
        "README-SCENE-2.txt"
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
