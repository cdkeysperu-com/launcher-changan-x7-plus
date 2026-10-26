@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title CHANGAN X7 PLUS - FIJAR LAUNCHER ONSTYLE DE F?BRICA
color 0E
cd /d "%~dp0"

cls
echo ===============================================================================
echo       CHANGAN X7 PLUS - ACTIVAR LAUNCHER ONSTYLE DE F?BRICA POR DEFECTO
echo ===============================================================================
echo.
echo Este script configura el Launcher Original de F?brica OnStyle (com.chinatsp.launcher)
echo como la pantalla principal predeterminada, tanto en el Emulador como en el Auto.
echo.

set "ADB_EXE="
if exist "%~dp0APK CHANGAN X7 PLUS\tools\adb.exe" (
    set "ADB_EXE=%~dp0APK CHANGAN X7 PLUS\tools\adb.exe"
) else if exist "%~dp0tools\adb.exe" (
    set "ADB_EXE=%~dp0tools\adb.exe"
) else (
    set "ADB_EXE=adb"
)

echo [*] Conectando con dispositivo Android...
"%ADB_EXE%" wait-for-device

echo [*] Configurando com.chinatsp.launcher.MainAct como Home Predeterminado...
"%ADB_EXE%" shell cmd package set-home-activity com.chinatsp.launcher/com.chinatsp.launcher.MainAct
"%ADB_EXE%" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
"%ADB_EXE%" shell am start -n com.chinatsp.launcher/com.chinatsp.launcher.MainAct
"%ADB_EXE%" shell input keyevent 3

echo.
echo ===============================================================================
echo [OK] ?LAUNCHER ONSTYLE DE F?BRICA ACTIVADO POR DEFECTO!
echo ===============================================================================
echo.
echo Recuerda que puedes volver al Launcher Cockpit Custom en cualquier momento
echo ejecutando: PONER_LAUNCHER_COCKPIT_DEFECTO.bat
echo.
pause
