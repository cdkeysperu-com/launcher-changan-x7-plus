@echo off
chcp 65001 >nul
title CHANGAN X7 PLUS - DIAGNOSTICO EN VIVO Y MAPEO DE TECLAS
color 0b

echo ==============================================================
echo   CHANGAN X7 PLUS - MONITOR EN VIVO Y CALIBRADOR DE TECLAS
echo ==============================================================
echo.
echo Conecta tu laptop al puerto USB de la consola central del auto
echo (o conectate a la misma red Wi-Fi).
echo.
echo Iniciando asistente interactivo...
echo.

python "%~dp0MAPEAR_TECLAS_Y_CAMARA_CHANGAN.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Si no tienes Python instalado en el sistema, ejecutando con Python portatil...
    "%~dp0APK CHANGAN X7 PLUS\tools\python\python.exe" "%~dp0MAPEAR_TECLAS_Y_CAMARA_CHANGAN.py"
)

echo.
pause
