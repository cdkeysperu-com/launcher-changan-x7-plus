@echo off
setlocal enabledelayedexpansion
title Changan X7 Plus Lab - Recopilar Registros Logcat

set SDK_ROOT=%LOCALAPPDATA%\Android\Sdk
set ADB_EXE=%SDK_ROOT%\platform-tools\adb.exe
set TARGET_DEV=emulator-5554
set LOG_DIR=%~dp0logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ==================================================================
echo   CHANGAN X7 PLUS LAB - RECOPILACION DE REGISTROS LOGCAT
echo ==================================================================
echo.

"%ADB_EXE%" devices | findstr /C:"%TARGET_DEV%	device" >nul
if %errorlevel% neq 0 (
    echo [ERROR] El emulador '%TARGET_DEV%' no esta en linea.
    pause
    exit /b 1
)

for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%a
set LOG_FILE=%LOG_DIR%\logcat_%TIMESTAMP%.txt
set LAUNCHER_LOG=%LOG_DIR%\logcat_launcher_%TIMESTAMP%.txt

echo Descargando registro completo de logcat...
"%ADB_EXE%" -s %TARGET_DEV% logcat -d > "%LOG_FILE%"

echo Filtrando errores y mensajes del launcher...
"%ADB_EXE%" -s %TARGET_DEV% logcat -d | findstr /I "com.changan.x7plus.launcher chromium WebView AndroidHost FATAL Exception Error" > "%LAUNCHER_LOG%"

echo.
echo ==================================================================
echo [EXITO] Registros guardados:
echo Log completo: "%LOG_FILE%"
echo Log Launcher: "%LAUNCHER_LOG%"
echo ==================================================================
echo.
pause
