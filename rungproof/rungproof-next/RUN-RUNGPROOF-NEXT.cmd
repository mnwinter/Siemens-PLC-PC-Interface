@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "DOTNET_ROOT=%PROJECT_DIR%.tools\dotnet"
set "GODOT_EXE=%PROJECT_DIR%.tools\godot\Godot_v4.7.2-stable_mono_win64\Godot_v4.7.2-stable_mono_win64.exe"

if not exist "%GODOT_EXE%" (
  echo RungProof Next cannot start because the pinned Godot executable is missing.
  echo Expected: %GODOT_EXE%
  exit /b 1
)

if not exist "%DOTNET_ROOT%\dotnet.exe" (
  echo RungProof Next cannot start because the pinned .NET executable is missing.
  echo Expected: %DOTNET_ROOT%\dotnet.exe
  exit /b 1
)

set "PATH=%DOTNET_ROOT%;%PATH%"
pushd "%PROJECT_DIR%"
"%DOTNET_ROOT%\dotnet.exe" build RungProof.Next.csproj --no-restore --nologo
if errorlevel 1 (
  echo RungProof Next build failed. The application was not started.
  popd
  exit /b 1
)
popd
start "RungProof Next" "%GODOT_EXE%" --path "%PROJECT_DIR%."
endlocal
