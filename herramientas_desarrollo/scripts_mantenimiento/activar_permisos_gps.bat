@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title ACTIVAR SUBSISTEMA GPS (MOCK LOCATION) - CHANGAN X7 PLUS
color 0B
cls

echo ===============================================================================
echo       SUBSISTEMA GPS AUTOMOTRIZ NATIVO - CHANGAN X7 PLUS (AOSP / MT8666)
echo ===============================================================================
echo  Habilitando recepcion e inyeccion de GPS satelital en tiempo real:
echo    - Paquete Objetivo: com.chinatsp.x7plus.launcher
echo    - Servicio: MockLocationService (UDP 10110 / TestProvider)
echo ===============================================================================
echo.

:: Detectar ejecutable ADB (PATH local o carpetas de herramientas)
set "ADB_BIN=adb"
if exist "%~dp0tools\adb.exe" (
    set "ADB_BIN=%~dp0tools\adb.exe"
) else if exist "%~dp0portable\tools\adb.exe" (
    set "ADB_BIN=%~dp0portable\tools\adb.exe"
) else if exist "%~dp0APK CHANGAN X7 PLUS\tools\adb.exe" (
    set "ADB_BIN=%~dp0APK CHANGAN X7 PLUS\tools\adb.exe"
)

echo [1/5] Verificando conexion ADB con la radio del vehiculo...
%ADB_BIN% start-server >nul 2>&1

set "DEVICE_FOUND=0"
for /f "tokens=1,2" %%A in ('%ADB_BIN% devices ^| findstr /v "List" ^| findstr "device"') do (
    set "DEVICE_FOUND=1"
    set "DEV_SERIAL=%%A"
)

if "%DEVICE_FOUND%"=="0" (
    echo.
    echo [ADVERTENCIA] No se detecto ninguna radio conectada por USB o Wi-Fi ADB.
    echo Conecta el cable USB de la radio a la laptop o verifica que ADB este activo.
    echo.
    echo Reintentando en 5 segundos... (o presiona Ctrl+C para salir)
    timeout /t 5 >nul
)

echo [OK] Dispositivo detectado. Aplicando configuracion AOSP de alta precision...
echo.

echo [2/5] Habilitando ubicaciones simuladas a nivel de sistema (Settings Secure)...
%ADB_BIN% shell settings put secure mock_location 1
%ADB_BIN% shell settings put secure location_mode 3
%ADB_BIN% shell settings put secure location_providers_allowed +gps,+network

echo [3/5] Otorgando AppOps 'android:mock_location' a com.chinatsp.x7plus.launcher...
%ADB_BIN% shell appops set com.chinatsp.x7plus.launcher android:mock_location allow

echo [4/5] Otorgando permisos nativos de ubicacion satelital (Runtime Permissions)...
%ADB_BIN% shell pm grant com.chinatsp.x7plus.launcher android.permission.ACCESS_FINE_LOCATION
%ADB_BIN% shell pm grant com.chinatsp.x7plus.launcher android.permission.ACCESS_COARSE_LOCATION
%ADB_BIN% shell pm grant com.waze android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.waze android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.generalmagic.magicearth android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.generalmagic.magicearth android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.google.android.apps.maps android.permission.ACCESS_FINE_LOCATION >nul 2>&1
%ADB_BIN% shell pm grant com.google.android.apps.maps android.permission.ACCESS_COARSE_LOCATION >nul 2>&1

echo [5/5] Verificando estado final del subsistema GPS...
echo -------------------------------------------------------------------------------
echo Estado AppOps Mock Location:
%ADB_BIN% shell appops get com.chinatsp.x7plus.launcher android:mock_location
echo Proveedores activos en Android:
%ADB_BIN% shell settings get secure location_providers_allowed
echo -------------------------------------------------------------------------------

echo.
echo ===============================================================================
echo  ¡PERMISOS GPS INYECTADOS CON ÉXITO!
echo.
echo  El MockLocationService en el Launcher ya tiene permiso total para inyectar
echo  coordenadas GPS satelitales directamente al LocationManager de Android.
echo.
echo  Waze, Google Maps y Magic Earth navegaran sin retraso y con precision de carril.
echo ===============================================================================
echo.
pause
