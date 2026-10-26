<#
.SYNOPSIS
    Lanzador en PowerShell para el emulador Changan X7 Plus (1920x720)
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " CHANGAN X7 PLUS LAB - INICIAR DISPOSITIVO VIRTUAL" -ForegroundColor Cyan
Write-Host " Resolucion: 1920x720 - Android 9 (API 28)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

$sdkRoot = "$env:LOCALAPPDATA\Android\Sdk"
$emulatorExe = "$sdkRoot\emulator\emulator.exe"
$adbExe = "$sdkRoot\platform-tools\adb.exe"
$avdName = "Changan_X7_Plus_API28_1920x720"

if ($args[0] -eq "160") { $avdName = "Changan_X7_Plus_API28_160DPI" }

$avdPath = "$HOME\.android\avd\$avdName.avd"

# 1. Limpiar procesos colgados y archivos de bloqueo
Write-Host "[1/3] Limpiando procesos previos y archivos de bloqueo..." -ForegroundColor Yellow
& $adbExe -s emulator-5554 emu kill 2>$null
Stop-Process -Name "qemu-system-x86_64", "emulator" -Force -ErrorAction SilentlyContinue

Remove-Item "$avdPath\hardware-qemu.ini.lock" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$avdPath\multiinstance.lock" -Force -ErrorAction SilentlyContinue
Remove-Item "$avdPath\*.lock" -Force -ErrorAction SilentlyContinue

# 2. Iniciar el emulador desde su propio directorio
Write-Host "[2/3] Iniciando emulador Android ($avdName)..." -ForegroundColor Yellow
Write-Host "      Resolucion: 1920x720" -ForegroundColor Gray
Write-Host "      Aceleracion: WHPX / AMD Ryzen" -ForegroundColor Gray
Write-Host ""

$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = $emulatorExe
$pinfo.Arguments = "-avd $avdName -gpu auto -accel on"
$pinfo.WorkingDirectory = "$sdkRoot\emulator"
$pinfo.UseShellExecute = $true

[System.Diagnostics.Process]::Start($pinfo) | Out-Null

# 3. Esperar a que el emulador responda en ADB
Write-Host "[3/3] Esperando conexion de Android..." -ForegroundColor Yellow
Write-Host "La ventana del emulador se abrira en tu pantalla." -ForegroundColor Gray
Write-Host ""

$booted = $false
for ($i = 0; $i -lt 30; $i++) {
    $devices = & $adbExe devices
    if ($devices -match "emulator-5554\s+device") {
        $booted = $true
        break
    }
    Start-Sleep -Seconds 2
}

if ($booted) {
    Write-Host "==================================================================" -ForegroundColor Green
    Write-Host " EMULADOR EN LINEA Y LISTO EN TU ESCRITORIO" -ForegroundColor Green
    Write-Host "==================================================================" -ForegroundColor Green
    & $adbExe -s emulator-5554 shell wm size
    & $adbExe -s emulator-5554 shell wm density
    Write-Host ""
    Write-Host "Para instalar Cockpit X7: haz doble clic en install_launcher.bat" -ForegroundColor Cyan
} else {
    Write-Host "[AVISO] El emulador esta cargando en segundo plano." -ForegroundColor Yellow
}

Write-Host "Presiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
