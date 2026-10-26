@echo off
setlocal
chcp 65001 >nul 2>&1
title CHANGAN X7 PLUS - DASHBOARD VISUAL Y SIMULADOR
cd /d "%~dp0"
color 0B

cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - DASHBOARD VISUAL Y SIMULADOR COCKPIT
echo                    (Android 9 / API 28 / MT8666 / 1920x720)
echo ===============================================================================
echo.

netstat -aon | findstr :5050 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo [OK] Servidor local ya esta activo y escuchando en el puerto 5050.
    goto LANZAR_NAVEGADOR
)

if exist "%~dp0runtime\python.exe" goto USE_PORTABLE
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    echo [i] Utilizando Python 3.11 detectado...
    goto INICIAR_PROCESO
)
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    echo [i] Utilizando Python 3.14 detectado...
    goto INICIAR_PROCESO
)
for /f "delims=" %%i in ('where python 2^>nul') do (
    if not "%%i"=="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
        set "PYTHON_CMD=%%i"
        goto USE_SYSTEM_FOUND
    )
)
where py >nul 2>&1
if not errorlevel 1 goto USE_PY
goto NO_PYTHON

:USE_PORTABLE
set "PYTHON_CMD=%~dp0runtime\python.exe"
echo [i] Utilizando Python portable integrado [runtime\python.exe]...
goto INICIAR_PROCESO

:USE_SYSTEM_FOUND
echo [i] Utilizando Python del sistema: %PYTHON_CMD%
goto INICIAR_PROCESO

:USE_SYSTEM
set "PYTHON_CMD=python"
echo [i] Utilizando Python del sistema...
goto INICIAR_PROCESO

:USE_PY
set "PYTHON_CMD=py"
echo [i] Utilizando lanzador py de Windows...
goto INICIAR_PROCESO

:NO_PYTHON
echo [ERROR] No se encontro runtime\python.exe ni Python en Windows.
echo Por favor asegurate de tener Python instalado.
pause
exit /b 1

:INICIAR_PROCESO
echo [1/2] Iniciando servidor web local en http://localhost:5050...
start "CHANGAN_X7_SERVER" /min "%PYTHON_CMD%" "%~dp0server.py"

echo [*] Esperando respuesta del servidor...
for /l %%i in (1,1,10) do (
    ping 127.0.0.1 -n 2 >nul
    netstat -aon | findstr :5050 | findstr LISTENING >nul 2>&1
    if not errorlevel 1 goto LANZAR_NAVEGADOR
)

:LANZAR_NAVEGADOR
echo [2/2] Abriendo Dashboard en tu navegador...
start "" "http://localhost:5050"
explorer "http://localhost:5050" >nul 2>&1

:BUCLE_MENU
cls
echo ===============================================================================
echo        CHANGAN X7 PLUS - DASHBOARD VISUAL Y SIMULADOR COCKPIT
echo ===============================================================================
echo.
echo  [ESTADO]  Servidor activo en: http://localhost:5050
echo  [PAGINA]  Dashboard: http://localhost:5050
echo  [PAGINA]  Simulador Cockpit: http://localhost:5050/cockpit.html
echo.
echo ===============================================================================
echo                         OPCIONES DISPONIBLES:
echo ===============================================================================
echo   [1] Volver a abrir Dashboard en el navegador
echo   [2] Abrir Simulador Cockpit 1920x720 directamente
echo   [3] Instalar Launcher y APKs en el Changan X7 Plus
echo   [4] Deshacer Cambios y Restaurar Changan de Fabrica (1-Clic)
echo   [5] Probar Conexion con el Auto (ADB)
echo   [6] Detener Servidor y Salir
echo ===============================================================================
echo.
choice /C 123456 /N /M "Presiona un numero [1-6]: "
if errorlevel 6 goto OP_6
if errorlevel 5 goto OP_5
if errorlevel 4 goto OP_4
if errorlevel 3 goto OP_3
if errorlevel 2 goto OP_2
if errorlevel 1 goto OP_1
goto BUCLE_MENU

:OP_1
start "" "http://localhost:5050"
explorer "http://localhost:5050" >nul 2>&1
goto BUCLE_MENU

:OP_2
start "" "http://localhost:5050/cockpit.html"
explorer "http://localhost:5050/cockpit.html" >nul 2>&1
goto BUCLE_MENU

:OP_3
call "INSTALAR_TODO_EN_EL_AUTO.bat"
goto BUCLE_MENU

:OP_4
call "DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat"
goto BUCLE_MENU

:OP_5
echo.
tools\adb.exe devices -l
echo.
pause
goto BUCLE_MENU

:OP_6
call "DETENER_DASHBOARD.bat"
exit /b 0
