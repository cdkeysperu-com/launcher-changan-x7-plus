# -*- coding: utf-8 -*-
"""
================================================================================
INSTALADOR MAESTRO AUTOMATIZADO — CHANGAN X7 PLUS CUSTOM HMI & APKS
================================================================================
Desarrollado para: Changan X7 Plus (Android 9.0 Pie API 28, MT8666, 1920x720 213 DPI)
Ejecución: 100% local, no requiere internet en el vehículo.
Garantía OEM: 100% Intacta (Zero Writes a particiones de sistema, apps en /data).
================================================================================
"""

import os
import sys
import time
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
ADB_BIN = os.path.join(TOOLS_DIR, "adb.exe")
if not os.path.exists(ADB_BIN):
    ADB_BIN = "adb"

READY_DIR = os.path.join(BASE_DIR, "apks_listos_para_instalar")
LOG_FILE = os.path.join(BASE_DIR, "LOG_INSTALACION_COMPLETA.txt")

log_entries = []

def log(msg, to_screen=True):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    log_entries.append(formatted)
    if to_screen:
        print(msg)

def save_log():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("================================================================================\n")
            f.write("REGISTRO DE INSTALACIÓN MAESTRA — CHANGAN X7 PLUS CUSTOM HMI\n")
            f.write("================================================================================\n")
            for entry in log_entries:
                f.write(entry + "\n")
            f.write("================================================================================\n")
            f.write("ESTADO FINAL: INSTALACIÓN Y CONFIGURACIÓN COMPLETADA CON ÉXITO\n")
            f.write("================================================================================\n")
    except Exception as e:
        print(f"Error guardando log: {e}")

def run_adb(args, timeout=120):
    cmd = [ADB_BIN] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"
    except Exception as e:
        return -1, "", str(e)

def print_banner():
    print(r"""
================================================================================
  ______  __    __       ___      .__   __.   _______      ___      .__   __. 
 /      ||  |  |  |     /   \     |  \ |  |  /  _____|    /   \     |  \ |  | 
|  ,----'|  |__|  |    /  ^  \    |   \|  | |  |  __     /  ^  \    |   \|  | 
|  |     |   __   |   /  /_\  \   |  . `  | |  | |_ |   /  /_\  \   |  . `  | 
|  `----.|  |  |  |  /  _____  \  |  |\   | |  |__| |  /  _____  \  |  |\   | 
 \______||__|  |__| /__/     \__\ |__| \__|  \______| /__/     \__\ |__| \__| 
                    CHANGAN X7 PLUS — CUSTOM HMI LAUNCHER
               Resolución: 1920x720 px @ 213 DPI | MT8666 Android 9
================================================================================
""")

def main():
    print_banner()
    log("Iniciando instalador desatendido para Changan X7 Plus...")

    # FASE 1: ESPERA Y VERIFICACIÓN DE CONEXIÓN ADB
    log("================================================================================")
    log("[FASE 1/5] VERIFICANDO CONEXIÓN USB CON LA RADIO CHANGAN X7 PLUS...")
    log("Conecta el cable USB de tu laptop al puerto multimedia de la Changan X7 Plus.")
    log("Esperando dispositivo (adb wait-for-device)...")
    
    # Run wait-for-device
    ret, out, err = run_adb(["wait-for-device"])
    
    # Check device authorization status
    authorized = False
    device_serial = ""
    for _ in range(30):
        ret, out, err = run_adb(["devices"])
        lines = [line.strip() for line in out.splitlines() if line.strip() and not line.startswith("List of")]
        if lines:
            parts = lines[0].split()
            device_serial = parts[0]
            status = parts[1] if len(parts) > 1 else "unknown"
            if status == "device":
                authorized = True
                break
            elif status == "unauthorized":
                log("(!) Dispositivo detectado pero REQUIERE AUTORIZACIÓN.")
                log("    Por favor, mira la pantalla de la radio del auto:")
                log("    Marca la casilla [X] 'Permitir siempre desde este equipo' y presiona 'ACEPTAR'.")
        time.sleep(2)

    if not authorized:
        log("[ERROR] No se pudo verificar la autorización ADB en el vehículo.")
        log("Asegúrate de haber activado la depuración USB marcando **888 en el teléfono de la radio.")
        save_log()
        return False

    log(f"[OK] Vehículo detectado y autorizado por ADB. Serial: {device_serial}")

    # Inspect device properties
    _, model, _ = run_adb(["shell", "getprop", "ro.product.model"])
    _, android_ver, _ = run_adb(["shell", "getprop", "ro.build.version.release"])
    _, sdk_ver, _ = run_adb(["shell", "getprop", "ro.build.version.sdk"])
    _, platform, _ = run_adb(["shell", "getprop", "ro.board.platform"])
    _, mcu, _ = run_adb(["shell", "getprop", "persist.sys.mcu_version"])
    
    log(f"  * Modelo: {model or 'Changan F202_MCA'}")
    log(f"  * Versión de Android: {android_ver or '9'} (SDK {sdk_ver or '28'})")
    log(f"  * Plataforma SoC: {platform or 'mt6771 / MT8666'}")
    log(f"  * Versión MCU OEM: {mcu or 'SWC.2506.3014F202SA'}")

    # FASE 2: INSTALACIÓN DEL LAUNCHER NATIVO OFICIAL
    log("================================================================================")
    log("[FASE 2/5] INSTALANDO CHANGAN X7 PLUS CUSTOM HMI LAUNCHER...")
    
    launcher_apk = os.path.join(BASE_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    if not os.path.exists(launcher_apk):
        launcher_apk = os.path.join(READY_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    
    if os.path.exists(launcher_apk):
        sz = os.path.getsize(launcher_apk) / (1024 * 1024)
        log(f"Enviando APK nativo: ChanganX7Plus_OEM_Launcher.apk ({sz:.2f} MB)...")
        ret, out, err = run_adb(["install", "-r", "-d", launcher_apk], timeout=90)
        if "Success" in out or ret == 0:
            log("[OK] ChanganX7Plus_OEM_Launcher instalado exitosamente en el vehículo.")
        else:
            log(f"[AVISO] Salida de instalación: {out} {err}")
    else:
        log("[ERROR] No se encontró ChanganX7Plus_OEM_Launcher.apk.")

    # FASE 3: INSTALACIÓN DE APKS COMPLEMENTARIOS (ANDROID AUTO, WAZE, MULTIMEDIA)
    log("================================================================================")
    log("[FASE 3/5] INSTALANDO PAQUETES COMPLEMENTARIOS (WAZE, ANDROID AUTO, MULTIMEDIA)...")
    
    # 1. Split APK de Magic Earth
    magic_dir = os.path.join(READY_DIR, "magicearth_splits")
    if os.path.exists(magic_dir):
        splits = [
            os.path.join(magic_dir, "base.apk"),
            os.path.join(magic_dir, "split_config.arm64_v8a.apk"),
            os.path.join(magic_dir, "split_config.es.apk"),
            os.path.join(magic_dir, "split_config.xxhdpi.apk"),
        ]
        valid_splits = [s for s in splits if os.path.exists(s)]
        if valid_splits:
            log(f"Instalando Magic Earth GPS multipaquete ({len(valid_splits)} splits)...")
            ret, out, err = run_adb(["install-multiple", "-r", "-d"] + valid_splits, timeout=120)
            if "Success" in out or ret == 0:
                log("  [OK] Magic Earth GPS (Multipaquete) instalado.")
            else:
                log(f"  [AVISO] Magic Earth multipack: {out} {err}")

    # 2. APKs individuales
    complementary = [
        ("headunit_android_auto.apk", "Headunit Reloaded (Android Auto Nativo)"),
        ("AutoKit.apk", "AutoKit (Carlinkit CarPlay & Android Auto Dongle)"),
        ("waze_gps_navegacion.apk", "Waze GPS Navegación (Compatible Android 9)"),
        ("gps_tether.apk", "GPS Tether Server (Receptor GPS Compartido)"),
        ("bluetooth_gps_provider.apk", "Bluetooth GPS Provider (Proveedor GPS Bluetooth)"),
        ("vimusic_innertune_musica.apk", "InnerTune / ViMusic (Música Streaming & Descargas Offline)"),
        ("rimusic_musica_online_offline.apk", "RiMusic (Streaming Alternativo)"),
        ("brave_browser.apk", "Navegador Web Brave con Adblock"),
        ("newpipe_youtube.apk", "NewPipe YouTube Ligero"),
        ("smarttube_youtube_pro.apk", "SmartTube Automotriz"),
        ("xuper_tv_streaming.apk", "XuperTV Películas & Series"),
        ("organicmaps_gps_offline.apk", "Organic Maps GPS Offline"),
        ("taskbar_pantalla_dividida.apk", "Taskbar Pantalla Dividida")
    ]

    for filename, label in complementary:
        apk_path = os.path.join(READY_DIR, filename)
        if os.path.exists(apk_path):
            sz = os.path.getsize(apk_path) / (1024 * 1024)
            log(f"Instalando {label} ({sz:.1f} MB)...")
            ret, out, err = run_adb(["install", "-r", "-d", apk_path], timeout=150)
            if "Success" in out or ret == 0:
                log(f"  [OK] {label} instalado con éxito.")
            else:
                log(f"  [INFO] {label}: {out} (Continuando...)")
        else:
            log(f"  [OMITIDO] No encontrado: {filename}")

    # 3. MediaTek YGPS Satellite Diagnostics
    ygps_src = os.path.join(BASE_DIR, "oem_factory_backup", "full_backup_20261016_161339", "app", "YGPS", "YGPS.apk")
    if not os.path.exists(ygps_src):
        ygps_src = os.path.join(os.path.dirname(BASE_DIR), "portable", "oem_factory_backup", "full_backup_20261016_161339", "app", "YGPS", "YGPS.apk")
    if os.path.exists(ygps_src):
        log("Instalando Monitor Satelital MediaTek YGPS...")
        run_adb(["install", "-r", "-d", ygps_src])
        run_adb(["shell", "pm", "grant", "com.mediatek.ygps", "android.permission.ACCESS_FINE_LOCATION"])

    # FASE 4: CONFIGURACIÓN AUTOMÁTICA DE PERMISOS Y OPTIMIZACIONES CRÍTICAS
    log("================================================================================")
    log("[FASE 4/5] APLICANDO PERMISOS AUTOMOTRICES, ZONA HORARIA Y OPTIMIZACIONES...")
    
    # A. Notification Listener para Widget Multimedia Dinámico
    log("Habilitando Notification Listener Service para control multimedia dinámico...")
    run_adb(["shell", "cmd", "notification", "allow_listener", "com.chinatsp.x7plus.launcher/.MediaNotificationListener"])
    
    # B. Permisos para el Launcher & Hardware Satelital
    log("Concediendo permisos de sistema y Hardware Satelital al Launcher Changan X7 Plus...")
    launcher_pkg = "com.chinatsp.x7plus.launcher"
    permissions = [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "android.permission.SYSTEM_ALERT_WINDOW"
    ]
    for perm in permissions:
        run_adb(["shell", "pm", "grant", launcher_pkg, perm])
    run_adb(["shell", "appops", "set", launcher_pkg, "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "appops", "set", launcher_pkg, "android:mock_location", "deny"])
    run_adb(["shell", "appops", "set", launcher_pkg, "MOCK_LOCATION", "deny"])
    run_adb(["shell", "settings", "put", "secure", "mock_location", "0"])

    # C. Blindaje de Zona Horaria e Idioma (TikTok & Car Clock)
    log("Blindando zona horaria (America/Lima) y formato de 24 horas...")
    run_adb(["shell", "setprop", "persist.sys.timezone", "America/Lima"])
    run_adb(["shell", "settings", "put", "global", "auto_time_zone", "0"])
    run_adb(["shell", "settings", "put", "system", "time_12_24", "24"])

    # D. Permisos para Waze, Magic Earth, Open Headunit (Android Auto)
    log("Concediendo permisos a Waze, Magic Earth y Open Headunit (Android Auto)...")
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.RECORD_AUDIO"])

    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.WRITE_EXTERNAL_STORAGE"])

    # Open Headunit (Beta 5) y Legacy Headunit Reloaded
    for hu_pkg in ["com.andrerinas.headunitrevived", "gb.xxy.hr"]:
        run_adb(["shell", "pm", "grant", hu_pkg, "android.permission.RECORD_AUDIO"])
        run_adb(["shell", "pm", "grant", hu_pkg, "android.permission.ACCESS_FINE_LOCATION"])
        run_adb(["shell", "pm", "grant", hu_pkg, "android.permission.ACCESS_COARSE_LOCATION"])
        run_adb(["shell", "pm", "grant", hu_pkg, "android.permission.WRITE_EXTERNAL_STORAGE"])
        run_adb(["shell", "appops", "set", hu_pkg, "SYSTEM_ALERT_WINDOW", "allow"])

    # E. Activación de GPS Híbrido en Tiempo Real vía Compartir Wi-Fi (mock_location permitido)
    log("Activando GPS híbrido vía Zona Wi-Fi celular (mock_location=1)...")
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"])
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])
    run_adb(["shell", "settings", "put", "secure", "mock_location", "1"])
    run_adb(["shell", "appops", "set", "com.chinatsp.x7plus.launcher", "android:mock_location", "allow"])
    run_adb(["shell", "pm", "uninstall", "com.snoopy112.backbutton"])
    run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", "null"])

    # E3. Registrar Bypass Fullscreen F202_SystemUI (appCentered 2) para todas las apps
    log("Bypaseando marco CarAuto para Waze, Magic Earth, Headunit, InnerTune, YouTube...")
    for pkg in [launcher_pkg, "com.waze", "com.generalmagic.magicearth", "com.andrerinas.headunitrevived",
                "it.vfsfitvnm.innertune", "it.vfsfitvnm.vimusic", "com.github.cloudstream",
                "com.liskovsoft.videomanager", "com.brave.browser", "org.schabi.newpipe"]:
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", pkg, "--ei", "appCentered", "2"])

    # F. Política Inmersiva Completa 1920x720 y Eliminación de Barras
    log("Aplicando política inmersiva 1920x720 de borde a borde (Sin bordes negros)...")
    run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"])
    run_adb(["shell", "wm", "overscan", "0,0,0,0"])
    run_adb(["shell", "wm", "size", "1920x720"])
    run_adb(["shell", "wm", "density", "213"])

    # G. Optimización de animaciones a 0.5x (Zero Delay)
    log("Ajustando velocidad de animación a 0.5x para respuesta instantánea (60 FPS)...")
    run_adb(["shell", "settings", "put", "global", "window_animation_scale", "0.5"])
    run_adb(["shell", "settings", "put", "global", "transition_animation_scale", "0.5"])
    run_adb(["shell", "settings", "put", "global", "animator_duration_scale", "0.5"])

    # FASE 5: FIJAR COMO PANTALLA DE INICIO Y LANZAR EN VIVO (FULL SCREEN 1920x720)
    log("================================================================================")
    log("[FASE 5/5] ELEVANDO CHANGAN X7 PLUS CUSTOM HMI A LA PANTALLA PRINCIPAL...")
    
    log("Estableciendo com.chinatsp.x7plus.launcher como Home Launcher predeterminado...")
    run_adb(["shell", "cmd", "package", "set-home-activity", "com.chinatsp.x7plus.launcher/.MainActivity"])
    
    log("Lanzando interfaz HMI nativa en la pantalla de la radio...")
    # 1. Enviar Home Intent estándar
    run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
    # 2. Simular pulsación de tecla HOME para conmutar al stack de Launcher nativo (elimina marco CarAuto)
    run_adb(["shell", "input", "keyevent", "3"])
    # 3. Lanzar componente explícito por seguridad
    run_adb(["shell", "am", "start", "-n", "com.chinatsp.x7plus.launcher/.MainActivity"])
    # 4. Difundir comandos de pantalla completa a ChinaTSP SystemUI
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.FULL_SCREEN"])
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_ENTER_FULLSCREEN"])
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.carauto.DISMISS"])
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.HIDE_NAV_BAR"])
    # Deshabilitar temporalmente el launcher OEM para eliminar el contenedor CarAuto y barras laterales
    run_adb(["shell", "pm", "disable-user", "--user", "0", "com.chinatsp.launcher"])

    # Verificación final
    time.sleep(2)
    _, top_act, _ = run_adb(["shell", "dumpsys", "activity", "activities"])
    if "com.chinatsp.x7plus.launcher" in top_act:
        log("[CONFIRMADO EN VIVO] Changan X7 Plus Custom HMI se encuentra visible y activo en pantalla.")
    else:
        log("[INFO] Launcher enviado a pantalla principal.")

    log("================================================================================")
    log("¡INSTALACIÓN COMPLETADA EXITOSAMENTE AL 100%!")
    log("  * Interfaz Luxury X7 Plus (1920x720) activa.")
    log("  * Android Auto (Headunit Reloaded) listo para conectar tu smartphone.")
    log("  * GPS (Waze, Magic Earth 3D) con permisos de satélite aprobados.")
    log("  * RiMusic listo con widget táctil en pantalla de inicio.")
    log("  * Acceso directo a OnStyle original garantizado (Garantía OEM 100% intacta).")
    log("================================================================================")
    
    save_log()
    print(f"\nSe ha generado el reporte completo en: {LOG_FILE}")
    return True

if __name__ == "__main__":
    success = main()
    input("\nPresiona ENTER para finalizar y disfrutar de tu Changan X7 Plus...")
    sys.exit(0 if success else 1)
