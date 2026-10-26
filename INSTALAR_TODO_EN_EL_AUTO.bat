@echo off
chcp 65001 >nul 2>&1
if exist "%~dp0portable\INSTALAR_TODO_EN_EL_AUTO.bat" (
    cd /d "%~dp0portable"
    call "INSTALAR_TODO_EN_EL_AUTO.bat"
) else if exist "%~dp0APK CHANGAN X7 PLUS\INSTALAR_TODO_EN_EL_AUTO.bat" (
    cd /d "%~dp0APK CHANGAN X7 PLUS"
    call "INSTALAR_TODO_EN_EL_AUTO.bat"
)
