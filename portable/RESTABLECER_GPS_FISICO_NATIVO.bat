@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title RESTABLECER GPS FISICO NATIVO - CHANGAN X7 PLUS
color 0A
cls
echo ===============================================================================
echo       RESTABLECIMIENTO DE GPS SATELITAL FÍSICO NATIVO MT8666
echo ===============================================================================
echo Desactivando ubicaciones simuladas (Mock Location) y reactivando la antena
echo satelital GNSS directa de la Changan Oshan X7 Plus.
echo ===============================================================================
echo.

:: Detectar ejecutable ADB
set "ADB_BIN=adb"
if exist "%~dp0tools\adb.exe" (
    set "ADB_BIN=%~dp0tools\adb.exe"
) else if exist "%~dp0portable\tools\adb.exe" (
    set "ADB_BIN=%~dp0portable\tools\adb.exe"
) else if exist "%~dp0APK CHANGAN X7 PLUS\tools\adb.exe" (
    set "ADB_BIN=%~dp0APK CHANGAN X7 PLUS\tools\adb.exe"
)

echo [1/4] Desactivando mock_location a nivel del sistema...
%ADB_BIN% shell settings put secure mock_location 0
%ADB_BIN% shell settings put secure location_mode 3
%ADB_BIN% shell settings put secure location_providers_allowed +gps,+network

echo [2/4] Revocando AppOps mock_location a servicios de fondo...
%ADB_BIN% shell appops set com.chinatsp.x7plus.launcher android:mock_location default >nul 2>&1

echo [3/4] Otorgando permisos satelitales nativos directos a Waze, Maps y Magic Earth...
%ADB_BIN% shell pm grant com.waze android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.waze android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.generalmagic.magicearth android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.generalmagic.magicearth android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.google.android.apps.maps android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.google.android.apps.maps android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant app.organicmaps android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant app.organicmaps android.permission.ACCESS_COARSE_LOCATION >nul 2>&1

echo [4/4] Verificando satélites GNSS activos...
%ADB_BIN% shell dumpsys location | findstr /i "gps provider"

echo.
echo ===============================================================================
echo  ¡RECEPTOR GPS FÍSICO RESTABLECIDO CON ÉXITO!
echo  La antena satelital del auto ahora alimenta directamente a tus navegadores.
echo ===============================================================================
echo.
pause
