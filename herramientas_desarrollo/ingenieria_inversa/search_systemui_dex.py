# -*- coding: utf-8 -*-
"""
DEX DISASSEMBLER & ANALYZER: Find classes and methods for ThirdAppFullScreen, mFullScreenList, and NavBars
"""
import zipfile
import re
import os

APK_PATH = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\oem_factory_backup\F202_SystemUI.apk"

def search_dex():
    with zipfile.ZipFile(APK_PATH, 'r') as z:
        dex_files = [f for f in z.namelist() if f.endswith(".dex")]
        for dex_name in dex_files:
            data = z.read(dex_name)
            print(f"=== ANALYZING {dex_name} ({len(data)} bytes) ===")
            
            # Find class definitions in dex
            # DEX string table and type descriptors
            # Search for Lcom/...
            classes = set(re.findall(b'Lcom/[a-zA-Z0-9_/$]+;', data))
            print(f"Total Lcom/ classes found: {len(classes)}")
            
            interesting_classes = []
            for c in sorted(classes):
                c_str = c.decode('utf-8', errors='ignore')
                if any(k in c_str.lower() for k in ["navigation", "chinatsp", "fullscreen", "car", "third", "hvac", "statusbar"]):
                    interesting_classes.append(c_str)
                    
            print(f"Clases de interés ({len(interesting_classes)}):")
            for ic in interesting_classes[:80]:
                print(f"  {ic}")

            # Search specific occurrences of hideThirdAppFullScreen and showThirdAppFullScreen
            for target in [b"showThirdAppFullScreen", b"hideThirdAppFullScreen", b"mFullScreenList", b"mWhiteList"]:
                pos = 0
                print(f"\n--- Buscando contexto de: {target.decode()} ---")
                while True:
                    idx = data.find(target, pos)
                    if idx == -1:
                        break
                    start = max(0, idx - 200)
                    end = min(len(data), idx + 200)
                    snippet = data[start:end]
                    # Print printable ascii characters around match
                    printable = "".join([chr(b) if 32 <= b <= 126 else "." for b in snippet])
                    print(f"Offset 0x{idx:X}: {printable}")
                    pos = idx + len(target)

if __name__ == "__main__":
    search_dex()
