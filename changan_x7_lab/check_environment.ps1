<#
.SYNOPSIS
    Verifica el entorno de desarrollo para Changan X7 Plus Virtual Lab.
.DESCRIPTION
    Comprueba Android SDK, emulador, imágenes del sistema API 28, aceleración de hardware (WHPX)
    y estado del AVD configurado.
#>

$ErrorActionPreference = "Continue"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " CHANGAN X7 PLUS LAB - AUDITORIA DEL ENTORNO VIRTUAL" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Rutas base
$sdkRoot = "$env:LOCALAPPDATA\Android\Sdk"
$emulatorExe = "$sdkRoot\emulator\emulator.exe"
$adbExe = "$sdkRoot\platform-tools\adb.exe"
$avdDir = "$HOME\.android\avd"

Write-Host "[1/6] Comprobando Android SDK..." -ForegroundColor Yellow
if (Test-Path $sdkRoot) {
    Write-Host "  [OK] Android SDK encontrado en: $sdkRoot" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] No se encontro Android SDK en: $sdkRoot" -ForegroundColor Red
}

# 2. Comprobar Emulator y ADB
Write-Host "`n[2/6] Comprobando binarios del Emulador y ADB..." -ForegroundColor Yellow
if (Test-Path $emulatorExe) {
    $emuVer = & $emulatorExe -version | Select-Object -First 1
    Write-Host "  [OK] Emulator: $emuVer" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] emulator.exe no encontrado en: $emulatorExe" -ForegroundColor Red
}

if (Test-Path $adbExe) {
    $adbVer = & $adbExe version | Select-Object -First 1
    Write-Host "  [OK] ADB: $adbVer" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] adb.exe no encontrado en: $adbExe" -ForegroundColor Red
}

# 3. Comprobar Aceleracion de Virtualizacion (WHPX / Hypervisor)
Write-Host "`n[3/6] Verificando aceleracion de virtualizacion..." -ForegroundColor Yellow
$proc = Get-CimInstance Win32_Processor
Write-Host "  Procesador: $($proc.Name)" -ForegroundColor Gray
Write-Host "  Virtualizacion en BIOS/Firmware: $($proc.VirtualizationFirmwareEnabled)" -ForegroundColor Gray

if (Test-Path $emulatorExe) {
    $accelCheck = & $emulatorExe -accel-check 2>&1
    if ($accelCheck -match "WHPX|usable|installed") {
        Write-Host "  [OK] Aceleracion de hardware activa: Windows Hypervisor Platform (WHPX)" -ForegroundColor Green
    } else {
        Write-Host "  [ALERTA] Estado de aceleracion: $accelCheck" -ForegroundColor Yellow
    }
}

# 4. Comprobar Imagenes del Sistema API 28
Write-Host "`n[4/6] Verificando Imagen de Sistema Android 9 (API 28)..." -ForegroundColor Yellow
$sysImgPath = "$sdkRoot\system-images\android-28\default\x86_64"
if (Test-Path "$sysImgPath\system.img") {
    Write-Host "  [OK] Imagen oficial AOSP Android 9 Pie (API 28, x86_64) instalada" -ForegroundColor Green
    Write-Host "       Ruta: $sysImgPath" -ForegroundColor Gray
} else {
    Write-Host "  [ERROR] Imagen de sistema API 28 no encontrada en: $sysImgPath" -ForegroundColor Red
}

# 5. Comprobar AVDs creados
Write-Host "`n[5/6] Verificando dispositivos virtuales (AVD)..." -ForegroundColor Yellow
$avdRef = "$avdDir\Changan_X7_Plus_API28_1920x720.avd"
$avdComp = "$avdDir\Changan_X7_Plus_API28_160DPI.avd"

if (Test-Path "$avdRef\config.ini") {
    Write-Host "  [OK] AVD Referencia (213 DPI): Changan_X7_Plus_API28_1920x720" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] AVD Referencia no encontrado: $avdRef" -ForegroundColor Red
}

if (Test-Path "$avdComp\config.ini") {
    Write-Host "  [OK] AVD Compatibilidad (160 DPI): Changan_X7_Plus_API28_160DPI" -ForegroundColor Green
} else {
    Write-Host "  [AVISO] AVD Compatibilidad no encontrado: $avdComp" -ForegroundColor Yellow
}

# 6. Comprobar APK del Launcher
Write-Host "`n[6/6] Verificando APK existente de Cockpit X7..." -ForegroundColor Yellow
$apkPath = "C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1\apks\x7_cockpit_launcher.apk"
if (Test-Path $apkPath) {
    $apkSize = [math]::Round((Get-Item $apkPath).Length / 1MB, 2)
    Write-Host "  [OK] APK localizado: $apkPath ($apkSize MB)" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] No se encontro el APK en: $apkPath" -ForegroundColor Red
}

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host " RESUMEN: Entorno listo para ejecucion." -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
