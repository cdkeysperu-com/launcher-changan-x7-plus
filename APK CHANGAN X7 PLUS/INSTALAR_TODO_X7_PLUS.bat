@echo off
chcp 65001 >nul
title INSTALADOR MAESTRO - CHANGAN X7 PLUS CUSTOM HMI (1920x720)
color 0B

echo ================================================================================
echo    CHANGAN X7 PLUS - INSTALADOR AUTOMATIZADO CONECTAR Y APLICAR
echo    Resoluci?n Nativa: 1920x720 px @ 213 DPI | MediaTek MT8666 Android 9
echo ================================================================================
echo.
echo  INSTRUCCIONES R?PIDAS:
echo  1. Enciende la radio de tu Changan X7 Plus.
echo  2. Aseg?rate de tener activa la Depuraci?n USB (marcador: **888).
echo  3. Conecta el cable USB de la laptop al puerto multimedia de la consola central.
echo.
echo ================================================================================
echo  [1/5] Esperando conexi?n USB con la radio (adb wait-for-device)...
echo ================================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "ADB_EXE=%SCRIPT_DIR%tools\adb.exe"
set "PYTHON_EXE=%SCRIPT_DIR%runtime\python.exe"

if not exist "%ADB_EXE%" (
    set "ADB_EXE=adb"
)

"%ADB_EXE%" wait-for-device

echo [OK] Dispositivo USB detectado. Verificando estado de autorizaci?n...
"%ADB_EXE%" devices

echo.
echo ================================================================================
echo  [2/5] Ejecutando instalaci?n maestra y configuraci?n automatizada...
echo ================================================================================
echo.

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" "%SCRIPT_DIR%instalar_todo_x7_plus.py"
) else (
    python "%SCRIPT_DIR%instalar_todo_x7_plus.py"
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] Ejecutando modo directo por comandos ADB batch...
    echo Instalando ChanganX7Plus_OEM_Launcher.apk...
    "%ADB_EXE%" install -r -d "%SCRIPT_DIR%ChanganX7Plus_OEM_Launcher.apk"
    
    echo Aplicando permisos...
    "%ADB_EXE%" shell cmd notification allow_listener com.changan.x7plus.launcher/.MediaNotificationListener
    "%ADB_EXE%" shell pm grant com.changan.x7plus.launcher android.permission.SYSTEM_ALERT_WINDOW
    "%ADB_EXE%" shell pm grant com.changan.x7plus.launcher android.permission.ACCESS_FINE_LOCATION
    "%ADB_EXE%" shell pm grant com.changan.x7plus.launcher android.permission.ACCESS_COARSE_LOCATION
    "%ADB_EXE%" shell pm grant com.changan.x7plus.launcher android.permission.READ_EXTERNAL_STORAGE
    "%ADB_EXE%" shell pm grant com.changan.x7plus.launcher android.permission.WRITE_EXTERNAL_STORAGE
    "%ADB_EXE%" shell appops set com.changan.x7plus.launcher SYSTEM_ALERT_WINDOW allow
    
    "%ADB_EXE%" shell settings put secure location_mode 3
    "%ADB_EXE%" shell settings put secure location_providers_allowed +gps,+network
    "%ADB_EXE%" shell settings put global window_animation_scale 0.5
    "%ADB_EXE%" shell settings put global transition_animation_scale 0.5
    "%ADB_EXE%" shell settings put global animator_duration_scale 0.5
    
    "%ADB_EXE%" shell cmd package set-home-activity com.changan.x7plus.launcher/.MainActivity
    "%ADB_EXE%" shell am start -n com.changan.x7plus.launcher/.MainActivity
    echo [OK] Completado por ADB Directo.
)

echo.
echo ================================================================================
echo  ?PROCESO FINALIZADO! DISFRUTA TU NUEVO DASHBOARD CHANGAN X7 PLUS
echo ================================================================================
echo.
pause
