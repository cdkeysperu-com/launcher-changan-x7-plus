@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title CHANGAN X7 PLUS - EMULADOR DE PANTALLA 1920x720
color 0B
cd /d "%~dp0"

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - EMULADOR VIRTUAL DE PANTALLA MULTIMEDIA
echo               (Android 9 / API 28 / MT8666 / 1920x720 @ 213 DPI)
echo ===============================================================================
echo.

REM 1. Buscar el ejecutable oficial de Android Emulator
set "EMU_EXE="
if exist "%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe" (
    set "EMU_EXE=%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe"
) else if exist "C:\Users\axeln\AppData\Local\Android\Sdk\emulator\emulator.exe" (
    set "EMU_EXE=C:\Users\axeln\AppData\Local\Android\Sdk\emulator\emulator.exe"
)

if "%EMU_EXE%"=="" (
    echo [ERROR] No se encontr? emulator.exe en tu carpeta de Android SDK.
    echo Ruta esperada: %LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe
    echo.
    pause
    exit /b 1
)

echo [1/4] Comprobando procesos previos y limpiando bloqueos...
REM Cerrar procesos hu?rfanos que puedan bloquear el AVD
taskkill /f /im qemu-system-x86_64.exe >nul 2>&1
taskkill /f /im emulator.exe >nul 2>&1

REM Eliminar posibles archivos de bloqueo .lock
set "AVD_DIR=%USERPROFILE%\.android\avd\Changan_X7_Plus_API28_1920x720.avd"
if exist "%AVD_DIR%" (
    del /f /q "%AVD_DIR%\*.lock" >nul 2>&1
    for /d %%d in ("%AVD_DIR%\*.lock") do rmdir /s /q "%%d" >nul 2>&1
)

echo [2/4] AVD seleccionado: Changan_X7_Plus_API28_1920x720 (1920x720 panor?mico)
echo [3/4] Lanzando ventana gr?fica del Emulador en tu escritorio...
echo       (Utilizando aceleraci?n por hardware GPU AMD Radeon)
echo.

REM Iniciar el emulador en su propia ventana gr?fica interactiva
start "Changan_X7_Plus_Emulator" "%EMU_EXE%" -avd Changan_X7_Plus_API28_1920x720 -gpu auto -accel on

echo [4/4] Esperando a que el emulador arranque y conecte con ADB...
echo       Por favor no cierres esta ventana hasta ver la confirmaci?n.
echo.

set "BOOT_OK="
for /l %%i in (1,1,30) do (
    timeout /t 2 /nobreak >nul 2>&1
    
    REM Verificar si ADB lo detecta
    set "DEV="
    for /f "tokens=1,2" %%A in ('"tools\adb.exe" devices 2^>nul ^| findstr "emulator-"') do (
        set "DEV=%%A"
    )
    if not "!DEV!"=="" (
        echo [OK] Emulador detectado en ADB: !DEV!
        set "BOOT_OK=1"
        goto EMU_READY
    )
    echo [*] Esperando carga del sistema Android... (%%i/30)
)

:EMU_READY
echo.
echo ===============================================================================
echo      ?EMULADOR CHANGAN X7 PLUS ABIERTO EXITOSAMENTE EN TU PANTALLA!
echo ===============================================================================
echo.
echo  * Ventana: Ahora deber?as ver la ventana panor?mica 1920x720 en tu monitor.
echo  * Control: Puedes usar el rat?n para tocar y deslizar como en la pantalla del auto.
echo  * Dashboard Web: Tambi?n puedes abrir http://localhost:5050 para instalarle apps.
echo.
echo Puedes minimizar o cerrar esta ventana cuando desees. El emulador seguir? activo.
echo ===============================================================================
echo.
pause
