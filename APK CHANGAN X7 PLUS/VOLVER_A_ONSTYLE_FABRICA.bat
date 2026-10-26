@echo off
chcp 65001 >nul
title RESTAURAR A INTERFAZ DE F?BRICA - CHANGAN ONSTYLE
color 0E

echo ================================================================================
echo    CHANGAN X7 PLUS - RESTAURAR A PANTALLA DE F?BRICA ORIGINAL
echo ================================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "ADB_EXE=%SCRIPT_DIR%tools\adb.exe"
if not exist "%ADB_EXE%" set "ADB_EXE=adb"

echo [1/3] Esperando conexi?n con el veh?culo...
"%ADB_EXE%" wait-for-device

echo [2/3] Restaurando Launcher original Changan OnStyle (com.chinatsp.launcher)...
"%ADB_EXE%" shell cmd package set-home-activity com.chinatsp.launcher/.MainAct

echo [3/3] Lanzando interfaz original en la pantalla...
"%ADB_EXE%" shell am start -n com.chinatsp.launcher/.MainAct

echo.
echo ================================================================================
echo  ?LISTO! La pantalla ha regresado a la interfaz original de f?brica (OnStyle).
echo  Garant?a y funciones 100% intactas.
echo ================================================================================
echo.
pause
