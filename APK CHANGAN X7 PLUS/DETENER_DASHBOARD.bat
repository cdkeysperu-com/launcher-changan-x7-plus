@echo off
setlocal
chcp 65001 >nul 2>&1
title DETENER DASHBOARD CHANGAN X7 PLUS
cd /d "%~dp0"
color 0C

cls
echo ===============================================================================
echo            DETENIENDO SERVIDOR DEL DASHBOARD CHANGAN X7 PLUS
echo ===============================================================================
echo.
echo Buscando procesos activos en el puerto 5050...

set "FOUND=0"
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    set "FOUND=1"
)

if "%FOUND%"=="1" (
    echo [OK] Servidor detenido exitosamente.
) else (
    echo [i] No habia ningun servidor activo en el puerto 5050.
)

echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
