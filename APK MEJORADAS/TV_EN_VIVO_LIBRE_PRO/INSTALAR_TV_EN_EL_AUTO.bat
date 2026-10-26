@echo off
chcp 65001 >nul
title CHANGAN X7 PLUS - INSTALADOR DE TV EN VIVO Y STREAMING LIBRE (XUPERTV ALTERNATIVE)
color 0E
cd /d "%~dp0"

echo ===============================================================================
echo       CHANGAN X7 PLUS - TV EN VIVO LIBRE Y STREAMING HD (SIN PAGOS NI ANUNCIOS)
echo            (Reemplazo seguro a XuperTV / MagisTV: OwnTV v5.2.1 y CloudStream 3)
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
    echo [ERROR] No se encontró adb.exe en el entorno.
    pause
    exit /b 1
)

echo [*] ADB localizado: %ADB_EXE%
echo.

echo [*] Buscando dispositivos conectados (Auto vía USB / WiFi o Emulador)...
"%ADB_EXE%" devices
echo.

"%ADB_EXE%" get-state >nul 2>&1
if errorlevel 1 (
    echo [AVISO] No hay dispositivo activo por ADB.
    echo Si deseas conectar a la radio por WiFi ingresa su dirección IP:
    set /p CAR_IP="IP del auto (ejemplo: 192.168.43.1): "
    if defined CAR_IP (
        "%ADB_EXE%" connect %CAR_IP%:5555
    )
)

echo.
echo ===============================================================================
echo [1/3] Transfiriendo lista maestra de 370+ canales VIP al auto...
echo ===============================================================================
"%ADB_EXE%" shell "mkdir -p /sdcard/IPTV" >nul 2>&1
"%ADB_EXE%" push "CANALES_VIP_LATAM_PERU_DEPORTES.m3u" "/sdcard/IPTV/canales_vip.m3u"
echo [OK] Lista precargada localmente en: /sdcard/IPTV/canales_vip.m3u
echo.

echo ===============================================================================
echo [2/3] SELECCIONA QUÉ APLICACIÓN DESEAS INSTALAR EN TU PANTALLA:
echo ===============================================================================
echo  [1] OwnTV v5.2.1 (TV de Cable en Vivo: Super rápida, ExoPlayer+MPV, 370+ canales)
echo  [2] CloudStream v4.8.0 ("XuperTV Libre": Películas, Series, Anime y Canales)
echo  [3] INSTALAR AMBAS APKS (Recomendado: Suite completa de entretenimiento)
echo ===============================================================================
set /p OPCION="Ingresa tu opción (1, 2 o 3): "

if "%OPCION%"=="1" goto INSTALAR_OWNTV
if "%OPCION%"=="2" goto INSTALAR_CLOUDSTREAM
if "%OPCION%"=="3" goto INSTALAR_TODO
goto INSTALAR_OWNTV

:INSTALAR_OWNTV
:INSTALAR_TODO
echo.
echo [*] Detectando arquitectura del dispositivo para OwnTV...
set "OWNTV_APK=OwnTV_v5.2.1_IPTV_Cable_En_Vivo.apk"
for /f "delims=" %%A in ('"%ADB_EXE%" shell getprop ro.product.cpu.abi') do (
    if "%%A"=="x86_64" set "OWNTV_APK=OwnTV_v5.2.1_x86_64_Para_Emulador.apk"
)

echo [*] Instalando %OWNTV_APK%...
"%ADB_EXE%" install -r -g "%OWNTV_APK%"
set "PKG=com.ahxn00.owntv"
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell appops set %PKG% SYSTEM_ALERT_WINDOW allow >nul 2>&1
"%ADB_EXE%" shell dumpsys deviceidle whitelist +%PKG% >nul 2>&1
:: Bypass de bordes negros pantalla panorámica Changan X7 (1920x720)
"%ADB_EXE%" shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "%PKG%" --ei appCentered 2 >nul 2>&1
"%ADB_EXE%" shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "%PKG%" >nul 2>&1
echo [OK] OwnTV instalado, con permisos y pantalla completa.
if "%OPCION%"=="3" goto SIGUIENTE_CLOUDSTREAM
goto FINALIZAR

:INSTALAR_CLOUDSTREAM
:SIGUIENTE_CLOUDSTREAM
echo.
echo [*] Instalando CloudStream v4.8.0 (XuperTV Open Source)...
"%ADB_EXE%" install -r -g "CloudStream_v4.8.0_XuperTV_OpenSource.apk"
set "PKG=com.lagradost.cloudstream3"
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell appops set %PKG% SYSTEM_ALERT_WINDOW allow >nul 2>&1
"%ADB_EXE%" shell dumpsys deviceidle whitelist +%PKG% >nul 2>&1
:: Bypass de bordes negros pantalla panorámica Changan X7 (1920x720)
"%ADB_EXE%" shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "%PKG%" --ei appCentered 2 >nul 2>&1
"%ADB_EXE%" shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "%PKG%" >nul 2>&1
echo [OK] CloudStream instalado con éxito y pantalla completa.
goto FINALIZAR

:FINALIZAR
echo.
echo ===============================================================================
echo [3/3] ¡INSTALACIÓN COMPLETADA CON ÉXITO!
echo ===============================================================================
echo Tus aplicaciones de TV en vivo están listas en la pantalla de tu Changan X7.
echo.
echo  - En OwnTV: Abre la app -> Añadir Lista -> Selecciona archivo local:
echo    "/sdcard/IPTV/canales_vip.m3u" para cargar los 370+ canales de inmediato.
echo.
echo  - En CloudStream: Lee 'GUIA_TV_EN_VIVO_Y_CONFIGURACION_XUPERTV.md' para activar
echo    los repositorios en español de películas, series y canales con 1 solo toque.
echo ===============================================================================
echo.
pause
