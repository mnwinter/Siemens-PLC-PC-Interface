@echo off
setlocal
pushd "%~dp0"

echo VALIDATE GRAPHICAL CONVEYOR VIEWER
echo This command validates both JSON files and does not connect to the PLC.
echo.

SiemensPlcPcInterface.exe scene-validate ^
    db14-conveyor-interface.json ^
    conveyor-scene-fast.json
set "RESULT=%ERRORLEVEL%"

echo.
if "%RESULT%"=="0" (
    echo Validation passed. No PLC connection was attempted.
) else (
    echo Validation failed with exit code %RESULT%.
)
pause
popd
exit /b %RESULT%
