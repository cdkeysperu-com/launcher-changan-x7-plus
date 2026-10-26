@echo off
chcp 65001 >nul 2>&1
if exist "%~dp0portable\INICIAR_DASHBOARD_CHANGAN.bat" (
    cd /d "%~dp0portable"
    call "INICIAR_DASHBOARD_CHANGAN.bat"
) else if exist "%~dp0APK CHANGAN X7 PLUS\INICIAR_DASHBOARD_CHANGAN.bat" (
    cd /d "%~dp0APK CHANGAN X7 PLUS"
    call "INICIAR_DASHBOARD_CHANGAN.bat"
)
