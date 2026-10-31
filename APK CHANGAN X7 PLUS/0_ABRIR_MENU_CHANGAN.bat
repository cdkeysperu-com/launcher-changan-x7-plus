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
echo   [2] Probar TODO en el Emulador de PC (100%% Identico al Auto - 1920x720)
echo   [3] Instalar TODO en el Auto (Launcher + Waze + Magic Earth + InnerTune + AVM 360)
echo   [4] Deshacer Cambios y Restaurar Changan de Fabrica (1-Clic Rollback)
echo   [5] Fijar Launcher OnStyle de Fabrica por Defecto (1-Clic)
echo   [6] Fijar Launcher Cockpit Custom por Defecto (1-Clic)
echo   [7] Capturar Telemetria Vehicular Avanzada (CAN / MCU / GNSS / Termico)
echo   [8] Probar Conexion con el Auto (Verificar Cable USB / ADB)
echo   [9] Conectar al Auto por Wi-Fi / Hotspot 5G (Inalambrico)
echo   [G] Restablecer GPS Satelital Fisico Nativo MT8666
echo   [M] Mapear Teclas en Vivo y Probar Camara 360 / Home (Laptop en el Auto)
echo   [0] Salir
echo.
echo ===============================================================================
choice /C 123456789GM0 /N /M "Presiona una opcion [1-9, G, M, 0]: "
if errorlevel 12 exit /b 0
if errorlevel 11 goto OP_MAPEAR
if errorlevel 10 goto OP_GPS
if errorlevel 9 goto OP_WIFI
if errorlevel 8 goto OP_CHECK
if errorlevel 7 goto OP_TELEMETRY
if errorlevel 6 goto OP_COCKPIT
if errorlevel 5 goto OP_ONSTYLE
if errorlevel 4 goto OP_RESTORE
if errorlevel 3 goto OP_INSTALL
if errorlevel 2 goto OP_EMU
if errorlevel 1 goto OP_DASHBOARD
goto MENU_PRINCIPAL

:OP_MAPEAR
call "%~dp0MAPEAR_TECLAS_Y_CAMARA_CHANGAN.py"
goto MENU_PRINCIPAL

:OP_GPS
call "%~dp0RESTABLECER_GPS_FISICO_NATIVO.bat"
goto MENU_PRINCIPAL

:OP_DASHBOARD
call "%~dp0INICIAR_DASHBOARD_CHANGAN.bat"
goto MENU_PRINCIPAL

:OP_EMU
echo.
echo Iniciando Clonacion y Pruebas en el Emulador Changan X7 Plus...
call "%~dp01_PROBAR_TODO_EN_EMULADOR.bat"
goto MENU_PRINCIPAL

:OP_INSTALL
call "%~dp0INSTALAR_TODO_EN_EL_AUTO.bat"
goto MENU_PRINCIPAL

:OP_RESTORE
call "%~dp0DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat"
goto MENU_PRINCIPAL

:OP_ONSTYLE
call "%~dp0VOLVER_A_ONSTYLE_FABRICA.bat"
goto MENU_PRINCIPAL

:OP_COCKPIT
if exist "%~dp0..\PONER_LAUNCHER_COCKPIT_DEFECTO.bat" (
    call "%~dp0..\PONER_LAUNCHER_COCKPIT_DEFECTO.bat"
)
goto MENU_PRINCIPAL

:OP_TELEMETRY
cls
echo ===============================================================================
echo          EXTRAYENDO TELEMETRIA Y DIAGNOSTICO DEL AUTO (LOG COMPLETO)
echo ===============================================================================
echo.
python -c "import server; res = server.execute_export_telemetry(); print(res.get('message', '')); print('Archivo:', res.get('filename', ''))"
echo.
echo El informe se ha guardado en la carpeta 'diagnostics\'.
echo.
pause
goto MENU_PRINCIPAL

:OP_CHECK
cls
echo ===============================================================================
echo                VERIFICANDO ESTADO DE CONEXION CON EL AUTO
echo ===============================================================================
echo.
set "ADB_EXE="
if exist "%~dp0tools\adb.exe" (
    set "ADB_EXE=%~dp0tools\adb.exe"
) else (
    set "ADB_EXE=adb"
)

"%ADB_EXE%" start-server >nul 2>&1
echo Dispositivos ADB detectados:
"%ADB_EXE%" devices -l
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
echo            CONEXION INALAMBRICA WI-FI / HOTSPOT 5G AL AUTO
echo ===============================================================================
echo.
echo Asegurate de que tanto tu laptop como la radio Changan esten conectados
echo a la misma red Wi-Fi (por ejemplo, el Hotspot 5G de tu celular o modem).
echo.
set "ADB_EXE="
if exist "%~dp0tools\adb.exe" (
    set "ADB_EXE=%~dp0tools\adb.exe"
) else (
    set "ADB_EXE=adb"
)

echo   [1] Conectar directamente por IP (ej: 192.168.43.x)
echo   [2] Habilitar modo inalambrico por cable primero (adb tcpip 5555)
echo   [3] Ver dispositivos actualmente conectados
echo   [0] Volver al menu principal
echo.
choice /C 1230 /N /M "Selecciona una opcion [1-3, 0]: "
if errorlevel 4 goto MENU_PRINCIPAL
if errorlevel 3 goto WIFI_DEVICES
if errorlevel 2 goto WIFI_TCPIP
if errorlevel 1 goto WIFI_CONNECT
goto MENU_PRINCIPAL

:WIFI_TCPIP
echo.
echo Ejecutando: adb tcpip 5555 en dispositivos conectados por cable...
"%ADB_EXE%" tcpip 5555
echo [OK] Puerto 5555 habilitado. Ya puedes desconectar el cable USB si lo deseas.
echo.
pause
goto OP_WIFI

:WIFI_DEVICES
echo.
echo Dispositivos detectados:
"%ADB_EXE%" devices -l
echo.
pause
goto OP_WIFI

:WIFI_CONNECT
echo.
set "IP_AUTO="
set /p IP_AUTO="Ingresa la IP de la radio del auto (ej: 192.168.43.15): "
if "%IP_AUTO%"=="" goto OP_WIFI

echo.
echo Conectando a %IP_AUTO%:5555...
"%ADB_EXE%" connect %IP_AUTO%:5555
echo.
echo Estado actual de conexiones:
"%ADB_EXE%" devices -l
echo.
pause
goto MENU_PRINCIPAL
