@echo off
title CHANGAN X7 PLUS - EMULADOR PC 100%% IDENTICO AL AUTO
color 0B
cd /d "%~dp0"

set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - PROBAR Y VALIDAR TODO EN EL EMULADOR DE PC
echo            Resolución 1920x720 px @ 213 DPI - MT8666 Android 9
echo ===============================================================================
echo.
echo Este script realiza de forma 100%% automática:
echo  1. Localiza el entorno Python de tu PC sin cerrar la ventana.
echo  2. Abre el Emulador Panorámico 1920x720 con aceleración GPU en tu monitor.
echo  3. Carga el Launcher Cockpit Mejorado (Clima superior, Radio/Música separadas, RAM).
echo  4. Instala la Suite Mejorada:
echo     - Open Headunit v3.5.0 Oficial Release (Android Auto Inalámbrico Nativo)
echo     - Spotube v5.1.2 (Spotify Libre con Descargas MP3)
echo     - SimpMusic v2.3.0 (Offline Pro sin bucles)
echo     - InnerTune v0.5.14 (Ultra Ligero 7MB)
echo     - OwnTV v5.2.1 + 370 Canales IPTV Precargados
echo     - CloudStream 3 (XuperTV Libre)
echo     - Waze GPS + Navegador Brave + SmartTube
echo  5. Concede todos los permisos automotrices y bypass de pantalla completa.
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
echo [2/3] Iniciando proceso de clonación y prueba con Launcher Cockpit en PC...
echo ===============================================================================
echo.

"%PYTHON_EXE%" "%~dp0CLONAR_AUTO_EN_EMULADOR.py"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ===============================================================================
if "%EXIT_CODE%"=="0" (
    echo [OK] Proceso finalizado exitosamente.
    echo Ya puedes interactuar directamente con el emulador en tu PC.
    echo El Launcher Cockpit y todas las APKs mejoradas están listas y visibles.
) else (
    echo [AVISO] El proceso terminó con código: %EXIT_CODE%
    echo Revisa los mensajes superiores para más detalles.
)
echo ===============================================================================
pause
