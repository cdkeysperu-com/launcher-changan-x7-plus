@echo off
setlocal enabledelayedexpansion
title Changan X7 Plus Lab - Cambiar Perfil de Densidad

set SDK_ROOT=%LOCALAPPDATA%\Android\Sdk
set ADB_EXE=%SDK_ROOT%\platform-tools\adb.exe
set TARGET_DEV=emulator-5554

echo ==================================================================
echo   CHANGAN X7 PLUS LAB - CAMBIO DE PERFIL DE DENSIDAD
echo ==================================================================
echo.
echo [1] Perfil de Referencia:    213 DPI (Valor de fabrica reportado)
echo [2] Perfil de Compatibilidad: 160 DPI (Valor probado anteriormente)
echo [3] Restablecer a Inicial:   wm density reset
echo.

set /p OPTION="Selecciona una opcion [1, 2, 3]: "

if "%OPTION%"=="1" (
    echo Aplicando Perfil de Referencia: 213 DPI...
    "%ADB_EXE%" -s %TARGET_DEV% shell wm density 213
)
if "%OPTION%"=="2" (
    echo Aplicando Perfil de Compatibilidad: 160 DPI...
    "%ADB_EXE%" -s %TARGET_DEV% shell wm density 160
)
if "%OPTION%"=="3" (
    echo Restableciendo densidad a configuracion inicial de hardware...
    "%ADB_EXE%" -s %TARGET_DEV% shell wm density reset
)

echo.
echo Estado actual de la pantalla:
"%ADB_EXE%" -s %TARGET_DEV% shell wm size
"%ADB_EXE%" -s %TARGET_DEV% shell wm density
echo.
pause
