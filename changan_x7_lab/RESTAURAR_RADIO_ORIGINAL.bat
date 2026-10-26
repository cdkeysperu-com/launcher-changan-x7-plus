@echo off
setlocal
title Changan X7 Plus - Restaurar Interfaz Original de Fabrica

echo ==================================================================
echo   CHANGAN X7 PLUS - RESTAURAR INTERFAZ ORIGINAL DE FABRICA
echo ==================================================================
echo.

set ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe

if not exist "%ADB_EXE%" (
    echo [ERROR] No se encontro adb.exe.
    pause
    exit /b 1
)

echo [1/3] Verificando conexion con la radio del vehiculo...
"%ADB_EXE%" devices | findstr /V "emulator" | findstr /R "[a-zA-Z0-9].*device" >nul
if %errorlevel% neq 0 (
    echo [AVISO] Conecta la laptop a la radio del auto por USB.
    pause
    exit /b 1
)

echo [2/3] Reactivando el lanzador oficial de fabrica (ChinaTSP)...
"%ADB_EXE%" shell pm enable com.chinatsp.launcher
"%ADB_EXE%" shell cmd package set-home-activity com.chinatsp.launcher/com.chinatsp.launcher.MainAct

echo [3/3] Iniciando pantalla de inicio de fabrica...
"%ADB_EXE%" shell am start -n com.chinatsp.launcher/com.chinatsp.launcher.MainAct
"%ADB_EXE%" shell input keyevent 3

echo.
echo ==================================================================
echo [EXITO] Interfaz original de Changan OnStyle restaurada al 100%.
echo ==================================================================
pause
