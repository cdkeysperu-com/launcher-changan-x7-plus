# -*- coding: utf-8 -*-
"""
================================================================================
CHANGAN X7 PLUS - SISTEMA AVANZADO DE CAPTURA Y AUDITORÍA DE TELEMETRÍA VEHICULAR
================================================================================
Extrae de forma forense y no destructiva:
1. Telemetría de Bus CAN y MCU del Vehículo (Propiedades de chasis, puertas, A/C, sensores).
2. Estado de Sensores y Hardware GNSS MediaTek (NMEA, satélites, estado de fijación).
3. Telemetría Térmica, Eléctrica y Rendimiento del SoC MT8666 Octa-Core.
4. Diagnóstico de Audio y Enrutamiento Multimedia de Fábrica.
5. Estado de Servicios del Ecosistema Propietario ChinaTSP F202.
================================================================================
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "tools")
ADB = os.path.join(TOOLS_DIR, "adb.exe")
if not os.path.exists(ADB):
    ADB = os.path.join(BASE_DIR, "tools", "adb.exe")
if not os.path.exists(ADB):
    ADB = "adb"

INFORMES_DIR = os.path.join(BASE_DIR, "informes")
os.makedirs(INFORMES_DIR, exist_ok=True)

def run_adb_shell(cmd_str, timeout=20):
    cmd = [ADB, "shell"] + cmd_str.split()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.stdout.strip()
    except Exception as e:
        return f"[ERROR: {e}]"

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json_path = os.path.join(INFORMES_DIR, f"telemetria_changan_x7_{timestamp}.json")
    out_txt_path = os.path.join(INFORMES_DIR, f"telemetria_changan_x7_{timestamp}.txt")

    print("=" * 80)
    print(" CHANGAN X7 PLUS — RECOLECTOR MAESTRO DE TELEMETRÍA VEHICULAR")
    print("=" * 80)
    print("[*] Verificando conexión con el vehículo (o emulador)...")

    # Verificar conexión ADB
    dev_res = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    lines = [l for l in dev_res.stdout.splitlines() if "\tdevice" in l]
    if not lines:
        print("[!] No se detectó ningún dispositivo conectado.")
        print("    Asegúrate de conectar tu laptop al puerto USB del auto con depuración activa.")
        print("    Esperando dispositivo...")
        subprocess.run([ADB, "wait-for-device"])

    print("[OK] Conexión establecida. Iniciando escaneo forense de telemetría...")
    telemetry = {
        "timestamp": timestamp,
        "date_iso": datetime.now().isoformat(),
        "device_fingerprint": {},
        "vehicle_can_mcu": {},
        "gnss_location": {},
        "thermal_and_power": {},
        "display_and_window": {},
        "audio_routing": {},
        "chinatsp_services": {}
    }

    # 1. Device Fingerprint
    print("[1/6] Extrayendo huella de hardware y compilación...")
    telemetry["device_fingerprint"] = {
        "model": run_adb_shell("getprop ro.product.model"),
        "brand": run_adb_shell("getprop ro.product.brand"),
        "hardware": run_adb_shell("getprop ro.hardware"),
        "soc": run_adb_shell("getprop ro.board.platform"),
        "android_version": run_adb_shell("getprop ro.build.version.release"),
        "sdk_api": run_adb_shell("getprop ro.build.version.sdk"),
        "build_id": run_adb_shell("getprop ro.build.display.id"),
        "serial": run_adb_shell("getprop ro.serialno"),
        "changan_project": run_adb_shell("getprop ro.chinatsp.project"),
        "changan_model": run_adb_shell("getprop ro.chinatsp.model"),
        "mcu_version": run_adb_shell("getprop persist.sys.mcu.version")
    }

    # 2. CAN Bus & MCU Telemetry
    print("[2/6] Analizando Bus CAN y propiedades del vehículo...")
    telemetry["vehicle_can_mcu"] = {
        "car_service_dump": run_adb_shell("dumpsys car_service"),
        "persist_changan_props": run_adb_shell("getprop | grep -i chinatsp"),
        "persist_mcu_props": run_adb_shell("getprop | grep -i mcu"),
        "vehicle_properties": run_adb_shell("dumpsys activity service com.chinatsp.vehiclecontrol/.VehicleControlService")
    }

    # 3. GNSS & Location
    print("[3/6] Capturando estado satelital GNSS y sensores de ubicación...")
    telemetry["gnss_location"] = {
        "location_mode": run_adb_shell("settings get secure location_mode"),
        "providers_allowed": run_adb_shell("settings get secure location_providers_allowed"),
        "mock_location_setting": run_adb_shell("settings get secure mock_location"),
        "dumpsys_location_summary": run_adb_shell("dumpsys location"),
        "ygps_service_status": run_adb_shell("dumpsys package com.mediatek.ygps")
    }

    # 4. Thermal & Power Telemetry
    print("[4/6] Monitoreando sensores térmicos y estado eléctrico...")
    telemetry["thermal_and_power"] = {
        "battery_dumpsys": run_adb_shell("dumpsys battery"),
        "cpu_thermal_zones": run_adb_shell("cat /sys/class/thermal/thermal_zone0/temp"),
        "cpu_frequencies": run_adb_shell("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"),
        "storage_df": run_adb_shell("df -h")
    }

    # 5. Display & Window Manager
    print("[5/6] Analizando configuración de pantalla panorámica 1920x720...")
    telemetry["display_and_window"] = {
        "screen_size": run_adb_shell("wm size"),
        "screen_density": run_adb_shell("wm density"),
        "overscan": run_adb_shell("wm overscan"),
        "policy_control": run_adb_shell("settings get global policy_control"),
        "current_focus_window": run_adb_shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
    }

    # 6. Audio Routing
    print("[6/6] Verificando enrutamiento de audio vehicular...")
    telemetry["audio_routing"] = {
        "audio_flinger": run_adb_shell("dumpsys media.audio_flinger"),
        "audio_policy": run_adb_shell("dumpsys media.audio_policy")
    }

    # Guardar informe JSON
    with open(out_json_path, "w", encoding="utf-8") as f_json:
        json.dump(telemetry, f_json, indent=2, ensure_ascii=False)

    # Guardar informe TXT legible
    with open(out_txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("=" * 80 + "\n")
        f_txt.write(" CHANGAN X7 PLUS — INFORME DE TELEMETRÍA VEHICULAR INTEGRAL\n")
        f_txt.write(f" Fecha de Captura: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_txt.write("=" * 80 + "\n\n")

        f_txt.write("1. INFORMACIÓN DEL HARDWARE & SISTEMA:\n")
        f_txt.write("-" * 40 + "\n")
        for k, v in telemetry["device_fingerprint"].items():
            f_txt.write(f"  {k:20}: {v}\n")
        f_txt.write("\n")

        f_txt.write("2. ESTADO DEL GNSS / GPS SATELITAL:\n")
        f_txt.write("-" * 40 + "\n")
        f_txt.write(f"  Modo de Ubicación   : {telemetry['gnss_location']['location_mode']} (3 = Alta Precisión Satelital GPS+Red)\n")
        f_txt.write(f"  Proveedores Activos : {telemetry['gnss_location']['providers_allowed']}\n")
        f_txt.write(f"  Mock Location (Falso): {telemetry['gnss_location']['mock_location_setting']} (0 = Inhabilitado, 100% Satelital Real)\n")
        f_txt.write("\n")

        f_txt.write("3. PANTALLA & MODO INMERSIVO:\n")
        f_txt.write("-" * 40 + "\n")
        f_txt.write(f"  Resolución wm size  : {telemetry['display_and_window']['screen_size']}\n")
        f_txt.write(f"  Densidad DPI        : {telemetry['display_and_window']['screen_density']}\n")
        f_txt.write(f"  Política Inmersiva  : {telemetry['display_and_window']['policy_control']}\n")
        f_txt.write(f"  Ventana con Foco    : {telemetry['display_and_window']['current_focus_window']}\n")
        f_txt.write("\n")

        f_txt.write("4. ESTADO DE ENERGÍA Y TEMPERATURA:\n")
        f_txt.write("-" * 40 + "\n")
        f_txt.write(f"  Temperatura CPU     : {telemetry['thermal_and_power']['cpu_thermal_zones']} mC\n")
        f_txt.write(f"  Frecuencia CPU0     : {telemetry['thermal_and_power']['cpu_frequencies']} KHz\n")
        f_txt.write("\n")

        f_txt.write("5. PROPIEDADES VEHICULARES PERSISTENTES (CAN / MCU):\n")
        f_txt.write("-" * 40 + "\n")
        f_txt.write(telemetry["vehicle_can_mcu"]["persist_changan_props"] + "\n\n")

    print("\n" + "=" * 80)
    print(" ¡TELEMETRÍA CAPTURADA Y REGISTRADA EXITOSAMENTE!")
    print(f" • Informe JSON: {out_json_path}")
    print(f" • Informe TXT : {out_txt_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
