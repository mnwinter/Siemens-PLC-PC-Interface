@echo off
setlocal
pushd "%~dp0"

echo LIVE GRAPHICAL CONVEYOR VIEWER
echo.
echo This is a best-effort visual PLC simulator, not a hard real-time runtime.
echo The scene exchanges DB14 data every 20 ms and redraws independently.
echo.
echo Preconditions:
echo   1. The PLC watchdog FB and simulated command rung are downloaded.
echo   2. DB14 offsets match db14-conveyor-interface.json.
echo   3. Keep the DB14 watch table visible for this first test.
echo   4. Set DB14.DBX10.0 Simulation_Enable to TRUE.
echo.
echo Authorized PC writes:
echo   DB14.DBX0.0 PC_To_PLC simulated photoeye
echo   DB14.DBD2    PC_Heartbeat
echo.
set /p "CONFIRM=Type RUN to open the graphical simulator: "
if /I not "%CONFIRM%"=="RUN" goto :cancel

SiemensPlcPcInterface.exe scene-visualize ^
    db14-conveyor-interface.json ^
    conveyor-scene-fast.json ^
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
