@echo off
setlocal
pushd "%~dp0"

echo LIVE SCENE 2 - CONVEYOR PUSHER
echo.
echo This is a best-effort visual PLC simulator, not a hard real-time runtime.
echo The scene exchanges DB14 data every 20 ms and redraws independently.
echo.
echo Preconditions:
echo   1. Open the separate Scene 2 TIA project copied from Scene 1.
echo   2. DB14 exactly matches scene-2-db14-pusher-interface.json.
echo   3. The watchdog and Scene 2 pusher logic are compiled and downloaded.
echo   4. Keep the Scene 2 DB14 watch table visible.
echo   5. Set DB14.DBX10.0 Simulation_Enable to TRUE.
echo.
echo Authorized PC writes:
echo   DB14.DBX0.0 Part_At_Pusher
echo   DB14.DBX0.1 Pusher_Extended
echo   DB14.DBX0.2 Pusher_Retracted
echo   DB14.DBD2    PC_Heartbeat
echo.
set /p "CONFIRM=Type RUN to open Scene 2: "
if /I not "%CONFIRM%"=="RUN" goto :cancel

SiemensPlcPcInterface.exe scene-visualize ^
    scene-2-db14-pusher-interface.json ^
    scene-2-conveyor-pusher.json ^
    --execute ^
    --write-safe-state-on-exit
set "RESULT=%ERRORLEVEL%"

echo.
echo Viewer finished with exit code %RESULT%.
echo Require SAFE_STATE_WRITE: PASS after closing the window.
echo Set DB14.DBX10.0 Simulation_Enable to FALSE before leaving the test.
pause
popd
exit /b %RESULT%

:cancel
echo Test cancelled. No PLC connection was attempted.
pause
popd
exit /b 2
