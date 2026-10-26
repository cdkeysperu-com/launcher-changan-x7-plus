@echo off
setlocal
title Changan X7 Plus - Aplicar Cockpit X7 Fullscreen en Auto Real

echo ==================================================================
echo   CHANGAN X7 PLUS - DESBLOQUEO PANTALLA COMPLETA 1920x720
echo   Aplicar Cockpit X7 como Launcher Primario del Vehiculo
echo ==================================================================
echo.

set ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe
set APK_PATH=C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1\apks\x7_cockpit_launcher.apk

if not exist "%ADB_EXE%" (
    echo [ERROR] No se encontro adb.exe en "%ADB_EXE%".
    pause
    exit /b 1
)

if not exist "%APK_PATH%" (
    echo [ERROR] No se encontro el archivo APK en "%APK_PATH%".
    pause
    exit /b 1
)

echo [1/5] Verificando conexion con la radio del vehiculo...
"%ADB_EXE%" devices | findstr /V "emulator" | findstr /R "[a-zA-Z0-9].*device" >nul
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] No se detecto la radio de tu Changan X7 Plus conectada por USB.
    echo.
    echo Pasos:
    echo 1. Enciende el vehiculo o la pantalla.
    echo 2. Conecta el cable USB de la laptop al puerto USB multimedia del auto.
    echo 3. Asegurate de haber activado 'Depuracion USB' en los Ajustes del auto.
    echo.
    echo Dispositivos actuales:
    "%ADB_EXE%" devices
    echo.
    pause
    exit /b 1
)

echo [OK] Radio Changan X7 Plus detectada por USB.
echo.

echo [2/5] Instalando Cockpit X7 v2.2.0 (Con aspecto 8:3 y Cutout desbloqueados)...
"%ADB_EXE%" install -r -g "%APK_PATH%"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion del APK en el vehiculo.
    pause
    exit /b 1
)

echo [3/5] Desactivando cuadro de modo inmersivo de Android...
"%ADB_EXE%" shell settings put secure immersive_mode_confirmations confirmed >nul 2>&1

echo [4/5] Designando Cockpit X7 como Home Launcher Oficial del auto...
"%ADB_EXE%" shell cmd package set-home-activity com.changan.x7plus.launcher/.MainActivity

echo [5/5] Desactivando lanzador secundario ChinaTSP para eliminar docks laterales...
"%ADB_EXE%" shell pm disable-user --user 0 com.chinatsp.launcher

echo.
echo Iniciando Cockpit X7 en la pantalla del auto...
"%ADB_EXE%" shell am start -n com.changan.x7plus.launcher/.MainActivity
"%ADB_EXE%" shell input keyevent 3

echo.
echo ==================================================================
echo [EXITO] COCKPIT X7 APLICADO EN TU VEHICULO
echo La pantalla del auto ahora debe mostrar Cockpit X7 en pantalla completa.
echo.
echo NOTA DE SEGURIDAD:
echo Si alguna vez deseas volver a la interfaz de fabrica ChinaTSP,
echo simplemente ejecuta: RESTAURAR_RADIO_ORIGINAL.bat
echo ==================================================================
pause
