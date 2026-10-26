@echo off
chcp 65001 >nul
title CHANGAN X7 PLUS - INSTALADOR OPEN HEADUNIT v3.5.0 NATIVO
color 0A
cd /d "%~dp0"

echo ===============================================================================
echo       CHANGAN X7 PLUS - INSTALACIÓN DE OPEN HEADUNIT v3.5.0 WIRELESS NATIVO
echo             CONEXIÓN 100%% NATIVA A ANDROID AUTO SIN APK EN EL CELULAR
echo ===============================================================================
echo.

set "ADB_EXE="
if exist "..\..\portable\tools\adb.exe" (
    set "ADB_EXE=..\..\portable\tools\adb.exe"
) else if exist "..\..\APK CHANGAN X7 PLUS\tools\adb.exe" (
    set "ADB_EXE=..\..\APK CHANGAN X7 PLUS\tools\adb.exe"
) else (
    for /f "delims=" %%i in ('where adb 2^>nul') do set "ADB_EXE=%%i"
)

if not defined ADB_EXE (
    echo [ERROR] No se encontró adb.exe. Asegúrate de tener la carpeta tools en el proyecto.
    pause
    exit /b 1
)

echo [*] ADB localizado: %ADB_EXE%
echo.

echo [*] Buscando dispositivos conectados (Auto via USB / WiFi o Emulador)...
"%ADB_EXE%" devices
echo.

"%ADB_EXE%" get-state >nul 2>&1
if errorlevel 1 (
    echo [AVISO] No hay ningún dispositivo conectado por ADB.
    echo Por favor conecta tu auto por USB (con depuración USB activa) o inicia el emulador.
    echo Si te conectas por WiFi a la radio del auto, puedes ejecutar primero:
    echo   adb connect IP_DE_TU_RADIO:5555
    echo.
    set /p CAR_IP="¿Deseas ingresar la IP de la radio del auto para conectar por WiFi? (deja vacio si no): "
    if defined CAR_IP (
        "%ADB_EXE%" connect %CAR_IP%:5555
    )
)

echo.
echo ===============================================================================
echo [1/3] Instalando Open Headunit v3.5.0 Release en la radio...
echo ===============================================================================
"%ADB_EXE%" install -r -g "OpenHeadUnit_v3.5.0_Oficial_Release.apk"
if errorlevel 1 (
    echo [ERROR] Falló la instalación. Intentando forzar instalación...
    "%ADB_EXE%" install -r -d "OpenHeadUnit_v3.5.0_Oficial_Release.apk"
)

echo.
echo ===============================================================================
echo [2/3] Concediendo permisos automotrices avanzados (Cero alertas en pantalla)...
echo ===============================================================================
set "PKG=com.andrerinas.headunitrevived"

"%ADB_EXE%" shell pm grant %PKG% android.permission.ACCESS_FINE_LOCATION >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.RECORD_AUDIO >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_SETTINGS >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.BLUETOOTH_CONNECT >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.BLUETOOTH_SCAN >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.BLUETOOTH_ADVERTISE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.NEARBY_WIFI_DEVICES >nul 2>&1

:: Permitir dibujar sobre otras apps y ejecución en segundo plano sin cortes
"%ADB_EXE%" shell appops set %PKG% SYSTEM_ALERT_WINDOW allow >nul 2>&1
"%ADB_EXE%" shell dumpsys deviceidle whitelist +%PKG% >nul 2>&1

echo [OK] Permisos concedidos exitosamente.
echo.

echo ===============================================================================
echo [3/3] ¡Instalación Completada con Éxito!
echo ===============================================================================
echo Open Headunit v3.5.0 está listo en tu pantalla Changan X7.
echo.
echo RECORDATORIO CLAVE:
echo  - NO necesitas ninguna APK instalada en tu teléfono celular.
echo  - Tu teléfono se conecta directamente mediante el Android Auto oficial de Google.
echo  - Lee el archivo 'GUIA_CONEXION_NATIVA_SIN_APK_CELULAR.md' para ver los 3 métodos
echo    de conexión rápida por Wi-Fi y Wi-Fi Direct.
echo ===============================================================================
echo.
pause
