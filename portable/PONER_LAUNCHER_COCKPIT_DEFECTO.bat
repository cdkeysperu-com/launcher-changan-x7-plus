@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title CHANGAN X7 PLUS - FIJAR LAUNCHER COCKPIT CUSTOM HMI
color 0B
cd /d "%~dp0"

cls
echo ===============================================================================
echo       CHANGAN X7 PLUS - ACTIVAR COCKPIT CUSTOM LAUNCHER POR DEFECTO
echo ===============================================================================
echo.
echo Este script configura el nuevo Launcher Cockpit Custom HMI (com.chinatsp.x7plus.launcher)
echo con soporte de fondos intercambiables, videos aleatorios, burbuja flotante y GPS.
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

echo [*] Configurando com.chinatsp.x7plus.launcher como Home Predeterminado...
"%ADB_EXE%" shell cmd package set-home-activity com.chinatsp.x7plus.launcher/.MainActivity
"%ADB_EXE%" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
"%ADB_EXE%" shell am start -n com.chinatsp.x7plus.launcher/.MainActivity
"%ADB_EXE%" shell input keyevent 3

echo [*] Aplicando bypass de pantalla completa 1920x720...
"%ADB_EXE%" shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName com.chinatsp.x7plus.launcher --ei appCentered 2
"%ADB_EXE%" shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName com.chinatsp.x7plus.launcher

echo.
echo ===============================================================================
echo [OK] ?LAUNCHER COCKPIT CUSTOM HMI ACTIVADO POR DEFECTO!
echo ===============================================================================
echo.
echo Puedes regresar al Launcher OnStyle de F?brica ejecutando:
echo PONER_LAUNCHER_ONSTYLE_DEFECTO.bat
echo.
pause
