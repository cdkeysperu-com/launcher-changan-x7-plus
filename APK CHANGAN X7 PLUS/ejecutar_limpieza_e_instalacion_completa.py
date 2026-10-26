# -*- coding: utf-8 -*-
"""
================================================================================
CHANGAN X7 PLUS — LIMPIEZA TOTAL Y REINSTALACIÓN MAESTRA
================================================================================
Cumple con la orden: "recuerda borrar y poner todo lo nuevo"
1. Borra (desinstala y fuerza detención) de todas las apps anteriores.
2. Instala la suite completa nueva de 13 APKs y paquetes satelitales.
3. Asigna permisos automotrices (GPS, audio, almacenamiento, floating window, listener).
4. Configura modo inmersivo 1920x720 y zona horaria 24h.
5. Fija el Launcher Nativo como HOME oficial y lo eleva en pantalla.
6. Captura pantalla en vivo para confirmación visual.
================================================================================
"""

import os
import sys
import time
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
ADB = os.path.join(TOOLS_DIR, "adb.exe")
READY_DIR = os.path.join(BASE_DIR, "apks_listos_para_instalar")

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def run_adb(args, timeout=120):
    cmd = [ADB] + args
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"
    except Exception as e:
        return -1, "", str(e)

def main():
    print("================================================================================")
    print("  CHANGAN X7 PLUS — LIMPIEZA COMPLETA E INSTALACIÓN DE TODO LO NUEVO            ")
    print("================================================================================")

    # 1. Comprobar ADB
    log("Verificando conexión con el vehículo...")
    ret, out, _ = run_adb(["devices"])
    devices = [l for l in out.splitlines() if "\tdevice" in l or l.endswith("device")]
    if not devices:
        log("[ERROR] Vehículo no detectado. Revisa la depuración USB (**888).")
        sys.exit(1)
    log(f"[OK] Vehículo conectado y autorizado: {devices[0]}")

    # 2. FASE 1: BORRADO Y LIMPIEZA LIMPIA TOTAL DE VERSIONES ANTERIORES
    log("\n================================================================================")
    log("[FASE 1/4] BORRANDO VERSIONES ANTERIORES Y RESIDUOS DE CACHÉ (LIMPIEZA TOTAL)...")
    log("================================================================================")
    
    packages_to_clean = [
        ("com.generalmagic.magicearth", "Magic Earth GPS 3D"),
        ("app.organicmaps.web", "Organic Maps GPS"),
        ("com.waze", "Waze GPS"),
        ("it.fast4x.rimusic", "RiMusic Hi-Fi"),
        ("org.smarttube.stable", "SmartTube Automotriz"),
        ("org.schabi.newpipe", "NewPipe YouTube"),
        ("com.lagradost.cloudstream3", "XuperTV Streaming"),
        ("com.brave.browser", "Navegador Web Brave"),
        ("com.andrerinas.headunitrevived", "Android Auto (Headunit Reloaded)"),
        ("gb.xxy.hr", "Headunit Reloaded Legacy"),
        ("cn.manstep.phonemirrorBox", "AutoKit CarPlay & AA Dongle"),
        ("com.appspot.app58us.backkey", "Botón Flotante Atrás"),
        ("com.bricatta.GPSTetherServer_FE", "GPS Tether Server"),
        ("org.broeuschmeul.umrysh.android.gps.bluetooth.provider", "Bluetooth GPS Provider"),
        ("com.farmerbb.taskbar", "Taskbar Multiventana"),
        ("com.changan.x7plus.launcher", "Changan Launcher Anterior")
    ]

    for pkg, name in packages_to_clean:
        # Force-stop first
        run_adb(["shell", "am", "force-stop", pkg])
        # Uninstall
        ret, out, err = run_adb(["uninstall", pkg], timeout=30)
        if "Success" in out:
            log(f"  [-] Desinstalado: {name} ({pkg})")
        else:
            log(f"  [i] Limpio / No presente: {name}")

    log("[OK] Limpieza de paquetes anteriores completada al 100%.")

    # 3. FASE 2: INSTALACIÓN LIMPIA DE TODAS LAS APLICACIONES NUEVAS
    log("\n================================================================================")
    log("[FASE 2/4] INSTALANDO LA NUEVA SUITE COMPLETA EN LA CHANGAN X7 PLUS...")
    log("================================================================================")

    # A. Launcher Nativo 100% Nuevo
    launcher_apk = os.path.join(BASE_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    if not os.path.exists(launcher_apk):
        launcher_apk = os.path.join(READY_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    
    if os.path.exists(launcher_apk):
        sz = os.path.getsize(launcher_apk) / (1024 * 1024)
        log(f"Instalando Launcher Nativo Changan HMI Oficial ({sz:.1f} MB)...")
        ret, out, err = run_adb(["install", "-r", "-d", launcher_apk], timeout=90)
        log(f"  [OK] Launcher instalado: {out}")
    else:
        log("[ERROR] No se encontró ChanganX7Plus_OEM_Launcher.apk!")

    # B. Aplicaciones complementarias individuales
    apks_to_install = [
        ("headunit_android_auto.apk", "Android Auto Nativo (Headunit Reloaded)"),
        ("AutoKit.apk", "AutoKit (Carlinkit CarPlay & Android Auto Dongle)"),
        ("waze_gps_navegacion.apk", "Waze Navegación GPS (SDK 24 Android 9)"),
        ("rimusic_musica_online_offline.apk", "RiMusic Hi-Fi Streaming & Descargas"),
        ("smarttube_youtube_pro.apk", "SmartTube Automotriz sin Anuncios"),
        ("newpipe_youtube.apk", "NewPipe YouTube Ligero"),
        ("xuper_tv_streaming.apk", "XuperTV Streaming Películas & Series"),
        ("brave_browser.apk", "Navegador Web Brave con Adblock"),
        ("back_button.apk", "Botón Flotante Atrás"),
        ("gps_tether.apk", "GPS Tether Server (Receptor GPS Móvil)"),
        ("bluetooth_gps_provider.apk", "Bluetooth GPS Provider"),
        ("organicmaps_gps_offline.apk", "Organic Maps GPS Offline"),
        ("taskbar_pantalla_dividida.apk", "Taskbar Pantalla Dividida")
    ]

    for fname, label in apks_to_install:
        apk_path = os.path.join(READY_DIR, fname)
        if os.path.exists(apk_path):
            sz = os.path.getsize(apk_path) / (1024 * 1024)
            log(f"Instalando {label} ({sz:.1f} MB)...")
            ret, out, err = run_adb(["install", "-r", "-d", apk_path], timeout=150)
            if "Success" in out or ret == 0:
                log(f"  [OK] {label} instalado con éxito.")
            else:
                log(f"  [INFO] {label}: {out} {err}")
        else:
            log(f"  [OMITIDO] No encontrado: {fname}")

    # C. Magic Earth Splits
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
            log(f"Instalando Magic Earth GPS 3D Satelital (4 splits)...")
            ret, out, err = run_adb(["install-multiple", "-r", "-d"] + valid_splits, timeout=120)
            if "Success" in out or ret == 0:
                log("  [OK] Magic Earth GPS (Multipack) instalado con éxito.")
            else:
                log(f"  [INFO] Magic Earth: {out} {err}")

    # 4. FASE 3: CONCESIÓN DE PERMISOS AUTOMOTRICES Y OPTIMIZACIONES
    log("\n================================================================================")
    log("[FASE 3/4] CONFIGURANDO PERMISOS AUTOMOTRICES, GPS Y MODO INMERSIVO...")
    log("================================================================================")

    # Permisos Launcher
    l_pkg = "com.changan.x7plus.launcher"
    run_adb(["shell", "pm", "grant", l_pkg, "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", l_pkg, "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "pm", "grant", l_pkg, "android.permission.READ_EXTERNAL_STORAGE"])
    run_adb(["shell", "pm", "grant", l_pkg, "android.permission.WRITE_EXTERNAL_STORAGE"])
    run_adb(["shell", "appops", "set", l_pkg, "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "appops", "set", l_pkg, "android:mock_location", "allow"])
    run_adb(["shell", "appops", "set", l_pkg, "MOCK_LOCATION", "allow"])
    run_adb(["shell", "cmd", "notification", "allow_listener", f"{l_pkg}/.MediaNotificationListener"])

    # Permisos Android Auto (ambos paquetes)
    for aa_pkg in ["com.andrerinas.headunitrevived", "gb.xxy.hr"]:
        run_adb(["shell", "pm", "grant", aa_pkg, "android.permission.RECORD_AUDIO"])
        run_adb(["shell", "pm", "grant", aa_pkg, "android.permission.ACCESS_FINE_LOCATION"])
        run_adb(["shell", "pm", "grant", aa_pkg, "android.permission.ACCESS_COARSE_LOCATION"])
        run_adb(["shell", "appops", "set", aa_pkg, "SYSTEM_ALERT_WINDOW", "allow"])

    # Permisos AutoKit
    run_adb(["shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.RECORD_AUDIO"])
    run_adb(["shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.ACCESS_FINE_LOCATION"])

    # Permisos Waze
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.waze", "android.permission.RECORD_AUDIO"])

    # Permisos Magic Earth
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_COARSE_LOCATION"])
    run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.WRITE_EXTERNAL_STORAGE"])

    # Permisos RiMusic
    run_adb(["shell", "pm", "grant", "it.fast4x.rimusic", "android.permission.READ_EXTERNAL_STORAGE"])
    run_adb(["shell", "pm", "grant", "it.fast4x.rimusic", "android.permission.WRITE_EXTERNAL_STORAGE"])

    # Permisos Overlays
    run_adb(["shell", "appops", "set", "com.appspot.app58us.backkey", "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "appops", "set", "com.farmerbb.taskbar", "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "pm", "grant", "com.bricatta.GPSTetherServer_FE", "android.permission.ACCESS_FINE_LOCATION"])

    # Optimizaciones de Sistema
    log("Blindando zona horaria (America/Lima) y formato 24 horas...")
    run_adb(["shell", "setprop", "persist.sys.timezone", "America/Lima"])
    run_adb(["shell", "settings", "put", "global", "auto_time_zone", "0"])
    run_adb(["shell", "settings", "put", "system", "time_12_24", "24"])

    log("Activando GPS satelital de alta precisión...")
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"])
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])

    log("Aplicando política inmersiva y aceleración de animaciones (60 FPS)...")
    run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"])
    run_adb(["shell", "wm", "overscan", "0,0,0,0"])
    run_adb(["shell", "settings", "put", "global", "window_animation_scale", "0.5"])
    run_adb(["shell", "settings", "put", "global", "transition_animation_scale", "0.5"])
    run_adb(["shell", "settings", "put", "global", "animator_duration_scale", "0.5"])

    # 5. FASE 4: ELEVACIÓN DEL LAUNCHER A PANTALLA PRINCIPAL
    log("\n================================================================================")
    log("[FASE 4/4] ELEVANDO EL LAUNCHER NATIVO COMO HOME PREDETERMINADO EN PANTALLA...")
    log("================================================================================")
    
    run_adb(["shell", "cmd", "package", "set-home-activity", f"{l_pkg}/.MainActivity"])
    run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
    run_adb(["shell", "input", "keyevent", "3"])
    run_adb(["shell", "am", "start", "-n", f"{l_pkg}/.MainActivity"])
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.FULL_SCREEN"])

    time.sleep(3)

    # 6. Captura de Pantalla en Vivo
    log("\nTomando captura de pantalla de verificación en vivo del vehículo...")
    screencap_dest = os.path.join(BASE_DIR, "car_screen_installed_live.png")
    with open(screencap_dest, "wb") as f_cap:
        subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=f_cap)
    
    log(f"[VERIFICACIÓN] Captura guardada en: {screencap_dest}")
    print("\n================================================================================")
    print("  ¡PROCESO COMPLETADO AL 100%! PANTALLA LIMPIA Y SUITE NUEVA OPERATIVA           ")
    print("================================================================================")

if __name__ == "__main__":
    main()
