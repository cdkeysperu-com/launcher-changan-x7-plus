@echo off
chcp 65001 >nul
title CHANGAN X7 PLUS - INSTALADOR DE SPOTIFY LIBRE Y REPRODUCTORES OFFLINE
color 0B
cd /d "%~dp0"

echo ===============================================================================
echo       CHANGAN X7 PLUS - MÚSICA GRATIS, SIN ANUNCIOS Y CON DESCARGA OFFLINE
echo       (Reemplazos definitivos a RiMusic: Spotube v5.1.2, SimpMusic y InnerTune)
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

echo [*] Verificando dispositivos conectados (Auto por USB/WiFi o Emulador)...
"%ADB_EXE%" devices
echo.

"%ADB_EXE%" get-state >nul 2>&1
if errorlevel 1 (
    echo [AVISO] No hay dispositivo activo por ADB.
    echo Si deseas conectar a la radio de tu auto por WiFi ingresa su IP:
    set /p CAR_IP="IP del auto (ejemplo: 192.168.43.1): "
    if defined CAR_IP (
        "%ADB_EXE%" connect %CAR_IP%:5555
    )
)

echo.
echo ===============================================================================
echo SELECCIONA QUÉ APLICACIÓN DESEAS INSTALAR EN TU PANTALLA:
echo ===============================================================================
echo  [1] Spotube v5.1.2 (El "Spotify Libre": Catálogo completo, sin anuncios, descargas MP3)
echo  [2] SimpMusic v2.3.0 (YouTube Music + Spotify: Descargas offline reales, letras, muy fluido)
echo  [3] InnerTune v0.5.14 (Ultra ligero: Solo 7 MB, arranque instantáneo, sin errores)
echo  [4] INSTALAR LA SUITE COMPLETA (Instala las 3 apps para probar cuál te gusta más)
echo ===============================================================================
set /p OPCION="Ingresa tu opción (1, 2, 3 o 4): "

:: Crear carpeta de música en el dispositivo para que las descargas funcionen siempre
"%ADB_EXE%" shell "mkdir -p /sdcard/Music" >nul 2>&1

if "%OPCION%"=="1" goto INSTALAR_SPOTUBE
if "%OPCION%"=="2" goto INSTALAR_SIMPMUSIC
if "%OPCION%"=="3" goto INSTALAR_INNERTUNE
if "%OPCION%"=="4" goto INSTALAR_TODO
goto INSTALAR_SPOTUBE

:INSTALAR_SPOTUBE
:INSTALAR_TODO
echo.
echo [*] Instalando Spotube v5.1.2 (Spotify Libre)...
"%ADB_EXE%" install -r -g "Spotube_v5.1.2_Spotify_Libre_Descargas.apk"
set "PKG=oss.krtirtho.spotube"
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell appops set %PKG% SYSTEM_ALERT_WINDOW allow >nul 2>&1
"%ADB_EXE%" shell dumpsys deviceidle whitelist +%PKG% >nul 2>&1
:: Bypass de pantalla completa panorámica Changan X7 (Sin bordes negros)
"%ADB_EXE%" shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "%PKG%" --ei appCentered 2 >nul 2>&1
"%ADB_EXE%" shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "%PKG%" >nul 2>&1
echo [OK] Spotube instalado, con permisos de descarga y pantalla completa 1920x720.
if "%OPCION%"=="4" goto SIGUIENTE_SIMPMUSIC
goto FINALIZAR

:INSTALAR_SIMPMUSIC
:SIGUIENTE_SIMPMUSIC
echo.
echo [*] Instalando SimpMusic v2.3.0 (Offline Pro)...
"%ADB_EXE%" install -r -g "SimpMusic_v2.3.0_Universal_Offline_Pro.apk"
set "PKG=com.maxrave.simpmusic"
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell appops set %PKG% SYSTEM_ALERT_WINDOW allow >nul 2>&1
"%ADB_EXE%" shell dumpsys deviceidle whitelist +%PKG% >nul 2>&1
:: Bypass de pantalla completa panorámica Changan X7
"%ADB_EXE%" shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "%PKG%" --ei appCentered 2 >nul 2>&1
"%ADB_EXE%" shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "%PKG%" >nul 2>&1
echo [OK] SimpMusic instalado y optimizado para segundo plano en el auto.
if "%OPCION%"=="4" goto SIGUIENTE_INNERTUNE
goto FINALIZAR

:INSTALAR_INNERTUNE
:SIGUIENTE_INNERTUNE
echo.
echo [*] Instalando InnerTune v0.5.14 (Ultra Ligero 7 MB)...
"%ADB_EXE%" install -r -g "InnerTune_v0.5.14_Universal_UltraLigero.apk"
set "PKG=com.malopieds.innertune"
"%ADB_EXE%" shell pm grant %PKG% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell pm grant %PKG% android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
"%ADB_EXE%" shell appops set %PKG% SYSTEM_ALERT_WINDOW allow >nul 2>&1
"%ADB_EXE%" shell dumpsys deviceidle whitelist +%PKG% >nul 2>&1
:: Bypass de pantalla completa panorámica Changan X7
"%ADB_EXE%" shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "%PKG%" --ei appCentered 2 >nul 2>&1
"%ADB_EXE%" shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "%PKG%" >nul 2>&1
echo [OK] InnerTune instalado con éxito y pantalla completa.
goto FINALIZAR

:FINALIZAR
echo.
echo ===============================================================================
echo [LISTO] Proceso terminado exitosamente.
echo Ya puedes abrir tu reproductor favorito desde la pantalla del Changan X7.
echo.
echo NOTA: Abre el archivo 'GUIA_SPOTIFY_LIBRE_Y_DESCARGAS_CHANGAN_X7.md' para ver
echo cómo descargar canciones completas a la memoria interna o memoria USB del auto.
echo ===============================================================================
echo.
pause
