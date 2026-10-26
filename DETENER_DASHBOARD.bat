@echo off
chcp 65001 >nul 2>&1
if exist "%~dp0portable\DETENER_DASHBOARD.bat" (
    cd /d "%~dp0portable"
    call "DETENER_DASHBOARD.bat"
) else (
    taskkill /f /im python.exe >nul 2>&1
    taskkill /f /im pythonw.exe >nul 2>&1
)
