# -*- coding: utf-8 -*-
"""
FASE 1: INGENIERIA INVERSA PROFUNDA DE F202_SystemUI.apk
Localiza IDs de recursos, layouts XML, y decompila bytecode Dalvik usando dexdump.exe
"""
import os
import subprocess
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS")
OEM_DIR = os.path.join(PROJECT_DIR, "oem_factory_backup")
SYSTEMUI_APK = os.path.join(OEM_DIR, "F202_SystemUI.apk")
LAUNCHER_APK = os.path.join(OEM_DIR, "F202_Launcher.apk")
AUTOKIT_APK = os.path.join(PROJECT_DIR, "apks_listos_para_instalar", "AutoKit.apk")
HEADUNIT_APK = os.path.join(PROJECT_DIR, "apks_listos_para_instalar", "headunit_android_auto.apk")

AAPT2 = os.path.join(PROJECT_DIR, "tools", "aapt2.exe")
DEXDUMP = r"C:\Users\axeln\AppData\Local\Android\Sdk\build-tools\34.0.0\dexdump.exe"

print("====================================================================")
print("FASE 1: INGENIERIA INVERSA DE F202_SystemUI.apk")
print("====================================================================")

# Paso 1: Dump strings and resources
print("\n[PASO 1] Extrayendo tabla de strings y recursos de SystemUI...")
p_res = subprocess.run([AAPT2, "dump", "resources", SYSTEMUI_APK], capture_output=True, text=True, encoding="utf-8", errors="replace")
resources_text = p_res.stdout

# Buscar los strings exactos solicitados
target_texts = [
    "Right slide",
    "vehicle control",
    "Down slide",
    "shortcut",
    "Connect phone",
    "CarAuto",
    "use more functions"
]

found_strings = {}
current_res_id = None
current_res_name = None

for line in resources_text.splitlines():
    if "resource 0x7f" in line:
        # e.g., resource 0x7f11005a com.android.systemui:string/carauto_tip
        m = re.search(r'resource (0x7f[0-9a-fA-F]+)\s+([a-zA-Z0-9_\.:/]+)', line)
        if m:
            current_res_id = m.group(1)
            current_res_name = m.group(2)
    if "(string)" in line or '"' in line:
        for t in target_texts:
            if t.lower() in line.lower():
                found_strings[current_res_id] = {
                    "name": current_res_name,
                    "text": line.strip()
                }

print(f"\nRecursos de texto identificados ({len(found_strings)}):")
for res_id, data in found_strings.items():
    print(f"  ID: {res_id} | Name: {data['name']} | Content: {data['text']}")

# Buscar también todos los layouts relacionados con carauto, nav, bar, thirdapp, fullscreen
layout_matches = {}
for line in resources_text.splitlines():
    if ":layout/" in line:
        m = re.search(r'resource (0x7f[0-9a-fA-F]+)\s+([a-zA-Z0-9_\.:/]+)', line)
        if m:
            lid = m.group(1)
            lname = m.group(2)
            if any(k in lname.lower() for k in ["carauto", "left", "right", "slide", "shortcut", "navigation", "third", "full", "overlay", "home", "dock"]):
                layout_matches[lid] = lname

print(f"\nLayouts de interés ({len(layout_matches)}):")
for lid, lname in list(layout_matches.items())[:25]:
    print(f"  ID: {lid} -> {lname}")

# Paso 2: Usar dexdump para buscar referencias a los IDs o a las funciones clave
print("\n[PASO 2] Ejecutando dexdump en F202_SystemUI.apk...")
# Guardamos la lista de IDs hexadecimales como enteros decimales y hex
search_hex_ids = [k.lower() for k in found_strings.keys() if k]
print(f"Buscando referencias a IDs: {search_hex_ids}")

# Ejecutar dexdump con desensamblado de código
output_file = os.path.join(BASE_DIR, "systemui_dexdump_summary.txt")

# Vamos a buscar en el bytecode Dalvik usando un script con expresiones regulares sobre dexdump
cmd = [DEXDUMP, "-d", SYSTEMUI_APK]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")

interesting_methods = []
current_class = ""
current_method = ""
method_lines = []
is_interesting = False

keywords = [
    "showThirdAppFullScreen",
    "hideThirdAppFullScreen",
    "mFullScreenList",
    "mWhiteList",
    "mSysWhitelistedApps",
    "LeftCarNavigationBar",
    "RightCarNavigationBar",
    "LeftNavigationBar",
    "RightNavigationBar",
    "navigationbar_left",
    "navigationbar_right",
    "carauto",
    "CarAuto"
] + [k.lower() for k in search_hex_ids]

print("Filtrando métodos relevantes de Dalvik...")
count = 0
with open(output_file, "w", encoding="utf-8") as out:
    for line in proc.stdout:
        if "Class descriptor" in line:
            current_class = line.strip()
        elif "Method name" in line:
            current_method = line.strip()
            method_lines = [f"{current_class} -> {current_method}"]
            is_interesting = False
        else:
            method_lines.append(line.strip())
            for kw in keywords:
                if kw in line:
                    is_interesting = True
            if len(method_lines) > 200:
                # no dejar que un método crezca infinitamente
                if not is_interesting:
                    method_lines = method_lines[:10]
        
        if "catches" in line or (len(method_lines) > 1 and "Method name" in line):
            if is_interesting:
                count += 1
                out.write("====================================================================\n")
                out.write("\n".join(method_lines) + "\n\n")
                if count <= 15:
                    print(f"  [METODO #{count}] {method_lines[0]}")
                is_interesting = False
                method_lines = []

proc.wait()
print(f"\nProceso completado. Se guardaron {count} bloques de métodos en {output_file}")
