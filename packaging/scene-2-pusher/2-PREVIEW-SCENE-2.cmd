@echo off
setlocal
pushd "%~dp0"

echo PREVIEW SCENE 2 GUARDED SCOPE
echo This command does not connect because --execute is omitted.
echo Exit code 2 is expected for this preview.
echo.

SiemensPlcPcInterface.exe scene-visualize ^
    scene-2-db14-pusher-interface.json ^
    scene-2-conveyor-pusher.json
set "RESULT=%ERRORLEVEL%"

echo.
echo Require PLC_CONNECTION_ATTEMPTED: False.
pause
popd
exit /b %RESULT%
