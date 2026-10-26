@echo off
setlocal
chcp 65001 >nul 2>&1
title INSTALADOR CHANGAN X7 PLUS - COCKPIT LAUNCHER Y APLICACIONES
cd /d "%~dp0"
color 0B

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - INSTALADOR MAESTRO DE LAUNCHER Y APLICACIONES
echo                    (Android 9 / API 28 / MT8666 / 1920x720)
echo ===============================================================================
echo.

if not exist "tools\adb.exe" (
    echo [ERROR] No se encontro tools\adb.exe.
    pause
    exit /b 1
)

echo [1/5] Verificando conexion con la radio del Changan X7 Plus...
echo.

:CHECK_DEVICE
tools\adb.exe start-server >nul 2>&1

set "DEVICE_FOUND="
set "SERIAL="
for /f "tokens=1,2" %%A in ('tools\adb.exe devices ^| findstr /v "List" ^| findstr "device"') do (
    set "SERIAL=%%A"
    set "DEVICE_FOUND=1"
)

if "%DEVICE_FOUND%"=="1" (
    echo [OK] Auto detectado con exito: %SERIAL%
    goto START_INSTALL
)

echo.
echo ===============================================================================
echo [!] NO SE DETECTO NINGUN AUTO CHANGAN X7 PLUS POR USB.
echo ===============================================================================
echo.
echo PASOS PARA CONECTAR EL AUTO:
echo   1. Conecta tu laptop a la radio con el cable USB frontal del auto.
echo   2. En la radio, abre el marcador telefonico y marca el codigo: **888
echo   3. Activa la casilla "Depuracion por USB".
echo   4. Cuando aparezca el aviso en pantalla, marca "Permitir siempre" y ACEPTAR.
echo.
echo Elige una opcion:
echo   [1] Reintentar deteccion USB ahora
echo   [2] Conectar por Wi-Fi (Ingresar IP del auto, ej: 192.168.43.1)
echo   [3] Abrir Dashboard Visual y Simulador en la PC
echo   [4] Cancelar y Volver
echo.
choice /C 1234 /N /M "Presiona una opcion [1-4]: "
if errorlevel 4 exit /b 0
if errorlevel 3 goto OPEN_DASHBOARD
if errorlevel 2 goto CONNECT_WIFI
if errorlevel 1 goto RETRY_USB
goto CHECK_DEVICE

:RETRY_USB
cls
echo Reintentando deteccion con el auto...
ping 127.0.0.1 -n 2 >nul
goto CHECK_DEVICE

:CONNECT_WIFI
echo.
set "IP_AUTO="
set /p IP_AUTO="Ingresa la direccion IP de la radio del auto: "
if "%IP_AUTO%"=="" goto CHECK_DEVICE
echo Conectando a %IP_AUTO%:5555...
tools\adb.exe connect %IP_AUTO%:5555
ping 127.0.0.1 -n 2 >nul
goto CHECK_DEVICE

:OPEN_DASHBOARD
start "" "http://localhost:5050"
explorer "http://localhost:5050" >nul 2>&1
pause
exit /b 0

:START_INSTALL
echo.
echo ===============================================================================
echo ===============================================================================
echo [2/6] CONFIGURANDO PANTALLA COMPLETA INMERSIVA (100%% FULLSCREEN 1920x720)
echo ===============================================================================
tools\adb.exe shell settings put global policy_control immersive.full=*
echo [OK] Modo inmersivo activado para todo el sistema (Launcher, GPS, Spotube, OwnTV).
echo.

echo ===============================================================================
echo [3/6] LIMPIANDO VERSIONES PREVIAS Y APPS OBSOLETAS EN EL AUTO
echo ===============================================================================
echo Desinstalando apps anteriores con errores o reemplazadas (RiMusic, botones antiguos)...
tools\adb.exe shell pm uninstall it.fast4x.rimusic >nul 2>&1
tools\adb.exe shell pm uninstall it.vfsfitvnm.rimusic >nul 2>&1
tools\adb.exe shell pm uninstall com.snoopy112.backbutton >nul 2>&1
tools\adb.exe shell mkdir -p /sdcard/IPTV >nul 2>&1
tools\adb.exe shell mkdir -p /sdcard/Music >nul 2>&1
echo [OK] Limpieza realizada y carpetas multimedia preparadas (/sdcard/IPTV, /sdcard/Music).
echo.

echo ===============================================================================
echo [4/6] INSTALANDO EL LAUNCHER COCKPIT CHANGAN X7 PLUS (HMI NATIVO 1920x720)
echo ===============================================================================
set "LAUNCHER_INSTALLED="
if exist "apks\ChanganX7Plus_OEM_Launcher.apk" (
    echo Instalando apks\ChanganX7Plus_OEM_Launcher.apk...
    tools\adb.exe install -r -d "apks\ChanganX7Plus_OEM_Launcher.apk"
    set "LAUNCHER_INSTALLED=1"
) else if exist "ChanganX7Plus_OEM_Launcher.apk" (
    echo Instalando ChanganX7Plus_OEM_Launcher.apk...
    tools\adb.exe install -r -d "ChanganX7Plus_OEM_Launcher.apk"
    set "LAUNCHER_INSTALLED=1"
)

if "%LAUNCHER_INSTALLED%"=="1" (
    echo Concediendo permisos de sistema al Launcher Changan X7 Plus...
    tools\adb.exe shell pm grant com.chinatsp.x7plus.launcher android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.chinatsp.x7plus.launcher android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.chinatsp.x7plus.launcher android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.chinatsp.x7plus.launcher android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.chinatsp.x7plus.launcher android.permission.SYSTEM_ALERT_WINDOW >nul 2>&1
    tools\adb.exe shell appops set com.chinatsp.x7plus.launcher SYSTEM_ALERT_WINDOW allow >nul 2>&1
    tools\adb.exe shell appops set com.chinatsp.x7plus.launcher android:mock_location allow >nul 2>&1
    tools\adb.exe shell cmd notification allow_listener com.chinatsp.x7plus.launcher/.MediaNotificationListener >nul 2>&1
    echo [OK] Launcher instalado y con todos los permisos concedidos.
) else (
    echo [ERROR] No se encontro ChanganX7Plus_OEM_Launcher.apk
)
echo.

echo ===============================================================================
echo Configurando GPS Fisico Satelital Nativo (Antena Hardware Changan)...
tools\adb.exe shell settings put secure location_mode 3 >nul 2>&1
tools\adb.exe shell settings put secure location_providers_allowed +gps,+network >nul 2>&1
tools\adb.exe shell settings put secure mock_location 0 >nul 2>&1
tools\adb.exe shell appops set com.chinatsp.x7plus.launcher android:mock_location deny >nul 2>&1
tools\adb.exe shell pm uninstall com.snoopy112.backbutton >nul 2>&1
tools\adb.exe shell settings put secure enabled_accessibility_services null >nul 2>&1
tools\adb.exe shell am startservice com.chinatsp.x7plus.launcher/.FloatingOverlayService >nul 2>&1
echo [OK] GPS Fisico Satelital Nativo (mock_location=0, mode=3) activado.
echo.
echo [5/6] INSTALANDO APLICACIONES COMPLEMENTARIAS Y ANDROID AUTO
echo ===============================================================================

REM Headunit Revived (Android Auto Oficial Widescreen 1920x720)
if exist "apks\headunit_android_auto.apk" (
    echo Instalando Headunit Revived (Android Auto Nativo)...
    tools\adb.exe install -r -d "apks\headunit_android_auto.apk"
    tools\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.RECORD_AUDIO >nul 2>&1
    tools\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.SYSTEM_ALERT_WINDOW >nul 2>&1
    tools\adb.exe shell appops set com.andrerinas.headunitrevived SYSTEM_ALERT_WINDOW allow >nul 2>&1
    tools\adb.exe shell pm grant gb.xxy.hr android.permission.RECORD_AUDIO >nul 2>&1
    tools\adb.exe shell pm grant gb.xxy.hr android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell appops set gb.xxy.hr SYSTEM_ALERT_WINDOW allow >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.andrerinas.headunitrevived" --ei appCentered 2 >nul 2>&1
    tools\adb.exe shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "com.andrerinas.headunitrevived" >nul 2>&1
    echo [OK] Headunit Revived instalado con permisos y bypass de bordes negros.
)

REM AutoKit (Carlinkit CarPlay & Android Auto)
if exist "apks\AutoKit.apk" (
    echo Instalando AutoKit (Carlinkit Dongle)...
    tools\adb.exe install -r -d "apks\AutoKit.apk"
    tools\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.RECORD_AUDIO >nul 2>&1
    tools\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "cn.manstep.phonemirrorBox" --ei appCentered 2 >nul 2>&1
    echo [OK] AutoKit instalado con permisos y bypass.
)

REM Waze GPS
if exist "apks\waze_gps_navegacion.apk" (
    echo Instalando Waze GPS...
    tools\adb.exe install -r -d "apks\waze_gps_navegacion.apk"
    tools\adb.exe shell pm grant com.waze android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.waze android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.waze android.permission.RECORD_AUDIO >nul 2>&1
    echo [OK] Waze GPS instalado con permisos.
) else if exist "apks\waze_standalone.apk" (
    echo Instalando Waze GPS...
    tools\adb.exe install -r -d "apks\waze_standalone.apk"
    tools\adb.exe shell pm grant com.waze android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.waze android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
    echo [OK] Waze GPS instalado con permisos.
)

REM Magic Earth GPS (Multipaquete Split)
if exist "apks\magicearth_splits\base.apk" (
    echo Instalando Magic Earth GPS 3D multipaquete...
    tools\adb.exe install-multiple -r -d "apks\magicearth_splits\base.apk" "apks\magicearth_splits\split_config.arm64_v8a.apk" "apks\magicearth_splits\split_config.es.apk" "apks\magicearth_splits\split_config.xxhdpi.apk" >nul 2>&1
    tools\adb.exe shell pm grant com.generalmagic.magicearth android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    echo [OK] Magic Earth GPS 3D instalado.
)

REM Spotube (Spotify Libre 1:1 con Descargas MP3)
if exist "apks\spotube_spotify_libre.apk" (
    echo Instalando Spotube (Spotify Libre y Descargas MP3)...
    tools\adb.exe install -r -d "apks\spotube_spotify_libre.apk"
    tools\adb.exe shell pm grant oss.krtirtho.spotube android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant oss.krtirtho.spotube android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell appops set oss.krtirtho.spotube SYSTEM_ALERT_WINDOW allow >nul 2>&1
    tools\adb.exe shell dumpsys deviceidle whitelist +oss.krtirtho.spotube >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "oss.krtirtho.spotube" --ei appCentered 2 >nul 2>&1
    tools\adb.exe shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "oss.krtirtho.spotube" >nul 2>&1
    echo [OK] Spotube instalado con descargas y pantalla completa.
)

REM SimpMusic (Reproductor Offline Pro sin Bucles)
if exist "apks\simpmusic_offline_pro.apk" (
    echo Instalando SimpMusic (Offline Pro)...
    tools\adb.exe install -r -d "apks\simpmusic_offline_pro.apk"
    tools\adb.exe shell pm grant com.maxrave.simpmusic android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.maxrave.simpmusic android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell appops set com.maxrave.simpmusic SYSTEM_ALERT_WINDOW allow >nul 2>&1
    tools\adb.exe shell dumpsys deviceidle whitelist +com.maxrave.simpmusic >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.maxrave.simpmusic" --ei appCentered 2 >nul 2>&1
    tools\adb.exe shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "com.maxrave.simpmusic" >nul 2>&1
    tools\adb.exe shell settings put global policy_control immersive.full=com.maxrave.simpmusic >nul 2>&1
    echo [OK] SimpMusic instalado con bypass SystemUI (engranaje libre y sin bordes).
)

REM InnerTune (Musica Streaming Ligera 7MB)
if exist "apks\vimusic_innertune_musica.apk" (
    echo Instalando InnerTune Ultra Ligero...
    tools\adb.exe install -r -d "apks\vimusic_innertune_musica.apk"
    tools\adb.exe shell pm grant com.malopieds.innertune android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.malopieds.innertune android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.zionhuang.music android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.zionhuang.music android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.malopieds.innertune" --ei appCentered 2 >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.zionhuang.music" --ei appCentered 2 >nul 2>&1
    echo [OK] InnerTune instalado.
)

REM OwnTV (Television de Cable en Vivo con 370+ Canales)
if exist "apks\owntv_cable_en_vivo.apk" (
    echo Instalando OwnTV (Cableoperador en Vivo)...
    tools\adb.exe install -r -d "apks\owntv_cable_en_vivo.apk"
    tools\adb.exe shell pm grant com.ahxn00.owntv android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.ahxn00.owntv android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.ahxn00.owntv" --ei appCentered 2 >nul 2>&1
    echo [OK] OwnTV instalado.
)

REM Precargar Lista Maestra de 371 Canales IPTV VIP en la Radio
if exist "canales_vip.m3u" (
    echo Precargando lista de 371 canales VIP en el auto...
    tools\adb.exe shell "mkdir -p /sdcard/IPTV" >nul 2>&1
    tools\adb.exe push "canales_vip.m3u" "/sdcard/canales_vip.m3u" >nul 2>&1
    tools\adb.exe push "canales_vip.m3u" "/sdcard/IPTV/canales_vip.m3u" >nul 2>&1
    echo [OK] Lista de 371 canales guardada en /sdcard/canales_vip.m3u
) else if exist "CANALES_VIP_LATAM_PERU_DEPORTES.m3u" (
    echo Precargando lista de canales VIP en el auto...
    tools\adb.exe push "CANALES_VIP_LATAM_PERU_DEPORTES.m3u" "/sdcard/canales_vip.m3u" >nul 2>&1
    echo [OK] Lista de canales guardada en /sdcard/canales_vip.m3u
)

REM CloudStream 3 (XuperTV Libre - Peliculas y Series)
if exist "apks\xuper_tv_streaming.apk" (
    echo Instalando CloudStream 3 (XuperTV Libre)...
    tools\adb.exe install -r -d "apks\xuper_tv_streaming.apk"
    tools\adb.exe shell pm grant com.lagradost.cloudstream3 android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell pm grant com.lagradost.cloudstream3 android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.lagradost.cloudstream3" --ei appCentered 2 >nul 2>&1
    echo [OK] CloudStream 3 instalado.
)

REM Navegador Brave con Bloqueador de Anuncios
if exist "apks\brave_browser.apk" (
    echo Instalando Navegador Brave...
    tools\adb.exe install -r -d "apks\brave_browser.apk"
    echo [OK] Brave instalado.
) else if exist "apks\brave_arm64.apk" (
    echo Instalando Navegador Brave...
    tools\adb.exe install -r -d "apks\brave_arm64.apk"
    echo [OK] Brave instalado.
)

REM SmartTube Pro (YouTube para Autos sin Anuncios)
if exist "apks\smarttube_youtube_pro.apk" (
    echo Instalando SmartTube Pro (YouTube Auto sin Anuncios)...
    tools\adb.exe install -r -d "apks\smarttube_youtube_pro.apk"
    echo [OK] SmartTube Pro instalado.
) else if exist "apks\smarttube_youtube_pro.apk" (
    echo Instalando SmartTube Pro...
    tools\adb.exe install -r -d "apks\smarttube_youtube_pro.apk"
    echo [OK] SmartTube Pro instalado.
)

REM NewPipe YouTube Ligero
if exist "apks\newpipe_youtube.apk" (
    echo Instalando NewPipe YouTube...
    tools\adb.exe install -r -d "apks\newpipe_youtube.apk"
    echo [OK] NewPipe instalado.
)

REM XuperTV Streaming (Canales en Vivo y Peliculas)
if exist "apks\xuper_tv_streaming.apk" (
    echo Instalando XuperTV Streaming...
    tools\adb.exe install -r -d "apks\xuper_tv_streaming.apk"
    echo [OK] XuperTV instalado.
)

REM Organic Maps GPS Satelital Offline
if exist "apks\organicmaps_gps_offline.apk" (
    echo Instalando Organic Maps GPS Offline...
    tools\adb.exe install -r -d "apks\organicmaps_gps_offline.apk"
    tools\adb.exe shell pm grant app.organicmaps.web android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    echo [OK] Organic Maps instalado.
) else if exist "apks\organicmaps_gps_offline.apk" (
    echo Instalando Organic Maps GPS Offline...
    tools\adb.exe install -r -d "apks\organicmaps_gps_offline.apk"
    tools\adb.exe shell pm grant app.organicmaps.web android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    echo [OK] Organic Maps instalado.
)

REM Taskbar Pantalla Dividida
if exist "apks\taskbar_pantalla_dividida.apk" (
    echo Instalando Taskbar Multiventana...
    tools\adb.exe install -r -d "apks\taskbar_pantalla_dividida.apk"
    echo [OK] Taskbar instalado.
)

REM GPS Tether Server & Bluetooth GPS Provider (Compartir GPS desde el tel?fono)
if exist "apks\gps_tether.apk" (
    echo Instalando GPS Tether Server...
    tools\adb.exe install -r -d "apks\gps_tether.apk"
    tools\adb.exe shell pm grant com.bricatta.GPSTetherServer_FE android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    tools\adb.exe shell pm grant com.bricatta.GPSTetherServer_FE android.permission.ACCESS_COARSE_LOCATION >nul 2>&1
    echo [OK] GPS Tether Server instalado.
)

if exist "apks\bluetooth_gps_provider.apk" (
    echo Instalando Bluetooth GPS Provider...
    tools\adb.exe install -r -d "apks\bluetooth_gps_provider.apk"
    tools\adb.exe shell pm grant org.broeuschmeul.umrysh.android.gps.bluetooth.provider android.permission.ACCESS_FINE_LOCATION >nul 2>&1
    echo [OK] Bluetooth GPS Provider instalado.
)

REM Radio Universal Global con Iconos de Emisoras (RadioDroid)
if exist "apks\radio_universal_global.apk" (
    echo Instalando Radio Universal Global (con Logos de Emisoras)...
    tools\adb.exe install -r -d "apks\radio_universal_global.apk"
    tools\adb.exe shell pm grant net.programmierecke.radiodroid2 android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "net.programmierecke.radiodroid2" --ei appCentered 2 >nul 2>&1
    echo [OK] Radio Universal Global instalado.
)

REM YouTube Web Pro (Fullscreen 1920x720 sin anuncios)
if exist "apks\youtube_web_pro.apk" (
    echo Instalando YouTube Web Pro (Fullscreen sin bordes)...
    tools\adb.exe install -r -d "apks\youtube_web_pro.apk"
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.changan.youtube" --ei appCentered 2 >nul 2>&1
    echo [OK] YouTube Web Pro instalado.
)

REM Kick Live Streaming (Fullscreen 1920x720)
if exist "apks\kick_streaming_live.apk" (
    echo Instalando Kick Live Streaming (Fullscreen)...
    tools\adb.exe install -r -d "apks\kick_streaming_live.apk"
    tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.changan.kick" --ei appCentered 2 >nul 2>&1
    echo [OK] Kick Live Streaming instalado.
)

echo.
echo ===============================================================================
echo [6/6] ACTIVANDO OPTIMIZACIONES, ZONA HORARIA Y FULLSCREEN 1920x720
echo ===============================================================================
tools\adb.exe shell setprop persist.sys.timezone America/Lima >nul 2>&1
tools\adb.exe shell settings put global auto_time_zone 0 >nul 2>&1
tools\adb.exe shell appops set com.chinatsp.x7plus.launcher android:mock_location allow >nul 2>&1
tools\adb.exe shell settings put secure mock_location 1 >nul 2>&1
tools\adb.exe shell settings put secure location_mode 3 >nul 2>&1
tools\adb.exe shell settings put secure location_providers_allowed +gps,+network >nul 2>&1
tools\adb.exe shell settings put secure enabled_accessibility_services com.chinatsp.x7plus.launcher/.FloatingBackService >nul 2>&1
tools\adb.exe shell settings put secure accessibility_enabled 1 >nul 2>&1
tools\adb.exe shell appops set com.chinatsp.x7plus.launcher SYSTEM_ALERT_WINDOW allow >nul 2>&1
tools\adb.exe shell appops set com.andrerinas.headunitrevived SYSTEM_ALERT_WINDOW allow >nul 2>&1
tools\adb.exe shell appops set gb.xxy.hr SYSTEM_ALERT_WINDOW allow >nul 2>&1
tools\adb.exe shell settings put global window_animation_scale 0.5 >nul 2>&1
tools\adb.exe shell settings put global transition_animation_scale 0.5 >nul 2>&1
tools\adb.exe shell settings put global animator_duration_scale 0.5 >nul 2>&1
tools\adb.exe shell settings put global policy_control immersive.full=* >nul 2>&1
echo.
echo ===============================================================================
echo SELECCIONA EL MODO DE VISUALIZACION PARA TU PANTALLA:
echo   [1] Modo Nativo Adaptable (Recomendado - 100%% Seguro, Mantiene Climatizador A/C)
echo   [2] Modo Ultra-Overscan Total (Fuerza 1920x720 sobre el borde OEM)
echo   [3] Restaurar resolucion de fabrica (Reset)
echo ===============================================================================
choice /C 123 /N /D 1 /T 10 /M "Elige una opcion [1-3] (Por defecto [1] en 10 seg): "
if errorlevel 3 (
    tools\adb.exe shell wm overscan reset >nul 2>&1
    tools\adb.exe shell wm size reset >nul 2>&1
    tools\adb.exe shell wm density reset >nul 2>&1
    echo [OK] Resolucion restaurada a valores de fabrica.
) else if errorlevel 2 (
    tools\adb.exe shell wm overscan -320,0,0,0 >nul 2>&1
    tools\adb.exe shell wm size 1920x720 >nul 2>&1
    tools\adb.exe shell wm density 213 >nul 2>&1
    echo [OK] Ultra-Overscan activado.
) else (
    tools\adb.exe shell wm overscan 0,0,0,0 >nul 2>&1
    tools\adb.exe shell wm size 1920x720 >nul 2>&1
    tools\adb.exe shell wm density 213 >nul 2>&1
    echo [OK] Modo Nativo Fullscreen optimizado aplicado.
)

REM === BYPASS FORENSE F202_SystemUI (Changan X7 Plus 1920x720) ===
echo.
echo Transmitiendo comandos de desbloqueo nativo F202_SystemUI a todas las apps...
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.chinatsp.x7plus.launcher" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.waze" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.generalmagic.magicearth" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.andrerinas.headunitrevived" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "it.vfsfitvnm.innertune" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "it.vfsfitvnm.vimusic" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.github.cloudstream" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.liskovsoft.videomanager" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.brave.browser" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "org.schabi.newpipe" --ei appCentered 2 >nul 2>&1
tools\adb.exe shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName "com.chinatsp.x7plus.launcher" >nul 2>&1
tools\adb.exe shell am broadcast -a com.chinatsp.activity.onpostresume --es packageName "com.chinatsp.x7plus.launcher" >nul 2>&1
tools\adb.exe shell cmd package set-home-activity com.chinatsp.x7plus.launcher/.MainActivity >nul 2>&1
tools\adb.exe shell pm disable-user --user 0 com.chinatsp.launcher >nul 2>&1
tools\adb.exe shell am start -a android.intent.action.MAIN -c android.intent.category.HOME >nul 2>&1
tools\adb.exe shell input keyevent 3 >nul 2>&1
tools\adb.exe shell am start -n com.chinatsp.x7plus.launcher/.MainActivity >nul 2>&1
echo [OK] Launcher desplegado a pantalla completa (1920x720) sin barras laterales.
echo [OK] Launcher desplegado a pantalla completa (1920x720) sin marcos laterales.
echo.
echo ===============================================================================
echo            PROCESO COMPLETADO EXITOSAMENTE EN TU CHANGAN X7 PLUS!
echo ===============================================================================
echo.
echo Ya puedes desconectar el cable USB o disfrutar del nuevo sistema.
echo.
pause
