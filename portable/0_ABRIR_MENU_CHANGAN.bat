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
echo   [3] Instalar TODO en el Auto (Cockpit Launcher + Android Auto + Spotify + TV Cable + Waze)
echo   [4] Deshacer Cambios y Restaurar Changan de F?brica (1-Clic Rollback)
echo   [5] Fijar Launcher OnStyle de F?brica por Defecto (1-Clic)
echo   [6] Fijar Launcher Cockpit Custom por Defecto (1-Clic)
echo   [7] Capturar Telemetr?a Vehicular Avanzada (CAN / MCU / GNSS / T?rmico)
echo   [8] Probar Conexi?n con el Auto (Verificar Cable USB / ADB)
echo   [9] Conectar al Auto por Wi-Fi (Inalambrico)
echo   [M] Mapear Teclas en Vivo y Probar Camara 360 / Home (Laptop en el Auto)
echo   [0] Salir
echo.
echo ===============================================================================
choice /C 123456789M0 /N /M "Presiona una opcion [1-9, M, 0]: "
if errorlevel 11 exit /b 0
if errorlevel 10 goto OP_MAPEAR
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
call "1_MAPEAR_TECLAS_EN_VIVO.bat"
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

:OP_ONSTYLE
call "PONER_LAUNCHER_ONSTYLE_DEFECTO.bat"
goto MENU_PRINCIPAL

:OP_COCKPIT
call "PONER_LAUNCHER_COCKPIT_DEFECTO.bat"
goto MENU_PRINCIPAL

:OP_TELEMETRY
call "CAPTURAR_TELEMETRIA_AVANZADA.bat"
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
) else if exist "%~dp0APK CHANGAN X7 PLUS\tools\adb.exe" (
    set "ADB_EXE=%~dp0APK CHANGAN X7 PLUS\tools\adb.exe"
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
echo                CONECTAR AL AUTO POR WI-FI (INALAMBRICO)
echo ===============================================================================
echo.
echo Conecta tu laptop a la misma red Wi-Fi que la radio del auto o comparte Wi-Fi.
echo.
set "IP_AUTO="
set /p IP_AUTO="Ingresa la IP de la radio del auto (ej: 192.168.43.1): "
if "%IP_AUTO%"=="" goto MENU_PRINCIPAL

set "ADB_EXE="
if exist "%~dp0APK CHANGAN X7 PLUS\tools\adb.exe" (
    set "ADB_EXE=%~dp0APK CHANGAN X7 PLUS\tools\adb.exe"
) else if exist "%~dp0tools\adb.exe" (
    set "ADB_EXE=%~dp0tools\adb.exe"
) else (
    set "ADB_EXE=adb"
)

echo Conectando a %IP_AUTO%:5555...
"%ADB_EXE%" connect %IP_AUTO%:5555
echo.
pause
goto MENU_PRINCIPAL
