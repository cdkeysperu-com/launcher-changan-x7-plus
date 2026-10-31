@echo off
chcp 65001 >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
echo [OK] Servidor Dashboard detenido.
