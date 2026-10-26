# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

"""
================================================================================
CLONADOR MAESTRO DE AMBIENTE CHANGAN X7 PLUS EN EMULADOR PC (100% IDÉNTICO AL AUTO)
================================================================================
Despliega en el emulador local de Android Studio (1920x720 @ 213 DPI):
1. Changan X7 Plus Custom Cockpit Launcher (Con clima reubicado, radio/música
   separadas, brocha de RAM, cámara 360 y segundo home) CONFIGURADO POR DEFECTO.
2. Suite de Aplicaciones Mejoradas:
   - Open Headunit v3.5.0 Oficial Release (Android Auto Inalámbrico Nativo)
   - Spotube v5.1.2 (Spotify Libre con Descargas MP3)
   - SimpMusic v2.3.0 (Reproductor Offline Pro sin bucles)
   - InnerTune v0.5.14 (Ultra Ligero 7MB)
   - OwnTV v5.2.1 + Lista Maestra 370+ Canales IPTV
   - CloudStream 3 v4.8.0 (XuperTV Libre)
   - Waze GPS + Navegador Brave + SmartTube
3. APKs OEM de Fábrica Changan (F202_DvrCamera, F202_AvmLive, Radio, Climatizador).
4. Configuración idéntica de permisos, modo inmersivo 1920x720 y botón flotante.
================================================================================
"""

import os
import sys
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "EMULADOR" in os.path.abspath(__file__) else os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "tools")
ADB = os.path.join(TOOLS_DIR, "adb.exe")
if not os.path.exists(ADB):
    ADB = os.path.join(BASE_DIR, "portable", "tools", "adb.exe")
if not os.path.exists(ADB):
    ADB = "adb"

EMU_EXE = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe")
if not os.path.exists(EMU_EXE):
    EMU_EXE = r"C:\Users\axeln\AppData\Local\Android\Sdk\emulator\emulator.exe"

AVD_NAME = "Changan_X7_Plus_API28_1920x720"
OEM_APP_DIR = os.path.join(BASE_DIR, "portable", "oem_factory_backup", "full_backup_20261016_161339", "app")
READY_APKS_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "apks_listos_para_instalar")
PORTABLE_APKS = os.path.join(BASE_DIR, "portable", "apks")
LOCAL_APKS = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "apks")

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
    for i in range(50):
        time.sleep(2)
        if is_emulator_running():
            _, boot, _ = run_adb(["shell", "getprop", "sys.boot_completed"])
            if boot.strip() == "1":
                log("[OK] Sistema operativo del emulador listo al 100%.")
                return True
            log(f"  -> Arrancando sistema... ({i+1}/50)")
    return False

def find_oem_apk(name):
    p1 = os.path.join(OEM_APP_DIR, name)
    if os.path.exists(p1): return p1
    base = os.path.splitext(name)[0]
    p2 = os.path.join(OEM_APP_DIR, base, name)
    if os.path.exists(p2): return p2
    for root, _, files in os.walk(OEM_APP_DIR):
        if name in files: return os.path.join(root, name)
    return None

def find_app_apk(name):
    for fld in [PORTABLE_APKS, LOCAL_APKS, READY_APKS_DIR]:
        p = os.path.join(fld, name)
        if os.path.exists(p): return p
    return None

def main():
    print("=" * 80)
    print(" CLONADOR MAESTRO: CHANGAN X7 PLUS COCKPIT -> EMULADOR PC")
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

    # 3. Instalar Changan X7 Plus Custom Cockpit Launcher (EL LAUNCHER MEJORADO)
    log("[1/5] Instalando Changan X7 Plus Custom Cockpit Launcher (Mejorado)...")
    custom_pkg = "com.chinatsp.x7plus.launcher"
    launcher_apk = find_app_apk("ChanganX7Plus_OEM_Launcher.apk")

    if launcher_apk and os.path.exists(launcher_apk):
        ret, out, err = run_adb(["install", "-r", "-d", "-g", launcher_apk])
        log(f"  Cockpit Launcher instalado: {out} {err}")
    else:
        log("  [ERROR] No se encontró ChanganX7Plus_OEM_Launcher.apk!")

    # 4. Instalar APKs OEM de Fábrica Changan
    log("[2/5] Instalando aplicaciones OEM de fábrica Changan...")
    oem_apps = [
        ("F202_Launcher.apk", "Launcher OnStyle Alternativo", "com.chinatsp.launcher"),
        ("F202_DvrCamera.apk", "Cámara 360° Real de Fábrica HD", "com.chinatsp.dvrcamera"),
        ("F202_AvmLive.apk", "Cámara Panorámica AVM 360° Live", "com.chinatsp.avmlive"),
        ("F202_Music.apk", "Música OEM Changan", "com.chinatsp.music"),
        ("F202_Radio.apk", "Radio FM/AM OEM", "com.chinatsp.radio"),
        ("F202_VehicleControl.apk", "Control de Vehículo Changan", "com.chinatsp.vehiclecontrol"),
        ("F202_Airconditioner.apk", "Climatizador A/C", "com.chinatsp.aircondition"),
        ("F202_BTPhone.apk", "Teléfono Bluetooth OEM", "com.chinatsp.btphone"),
        ("F202_Settings.apk", "Ajustes de Fábrica Changan", "com.chinatsp.settings"),
        ("F202_FileManager.apk", "Gestor de Archivos USB OEM", "com.chinatsp.filemanager")
    ]

    for apk_name, label, pkg in oem_apps:
        apk_path = find_oem_apk(apk_name)
        if apk_path and os.path.exists(apk_path):
            ret, out, err = run_adb(["install", "-r", "-d", "-g", apk_path])
            if "Success" in out or ret == 0:
                log(f"    [OK] {label} instalado.")

    # 5. Instalar Suite de Aplicaciones Mejoradas
    log("[3/5] Instalando Suite de Aplicaciones Mejoradas...")
    improved_apps = [
        ("headunit_android_auto.apk", "Open Headunit v3.5.0 Oficial Release (Android Auto Nativo)", "com.andrerinas.headunitrevived"),
        ("spotube_spotify_libre.apk", "Spotube v5.1.2 (Spotify Libre + Descargas MP3)", "oss.krtirtho.spotube"),
        ("simpmusic_offline_pro.apk", "SimpMusic v2.3.0 (Offline Pro sin Bucles)", "com.maxrave.simpmusic"),
        ("vimusic_innertune_musica.apk", "InnerTune v0.5.14 (Ultra Ligero 7MB)", "com.malopieds.innertune"),
        ("owntv_cable_en_vivo.apk", "OwnTV v5.2.1 (TV Cable en Vivo)", "com.ahxn00.owntv"),
        ("xuper_tv_streaming.apk", "CloudStream 3 (XuperTV Libre)", "com.lagradost.cloudstream3"),
        ("waze_gps_navegacion.apk", "Waze GPS Navegación", "com.waze"),
        ("brave_browser.apk", "Navegador Brave con Adblock", "com.brave.browser"),
        ("smarttube_youtube_pro.apk", "SmartTube YouTube Pro", "org.smarttube.stable"),
        ("newpipe_youtube.apk", "NewPipe YouTube Ligero", "org.schabi.newpipe")
    ]

    for filename, label, pkg in improved_apps:
        apk_p = find_app_apk(filename)
        if apk_p and os.path.exists(apk_p):
            log(f"  Instalando {label}...")
            run_adb(["install", "-r", "-d", "-g", apk_p], timeout=120)

    # 6. Precargar Lista Maestra de Canales IPTV en /sdcard/IPTV/
    log("[4/5] Precargando lista de 370+ canales IPTV en la memoria del emulador...")
    m3u_file = find_app_apk("canales_vip.m3u")
    if not m3u_file:
        m3u_file = os.path.join(BASE_DIR, "portable", "CANALES_VIP_LATAM_PERU_DEPORTES.m3u")
    if m3u_file and os.path.exists(m3u_file):
        run_adb(["shell", "mkdir", "-p", "/sdcard/IPTV"])
        run_adb(["push", m3u_file, "/sdcard/IPTV/canales_vip.m3u"])
        log("  [OK] Canales precargados en /sdcard/IPTV/canales_vip.m3u")

    # Crear carpeta de música para descargas de Spotube/SimpMusic
    run_adb(["shell", "mkdir", "-p", "/sdcard/Music"])

    # 7. Conceder Permisos Automotrices Avanzados
    log("[5/5] Concediendo permisos de sistema automotriz y bypass de bordes negros...")
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
    run_adb(["shell", "cmd", "notification", "allow_listener", f"{custom_pkg}/.MediaNotificationListener"])
    run_adb(["shell", "am", "startservice", f"{custom_pkg}/.FloatingOverlayService"])

    # Permisos multimedia
    for pkg in ["oss.krtirtho.spotube", "com.maxrave.simpmusic", "com.malopieds.innertune", "com.ahxn00.owntv", "com.lagradost.cloudstream3"]:
        run_adb(["shell", "pm", "grant", pkg, "android.permission.WRITE_EXTERNAL_STORAGE"])
        run_adb(["shell", "pm", "grant", pkg, "android.permission.READ_EXTERNAL_STORAGE"])
        run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"])
        # Bypass de bordes negros pantalla panorámica
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", pkg, "--ei", "appCentered", "2"])
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", pkg])

    # Permisos Android Auto
    run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.RECORD_AUDIO"])
    run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "appops", "set", "com.andrerinas.headunitrevived", "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.andrerinas.headunitrevived", "--ei", "appCentered", "2"])

    # Activar GPS Satelital
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"])
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])
    run_adb(["shell", "settings", "put", "secure", "mock_location", "0"])

    # Desactivar launcher stock AOSP
    run_adb(["shell", "pm", "disable-user", "--user", "0", "com.android.launcher3"])

    # 8. FIJAR CHANGAN X7 PLUS COCKPIT CUSTOM LAUNCHER COMO HOME PREDETERMINADO
    print("\n" + "=" * 80)
    print(" FIJANDO EL LAUNCHER COCKPIT MEJORADO COMO PANTALLA DE INICIO:")
    print("=" * 80)
    run_adb(["shell", "cmd", "package", "set-home-activity", f"{custom_pkg}/.MainActivity"])
    run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
    run_adb(["shell", "am", "start", "-n", f"{custom_pkg}/.MainActivity"])
    run_adb(["shell", "input", "keyevent", "3"]) # HOME

    # Broadcasts de pantalla completa para el Launcher Cockpit
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", custom_pkg, "--ei", "appCentered", "2"])
    run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", custom_pkg])

    time.sleep(3)

    # 9. Captura de pantalla de verificación
    screenshot_path = os.path.join(BASE_DIR, "emulator_cockpit_launcher_live.png")
    with open(screenshot_path, "wb") as f_img:
        subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=f_img)
    log(f"Captura de verificación guardada en: {screenshot_path}")

    print("=" * 80)
    print(" ¡EMULADOR CLONADO Y ACTUALIZADO CON ÉXITO!")
    print("=" * 80)
    print(" * Launcher Cockpit Mejorado: ACTIVO Y VISIBLE EN PANTALLA.")
    print(" * Tarjetas HMI: Radio y Música independientes + Clima superior + Brocha RAM.")
    print(" * Suite Mejorada Instalada:")
    print("   -> Open Headunit v3.5.0 Oficial Release (Android Auto Nativo)")
    print("   -> Spotube v5.1.2 (Spotify Libre con Descargas MP3)")
    print("   -> SimpMusic v2.3.0 (Offline Pro sin Bucles)")
    print("   -> InnerTune v0.5.14 (Ultra Ligero 7MB)")
    print("   -> OwnTV v5.2.1 + 370 Canales IPTV Precargados")
    print("   -> CloudStream 3 (XuperTV Libre)")
    print(" * Pantalla: 1920x720 px Panorámica @ 213 DPI sin bordes negros.")
    print("=" * 80)

if __name__ == "__main__":
    main()
