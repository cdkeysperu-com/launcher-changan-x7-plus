@echo off
setlocal enabledelayedexpansion
title Changan X7 Plus Lab - Instalar Launcher Cockpit X7

echo ==================================================================
echo   CHANGAN X7 PLUS LAB - INSTALAR / ACTUALIZAR COCKPIT X7
echo ==================================================================
echo.

set SDK_ROOT=%LOCALAPPDATA%\Android\Sdk
set ADB_EXE=%SDK_ROOT%\platform-tools\adb.exe
set TARGET_DEV=emulator-5554
set APK_PATH=C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1\apks\x7_cockpit_launcher.apk

if not exist "%ADB_EXE%" (
    echo [ERROR] No se encontro adb.exe en: "%ADB_EXE%"
    pause
    exit /b 1
)

if not exist "%APK_PATH%" (
    echo [ERROR] No se encontro el archivo APK en: "%APK_PATH%"
    pause
    exit /b 1
)

:: REGLA DE SEGURIDAD CRITICA:
:: Verificar que el dispositivo destino sea exclusivamente el emulador (emulator-5554).
:: NUNCA instalar contra un dispositivo fisico (auto o telefono).
echo [SEGURIDAD] Verificando que el emulador (%TARGET_DEV%) este activo...
"%ADB_EXE%" devices | findstr /C:"%TARGET_DEV%	device" >nul
if %errorlevel% neq 0 (
    echo [ERROR DE SEGURIDAD / CONEXION]
    echo El emulador virtual '%TARGET_DEV%' no esta en linea o no esta listo.
    echo.
    echo Dispositivos ADB detectados:
    "%ADB_EXE%" devices
    echo.
    echo Por proteccion del vehiculo fisico, la instalacion se ha detenido.
    echo Inicia primero el emulador con 'start_emulator.bat'.
    pause
    exit /b 1
)

echo [OK] Emulador confirmado: %TARGET_DEV%
echo Instalando o actualizando APK: "%APK_PATH%"...
echo.

:: Desactivar mensaje molesto de modo inmersivo en el emulador
"%ADB_EXE%" -s %TARGET_DEV% shell settings put secure immersive_mode_confirmations confirmed >nul 2>&1

:: Instalar APK preservando datos
"%ADB_EXE%" -s %TARGET_DEV% install -r -g "%APK_PATH%"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion del APK en el emulador.
    pause
    exit /b 1
)

echo.
echo [EXITO] APK instalado correctamente en el emulador.
echo Iniciando actividad principal (MainActivity)...
"%ADB_EXE%" -s %TARGET_DEV% shell am start -n com.changan.x7plus.launcher/.MainActivity
echo.
echo Estado de la ventana del launcher:
"%ADB_EXE%" -s %TARGET_DEV% shell dumpsys window displays | findstr "cur="
echo.
echo ==================================================================
echo Instalacion y ejecucion completadas con exito.
echo ==================================================================
pause
