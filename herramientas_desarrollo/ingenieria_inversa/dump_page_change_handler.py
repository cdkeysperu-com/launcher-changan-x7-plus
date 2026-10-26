# -*- coding: utf-8 -*-
import subprocess
import os

DEXDUMP = r"C:\Users\axeln\AppData\Local\Android\Sdk\build-tools\34.0.0\dexdump.exe"
SYSTEMUI_APK = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\oem_factory_backup\F202_SystemUI.apk"
OUTPUT = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\PageChangeHandler_disassembly.txt"

print("Iniciando dexdump con streaming Python...")
cmd = [DEXDUMP, "-d", SYSTEMUI_APK]

target_classes = [
    "Lcom/chinatsp/custom/PageChangeHandler;",
    "Lcom/chinatsp/custom/view/NavigationBarLeft;",
    "Lcom/chinatsp/custom/view/NavigationBarRight;",
    "Lcom/chinatsp/custom/view/NavigationBarLeftFullScreen;",
    "Lcom/chinatsp/custom/view/NavigationBarLeftFullScreenBottom;",
    "Lcom/chinatsp/custom/view/PullExpanedView;",
    "Lcom/chinatsp/custom/view/PullExpandedRightView;"
]

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1024*1024, text=True, encoding="utf-8", errors="replace")

with open(OUTPUT, "w", encoding="utf-8") as out:
    capturing = False
    current_class = ""
    lines_captured = 0
    
    for line in p.stdout:
        if "Class descriptor" in line:
            current_class = line.strip()
            if any(tc in line for tc in target_classes):
                capturing = True
                out.write("\n" + "="*80 + "\n")
                out.write(f"=== {current_class} ===\n")
                out.write("="*80 + "\n")
            else:
                capturing = False
        
        if capturing:
            out.write(line)
            lines_captured += 1

p.wait()
print(f"Completado! Se capturaron {lines_captured} lineas en {OUTPUT}")
