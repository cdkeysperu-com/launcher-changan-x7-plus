@echo off
setlocal
title Changan X7 Plus Lab - Iniciar Emulador 1920x720

echo ==================================================================
echo   CHANGAN X7 PLUS LAB - INICIAR DISPOSITIVO VIRTUAL
echo   Resolucion: 1920x720 - Android 9 - API 28
echo ==================================================================
echo.

set "SDK_ROOT=C:\Users\axeln\AppData\Local\Android\Sdk"
set "EMULATOR_EXE=%SDK_ROOT%\emulator\emulator.exe"
set "ADB_EXE=%SDK_ROOT%\platform-tools\adb.exe"

if not exist "%EMULATOR_EXE%" (
    echo [ERROR] No se encontro emulator.exe en: "%EMULATOR_EXE%"
    echo Ejecuta primero el script check_environment.ps1.
    pause
    exit /b 1
)

:: Seleccionar perfil de AVD
set "AVD_NAME=Changan_X7_Plus_API28_1920x720"
if "%~1"=="160" set "AVD_NAME=Changan_X7_Plus_API28_160DPI"
if "%~1"=="213" set "AVD_NAME=Changan_X7_Plus_API28_1920x720"

set "AVD_PATH=C:\Users\axeln\.android\avd\%AVD_NAME%.avd"

:: 1. Limpieza preventiva de instancias fantasma y bloqueos
echo [1/3] Limpiando procesos previos y archivos de bloqueo...
"%ADB_EXE%" -s emulator-5554 emu kill >nul 2>&1
taskkill /F /IM qemu-system-x86_64.exe >nul 2>&1
taskkill /F /IM emulator.exe >nul 2>&1

if exist "%AVD_PATH%\hardware-qemu.ini.lock" rmdir /s /q "%AVD_PATH%\hardware-qemu.ini.lock" >nul 2>&1
if exist "%AVD_PATH%\multiinstance.lock" del /f /q "%AVD_PATH%\multiinstance.lock" >nul 2>&1
del /f /q "%AVD_PATH%\*.lock" >nul 2>&1

:: 2. Lanzar emulador desde su propio directorio
echo [2/3] Iniciando emulador Android (%AVD_NAME%)...
echo       Resolucion: 1920x720
echo       Aceleracion: WHPX / AMD Ryzen
echo.

cd /d "%SDK_ROOT%\emulator"
start "Android Emulator" "%EMULATOR_EXE%" -avd %AVD_NAME% -gpu auto -accel on

:: 3. Esperar arranque
echo [3/3] Esperando conexion de Android...
echo La ventana del emulador se abrira en tu pantalla.
echo.

:wait_loop
"%ADB_EXE%" devices | findstr /C:"emulator-5554	device" >nul
if %errorlevel% equ 0 goto booted
ping 127.0.0.1 -n 3 >nul
goto wait_loop

:booted
echo ==================================================================
echo  EMULADOR EN LINEA Y LISTO EN TU ESCRITORIO
echo ==================================================================
echo.
"%ADB_EXE%" -s emulator-5554 shell wm size
"%ADB_EXE%" -s emulator-5554 shell wm density
echo.
echo Para instalar Cockpit X7: haz doble clic en install_launcher.bat
echo ==================================================================
pause
