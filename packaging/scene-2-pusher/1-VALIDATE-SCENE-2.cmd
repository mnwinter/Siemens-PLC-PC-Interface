@echo off
setlocal
pushd "%~dp0"

echo VALIDATE SCENE 2 - CONVEYOR PUSHER
echo This command validates both JSON files and does not connect to the PLC.
echo.

SiemensPlcPcInterface.exe scene-validate ^
    scene-2-db14-pusher-interface.json ^
    scene-2-conveyor-pusher.json
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
