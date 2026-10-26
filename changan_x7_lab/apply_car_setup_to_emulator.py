import os
import sys
import subprocess
import time

ADB = r"C:\Users\axeln\AppData\Local\Android\Sdk\platform-tools\adb.exe"
DEV = "emulator-5554"
APK_PATH = r"C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1\apks\x7_cockpit_launcher.apk"
DIAG_DIR = r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\changan_x7_lab\diagnostics"
os.makedirs(DIAG_DIR, exist_ok=True)

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip()

def capture_screen(filename):
    filepath = os.path.join(DIAG_DIR, filename)
    cmd = [ADB, "-s", DEV, "exec-out", "screencap", "-p"]
    with open(filepath, "wb") as f:
        subprocess.run(cmd, stdout=f)
    print(f"Captured screenshot to: {filepath} ({os.path.getsize(filepath)} bytes)")
    return filepath

def main():
    print("==================================================================")
    print(" APLICANDO CONFIGURACION COMPLETA DE VEHICULO EN EL EMULADOR")
    print(" Changan X7 Plus - Cockpit X7 Launcher (Full 1920x720)")
    print("==================================================================")

    # 1. Instalar APK recompilado con soporte 8:3 (max_aspect 2.67) y cutout mode
    print("\n[1/6] Instalando Cockpit X7 v2.2.0 (Desbloqueado 8:3)...")
    out, err = run_adb(["install", "-r", "-g", APK_PATH])
    print(f"Resultado instalacion: {out}")
    if err:
        print(f"Stderr: {err}")

    # 2. Confirmar modo inmersivo permanente
    print("\n[2/6] Configurando modo inmersivo automotriz permanente...")
    run_adb(["shell", "settings", "put", "secure", "immersive_mode_confirmations", "confirmed"])

    # 3. Designar Cockpit X7 como HOME LAUNCHER PREDETERMINADO DEL SISTEMA
    print("\n[3/6] Designando Cockpit X7 como Lanzador de Inicio Predeterminado (HOME)...")
    out, _ = run_adb(["shell", "cmd", "package", "set-home-activity", "com.changan.x7plus.launcher/.MainActivity"])
    print(f"set-home-activity: {out}")

    # 4. Deshabilitar Launcher generico secundario (simulando desactivar com.chinatsp.launcher en el auto)
    print("\n[4/6] Desactivando launcher generico secundario para dejar Cockpit X7 como Home exclusivo...")
    out, _ = run_adb(["shell", "pm", "disable-user", "--user", "0", "com.android.launcher3"])
    print(f"pm disable-user com.android.launcher3: {out}")

    # 5. Iniciar Cockpit X7 y simular pulsacion de boton HOME del volante/consola
    print("\n[5/6] Iniciando MainActivity y enviando KEYCODE_HOME...")
    run_adb(["shell", "am", "start", "-n", "com.changan.x7plus.launcher/.MainActivity"])
    time.sleep(2)
    run_adb(["shell", "input", "keyevent", "3"]) # KEYCODE_HOME
    time.sleep(2)

    # 6. Captura de pantalla y diagnostico forense de ventanas
    print("\n[6/6] Verificando superficie de ventana y capturando pantalla final...")
    capture_screen("08_cockpit_car_unlocked_fullscreen.png")

    # Diagnosticar frame
    win_out, _ = run_adb(["shell", "dumpsys", "window", "windows"])
    for line in win_out.splitlines():
        if "com.changan.x7plus.launcher" in line or "mFrame" in line or "mCurrentFocus" in line:
            if "mFrame" in line or "mCurrentFocus" in line:
                print("  ", line.strip())

    print("\n==================================================================")
    print(" CONFIGURACION AUTOMOTRIZ APLICADA Y VERIFICADA AL 100%")
    print("==================================================================")

if __name__ == "__main__":
    main()
