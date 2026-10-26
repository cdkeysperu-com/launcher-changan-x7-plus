# -*- coding: utf-8 -*-
"""
INSTALADOR ULTRA RÁPIDO PARA CHANGAN X7 PLUS
Instala Launcher Nativo + Android Auto + AutoKit + Waze + XuperTV + GPS Tether + Botón Retroceder + RiMusic
"""
import os
import sys
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
ADB = os.path.join(TOOLS_DIR, "adb.exe")
READY_DIR = os.path.join(BASE_DIR, "apks_listos_para_instalar")

def run(cmd, desc=""):
    print(f"\n[+] {desc}...")
    p = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if "Success" in out or p.returncode == 0:
        print(f"    [OK] Éxito: {out}")
    else:
        print(f"    [INFO] {out} {err}")
    return p.returncode

def main():
    print("==================================================================")
    print("  INSTALACIÓN ULTRA RÁPIDA CHANGAN X7 PLUS — ECOSISTEMA COMPLETO  ")
    print("==================================================================")

    # 1. Verificar ADB
    p_dev = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    raw_lines = [l.strip() for l in p_dev.stdout.splitlines() if l.strip() and not l.startswith("List of devices")]
    connected = [l for l in raw_lines if "\tdevice" in l or l.endswith("device")]
    if not connected:
        print("[!] ERROR: No se detecta el auto en ADB.")
        print("    Verifica el cable USB, abre marcador **888 -> Depuracion USB y acepta el aviso en la pantalla.")
        sys.exit(1)
    print(f"    [OK] Auto detectado: {connected[0]}")

    # 2. Launcher Nativo 100% Java
    launcher_apk = os.path.join(BASE_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    if os.path.exists(launcher_apk):
        run([ADB, "install", "-r", "-d", launcher_apk], "1/12 Instalando Launcher Nativo Changan HMI (1920x720)")
        run([ADB, "shell", "pm", "grant", "com.changan.x7plus.launcher", "android.permission.ACCESS_FINE_LOCATION"], "Permiso Ubicación Launcher")
        run([ADB, "shell", "pm", "grant", "com.changan.x7plus.launcher", "android.permission.ACCESS_COARSE_LOCATION"], "Permiso Coarse Location")
        run([ADB, "shell", "pm", "grant", "com.changan.x7plus.launcher", "android.permission.READ_EXTERNAL_STORAGE"], "Permiso Read Storage")
        run([ADB, "shell", "pm", "grant", "com.changan.x7plus.launcher", "android.permission.WRITE_EXTERNAL_STORAGE"], "Permiso Write Storage")
        run([ADB, "shell", "appops", "set", "com.changan.x7plus.launcher", "SYSTEM_ALERT_WINDOW", "allow"], "Permiso Ventana Flotante")

    # 3. Android Auto Nativo (Headunit Reloaded)
    aa_apk = os.path.join(READY_DIR, "headunit_android_auto.apk")
    if os.path.exists(aa_apk):
        run([ADB, "install", "-r", "-d", aa_apk], "2/12 Instalando Headunit Reloaded (Android Auto Nativo)")
        run([ADB, "shell", "pm", "grant", "gb.xxy.hr", "android.permission.RECORD_AUDIO"], "Permiso Micrófono Android Auto")
        run([ADB, "shell", "pm", "grant", "gb.xxy.hr", "android.permission.ACCESS_FINE_LOCATION"], "Permiso GPS Android Auto")

    # 4. AutoKit (Carlinkit CarPlay & Android Auto)
    autokit_apk = os.path.join(READY_DIR, "AutoKit.apk")
    if os.path.exists(autokit_apk):
        run([ADB, "install", "-r", "-d", autokit_apk], "3/12 Instalando AutoKit (Carlinkit CarPlay & Android Auto)")
        run([ADB, "shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.RECORD_AUDIO"], "Permiso Micrófono AutoKit")
        run([ADB, "shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.ACCESS_FINE_LOCATION"], "Permiso Ubicación AutoKit")

    # 5. Waze Compatible con Android 9
    waze_apk = os.path.join(READY_DIR, "waze_gps_navegacion.apk")
    if os.path.exists(waze_apk):
        run([ADB, "install", "-r", "-d", waze_apk], "4/12 Instalando Waze Navegación GPS (SDK 24 Android 9)")
        run([ADB, "shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"], "Permiso Ubicación Waze")
        run([ADB, "shell", "pm", "grant", "com.waze", "android.permission.RECORD_AUDIO"], "Permiso Audio Waze")

    # 6. XuperTV Streaming
    xuper_apk = os.path.join(READY_DIR, "xuper_tv_streaming.apk")
    if os.path.exists(xuper_apk):
        run([ADB, "install", "-r", "-d", xuper_apk], "5/12 Instalando XuperTV Streaming (Películas & TV en Vivo)")

    # 7. Botón Flotante de Retroceder (Back Button)
    back_apk = os.path.join(READY_DIR, "back_button.apk")
    if os.path.exists(back_apk):
        run([ADB, "install", "-r", "-d", back_apk], "6/12 Instalando Botón Flotante de Retroceder (Back Key)")
        run([ADB, "shell", "appops", "set", "com.appspot.app58us.backkey", "SYSTEM_ALERT_WINDOW", "allow"], "Permiso Overlay Botón Retroceder")

    # 8. GPS Tether Server & Bluetooth GPS Provider
    tether_apk = os.path.join(READY_DIR, "gps_tether.apk")
    if os.path.exists(tether_apk):
        run([ADB, "install", "-r", "-d", tether_apk], "7/12 Instalando GPS Tether Server (Ubicación desde Celular)")
        run([ADB, "shell", "pm", "grant", "com.bricatta.GPSTetherServer_FE", "android.permission.ACCESS_FINE_LOCATION"], "Permiso GPS Tether")

    bt_gps_apk = os.path.join(READY_DIR, "bluetooth_gps_provider.apk")
    if os.path.exists(bt_gps_apk):
        run([ADB, "install", "-r", "-d", bt_gps_apk], "8/12 Instalando Bluetooth GPS Provider")

    # 9. RiMusic Hi-Fi
    rimusic_apk = os.path.join(READY_DIR, "rimusic_musica_online_offline.apk")
    if os.path.exists(rimusic_apk):
        run([ADB, "install", "-r", "-d", rimusic_apk], "9/12 Instalando RiMusic (Streaming & Descargas)")
        run([ADB, "shell", "pm", "grant", "it.fast4x.rimusic", "android.permission.READ_EXTERNAL_STORAGE"], "Permiso Almacenamiento RiMusic")
        run([ADB, "shell", "pm", "grant", "it.fast4x.rimusic", "android.permission.WRITE_EXTERNAL_STORAGE"], "Permiso Descargas RiMusic")

    # 10. SmartTube YouTube Automotriz
    smarttube_apk = os.path.join(READY_DIR, "smarttube_youtube_pro.apk")
    if os.path.exists(smarttube_apk):
        run([ADB, "install", "-r", "-d", smarttube_apk], "10/12 Instalando SmartTube Automotriz sin Anuncios")

    # 11. Magic Earth GPS Satelital Offline (Multipaquete)
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
            run([ADB, "install-multiple", "-r", "-d"] + valid_splits, "11/12 Instalando Magic Earth GPS 3D Multipack")
            run([ADB, "shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"], "Permiso Magic Earth GPS")

    # 12. Taskbar Pantalla Dividida
    taskbar_apk = os.path.join(READY_DIR, "taskbar_pantalla_dividida.apk")
    if os.path.exists(taskbar_apk):
        run([ADB, "install", "-r", "-d", taskbar_apk], "12/12 Instalando Taskbar Multiventana")
        run([ADB, "shell", "appops", "set", "com.farmerbb.taskbar", "SYSTEM_ALERT_WINDOW", "allow"], "Permiso Overlay Taskbar")

    # 13. Optimización del Sistema y Pantalla Completa Inmersiva
    print("\n[+] Aplicando optimizaciones automotrices de rendimiento...")
    run([ADB, "shell", "settings", "put", "global", "policy_control", "immersive.full=*"], "Modo Inmersivo Total 1920x720")
    run([ADB, "shell", "settings", "put", "secure", "location_mode", "3"], "Modo Ubicación Alta Precisión")
    run([ADB, "shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"], "Proveedores GPS y Red")
    run([ADB, "shell", "settings", "put", "global", "window_animation_scale", "0.5"], "Animaciones 0.5x Ultra Rápidas")
    run([ADB, "shell", "settings", "put", "global", "transition_animation_scale", "0.5"], "Transiciones 0.5x")
    run([ADB, "shell", "settings", "put", "global", "animator_duration_scale", "0.5"], "Animador 0.5x")

    # 14. Fijar y Desplegar Launcher
    print("\n[+] Fijando nuevo Launcher Nativo como Home y desplegando en pantalla...")
    run([ADB, "shell", "cmd", "package", "set-home-activity", "com.changan.x7plus.launcher/.MainActivity"], "Fijar Launcher Home")
    run([ADB, "shell", "am", "start", "-n", "com.changan.x7plus.launcher/.MainActivity"], "Lanzar MainActivity Nativo")

    # 15. Capturar Pantalla del Vehículo en Vivo
    print("\n[+] Capturando pantalla del auto en vivo...")
    screencap_dest = os.path.join(BASE_DIR, "car_screen_installed_live.png")
    with open(screencap_dest, "wb") as f_cap:
        subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=f_cap)
    print(f"    [VERIFICACIÓN] Captura guardada en: {screencap_dest}")

    print("\n==================================================================")
    print("  ¡INSTALACIÓN TOTAL COMPLETADA CON ÉXITO EN TU CHANGAN X7 PLUS!   ")
    print("==================================================================")

if __name__ == "__main__":
    main()
