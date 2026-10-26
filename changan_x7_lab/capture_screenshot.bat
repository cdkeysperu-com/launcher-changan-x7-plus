@echo off
setlocal enabledelayedexpansion
title Changan X7 Plus Lab - Captura de Pantalla

set SDK_ROOT=%LOCALAPPDATA%\Android\Sdk
set ADB_EXE=%SDK_ROOT%\platform-tools\adb.exe
set TARGET_DEV=emulator-5554
set DIAG_DIR=%~dp0diagnostics
if not exist "%DIAG_DIR%" mkdir "%DIAG_DIR%"

echo ==================================================================
echo   CHANGAN X7 PLUS LAB - CAPTURAR SCREENSHOT
echo ==================================================================
echo.

"%ADB_EXE%" devices | findstr /C:"%TARGET_DEV%	device" >nul
if %errorlevel% neq 0 (
    echo [ERROR] El emulador '%TARGET_DEV%' no esta en linea.
    echo Inicia primero el emulador con 'start_emulator.bat'.
    pause
    exit /b 1
)

for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%a

set FILENAME=screenshot_%TIMESTAMP%.png
if not "%~1"=="" set FILENAME=%~1.png

set OUTFILE=%DIAG_DIR%\%FILENAME%

echo Capturando pantalla de %TARGET_DEV% (1920x720)...
"%ADB_EXE%" -s %TARGET_DEV% exec-out screencap -p > "%OUTFILE%"

if exist "%OUTFILE%" (
    echo [EXITO] Captura guardada en:
    echo "%OUTFILE%"
) else (
    echo [ERROR] No se pudo guardar la captura.
)
echo.
pause
