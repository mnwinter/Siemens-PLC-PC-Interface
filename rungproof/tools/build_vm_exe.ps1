[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [string]$PackageVersion = "",
    [switch]$EnableRealPlc,
    [string]$PythonExecutable = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$versionFile = Join-Path $repoRoot "VERSION"
if (-not (Test-Path -LiteralPath $versionFile -PathType Leaf)) {
    throw "Release version file is missing: $versionFile"
}
$declaredVersion = (Get-Content -LiteralPath $versionFile -Raw).Trim()
$semVerPattern = '^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)*)?$'
if ($declaredVersion -notmatch $semVerPattern) {
    throw "VERSION is not a supported semantic version: $declaredVersion"
}
if ($PackageVersion -and $PackageVersion -ne $declaredVersion) {
    throw (
        "PackageVersion $PackageVersion does not match VERSION " +
        "$declaredVersion. Update VERSION as the single release source."
    )
}
$PackageVersion = $declaredVersion

$buildRoot = Join-Path $repoRoot "build"
$packageDir = Join-Path $buildRoot "RungProof-VM"
$versionedPackageDir = Join-Path $buildRoot "RungProof-VM-v$PackageVersion"
$pyinstallerDist = Join-Path $buildRoot "pyinstaller-dist"
$builtAppDir = Join-Path $pyinstallerDist "RungProof"
$workDir = Join-Path $buildRoot "pyinstaller-work"
$specDir = Join-Path $buildRoot "pyinstaller-spec"
$buildEnvDir = Join-Path $buildRoot ".venv-rungproof"
$buildPython = Join-Path $buildEnvDir "Scripts\python.exe"
$zipPath = Join-Path $buildRoot "RungProof-VM.zip"
$versionedZipPath = Join-Path $buildRoot "RungProof-VM-v$PackageVersion.zip"
$executable = Join-Path $packageDir "RungProof.exe"
$profilesSource = Join-Path $repoRoot "prototype\plc-profiles"
$profilesDestination = Join-Path $packageDir "plc-profiles"
$licensesSource = Join-Path $repoRoot "vendor\licenses"
$licensesDestination = Join-Path $packageDir "licenses"
$interfaceSource = Join-Path $repoRoot "vendor\siemens-plc-pc-interface"
$interfaceProvenance = Join-Path $interfaceSource "PROVENANCE.md"
$requirementsFile = Join-Path $repoRoot "requirements-build.txt"
$requirementsLockFile = Join-Path $repoRoot "requirements-build.lock"

function Assert-BuildPath {
    param([Parameter(Mandatory)][string]$Path)

    $resolvedBuild = [System.IO.Path]::GetFullPath($buildRoot)
    $resolvedPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $resolvedPath.StartsWith(
        $resolvedBuild,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Refusing to modify a path outside $resolvedBuild`: $Path"
    }
}

foreach ($path in @(
    $packageDir,
    $pyinstallerDist,
    $builtAppDir,
    $workDir,
    $specDir,
    $buildEnvDir,
    $zipPath
)) {
    Assert-BuildPath -Path $path
}
Assert-BuildPath -Path $versionedZipPath
Assert-BuildPath -Path $versionedPackageDir
Assert-BuildPath -Path $profilesDestination
Assert-BuildPath -Path $licensesDestination

if (-not (Test-Path -LiteralPath $interfaceSource -PathType Container)) {
    throw "Pinned guarded PLC interface source is missing: $interfaceSource"
}
if (
    -not (Test-Path -LiteralPath $interfaceProvenance -PathType Leaf) -or
    (Get-Content -LiteralPath $interfaceProvenance -Raw) -notmatch
        "754fcfb88192f2a932bd7df70feea0d08088ab97"
) {
    throw "Pinned Siemens interface provenance is missing or incorrect."
}
if (-not (Test-Path -LiteralPath $profilesSource -PathType Container)) {
    throw "PLC profile source is missing: $profilesSource"
}
if (-not (Test-Path -LiteralPath $licensesSource -PathType Container)) {
    throw "Third-party license source is missing: $licensesSource"
}
if (-not (Test-Path -LiteralPath $requirementsFile -PathType Leaf)) {
    throw "Pinned build requirements are missing: $requirementsFile"
}
if (-not (Test-Path -LiteralPath $requirementsLockFile -PathType Leaf)) {
    throw "Hashed build lock is missing: $requirementsLockFile"
}

# The wheel hashes and release evidence target this exact x64 interpreter.
# Validate it BEFORE removing an existing environment or installing packages.
# Otherwise `py -3` can pick a different ABI and fail partway through the build.
$bootstrapPythonArgs = @()
if ($SkipBuild -and (Test-Path -LiteralPath $buildPython -PathType Leaf)) {
    $bootstrapPython = $buildPython
} elseif ($PythonExecutable) {
    if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
        throw "Python executable not found: $PythonExecutable"
    }
    $bootstrapPython = [System.IO.Path]::GetFullPath($PythonExecutable)
} else {
    $pythonLauncher = Get-Command py -CommandType Application -ErrorAction SilentlyContinue
    if ($null -eq $pythonLauncher) {
        throw "Packaging requires Python 3.14.5 x64. Install it or pass -PythonExecutable with its full path. Existing build files were preserved."
    }
    $bootstrapPython = $pythonLauncher.Source
    $bootstrapPythonArgs = @("-3.14")
}
$pythonProbeJson = & $bootstrapPython @bootstrapPythonArgs -c 'import json, struct, sys; print(json.dumps({"version": ".".join(map(str, sys.version_info[:3])), "bits": struct.calcsize("P") * 8}))'
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect Python 3.14.5 x64 for packaging. Existing build files were preserved."
}
$pythonProbe = $pythonProbeJson | ConvertFrom-Json
if ($pythonProbe.version -ne "3.14.5" -or $pythonProbe.bits -ne 64) {
    throw "Packaging requires Python 3.14.5 x64; selected $($pythonProbe.version) $($pythonProbe.bits)-bit. Existing build files were preserved."
}

if (-not $SkipBuild -and (Test-Path -LiteralPath $buildEnvDir)) {
    Remove-Item -LiteralPath $buildEnvDir -Recurse -Force
}
if (-not (Test-Path -LiteralPath $buildPython -PathType Leaf)) {
    & $bootstrapPython @bootstrapPythonArgs -m venv $buildEnvDir
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the isolated package build environment."
    }
}
& $buildPython -m pip install `
    --disable-pip-version-check `
    --require-hashes `
    --requirement $requirementsFile
if ($LASTEXITCODE -ne 0) {
    throw "Could not install the pinned package build environment."
}

$dependencyAuditJson = & $buildPython -c @"
import importlib.metadata as metadata
import json
from pathlib import Path
import re

expected = {}
for raw_line in Path(r'$requirementsLockFile').read_text(encoding='utf-8').splitlines():
    line = raw_line.strip()
    if not line or line.startswith('#'):
        continue
    requirement = line.split(' --hash=', 1)[0]
    match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([^\s]+)', requirement)
    if match is None:
        raise SystemExit(f'Unsupported locked requirement: {line}')
    expected[match.group(1).lower().replace('_', '-')] = match.group(2)

installed = {
    distribution.metadata['Name'].lower().replace('_', '-'): distribution.version
    for distribution in metadata.distributions()
    if distribution.metadata.get('Name')
}
allowed_extra = {'pip'}
missing = sorted(set(expected) - set(installed))
unexpected = sorted(set(installed) - set(expected) - allowed_extra)
mismatched = {
    name: {'expected': expected[name], 'actual': installed.get(name)}
    for name in expected
    if installed.get(name) != expected[name]
}
print(json.dumps({
    'ok': not missing and not unexpected and not mismatched,
    'missing': missing,
    'unexpected': unexpected,
    'mismatched': mismatched,
    'count': len(expected),
}))
"@
if ($LASTEXITCODE -ne 0) {
    throw "Could not audit the installed build distributions."
}
$dependencyAudit = $dependencyAuditJson | ConvertFrom-Json
if (-not $dependencyAudit.ok) {
    throw (
        "Build distribution audit failed: " +
        ($dependencyAuditJson | Out-String)
    )
}

& $buildPython (Join-Path $repoRoot "tools\verify_vendor_manifest.py")
if ($LASTEXITCODE -ne 0) {
    throw "Pinned Siemens interface source verification failed."
}

$versionJson = & $buildPython -c @"
import importlib.metadata as m, json
print(json.dumps({
    'Python': '.'.join(map(str, __import__('sys').version_info[:3])),
    'PyInstaller': m.version('PyInstaller'),
    'PySide6': m.version('PySide6'),
    'python-snap7': m.version('python-snap7'),
    'jsonschema': m.version('jsonschema'),
}))
"@
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect the Python build environment."
}
$versions = $versionJson | ConvertFrom-Json
$expectedVersions = @{
    "Python" = "3.14.5"
    "PyInstaller" = "6.21.0"
    "PySide6" = "6.11.1"
    "python-snap7" = "3.1.0"
    "jsonschema" = "4.25.1"
}
foreach ($name in $expectedVersions.Keys) {
    if ($versions.$name -ne $expectedVersions[$name]) {
        throw (
            "$name version $($versions.$name) is installed; expected " +
            "$($expectedVersions[$name]). Recreate the package environment " +
            "with this script and Python 3.14.5 x64; preserve the build lock."
        )
    }
}

if (-not $SkipBuild) {
    foreach ($path in @($packageDir, $pyinstallerDist)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Recurse -Force
        }
    }
}
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null

if (-not $SkipBuild) {
    & $buildPython -m PyInstaller `
        --noconfirm `
        --clean `
        --onedir `
        --contents-directory "." `
        --noconsole `
        --name "RungProof" `
        --paths $interfaceSource `
        --paths (Join-Path $repoRoot "tools") `
        --hidden-import "native_runtime" `
        --hidden-import "native_software_viewport" `
        --hidden-import "plc_diagnostics" `
        --hidden-import "PySide6.QtCore" `
        --hidden-import "PySide6.QtGui" `
        --hidden-import "PySide6.QtWidgets" `
        --hidden-import "PySide6.Qt3DCore" `
        --hidden-import "PySide6.Qt3DExtras" `
        --hidden-import "PySide6.Qt3DRender" `
        --hidden-import "siemens_plc_pc_interface.components" `
        --hidden-import "siemens_plc_pc_interface.config" `
        --hidden-import "siemens_plc_pc_interface.heartbeat" `
        --hidden-import "siemens_plc_pc_interface.points" `
        --hidden-import "siemens_plc_pc_interface.runtime" `
        --hidden-import "siemens_plc_pc_interface.transport" `
        --hidden-import "siemens_plc_pc_interface.update_loop" `
        --collect-all "snap7" `
        --add-data "$repoRoot\prototype\scenes;prototype\scenes" `
        --distpath $pyinstallerDist `
        --workpath $workDir `
        --specpath $specDir `
        (Join-Path $repoRoot "tools\rungproof_native.py")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
    if (-not (Test-Path -LiteralPath $builtAppDir -PathType Container)) {
        throw "PyInstaller native application folder is missing: $builtAppDir"
    }
    Copy-Item `
        -Path (Join-Path $builtAppDir "*") `
        -Destination $packageDir `
        -Recurse `
        -Force

    # Qt 6.11 on Windows links to the operating system's unversioned ICU
    # compatibility API. PyInstaller 6.21 can collect the versioned ICU 78
    # implementation as root\icuuc.dll instead; application-directory search
    # order then shadows the Windows compatibility DLL and QtCore fails with
    # "The specified procedure could not be found." The collected DLL is not
    # a valid substitute, so keep it out of the one-folder package.
    $conflictingQtIcu = Join-Path $packageDir "icuuc.dll"
    if (Test-Path -LiteralPath $conflictingQtIcu -PathType Leaf) {
        Remove-Item -LiteralPath $conflictingQtIcu -Force
    }
}

if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "Packaged executable is missing: $executable"
}

if (Test-Path -LiteralPath $profilesDestination) {
    Remove-Item -LiteralPath $profilesDestination -Recurse -Force
}
Copy-Item `
    -LiteralPath $profilesSource `
    -Destination $profilesDestination `
    -Recurse `
    -Force

if (Test-Path -LiteralPath $licensesDestination) {
    Remove-Item -LiteralPath $licensesDestination -Recurse -Force
}
Copy-Item `
    -LiteralPath $licensesSource `
    -Destination $licensesDestination `
    -Recurse `
    -Force

Copy-Item `
    -LiteralPath $requirementsFile `
    -Destination (Join-Path $packageDir "requirements-build.txt") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "requirements-build.lock") `
    -Destination (Join-Path $packageDir "requirements-build.lock") `
    -Force

Copy-Item `
    -LiteralPath $versionFile `
    -Destination (Join-Path $packageDir "VERSION") `
    -Force

$capabilities = [ordered]@{
    schemaVersion = 1
    realPlcWritesEnabled = [bool]$EnableRealPlc
    plcPilotMode = if ($EnableRealPlc) {
        "operator-authorized-live-bench"
    }
    else {
        "read-only"
    }
}
$capabilities | ConvertTo-Json | Set-Content `
    -LiteralPath (Join-Path $packageDir "PILOT-CAPABILITIES.json") `
    -Encoding ascii

Copy-Item `
    -LiteralPath (Join-Path $repoRoot "THIRD_PARTY_NOTICES.md") `
    -Destination (Join-Path $packageDir "THIRD_PARTY_NOTICES.md") `
    -Force

Copy-Item `
    -LiteralPath $interfaceProvenance `
    -Destination (Join-Path $packageDir "SIEMENS-INTERFACE-PROVENANCE.md") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $interfaceSource "SOURCE-SHA256.txt") `
    -Destination (Join-Path $packageDir "SIEMENS-INTERFACE-SOURCE-SHA256.txt") `
    -Force

$sbomPath = Join-Path $packageDir "RungProof.cdx.json"
& $buildPython (Join-Path $repoRoot "tools\generate_sbom.py") `
    --output $sbomPath
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $sbomPath)) {
    throw "Could not generate the package SBOM."
}

@(
    "RungProof package build"
    "PackageVersion=$PackageVersion"
    "Python=$($versions.Python)"
    "PyInstaller=$($versions.PyInstaller)"
    "PySide6=$($versions.PySide6)"
    "python-snap7=$($versions.'python-snap7')"
    "jsonschema=$($versions.jsonschema)"
    "DependencyAudit=exact-hash-locked-$($dependencyAudit.count)-distributions"
    "VendorSourceManifest=verified"
    "entrypoint=native-qt-software-direct-snap7"
    "siemens-interface=754fcfb88192f2a932bd7df70feea0d08088ab97+native-live-runtime"
) | Set-Content `
    -LiteralPath (Join-Path $packageDir "BUILD-VERSIONS.txt") `
    -Encoding ascii

Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\README-VM.txt") `
    -Destination (Join-Path $packageDir "README-VM.txt") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\DELTA-RETEST-QUICKSTART.txt") `
    -Destination (Join-Path $packageDir "DELTA-RETEST-QUICKSTART.txt") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\VERIFY-PACKAGE.ps1") `
    -Destination (Join-Path $packageDir "VERIFY-PACKAGE.ps1") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\CAPTURE-VIEWS.ps1") `
    -Destination (Join-Path $packageDir "CAPTURE-VIEWS.ps1") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\BENCH-PREFLIGHT.ps1") `
    -Destination (Join-Path $packageDir "BENCH-PREFLIGHT.ps1") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\VALIDATE-BENCH-RESULT.ps1") `
    -Destination (Join-Path $packageDir "VALIDATE-BENCH-RESULT.ps1") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "packaging\vm\VALIDATE-BENCH-DELTA.ps1") `
    -Destination (Join-Path $packageDir "VALIDATE-BENCH-DELTA.ps1") `
    -Force
foreach ($document in @(
    "CHANGELOG.md",
    "SECURITY.md",
    "docs\KNOWN_LIMITATIONS.md",
    "docs\LIVE_PLC_PILOT_CHECKLIST.md",
    "docs\SECURITY_REVIEW_2026-08-05.md",
    "docs\SUPPORTED_CONFIGURATION.md",
    "docs\SUPPORT_RUNBOOK.md"
)) {
    Copy-Item `
        -LiteralPath (Join-Path $repoRoot $document) `
        -Destination (Join-Path $packageDir ([System.IO.Path]::GetFileName($document))) `
        -Force
}

$hashLines = Get-ChildItem -LiteralPath $packageDir -File -Recurse |
    Where-Object Name -ne "SHA256.txt" |
    Sort-Object FullName |
    ForEach-Object {
        $hash = Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256
        $relativePath = $_.FullName.Substring(
            $packageDir.Length
        ).TrimStart("\").Replace("\", "/")
        "$($hash.Hash.ToLowerInvariant())  $relativePath"
    }
Set-Content `
    -LiteralPath (Join-Path $packageDir "SHA256.txt") `
    -Value $hashLines `
    -Encoding ascii

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive `
    -Path (Join-Path $packageDir "*") `
    -DestinationPath $zipPath `
    -CompressionLevel Optimal

if (Test-Path -LiteralPath $versionedZipPath) {
    Remove-Item -LiteralPath $versionedZipPath -Force
}
Copy-Item `
    -LiteralPath $zipPath `
    -Destination $versionedZipPath `
    -Force

if (Test-Path -LiteralPath $versionedPackageDir) {
    Remove-Item -LiteralPath $versionedPackageDir -Recurse -Force
}
Copy-Item `
    -LiteralPath $packageDir `
    -Destination $versionedPackageDir `
    -Recurse `
    -Force

Write-Host "EXE: $executable"
Write-Host "PACKAGE_DIR: $packageDir"
Write-Host "ZIP: $zipPath"
Write-Host "VERSIONED_ZIP: $versionedZipPath"
Write-Host "VERSIONED_PACKAGE_DIR: $versionedPackageDir"
