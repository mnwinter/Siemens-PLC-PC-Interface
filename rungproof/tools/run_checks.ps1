[CmdletBinding()]
param(
    [ValidateSet("fast", "full", "release")]
    [string]$Lane = "fast",
    [string]$NodePath = "",
    [switch]$EnableRealPlc
)

$ErrorActionPreference = "Stop"
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))

if ($EnableRealPlc -and $Lane -ne "release") {
    throw "EnableRealPlc applies only to the release lane."
}

if (-not $NodePath) {
    $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
    if ($null -ne $nodeCommand) {
        $NodePath = $nodeCommand.Source
    }
}
if (-not $NodePath -and $env:USERPROFILE) {
    $bundledNode = Join-Path $env:USERPROFILE (
        ".cache\codex-runtimes\codex-primary-runtime\" +
        "dependencies\node\bin\node.exe"
    )
    if (Test-Path -LiteralPath $bundledNode -PathType Leaf) {
        $NodePath = $bundledNode
    }
}
if (-not $NodePath -or -not (Test-Path -LiteralPath $NodePath -PathType Leaf)) {
    throw "Node.js 24 is required. Pass -NodePath with the node executable."
}

$nodeVersion = & $NodePath --version
if ($LASTEXITCODE -ne 0 -or $nodeVersion -notmatch "^v24\.") {
    throw "Node.js 24 is required; received $nodeVersion."
}

Push-Location $repoRoot
try {
    if ($Lane -eq "release") {
        $gitStatus = @(
            & git status --porcelain=v1 --untracked-files=all
        )
        if ($LASTEXITCODE -ne 0) {
            throw "Could not inspect the Git working tree."
        }
        if ($gitStatus.Count -ne 0) {
            throw (
                "Release verification requires a clean Git working tree. " +
                "Review and commit the intended release changes first."
            )
        }
    }

    $javascriptFiles = @(
        Get-ChildItem prototype,scene-editor-prototype,tools `
            -Recurse `
            -File `
            -Include *.js,*.mjs
    )
    foreach ($file in $javascriptFiles) {
        & $NodePath --check $file.FullName
        if ($LASTEXITCODE -ne 0) {
            throw "JavaScript syntax failed: $($file.FullName)"
        }
    }

    $nodeTests = @(
        Get-ChildItem tools -File -Filter "test_*.mjs" |
            Sort-Object Name |
            ForEach-Object FullName
    )
    & $NodePath --test @nodeTests
    if ($LASTEXITCODE -ne 0) {
        throw "Node test lane failed."
    }

    & py -3 -m unittest discover -s tools -p "test_*.py" -v
    if ($LASTEXITCODE -ne 0) {
        throw "Python test lane failed."
    }

    & py -3 -m compileall -q tools
    if ($LASTEXITCODE -ne 0) {
        throw "Python compile check failed."
    }

    if ($Lane -in @("full", "release")) {
        & $NodePath tools\verify_training_scenes.mjs
        if ($LASTEXITCODE -ne 0) {
            throw "Training-scene verification failed."
        }
        & $NodePath tools\test_scene_tag_contract.mjs
        if ($LASTEXITCODE -ne 0) {
            throw "Scene tag-contract verification failed."
        }
    }

    if ($Lane -eq "release") {
        $buildArguments = @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", "tools\build_vm_exe.ps1"
        )
        if ($EnableRealPlc) {
            $buildArguments += "-EnableRealPlc"
        }
        & powershell @buildArguments
        if ($LASTEXITCODE -ne 0) {
            throw "RungProof package build failed."
        }
        $nativePython = Join-Path `
            $repoRoot `
            "build\.venv-rungproof\Scripts\python.exe"
        $previousQpaPlatform = $env:QT_QPA_PLATFORM
        try {
            $env:QT_QPA_PLATFORM = "offscreen"
            & $nativePython -m unittest `
                tools.test_native_qt `
                tools.test_native_static_editor_qt `
                -v
            if ($LASTEXITCODE -ne 0) {
                throw "RungProof native Qt lifecycle tests failed."
            }
        }
        finally {
            $env:QT_QPA_PLATFORM = $previousQpaPlatform
        }
        $smokeArguments = @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", "tools\smoke_test_vm_exe.ps1"
        )
        if ($EnableRealPlc) {
            $smokeArguments += "-ExpectRealPlcWritesEnabled"
        }
        & powershell @smokeArguments
        if ($LASTEXITCODE -ne 0) {
            throw "RungProof package smoke test failed."
        }
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File tools\test_app_window_exe.ps1
        if ($LASTEXITCODE -ne 0) {
            throw "RungProof native app-window test failed."
        }
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File tools\collect_release_evidence.ps1
        if ($LASTEXITCODE -ne 0) {
            throw "RungProof release-evidence collection failed."
        }
    }

    Write-Host "RUNGPROOF_CHECKS: PASS"
    Write-Host "LANE: $($Lane.ToUpperInvariant())"
    Write-Host "NODE: $nodeVersion"
    Write-Host "PYTHON: $(py -3 --version)"
}
finally {
    Pop-Location
}
