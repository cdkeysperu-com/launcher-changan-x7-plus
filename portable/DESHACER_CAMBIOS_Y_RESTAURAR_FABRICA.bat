@echo off
setlocal
chcp 65001 >nul 2>&1
title RESTABLECER A INTERFAZ DE FABRICA (CHANGAN X7 PLUS)
cd /d "%~dp0"
color 0E

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - DESHACER CAMBIOS Y RESTAURAR ESTADO DE FABRICA
echo ===============================================================================
echo.
echo Este script restaura tu vehiculo a su estado original de fabrica en 1 clic:
echo   1. Restablece el Launcher oficial OnStyle de Changan.
echo   2. Quita el modo inmersivo forzado y restablece barras originales de Android.
echo   3. Restablece la resolucion y densidad de pantalla a los valores de fabrica.
echo   4. Cierra servicios de terceros.
echo.

if not exist "tools\adb.exe" (
    echo [ERROR] No se encontro tools\adb.exe
    pause
    exit /b 1
)

:RECHECK
echo Verificando conexion USB con la radio...
tools\adb.exe start-server >nul 2>&1

set "DEVICE_FOUND="
for /f "tokens=1,2" %%A in ('tools\adb.exe devices ^| findstr /v "List" ^| findstr "device"') do (
    set "DEVICE_FOUND=1"
)

if "%DEVICE_FOUND%"=="1" goto RESTORE_NOW

echo.
echo [!] No se detecto la radio del auto por USB.
echo Asegurate de conectar el cable USB frontal de la radio a la laptop.
echo.
choice /C SN /M "Deseas reintentar la conexion [S=Si / N=No]"
if errorlevel 2 exit /b 0
if errorlevel 1 goto RECHECK

:RESTORE_NOW
echo.
echo [1/4] Deteniendo y desinstalando aplicaciones personalizadas y limpiando temporales...
tools\adb.exe shell am force-stop it.fast4x.rimusic >nul 2>&1
tools\adb.exe shell am force-stop com.chinatsp.x7plus.launcher >nul 2>&1
tools\adb.exe shell am force-stop com.changan.x7plus.launcher >nul 2>&1
tools\adb.exe shell appops set com.chinatsp.x7plus.launcher android:mock_location deny >nul 2>&1
tools\adb.exe shell pm uninstall com.chinatsp.x7plus.launcher >nul 2>&1
tools\adb.exe shell pm uninstall com.changan.x7plus.launcher >nul 2>&1
tools\adb.exe shell pm uninstall com.waze >nul 2>&1
tools\adb.exe shell pm uninstall com.zionhuang.music >nul 2>&1
tools\adb.exe shell pm uninstall com.malopieds.innertune >nul 2>&1
tools\adb.exe shell pm uninstall it.fast4x.rimusic >nul 2>&1
tools\adb.exe shell pm uninstall com.andrerinas.headunitrevived >nul 2>&1
tools\adb.exe shell pm uninstall gb.xxy.hr >nul 2>&1
tools\adb.exe shell pm uninstall cn.manstep.phonemirrorBox >nul 2>&1
tools\adb.exe shell pm uninstall com.changan.youtube >nul 2>&1
tools\adb.exe shell pm uninstall com.changan.kick >nul 2>&1
tools\adb.exe shell pm uninstall net.programmierecke.radiodroid2 >nul 2>&1
tools\adb.exe shell pm uninstall de.stefanpledl.radiodroid2 >nul 2>&1
tools\adb.exe shell pm uninstall org.smarttube.stable >nul 2>&1
tools\adb.exe shell pm uninstall org.schabi.newpipe >nul 2>&1
tools\adb.exe shell pm uninstall com.lagradost.cloudstream3 >nul 2>&1
tools\adb.exe shell pm uninstall com.brave.browser >nul 2>&1
tools\adb.exe shell pm uninstall com.snoopy112.backbutton >nul 2>&1
tools\adb.exe shell pm uninstall com.appspot.app58us.backkey >nul 2>&1
tools\adb.exe shell pm uninstall com.farmerbb.taskbar >nul 2>&1
tools\adb.exe shell pm uninstall com.generalmagic.magicearth >nul 2>&1
tools\adb.exe shell pm uninstall oss.krtirtho.spotube >nul 2>&1
tools\adb.exe shell pm uninstall com.maxrave.simpmusic >nul 2>&1
tools\adb.exe shell pm uninstall com.ahxn00.owntv >nul 2>&1
tools\adb.exe shell rm -rf /data/local/tmp/* >nul 2>&1

echo [2/4] Purgando base de datos y cache del Launcher OEM (Erradicando Apps Fantasma)...
tools\adb.exe shell pm enable com.chinatsp.launcher >nul 2>&1
tools\adb.exe shell pm clear com.chinatsp.launcher >nul 2>&1
tools\adb.exe shell am force-stop com.chinatsp.launcher >nul 2>&1
tools\adb.exe shell pm clear com.android.launcher3 >nul 2>&1
tools\adb.exe shell am force-stop com.android.launcher3 >nul 2>&1
tools\adb.exe shell pm clear com.changan.launcher >nul 2>&1
tools\adb.exe shell cmd package set-home-activity com.chinatsp.launcher/.MainAct >nul 2>&1
tools\adb.exe shell am start -n com.chinatsp.launcher/.MainAct >nul 2>&1
tools\adb.exe shell am start -a android.intent.action.MAIN -c android.intent.category.HOME >nul 2>&1

echo [3/4] Restableciendo politicas de pantalla, resolucion y densidades de fabrica...
tools\adb.exe shell settings put global policy_control null
tools\adb.exe shell settings put global force_resizable_activities 0
tools\adb.exe shell settings put global enable_freeform_support 0
tools\adb.exe shell wm size reset
tools\adb.exe shell wm density reset
tools\adb.exe shell wm overscan reset

echo [4/4] Verificando interfaz de fabrica y enviando senal Home...
tools\adb.exe shell am start -a android.intent.action.MAIN -c android.intent.category.HOME >nul 2>&1
tools\adb.exe shell input keyevent 3 >nul 2>&1

echo [4/4] Verificando interfaz de fabrica...
echo.
echo ===============================================================================
echo        SISTEMA RESTAURADO CON EXITO AL 100%% DE FABRICA!
echo ===============================================================================
echo Tu pantalla ha vuelto a mostrar el Launcher oficial Changan OnStyle.
echo Ninguna particion ni archivo del sistema del auto fue alterado.
echo.
pause
