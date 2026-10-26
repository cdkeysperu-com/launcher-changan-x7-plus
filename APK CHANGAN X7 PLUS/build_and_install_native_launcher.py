# -*- coding: utf-8 -*-
"""
Pipeline de Compilación, Empaquetado, Firma e Instalación del Launcher 100% Nativo
Changan X7 Plus Custom HMI (Android 9.0 API 28)
"""
import os
import sys
import subprocess
import zipfile
import shutil
import glob
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "launcher_android")
TOOLS_DIR = os.path.join(BASE_DIR, "tools")

AAPT2 = os.path.join(TOOLS_DIR, "aapt2.exe")
ANDROID_JAR = os.path.join(TOOLS_DIR, "android.jar")
R8_JAR = os.path.join(TOOLS_DIR, "r8.jar")
JAVAC = os.path.join(TOOLS_DIR, "jdk", "bin", "javac.exe")
JAVA = os.path.join(TOOLS_DIR, "jdk", "bin", "java.exe")
JARSIGNER = os.path.join(TOOLS_DIR, "jdk", "bin", "jarsigner.exe")
ADB = os.path.join(TOOLS_DIR, "adb.exe")

KEYSTORE = os.path.join(PROJECT_DIR, "release.keystore")
KEY_ALIAS = "changan_x7"
KEY_PASS = "changan2026"

RES_DIR = os.path.join(PROJECT_DIR, "res")
MANIFEST = os.path.join(PROJECT_DIR, "AndroidManifest.xml")
COMPILED_RES = os.path.join(PROJECT_DIR, "compiled_res.zip")
GEN_DIR = os.path.join(PROJECT_DIR, "gen")
CLASSES_DIR = os.path.join(PROJECT_DIR, "classes")
DEX_DIR = os.path.join(PROJECT_DIR, "dex")
BIN_DIR = os.path.join(PROJECT_DIR, "bin")

BASE_APK = os.path.join(BIN_DIR, "base.apk")
FINAL_APK = os.path.join(BASE_DIR, "ChanganX7Plus_OEM_Launcher.apk")

def run(cmd, desc):
    print(f"\n==> [PASO] {desc}")
    print("Comando:", " ".join(cmd) if isinstance(cmd, list) else cmd)
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if p.returncode != 0:
        print(f"ERROR en {desc}!")
        print("STDOUT:", p.stdout)
        print("STDERR:", p.stderr)
        sys.exit(1)
    if p.stdout.strip():
        print(p.stdout.strip())
    print(f"[OK] {desc} completado exitosamente.")

def main():
    print("==============================================================")
    print("  COMPILADOR NATIVO ANDROID: CHANGAN X7 PLUS CUSTOM HMI       ")
    print("==============================================================")

    # 1. Prepare directories
    for d in [GEN_DIR, CLASSES_DIR, DEX_DIR, BIN_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # 2. AAPT2 Compile Resources
    run([AAPT2, "compile", "--dir", RES_DIR, "-o", COMPILED_RES], "Compilar recursos XML y gráficos con AAPT2")

    # 3. AAPT2 Link to generate R.java and base APK
    run([
        AAPT2, "link",
        "-I", ANDROID_JAR,
        "--manifest", MANIFEST,
        "--java", GEN_DIR,
        "-o", BASE_APK,
        "--auto-add-overlay",
        COMPILED_RES
    ], "Enlazar APK y generar R.java con AAPT2")

    # 4. Java Compilation (javac)
    java_files = []
    for root, _, files in os.walk(os.path.join(PROJECT_DIR, "src")):
        for f in files:
            if f.endswith(".java"):
                java_files.append(os.path.join(root, f))
    for root, _, files in os.walk(GEN_DIR):
        for f in files:
            if f.endswith(".java"):
                java_files.append(os.path.join(root, f))

    print(f"Archivos Java a compilar ({len(java_files)}):", [os.path.basename(f) for f in java_files])
    javac_cmd = [
        JAVAC,
        "-encoding", "UTF-8",
        "-cp", ANDROID_JAR,
        "-d", CLASSES_DIR
    ] + java_files
    run(javac_cmd, "Compilar código fuente Java con OpenJDK javac")

    # 5. D8 Dex Compiler
    class_files = []
    for root, _, files in os.walk(CLASSES_DIR):
        for f in files:
            if f.endswith(".class"):
                class_files.append(os.path.join(root, f))

    print(f"Clases a convertir a DEX ({len(class_files)}):", [os.path.basename(f) for f in class_files])
    d8_cmd = [
        JAVA,
        "-cp", R8_JAR,
        "com.android.tools.r8.D8",
        "--output", DEX_DIR,
        "--lib", ANDROID_JAR,
        "--min-api", "21"
    ] + class_files
    run(d8_cmd, "Compilar Bytecode Java a Dalvik Executable (classes.dex) con D8")

    # 6. Assemble classes.dex into APK
    classes_dex = os.path.join(DEX_DIR, "classes.dex")
    if not os.path.exists(classes_dex):
        print("ERROR: No se encontró classes.dex!")
        sys.exit(1)

    unsigned_apk = os.path.join(BIN_DIR, "unsigned.apk")
    shutil.copy2(BASE_APK, unsigned_apk)

    # Use python zipfile to add classes.dex cleanly
    with zipfile.ZipFile(unsigned_apk, 'a', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(classes_dex, "classes.dex")
    print(f"[OK] classes.dex empaquetado en {unsigned_apk}")

    # 7. Sign APK with jarsigner using release.keystore with -signedjar
    signed_temp = os.path.join(BIN_DIR, "signed.apk")
    if os.path.exists(signed_temp):
        try:
            os.remove(signed_temp)
        except Exception:
            pass

    sign_cmd = [
        JARSIGNER,
        "-keystore", KEYSTORE,
        "-storepass", KEY_PASS,
        "-keypass", KEY_PASS,
        "-digestalg", "SHA-256",
        "-sigalg", "SHA256withRSA",
        "-signedjar", signed_temp,
        unsigned_apk,
        KEY_ALIAS
    ]
    run(sign_cmd, "Firmar APK con Keystore Changan Oficial")

    # Verify signature
    verify_cmd = [JARSIGNER, "-verify", signed_temp]
    run(verify_cmd, "Verificar firma digital del APK")

    time.sleep(1)
    if os.path.exists(FINAL_APK):
        try:
            os.remove(FINAL_APK)
        except Exception:
            pass
    shutil.copy2(signed_temp, FINAL_APK)

    # Copy to distribution paths
    portable_apk = os.path.join(os.path.dirname(BASE_DIR), "portable", "apks", "ChanganX7Plus_OEM_Launcher.apk")
    dist_paths = [
        os.path.join(BASE_DIR, "apks", "ChanganX7Plus_OEM_Launcher.apk"),
        portable_apk
    ]
    for dp in dist_paths:
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(FINAL_APK, dp)
        print(f"Copiado a: {dp}")

    apk_size_mb = os.path.getsize(FINAL_APK) / (1024 * 1024)
    print("\n==============================================================")
    print(f" ¡APK NATIVO COMPILADO Y FIRMADO CON ÉXITO! ({apk_size_mb:.2f} MB) ")
    print("==============================================================")

    # 8. Check vehicle ADB connection and Install Suite
    print("\nComprobando conexión ADB con el vehículo...")
    p_dev = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    print(p_dev.stdout.strip())

    has_device = any("device" in line and not line.startswith("List of") for line in p_dev.stdout.splitlines())

    if has_device:
        print("\n==> Instalando suite completa en Changan X7 Plus via ADB...")
        
        # 1. Launcher Nativo
        print("1. Instalando Launcher Nativo Changan X7 Plus...")
        subprocess.run([ADB, "install", "-r", "-d", FINAL_APK])
        subprocess.run([ADB, "shell", "pm", "grant", "com.chinatsp.x7plus.launcher", "android.permission.ACCESS_FINE_LOCATION"])
        subprocess.run([ADB, "shell", "pm", "grant", "com.chinatsp.x7plus.launcher", "android.permission.ACCESS_COARSE_LOCATION"])
        subprocess.run([ADB, "shell", "pm", "grant", "com.chinatsp.x7plus.launcher", "android.permission.READ_EXTERNAL_STORAGE"])
        subprocess.run([ADB, "shell", "pm", "grant", "com.chinatsp.x7plus.launcher", "android.permission.WRITE_EXTERNAL_STORAGE"])
        # GPS Real de Hardware: Activar alta precisión satelital nativa (Modo 3: GPS + Network + Sensores)
        subprocess.run([ADB, "shell", "settings", "put", "secure", "location_mode", "3"])
        subprocess.run([ADB, "shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])
        subprocess.run([ADB, "shell", "settings", "put", "secure", "mock_location", "0"])
        # Permisos nativos de ubicación satelital para Waze, Magic Earth y Launcher
        subprocess.run([ADB, "shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"], capture_output=True)
        subprocess.run([ADB, "shell", "pm", "grant", "com.waze", "android.permission.ACCESS_COARSE_LOCATION"], capture_output=True)
        subprocess.run([ADB, "shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"], capture_output=True)
        subprocess.run([ADB, "shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_COARSE_LOCATION"], capture_output=True)
        
        # 2. AutoKit (Carlinkit CarPlay & Android Auto)
        autokit_apk = os.path.join(BASE_DIR, "apks_listos_para_instalar", "AutoKit.apk")
        if os.path.exists(autokit_apk):
            print("2. Instalando AutoKit (Carlinkit Dongle)...")
            subprocess.run([ADB, "install", "-r", "-d", autokit_apk])
            subprocess.run([ADB, "shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.RECORD_AUDIO"])
            subprocess.run([ADB, "shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.ACCESS_FINE_LOCATION"])

        # 3. Android Auto Nativo (Headunit Reloaded)
        aa_apk = os.path.join(BASE_DIR, "apks_listos_para_instalar", "headunit_android_auto.apk")
        if os.path.exists(aa_apk):
            print("3. Instalando Android Auto (Headunit Reloaded)...")
            subprocess.run([ADB, "install", "-r", "-d", aa_apk])
            subprocess.run([ADB, "shell", "pm", "grant", "gb.xxy.hr", "android.permission.RECORD_AUDIO"])
            subprocess.run([ADB, "shell", "pm", "grant", "gb.xxy.hr", "android.permission.ACCESS_FINE_LOCATION"])

        # 4. Waze Compatible Android 9
        waze_apk = os.path.join(BASE_DIR, "apks_listos_para_instalar", "waze_gps_navegacion.apk")
        if os.path.exists(waze_apk):
            print("4. Instalando Waze Navegación GPS...")
            subprocess.run([ADB, "install", "-r", "-d", waze_apk])
            subprocess.run([ADB, "shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"])
            subprocess.run([ADB, "shell", "pm", "grant", "com.waze", "android.permission.RECORD_AUDIO"])

        # 5. XuperTV Streaming
        xuper_apk = os.path.join(BASE_DIR, "apks_listos_para_instalar", "xuper_tv_streaming.apk")
        if os.path.exists(xuper_apk):
            print("5. Instalando XuperTV Streaming...")
            subprocess.run([ADB, "install", "-r", "-d", xuper_apk])

        # 6. GPS Tether Server & Bluetooth GPS
        tether_apk = os.path.join(BASE_DIR, "apks_listos_para_instalar", "gps_tether.apk")
        if os.path.exists(tether_apk):
            print("6. Instalando GPS Tether Server...")
            subprocess.run([ADB, "install", "-r", "-d", tether_apk])
            subprocess.run([ADB, "shell", "pm", "grant", "com.bricatta.GPSTetherServer_FE", "android.permission.ACCESS_FINE_LOCATION"])

        bt_gps_apk = os.path.join(BASE_DIR, "apks_listos_para_instalar", "bluetooth_gps_provider.apk")
        if os.path.exists(bt_gps_apk):
            print("7. Instalando Bluetooth GPS Provider...")
            subprocess.run([ADB, "install", "-r", "-d", bt_gps_apk])

        # 7. Modo Inmersivo Fullscreen 1920x720 y Lanzamiento
        print("8. Activando modo inmersivo total 1920x720 (213 DPI) y fijando Launcher...")
        subprocess.run([ADB, "shell", "settings", "put", "global", "policy_control", "immersive.full=*"])
        subprocess.run([ADB, "shell", "wm", "overscan", "0,0,0,0"])
        subprocess.run([ADB, "shell", "wm", "size", "1920x720"])
        subprocess.run([ADB, "shell", "wm", "density", "213"])
        
        # Otorgar permiso de Notification Listener para el widget de música
        subprocess.run([ADB, "shell", "cmd", "notification", "allow_listener", 
                        "com.chinatsp.x7plus.launcher/.MediaNotificationListener"], capture_output=True)
        subprocess.run([ADB, "shell", "cmd", "notification", "allow_listener", 
                        "com.chinatsp.x7plus.launcher/com.chinatsp.x7plus.launcher.MediaNotificationListener"], capture_output=True)
        
        # Desbloqueo F202_SystemUI (Bypass verificado en Dalvik Bytecode)
        print("9. Transmitiendo Broadcasts de Desbloqueo Nativo F202_SystemUI...")
        subprocess.run([ADB, "shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", 
                        "--es", "packageName", "com.chinatsp.x7plus.launcher", "--ei", "appCentered", "2"])
        subprocess.run([ADB, "shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR",
                        "--es", "packageName", "com.chinatsp.x7plus.launcher"])
        subprocess.run([ADB, "shell", "am", "broadcast", "-a", "com.chinatsp.activity.onpostresume",
                        "--es", "packageName", "com.chinatsp.x7plus.launcher"])
        
        # Establecer como Home Launcher y arrancar
        subprocess.run([ADB, "shell", "cmd", "package", "set-home-activity", "com.chinatsp.x7plus.launcher/.MainActivity"])
        subprocess.run([ADB, "shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
        subprocess.run([ADB, "shell", "am", "start", "-n", "com.chinatsp.x7plus.launcher/.MainActivity"])

        print("[ÉXITO TOTAL] ¡Launcher nativo y aplicaciones desplegadas en el vehículo!")
        
        # Tomar captura de pantalla de verificación
        print("==> Capturando pantalla del auto en vivo...")
        screencap_dest = os.path.join(BASE_DIR, "car_screen_native_live.png")
        with open(screencap_dest, "wb") as f_cap:
            subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=f_cap)
        print(f"[VERIFICACIÓN] Captura guardada en: {screencap_dest}")
    else:
        print("Vehículo en espera. Por favor conecta el cable USB y ejecuta INSTALAR_TODO_EN_EL_AUTO.bat")

if __name__ == "__main__":
    main()
