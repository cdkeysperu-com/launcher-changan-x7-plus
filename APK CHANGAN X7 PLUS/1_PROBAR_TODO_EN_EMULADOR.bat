@echo off
title CHANGAN X7 PLUS - EMULADOR PC 100%% IDENTICO AL AUTO
color 0B
cd /d "%~dp0"

set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - PROBAR Y VALIDAR TODO EN EL EMULADOR DE PC
echo            Resolucion 1920x720 px @ 213 DPI - MT8666 Android 9
echo ===============================================================================
echo.
echo Este script realiza de forma 100%% automatica:
echo  1. Localiza el entorno Python 3.11 de tu PC sin cerrar la ventana.
echo  2. Abre el Emulador Panoramico 1920x720 con aceleracion GPU en tu monitor.
echo  3. Instala los APKs OEM de Fabrica (Launcher OnStyle, Camara 360 HD, etc.).
echo  4. Configura el Launcher OnStyle por defecto o el Cockpit Custom.
echo  5. Instala Waze, Open Headunit Beta 5, InnerTune, Brave y Magic Earth.
echo  6. Concede todos los permisos automotrices y activa la burbuja flotante.
echo.
echo ===============================================================================
echo [1/3] Localizando ejecutable de Python...
echo ===============================================================================

set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
) else (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if not "%%i"=="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
        )
    )
)
if not defined PYTHON_EXE set "PYTHON_EXE=python"

echo [*] Python detectado: %PYTHON_EXE%
echo.
echo ===============================================================================
echo [2/3] Iniciando proceso de clonacion y prueba en PC...
echo ===============================================================================
echo.

"%PYTHON_EXE%" "%~dp0CLONAR_AUTO_EN_EMULADOR.py"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ===============================================================================
if "%EXIT_CODE%"=="0" (
    echo [OK] Proceso finalizado exitosamente.
    echo Ya puedes interactuar directamente con el emulador en tu PC.
) else (
    echo [AVISO] El proceso termino con codigo: %EXIT_CODE%
    echo Revisa los mensajes superiores para mas detalles.
)
echo ===============================================================================
echo.
echo Presiona cualquier tecla para salir...
pause
