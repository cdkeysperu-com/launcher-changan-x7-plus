@echo off
setlocal
chcp 65001 >nul 2>&1
title CHANGAN X7 PLUS - CENTRO DE CONTROL MAESTRO
cd /d "%~dp0"
color 0B

:MENU_PRINCIPAL
cls
echo ===============================================================================
echo                CHANGAN X7 PLUS - CENTRO DE CONTROL MAESTRO
echo                    (Android 9 / API 28 / MT8666 / 1920x720)
echo ===============================================================================
echo.
echo   [1] Iniciar Dashboard Visual y Simulador en tu Navegador (http://localhost:5050)
echo   [2] Probar TODO en el Emulador de PC (100%% Id?ntico al Auto - 1920x720)
echo   [3] Instalar TODO en el Auto (Launcher + Waze + Magic Earth + InnerTune + AVM 360)
echo   [4] Deshacer Cambios y Restaurar Changan de Fabrica (1-Clic Rollback)
echo   [5] Probar Conexion con el Auto (Verificar Cable USB / ADB)
echo   [6] Conectar al Auto por Wi-Fi (Inalambrico)
echo   [7] Activar Pantalla Completa Inmersiva (1920x720 sin barras negras)
echo   [8] Extraer Telemetr?a y Diagn?stico Completo del Auto (Guardar Log .txt)
echo   [9] Detener Servidor del Dashboard
echo   [0] Salir
echo.
echo ===============================================================================
choice /C 1234567890 /N /M "Presiona una opcion [0-9]: "
if errorlevel 10 exit /b 0
if errorlevel 9 goto OP_STOP
if errorlevel 8 goto OP_TELEMETRY
if errorlevel 7 goto OP_FULLSCREEN
if errorlevel 6 goto OP_WIFI
if errorlevel 5 goto OP_CHECK
if errorlevel 4 goto OP_RESTORE
if errorlevel 3 goto OP_INSTALL
if errorlevel 2 goto OP_EMU
if errorlevel 1 goto OP_DASHBOARD
goto MENU_PRINCIPAL

:OP_TELEMETRY
cls
echo ===============================================================================
echo          EXTRAYENDO TELEMETR?A Y DIAGN?STICO DEL AUTO (LOG COMPLETO)
echo ===============================================================================
echo.
if exist "runtime\python.exe" (
    "runtime\python.exe" -c "import server; res = server.execute_export_telemetry(); print(res.get('message', '')); print('Archivo:', res.get('filename', ''))"
) else (
    python -c "import server; res = server.execute_export_telemetry(); print(res.get('message', '')); print('Archivo:', res.get('filename', ''))"
)
echo.
echo El informe se ha guardado en la carpeta 'diagnostics\'.
echo.
pause
goto MENU_PRINCIPAL

:OP_DASHBOARD
call "INICIAR_DASHBOARD_CHANGAN.bat"
goto MENU_PRINCIPAL

:OP_EMU
echo.
echo Iniciando Clonaci?n y Pruebas en el Emulador Changan X7 Plus...
call "1_PROBAR_TODO_EN_EMULADOR.bat"
goto MENU_PRINCIPAL

:OP_INSTALL
call "INSTALAR_TODO_EN_EL_AUTO.bat"
goto MENU_PRINCIPAL

:OP_RESTORE
call "DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat"
goto MENU_PRINCIPAL

:OP_CHECK
cls
echo ===============================================================================
echo                VERIFICANDO ESTADO DE CONEXION CON EL AUTO
echo ===============================================================================
echo.
tools\adb.exe start-server >nul 2>&1
echo Dispositivos ADB detectados:
tools\adb.exe devices -l
echo.
echo ===============================================================================
echo Si no aparece ningun dispositivo:
echo  1. Conecta el cable USB de la radio frontal a tu laptop.
echo  2. En la radio Changan abre el marcador de telefono y escribe: **888
echo  3. Activa "Depuracion por USB" y marca "Permitir siempre".
echo ===============================================================================
echo.
pause
goto MENU_PRINCIPAL

:OP_WIFI
cls
echo ===============================================================================
echo                CONECTAR AL AUTO POR WI-FI (INALAMBRICO)
echo ===============================================================================
echo.
echo Conecta tu laptop a la misma red Wi-Fi que la radio del auto o comparte Wi-Fi.
echo.
set "IP_AUTO="
set /p IP_AUTO="Ingresa la IP de la radio del auto (ej: 192.168.43.1): "
if "%IP_AUTO%"=="" goto MENU_PRINCIPAL

echo Conectando a %IP_AUTO%:5555...
tools\adb.exe connect %IP_AUTO%:5555
echo.
pause
goto MENU_PRINCIPAL

:OP_FULLSCREEN
cls
echo ===============================================================================
echo          ACTIVAR PANTALLA COMPLETA INMERSIVA (1920x720 SIN BARRAS)
echo ===============================================================================
echo.
tools\adb.exe shell settings put global policy_control immersive.full=*
echo [OK] Politica inmersiva aplicada para todas las apps.
echo.
pause
goto MENU_PRINCIPAL

:OP_STOP
call "DETENER_DASHBOARD.bat"
goto MENU_PRINCIPAL
