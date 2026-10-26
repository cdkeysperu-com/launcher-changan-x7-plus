@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title CHANGAN X7 PLUS - CAPTURAR TELEMETR?A VEHICULAR AVANZADA
color 0A
cd /d "%~dp0"

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - CAPTURA FORENSE DE TELEMETR?A VEHICULAR
echo ===============================================================================
echo.
echo Este script extrae de forma no invasiva:
echo  1. Estado y c?digos del Bus CAN y MCU del auto.
echo  2. Diagn?stico del chip MediaTek GNSS y sat?lites fijados.
echo  3. Temperaturas del procesador y estado el?ctrico.
echo  4. Diagn?stico de la pantalla panor?mica 1920x720.
echo  5. Registra el informe en la carpeta 'informes/'.
echo.
echo ===============================================================================
echo [1/2] Localizando ejecutable de Python...
echo ===============================================================================

set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
) else (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if not "%%i"=="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
            if "!PYTHON_EXE!"=="" set "PYTHON_EXE=%%i"
        )
    )
)
if "!PYTHON_EXE!"=="" set "PYTHON_EXE=python"

echo [*] Python detectado: !PYTHON_EXE!
echo.
echo ===============================================================================
echo [2/2] Iniciando captura de telemetr?a...
echo ===============================================================================
echo.

"!PYTHON_EXE!" "%~dp0capturar_telemetria_avanzada.py"

echo.
echo ===============================================================================
echo Telemetr?a registrada. Revisa los archivos generados en la carpeta 'informes/'.
echo ===============================================================================
echo.
pause
