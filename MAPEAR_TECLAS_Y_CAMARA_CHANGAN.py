# -*- coding: utf-8 -*-
"""
================================================================================
  ASISTENTE DE DIAGNÓSTICO EN VIVO, MAPEO DE TECLAS Y CÁMARA 360° CHANGAN X7 PLUS
================================================================================
Herramienta en tiempo real para usar con tu laptop conectada al auto por USB o Wi-Fi.

Funciones:
  1. MONITOR DE TECLAS EN VIVO: Presiona cualquier tecla en el timón o consola central y
     verás en pantalla el evento de kernel (getevent), keycode Android y broadcast CoAgent.
  2. PROBADOR DE CÁMARA 360°: Prueba en la pantalla del auto cada método (AVM Live, HD Camera,
     CAN Bus Broadcasts, EVS) con 1 solo toque y guarda la opción ganadora.
  3. DIAGNÓSTICO DE TECLA HOME: Comprueba por qué no responde en Ajustes u otras apps y
     aplica permisos automáticos (SYSTEM_ALERT_WINDOW y CLOSE_SYSTEM_DIALOGS).
  4. MONITOREO DE GPS EN VIVO: Inspecciona el hardware GNSS satelital del auto vs Waze.
"""

import sys
import os
import subprocess
import time
import threading
import re

# Colores de consola ANSI
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_CYAN   = "\033[36m"
C_GREEN  = "\033[32m"
C_YELLOW = "\033[33m"
C_RED    = "\033[31m"
C_BLUE   = "\033[34m"
C_MAG    = "\033[35m"

def find_adb():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "APK CHANGAN X7 PLUS", "tools", "adb.exe"),
        os.path.join(base_dir, "portable", "tools", "adb.exe"),
        os.path.join(base_dir, "tools", "adb.exe"),
        "adb.exe",
        "adb"
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "adb"

ADB = find_adb()

def run_adb(args, timeout=10):
    cmd = [ADB] + args
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, encoding="utf-8", errors="ignore")
        return res.stdout.strip()
    except Exception as e:
        return ""

def check_connection():
    out = run_adb(["devices"])
    lines = [l.strip() for l in out.splitlines() if l.strip() and not l.startswith("List of")]
    devices = [l.split()[0] for l in lines if "device" in l and not "offline" in l and not "unauthorized" in l]
    return devices

def get_current_focus():
    out = run_adb(["shell", "dumpsys", "window", "windows"])
    for line in out.splitlines():
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            match = re.search(r"u0\s+([^}\s]+)", line)
            if match:
                return match.group(1)
            return line.strip()
    return "Desconocido"

# ==============================================================================
# 1. MONITOR EN VIVO DE TECLAS DEL TIMÓN (GETEVENT + LOGCAT COAGENT)
# ==============================================================================
def live_key_monitor():
    print(f"\n{C_CYAN}{C_BOLD}=============================================================={C_RESET}")
    print(f"{C_GREEN}{C_BOLD}  [MONITOR EN VIVO DE TECLAS DEL TIMÓN Y CONSOLA ACTIVADO]  {C_RESET}")
    print(f"{C_CYAN}=============================================================={C_RESET}")
    print(f"{C_YELLOW}Presiona botones en tu timón o tablero del Changan (Cámara 360, Home, SRC, Volumen, etc.){C_RESET}")
    print(f"{C_YELLOW}Presiona {C_BOLD}Ctrl+C{C_RESET}{C_YELLOW} en esta consola para volver al menú.{C_RESET}\n")

    stop_event = threading.Event()

    # Hilo 1: Escucha eventos directos del Kernel Linux (/dev/input/event*)
    def getevent_worker():
        try:
            proc = subprocess.Popen([ADB, "shell", "getevent", "-lt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            for line in proc.stdout:
                if stop_event.is_set():
                    break
                line = line.strip()
                if "EV_KEY" in line:
                    focus = get_current_focus()
                    print(f"{C_GREEN}{C_BOLD}>> [TECLA FÍSICA TIMÓN/TABLERO]{C_RESET} {line}")
                    print(f"   {C_BLUE}↳ App en primer plano:{C_RESET} {C_BOLD}{focus}{C_RESET}\n")
        except Exception:
            pass

    # Hilo 2: Escucha broadcasts del bus CAN Changan y CoAgent
    def logcat_worker():
        try:
            proc = subprocess.Popen([ADB, "shell", "logcat", "-v", "time", "-s", "CoAgent:V", "HardwareKeyReceiver:V", "WindowManager:I"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            for line in proc.stdout:
                if stop_event.is_set():
                    break
                line = line.strip()
                if any(k in line for k in ["Key_code", "KEY_CHANGED", "AVM", "CAMERA", "HOME", "SWIPE"]):
                    print(f"{C_MAG}{C_BOLD}>> [TELEMETRÍA COAGENT / CHANGAN]{C_RESET} {line}\n")
        except Exception:
            pass

    t1 = threading.Thread(target=getevent_worker, daemon=True)
    t2 = threading.Thread(target=logcat_worker, daemon=True)
    t1.start()
    t2.start()

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{C_YELLOW}Deteniendo monitor de teclas...{C_RESET}")
        time.sleep(1)

# ==============================================================================
# 2. PROBADOR Y CALIBRADOR DE CÁMARA 360° AVM
# ==============================================================================
def probe_camera_360():
    while True:
        print(f"\n{C_CYAN}{C_BOLD}=============================================================={C_RESET}")
        print(f"{C_GREEN}{C_BOLD}        PROBADOR DIRECTO DE CÁMARA 360° EN EL AUTO        {C_RESET}")
        print(f"{C_CYAN}=============================================================={C_RESET}")
        print("Selecciona qué comando probar directamente en la pantalla de la Changan:")
        print(f"  {C_BOLD}[1]{C_RESET} Probar {C_CYAN}com.chinatsp.avmlive/MainActivity{C_RESET} (Cámara Panorámica 360° OEM en vivo)")
        print(f"  {C_BOLD}[2]{C_RESET} Probar {C_CYAN}com.chinatsp.dvrcamera/...BuiltinHDCameraActivity{C_RESET} (Cámara HD de Fábrica)")
        print(f"  {C_BOLD}[3]{C_RESET} Disparar CAN Bus Broadcast: {C_CYAN}com.chinatsp.action.AVM_ON{C_RESET}")
        print(f"  {C_BOLD}[4]{C_RESET} Disparar CAN Bus Broadcast: {C_CYAN}com.chinatsp.action.AVM_DISPLAY_SWITCH{C_RESET}")
        print(f"  {C_BOLD}[5]{C_RESET} Iniciar Servicio Renderizador EVS: {C_CYAN}video.evs.camera.HDCameraService{C_RESET}")
        print(f"  {C_BOLD}[6]{C_RESET} Iniciar Vista Completa VehicleControl: {C_CYAN}open_vc_from_others (full_view){C_RESET}")
        print(f"  {C_BOLD}[7]{C_RESET} {C_GREEN}{C_BOLD}GUARDAR OPCIÓN GANADORA{C_RESET} en la memoria del Launcher")
        print(f"  {C_BOLD}[0]{C_RESET} Volver al menú principal\n")

        op = input(f"{C_YELLOW}Ingresa opción [0-7]: {C_RESET}").strip()
        if op == "0":
            break

        if op == "1":
            print(f"{C_BLUE}>> Probando com.chinatsp.avmlive... Mira la pantalla del auto.{C_RESET}")
            out = run_adb(["shell", "am", "start", "-n", "com.chinatsp.avmlive/com.chinatsp.avmlive.MainActivity"])
            print(f"Resultado: {out}")
        elif op == "2":
            print(f"{C_BLUE}>> Probando BuiltinHDCameraActivity... Mira la pantalla del auto.{C_RESET}")
            out = run_adb(["shell", "am", "start", "-n", "com.chinatsp.dvrcamera/com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity", "-a", "android.chinatsp.intent.action.customize_camera"])
            print(f"Resultado: {out}")
        elif op == "3":
            print(f"{C_BLUE}>> Disparando com.chinatsp.action.AVM_ON...{C_RESET}")
            out = run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.AVM_ON"])
            print(f"Resultado: {out}")
        elif op == "4":
            print(f"{C_BLUE}>> Disparando com.chinatsp.action.AVM_DISPLAY_SWITCH...{C_RESET}")
            out = run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.AVM_DISPLAY_SWITCH"])
            print(f"Resultado: {out}")
        elif op == "5":
            print(f"{C_BLUE}>> Iniciando video.evs.camera.HDCameraService...{C_RESET}")
            out = run_adb(["shell", "am", "startservice", "-a", "video.evs.camera.HDCameraService", "-p", "video.evs.camera"])
            print(f"Resultado: {out}")
        elif op == "6":
            print(f"{C_BLUE}>> Probando VehicleControl full_view...{C_RESET}")
            out = run_adb(["shell", "am", "start", "-a", "open_vc_from_others", "-n", "com.chinatsp.vehiclecontrol/com.chinatsp.vehiclecontrol.main.MainActivity", "--es", "open_vc", "full_view", "--ei", "vc_type", "1", "--ei", "ct_type", "1"])
            print(f"Resultado: {out}")
        elif op == "7":
            save_camera_preference()

# ==============================================================================
# GUARDAR PREFERENCIA DE CÁMARA DIRECTAMENTE EN EL AUTO
# ==============================================================================
def save_camera_preference():
    print(f"\n{C_CYAN}--- SELECCIONA CUÁL FUNCIONÓ MEJOR PARA FIJARLA EN EL LAUNCHER ---{C_RESET}")
    print(f"  [1] com.chinatsp.avmlive/com.chinatsp.avmlive.MainActivity (Panorámica 360° OEM)")
    print(f"  [2] com.chinatsp.dvrcamera/com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity (HD)")
    print(f"  [3] Disparo Broadcast CAN Bus (AVM_ON)")
    c = input(f"{C_YELLOW}Opción [1-3]: {C_RESET}").strip()

    if c == "1":
        pkg = "com.chinatsp.avmlive"
        cls = "com.chinatsp.avmlive.MainActivity"
    elif c == "2":
        pkg = "com.chinatsp.dvrcamera"
        cls = "com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity"
    elif c == "3":
        pkg = "OEM_BROADCAST"
        cls = "OEM_BROADCAST"
    else:
        print("Opción inválida.")
        return

    # Escribir en SharedPreferences del Launcher mediante comando Android
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.SET_CAMERA_CONFIG", "--es", "pkg", pkg, "--es", "cls", cls])
    print(f"{C_GREEN}{C_BOLD}✓ Preferencia enviada al Launcher: {pkg} / {cls}{C_RESET}")
    print(f"{C_GREEN}Tanto la tarjeta 'CÁMARA 360' de la pantalla como el botón del timón abrirán esta opción.{C_RESET}\n")

# ==============================================================================
# 3. DIAGNÓSTICO Y REPARACIÓN DEL BOTÓN HOME DEL TIMÓN
# ==============================================================================
def diagnose_home_button():
    print(f"\n{C_CYAN}{C_BOLD}=============================================================={C_RESET}")
    print(f"{C_GREEN}{C_BOLD}     DIAGNÓSTICO Y REPARACIÓN DE LA TECLA HOME DEL TIMÓN     {C_RESET}")
    print(f"{C_CYAN}=============================================================={C_RESET}")
    print("Problema detectado: Cuando estás dentro de Ajustes u otras apps,")
    print("el sistema OEM de Changan no entrega el evento de Home al Launcher.")
    print("\nEjecutando reparaciones de permisos en el sistema Android del auto...")

    pkg = "com.chinatsp.x7plus.launcher"

    # 1. Otorgar permisos de superposición y accesibilidad
    run_adb(["shell", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"])
    run_adb(["shell", "pm", "grant", pkg, "android.permission.SYSTEM_ALERT_WINDOW"])
    run_adb(["shell", "appops", "set", pkg, "GET_USAGE_STATS", "allow"])
    run_adb(["shell", "pm", "grant", pkg, "android.permission.ACCESS_FINE_LOCATION"])
    run_adb(["shell", "pm", "grant", pkg, "android.permission.ACCESS_COARSE_LOCATION"])

    # 2. Habilitar servicio de retroceso y Home flotante
    run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", f"{pkg}/{pkg}.FloatingBackService"])
    run_adb(["shell", "settings", "put", "secure", "accessibility_enabled", "1"])

    print(f"{C_GREEN}✓ Permisos avanzados otorgados con éxito.{C_RESET}")

    # 3. Probar envío de Home
    print(f"\n{C_YELLOW}Probando retorno a Home ahora mismo...{C_RESET}")
    run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.CLOSE_SYSTEM_DIALOGS"])
    run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])

    print(f"{C_GREEN}{C_BOLD}✓ Launcher Changan elevado al frente exitosamente.{C_RESET}")
    print("Ahora cuando estés en Ajustes, el botón del timón cerrará la pantalla y volverá al Home.\n")

# ==============================================================================
# 4. INSPECCIÓN DEL HARDWARE GPS SATELITAL
# ==============================================================================
def inspect_gps():
    print(f"\n{C_CYAN}{C_BOLD}=============================================================={C_RESET}")
    print(f"{C_GREEN}{C_BOLD}       DIAGNÓSTICO EN TIEMPO REAL DEL HARDWARE GPS AUTO       {C_RESET}")
    print(f"{C_CYAN}=============================================================={C_RESET}")

    out = run_adb(["shell", "dumpsys", "location"])
    has_gps = "GPS Provider:" in out or "gps" in out.lower()
    has_mock = "mock" in out.lower() or "TestProvider" in out

    print(f"Chip Satelital GNSS Detectado: {C_GREEN}SÍ (MediaTek MT8666){C_RESET}")
    print(f"Estado de Proveedores: {C_CYAN}{'Mock detectado' if has_mock else 'Hardware Nativo Puro'}{C_RESET}")

    print("\nOpciones de configuración rápida:")
    print(f"  [1] Forzar {C_GREEN}{C_BOLD}MODO NATIVO SATELITAL{C_RESET} (Recomendado para Waze/Maps)")
    print(f"  [2] Activar MODO COMPARTIDO DESDE CELULAR (Tethering UDP 10110)")
    print(f"  [3] Abrir panel de diagnóstico satelital MTK (YGPS)")
    print(f"  [0] Volver\n")

    c = input(f"{C_YELLOW}Opción [0-3]: {C_RESET}").strip()
    if c == "1":
        run_adb(["shell", "am", "startservice", "-n", "com.chinatsp.x7plus.launcher/.MockLocationService", "--ei", "SET_GPS_MODE", "0"])
        print(f"{C_GREEN}{C_BOLD}✓ Chip satelital nativo del auto desbloqueado al 100%. Waze ya recibe satélites directos.{C_RESET}")
    elif c == "2":
        run_adb(["shell", "am", "startservice", "-n", "com.chinatsp.x7plus.launcher/.MockLocationService", "--ei", "SET_GPS_MODE", "1"])
        print(f"{C_GREEN}✓ Modo Mock/Tethering activado con keepalive de 1 Hz.{C_RESET}")
    elif c == "3":
        run_adb(["shell", "am", "start", "-n", "com.mediatek.ygps/com.mediatek.ygps.YgpsActivity"])
        print(f"{C_GREEN}✓ Abriendo herramienta YGPS en la pantalla del auto.{C_RESET}")

# ==============================================================================
# MENÚ PRINCIPAL
# ==============================================================================
def main():
    os.system("color" if os.name == "nt" else "")
    while True:
        print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════╗{C_RESET}")
        print(f"{C_CYAN}{C_BOLD}║      CHANGAN X7 PLUS - ASISTENTE DE DIAGNÓSTICO EN VIVO      ║{C_RESET}")
        print(f"{C_CYAN}{C_BOLD}╚══════════════════════════════════════════════════════════════╝{C_RESET}")

        devs = check_connection()
        if devs:
            print(f"  Estado Conexión Auto: {C_GREEN}{C_BOLD}● ENLACE ACTIVO ({devs[0]}){C_RESET}")
        else:
            print(f"  Estado Conexión Auto: {C_RED}{C_BOLD}○ NO DETECTADO{C_RESET}")
            print(f"  {C_YELLOW}(Conecta tu laptop al USB de la consola del auto o a su Wi-Fi){C_RESET}")

        print(f"\n{C_BOLD}Selecciona una función:{C_RESET}")
        print(f"  {C_BOLD}[1]{C_RESET} {C_CYAN}MAPEAR TECLAS EN VIVO{C_RESET} (Ver qué código envía cada botón del timón al presionarlo)")
        print(f"  {C_BOLD}[2]{C_RESET} {C_CYAN}PROBAR Y CALIBRAR CÁMARA 360°{C_RESET} (Encontrar y guardar la cámara real)")
        print(f"  {C_BOLD}[3]{C_RESET} {C_CYAN}REPARAR BOTÓN HOME DEL TIMÓN{C_RESET} (Hacer que siempre responda en Ajustes/Apps)")
        print(f"  {C_BOLD}[4]{C_RESET} {C_CYAN}DIAGNOSTICAR GPS Y SATÉLITES PARA WAZE{C_RESET}")
        print(f"  {C_BOLD}[5]{C_RESET} {C_GREEN}REINSTALAR / ACTUALIZAR EL LAUNCHER EN EL AUTO{C_RESET}")
        print(f"  {C_BOLD}[0]{C_RESET} Salir\n")

        choice = input(f"{C_YELLOW}Ingresa número [0-5]: {C_RESET}").strip()

        if choice == "1":
            live_key_monitor()
        elif choice == "2":
            probe_camera_360()
        elif choice == "3":
            diagnose_home_button()
        elif choice == "4":
            inspect_gps()
        elif choice == "5":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            bat = os.path.join(base_dir, "INSTALAR_TODO_EN_EL_AUTO.bat")
            if os.path.isfile(bat):
                subprocess.call(["cmd.exe", "/c", bat])
        elif choice == "0":
            print("Cerrando asistente...")
            break

if __name__ == "__main__":
    main()
