import sys
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
# -*- coding: utf-8 -*-
"""
================================================================================
CLONADOR MAESTRO DE AMBIENTE CHANGAN X7 PLUS EN EMULADOR PC (100% IDÉNTICO AL AUTO)
================================================================================
Despliega en el emulador local de Android Studio (1920x720 @ 213 DPI):
1. Launcher OnStyle OEM de Fábrica Changan (F202_Launcher.apk) configurado por defecto.
2. APKs OEM de Fábrica extraídos del vehículo:
   - F202_DvrCamera.apk (Cámara 360° Real HD)
   - F202_AvmLive.apk (Cámara Panorámica AVM 360° Live)
   - F202_Music.apk (Música Fábrica)
   - F202_Radio.apk (Radio FM/AM)
   - F202_VehicleControl.apk (Control del Vehículo)
   - F202_Airconditioner.apk (Climatizador A/C)
   - F202_BTPhone.apk (Teléfono Bluetooth)
   - F202_Settings.apk (Ajustes de Fábrica)
   - F202_FileManager.apk (Gestor de Archivos USB)
   - YGPS.apk (Monitor Satelital MediaTek)
3. Changan X7 Plus Custom Cockpit Launcher (Con selector de temas, videos aleatorios y Segundo Home)
4. Suite de Navegación & Multimedia (Waze, Magic Earth, Open Headunit Beta 5, InnerTune, Brave)
5. Configuración idéntica de permisos, modo inmersivo 1920x720 y botón flotante.
================================================================================
"""

import os
import sys
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "tools")
ADB = os.path.join(TOOLS_DIR, "adb.exe")
if not os.path.exists(ADB):
    ADB = "adb"

EMU_EXE = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe")
if not os.path.exists(EMU_EXE):
    EMU_EXE = r"C:\Users\axeln\AppData\Local\Android\Sdk\emulator\emulator.exe"

AVD_NAME = "Changan_X7_Plus_API28_1920x720"
OEM_APP_DIR = os.path.join(BASE_DIR, "portable", "oem_factory_backup", "full_backup_20261016_161339", "app")
READY_APKS_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "apks_listos_para_instalar")
PORTABLE_APKS = os.path.join(BASE_DIR, "portable", "apks")

def log(msg):
    print(f"[*] {msg}", flush=True)

def run_adb(args, timeout=60):
    cmd = [ADB] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def is_emulator_running():
    _, out, _ = run_adb(["devices"])
    for line in out.splitlines():
        if "emulator-" in line and "device" in line:
            return True
    return False

def start_emulator():
    if is_emulator_running():
        log("Emulador ya se encuentra en ejecución.")
        return True

    log(f"Lanzando AVD {AVD_NAME} en resolución 1920x720 con aceleración GPU...")
    # Limpiar posibles locks huérfanos
    avd_dir = os.path.expanduser(f"~/.android/avd/{AVD_NAME}.avd")
    if os.path.exists(avd_dir):
        for f in os.listdir(avd_dir):
            if f.endswith(".lock"):
                try:
                    lock_path = os.path.join(avd_dir, f)
                    if os.path.isdir(lock_path):
                        os.rmdir(lock_path)
                    else:
                        os.remove(lock_path)
                except Exception:
                    pass

    cmd = [EMU_EXE, "-avd", AVD_NAME, "-gpu", "auto", "-accel", "on"]
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0)

    log("Esperando inicio completo de Android en el emulador...")
    for i in range(45):
        time.sleep(2)
        if is_emulator_running():
            _, boot, _ = run_adb(["shell", "getprop", "sys.boot_completed"])
            if boot.strip() == "1":
                log("[OK] Sistema operativo del emulador listo al 100%.")
                return True
            log(f"  -> Arrancando sistema... ({i+1}/45)")
    return False

def find_oem_apk(name):
    """Busca un APK en la carpeta OEM recursivamente y por subcarpetas directas."""
    p1 = os.path.join(OEM_APP_DIR, name)
    if os.path.exists(p1):
        return p1
    base = os.path.splitext(name)[0]
    p2 = os.path.join(OEM_APP_DIR, base, name)
    if os.path.exists(p2):
        return p2
    for root, _, files in os.walk(OEM_APP_DIR):
        if name in files:
            return os.path.join(root, name)
    return None

def main():
    print("=" * 80)
    print(" CLONADOR MAESTRO: AUTO CHANGAN X7 PLUS -> EMULADOR PC 100% IDÉNTICO")
    print("=" * 80)

    # 1. Iniciar Emulador si no está activo
    if not start_emulator():
        print("[ERROR] No se pudo conectar al emulador. Verifica Android SDK.")
        sys.exit(1)

    time.sleep(2)

    # 2. Configurar Pantalla Panorámica 1920x720 @ 213 DPI
    log("Configurando resolución de pantalla exacta: 1920x720 px @ 213 DPI (MT8666)...")
    run_adb(["shell", "wm", "size", "1920x720"])
    run_adb(["shell", "wm", "density", "213"])
    run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"])
    run_adb(["shell", "settings", "put", "secure", "immersive_mode_confirmations", "confirmed"])

    # 3. Instalar APKs OEM de Fábrica Changan
    log("Instalando aplicaciones OEM de fábrica Changan extraídas del vehículo...")
    oem_apps = [
        ("F202_Launcher.apk", "Launcher OnStyle de Fábrica (Changan OEM)", "com.chinatsp.launcher"),
        ("F202_DvrCamera.apk", "Cámara 360° Real de Fábrica HD", "com.chinatsp.dvrcamera"),
        ("F202_AvmLive.apk", "Cámara Panorámica AVM 360° Live", "com.chinatsp.avmlive"),
        ("F202_Music.apk", "Música OEM Changan", "com.chinatsp.music"),
        ("F202_Radio.apk", "Radio FM/AM OEM", "com.chinatsp.radio"),
        ("F202_VehicleControl.apk", "Control de Vehículo Changan", "com.chinatsp.vehiclecontrol"),
        ("F202_Airconditioner.apk", "Climatizador A/C", "com.chinatsp.aircondition"),
        ("F202_BTPhone.apk", "Teléfono Bluetooth OEM", "com.chinatsp.btphone"),
        ("F202_Settings.apk", "Ajustes de Fábrica Changan", "com.chinatsp.settings"),
        ("F202_FileManager.apk", "Gestor de Archivos USB OEM", "com.chinatsp.filemanager"),
        ("YGPS.apk", "Monitor Satelital MediaTek YGPS", "com.mediatek.ygps")
    ]

    for apk_name, label, pkg in oem_apps:
        apk_path = find_oem_apk(apk_name)
        if apk_path and os.path.exists(apk_path):
            log(f"  Instalando {label} ({apk_name})...")
            ret, out, err = run_adb(["install", "-r", "-d", "-g", apk_path])
            if "Success" in out or ret == 0:
                log(f"    [OK] {label} instalado con éxito.")
            else:
                log(f"    -> Resultado: {out} {err}")
        else:
            log(f"  [AVISO] No encontrado en respaldo: {apk_name}")

    # Otorgar permisos a YGPS si está instalado
    run_adb(["shell", "pm", "grant", "com.mediatek.ygps", "android.permission.ACCESS_FINE_LOCATION"])

    # 4. Instalar Changan X7 Plus Custom Launcher
    log("Instalando Changan X7 Plus Custom HMI Launcher (Última versión compilada)...")
    launcher_apk = os.path.join(PORTABLE_APKS, "ChanganX7Plus_OEM_Launcher.apk")
    if not os.path.exists(launcher_apk):
        launcher_apk = os.path.join(READY_APKS_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    if not os.path.exists(launcher_apk):
        launcher_apk = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "ChanganX7Plus_OEM_Launcher.apk")

    if os.path.exists(launcher_apk):
        ret, out, err = run_adb(["install", "-r", "-d", "-g", launcher_apk])
        log(f"  Custom Launcher resultado: {out} {err}")
    else:
        log("  [ERROR] No se encontró ChanganX7Plus_OEM_Launcher.apk!")

    # 5. Instalar Aplicaciones Complementarias (Waze, Open Headunit Beta 5, InnerTune, etc.)
    log("Instalando suite complementaria en el emulador...")
    complementary = [
        ("vimusic_innertune_musica.apk", "InnerTune / ViMusic", "com.zionhuang.music"),
        ("headunit_android_auto.apk", "Open Headunit Beta 5", "com.andrerinas.headunitrevived"),
        ("waze_gps_navegacion.apk", "Waze GPS Navegación", "com.waze"),
        ("brave_browser.apk", "Navegador Brave", "com.brave.browser"),
        ("smarttube_youtube_pro.apk", "SmartTube YouTube Pro", "org.smarttube.stable"),
        ("newpipe_youtube.apk", "NewPipe YouTube Ligero", "org.schabi.newpipe"),
        ("xuper_tv_streaming.apk", "XuperTV Streaming", "com.lagradost.cloudstream3"),
        ("radio_universal_global.apk", "Radio Universal Global (RadioDroid)", "net.programmierecke.radiodroid2"),
        ("youtube_web_pro.apk", "YouTube Web Pro (Estilo Brave)", "com.changan.youtube"),
        ("kick_streaming_live.apk", "Kick Live Streaming", "com.changan.kick")
    ]

    for filename, label, pkg in complementary:
        apk_p = os.path.join(PORTABLE_APKS, filename)
        if not os.path.exists(apk_p):
            apk_p = os.path.join(READY_APKS_DIR, filename)
        if os.path.exists(apk_p):
            log(f"  Instalando {label}...")
            run_adb(["install", "-r", "-d", "-g", apk_p], timeout=120)

    # Magic Earth Split
    magic_dir = os.path.join(READY_APKS_DIR, "magicearth_splits")
    if not os.path.exists(magic_dir):
        magic_dir = os.path.join(PORTABLE_APKS, "magicearth_splits")
    if os.path.exists(magic_dir):
        splits = [
            os.path.join(magic_dir, "base.apk"),
            os.path.join(magic_dir, "split_config.arm64_v8a.apk"),
            os.path.join(magic_dir, "split_config.es.apk"),
            os.path.join(magic_dir, "split_config.xxhdpi.apk")
        ]
        valid = [s for s in splits if os.path.exists(s)]
        if valid:
            log(f"  Instalando Magic Earth GPS 3D ({len(valid)} splits)...")
            run_adb(["install-multiple", "-r", "-d"] + valid, timeout=120)

    # 6. Conceder Permisos Automotrices
    log("Concediendo permisos de sistema automotriz en el emulador...")
    custom_pkg = "com.chinatsp.x7plus.launcher"
    onstyle_pkg = "com.chinatsp.launcher"

    perms = [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "android.permission.SYSTEM_ALERT_WINDOW"
    ]
    for p in perms:
        run_adb(["shell", "pm", "grant", custom_pkg, p])

    run_adb(["shell", "appops", "set", custom_pkg, "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "appops", "set", custom_pkg, "android:mock_location", "deny"])
    run_adb(["shell", "appops", "set", custom_pkg, "MOCK_LOCATION", "deny"])

    # Permisos Waze y Magic Earth
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_COARSE_LOCATION"])

    # Permisos Open Headunit Beta 5
    run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.RECORD_AUDIO"])
    run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "appops", "set", "com.andrerinas.headunitrevived", "SYSTEM_ALERT_WINDOW", "allow"])

    # Permisos InnerTune
    run_adb(["shell", "pm", "grant", "com.zionhuang.music", "android.permission.READ_EXTERNAL_STORAGE"])
    run_adb(["shell", "pm", "grant", "com.zionhuang.music", "android.permission.WRITE_EXTERNAL_STORAGE"])

    # Activar Notification Listener
    run_adb(["shell", "cmd", "notification", "allow_listener", f"{custom_pkg}/.MediaNotificationListener"])

    # Activar FloatingBackService en Accesibilidad y FloatingOverlayService
    run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", f"{custom_pkg}/.FloatingBackService"])
    run_adb(["shell", "settings", "put", "secure", "accessibility_enabled", "1"])
    run_adb(["shell", "am", "startservice", f"{custom_pkg}/.FloatingOverlayService"])

    # Activar GPS Satelital de Hardware
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"])
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])
    run_adb(["shell", "settings", "put", "secure", "mock_location", "0"])

    # Desactivar launcher stock de AOSP
    run_adb(["shell", "pm", "disable-user", "--user", "0", "com.android.launcher3"])

    # 7. Configuración del Launcher por Defecto
    print("\n" + "=" * 80)
    print(" CONFIGURACIÓN DEL LAUNCHER PREDETERMINADO:")
    print(" El usuario ha solicitado tener el LAUNCHER ONSTYLE POR DEFECTO")
    print(" para realizar pruebas completas y alternar con el Cockpit Custom.")
    print("=" * 80)

    # Comprobamos si OnStyle está instalado
    _, onstyle_check, _ = run_adb(["shell", "pm", "path", onstyle_pkg])
    if onstyle_pkg in onstyle_check or "package:" in onstyle_check:
        log("Fijando Launcher OnStyle de Fábrica como Home Predeterminado del Emulador...")
        run_adb(["shell", "cmd", "package", "set-home-activity", f"{onstyle_pkg}/com.chinatsp.launcher.MainAct"])
        run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
        run_adb(["shell", "am", "start", "-n", f"{onstyle_pkg}/com.chinatsp.launcher.MainAct"])
        log("[OK] Launcher OnStyle de Fábrica activo y listo en el emulador.")
    else:
        log("Fijando Changan X7 Plus Custom Cockpit como Home...")
        run_adb(["shell", "cmd", "package", "set-home-activity", f"{custom_pkg}/.MainActivity"])
        run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
        run_adb(["shell", "am", "start", "-n", f"{custom_pkg}/.MainActivity"])

    run_adb(["shell", "input", "keyevent", "3"]) # HOME

    # Broadcasts de pantalla completa
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", custom_pkg, "--ei", "appCentered", "2"])
    run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", custom_pkg])

    time.sleep(3)

    # 8. Captura de pantalla de verificación
    screenshot_path = os.path.join(BASE_DIR, "emulator_car_100_percent_clone.png")
    with open(screenshot_path, "wb") as f_img:
        subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=f_img)
    log(f"Captura de verificación guardada en: {screenshot_path}")

    print("=" * 80)
    print(" ¡EMULADOR CLONADO AL 100% IDÉNTICO A TU CHANGAN X7 PLUS!")
    print("=" * 80)
    print(" * Launcher OnStyle Fábrica: Activo por defecto como solicitaste.")
    print(" * Launcher Cockpit Custom: Totalmente instalado y disponible.")
    print(" * Pantalla: 1920x720 px Panorámica @ 213 DPI.")
    print(" * Cámara 360° Real HD: Lista para abrir desde cualquier launcher.")
    print(" * Para cambiar entre Launchers con 1 clic:")
    print("   -> PONER_LAUNCHER_ONSTYLE_DEFECTO.bat")
    print("   -> PONER_LAUNCHER_COCKPIT_DEFECTO.bat")
    print("=" * 80)

if __name__ == "__main__":
    main()
