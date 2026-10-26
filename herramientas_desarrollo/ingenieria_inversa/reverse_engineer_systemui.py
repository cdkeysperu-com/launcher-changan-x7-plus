# -*- coding: utf-8 -*-
"""
FORENSIC REVERSE ENGINEERING SCRIPT: F202_SystemUI.apk & F202_Launcher.apk
Analiza recursos, strings, layouts y clases DEX de la unidad multimedia Changan X7 Plus
"""
import os
import sys
import zipfile
import re
import struct
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS")
OEM_DIR = os.path.join(PROJECT_DIR, "oem_factory_backup")
SYSTEMUI_APK = os.path.join(OEM_DIR, "F202_SystemUI.apk")
LAUNCHER_APK = os.path.join(OEM_DIR, "F202_Launcher.apk")
AAPT2 = os.path.join(PROJECT_DIR, "tools", "aapt2.exe")

print(f"Target SystemUI: {SYSTEMUI_APK}")
print(f"Target Launcher: {LAUNCHER_APK}")

# 1. Buscar las cadenas de texto en los recursos con AAPT2 dump strings
def dump_aapt_strings():
    print("\n--- 1. BUSCANDO STRINGS EXACTOS EN F202_SystemUI.apk ---")
    p = subprocess.run([AAPT2, "dump", "strings", SYSTEMUI_APK], capture_output=True, text=True, encoding="utf-8", errors="replace")
    target_keywords = ["Right slide", "vehicle control", "Down slide", "shortcut", "Connect phone", "CarAuto", "Click to homepage", "homepage"]
    matched_strings = []
    for line in p.stdout.splitlines():
        for kw in target_keywords:
            if kw.lower() in line.lower():
                matched_strings.append(line.strip())
                print(f"  [STRING ENCONTRADO]: {line.strip()}")
    return matched_strings

# 2. Volcar recursos XML y árbol de recursos con AAPT2
def dump_resources_and_ids():
    print("\n--- 2. DUMPING RESOURCES TABLE & IDS ---")
    p = subprocess.run([AAPT2, "dump", "resources", SYSTEMUI_APK], capture_output=True, text=True, encoding="utf-8", errors="replace")
    target_ids = {}
    current_entry = ""
    for line in p.stdout.splitlines():
        # Match resource definition: resource 0x7f0b0012 com.android.systemui:string/carauto_tip
        if "resource 0x7f" in line:
            current_entry = line.strip()
        for kw in ["slide", "vehicle", "control", "shortcut", "carauto", "homepage", "dock", "side", "panel", "quick", "bar"]:
            if kw in line.lower() and "resource 0x7f" in line:
                target_ids[line.strip()] = []
    print(f"Encontrados {len(target_ids)} recursos potencialmente relacionados con barras/paneles.")
    return p.stdout

# 3. Analizar DEX de SystemUI buscando referencias a strings y clases
def analyze_dex_strings_and_classes():
    print("\n--- 3. EXTRAYENDO Y ANALIZANDO classes.dex DE F202_SystemUI.apk ---")
    with zipfile.ZipFile(SYSTEMUI_APK, 'r') as z:
        dex_files = [f for f in z.namelist() if f.endswith(".dex")]
        print(f"Archivos DEX encontrados: {dex_files}")
        for dex_name in dex_files:
            dex_bytes = z.read(dex_name)
            print(f"Analizando {dex_name} ({len(dex_bytes)} bytes)...")
            
            # Buscar strings en crudo en el bytecode DEX
            # Patrón de strings UTF-8 en DEX
            raw_strings = re.findall(b'[\x20-\x7e]{4,}', dex_bytes)
            str_set = [s.decode('utf-8', errors='ignore') for s in raw_strings]
            
            # Buscar menciones a CarAuto, Chinatsp, fullscreen, nav, etc.
            keywords = ["carauto", "chinatsp", "fullscreen", "nav_bar", "navigationbar", 
                        "right_slide", "down_slide", "quick_control", "policy_control",
                        "package_whitelist", "whitelist", "set-home-activity", "ACTION_ENTER_FULLSCREEN"]
            
            print(f"\n--- Coincidencias en {dex_name} para palabras clave ---")
            found = set()
            for s in str_set:
                low = s.lower()
                for kw in keywords:
                    if kw in low:
                        found.add(s)
            
            for item in sorted(found):
                if len(item) < 120:
                    print(f"  {item}")

if __name__ == "__main__":
    dump_aapt_strings()
    analyze_dex_strings_and_classes()
