@echo off
setlocal enabledelayedexpansion
title Changan X7 Plus Lab - Diagnostico Completo

set SDK_ROOT=%LOCALAPPDATA%\Android\Sdk
set ADB_EXE=%SDK_ROOT%\platform-tools\adb.exe
set TARGET_DEV=emulator-5554
set DIAG_DIR=%~dp0diagnostics
if not exist "%DIAG_DIR%" mkdir "%DIAG_DIR%"

echo ==================================================================
echo   CHANGAN X7 PLUS LAB - DIAGNOSTICO COMPLETO DE PANTALLA Y VENTANAS
echo ==================================================================
echo.

"%ADB_EXE%" devices | findstr /C:"%TARGET_DEV%	device" >nul
if %errorlevel% neq 0 (
    echo [ERROR] El emulador '%TARGET_DEV%' no esta en linea.
    pause
    exit /b 1
)

for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%a
set REPORT_FILE=%DIAG_DIR%\diagnostic_report_%TIMESTAMP%.txt
set SCREENSHOT_FILE=%DIAG_DIR%\diagnostic_screen_%TIMESTAMP%.png

echo Generando reporte de diagnostico...
echo ================================================================== > "%REPORT_FILE%"
echo  CHANGAN X7 PLUS VIRTUAL LAB - REPORTE FORENSE DE PANTALLA >> "%REPORT_FILE%"
echo  Fecha y hora: %date% %time% >> "%REPORT_FILE%"
echo  Dispositivo objetivo: %TARGET_DEV% >> "%REPORT_FILE%"
echo ================================================================== >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [1/5] Propiedades del Sistema Android: >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell getprop ro.build.version.release >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell getprop ro.build.version.sdk >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell getprop ro.product.cpu.abi >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [2/5] Resolucion Fisica y Override de Pantalla (wm size): >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell wm size >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [3/5] Densidad de Pixeles (wm density): >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell wm density >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [4/5] Dimensiones de Display (dumpsys window displays): >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell dumpsys window displays >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [5/5] Actividad y Ventana en Foco (MainActivity bounds): >> "%REPORT_FILE%"
"%ADB_EXE%" -s %TARGET_DEV% shell dumpsys window windows | findstr /R "com.changan.x7plus.launcher mFrame mCurrentFocus mFocusedApp" >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo Capturando screenshot sincronizada...
"%ADB_EXE%" -s %TARGET_DEV% exec-out screencap -p > "%SCREENSHOT_FILE%"

echo.
echo ==================================================================
echo [EXITO] Diagnostico completado:
echo Reporte:    "%REPORT_FILE%"
echo Screenshot: "%SCREENSHOT_FILE%"
echo ==================================================================
echo.
type "%REPORT_FILE%" | findstr /R "Physical Override mFrame mCurrentFocus"
echo.
pause
