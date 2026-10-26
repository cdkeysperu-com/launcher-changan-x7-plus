@echo off
chcp 65001 >nul 2>&1
if exist "%~dp0portable\DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat" (
    cd /d "%~dp0portable"
    call "DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat"
) else if exist "%~dp0APK CHANGAN X7 PLUS\DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat" (
    cd /d "%~dp0APK CHANGAN X7 PLUS"
    call "DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat"
)
