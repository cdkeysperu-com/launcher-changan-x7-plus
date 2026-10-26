# -*- coding: utf-8 -*-
"""
Preparador Autónomo de APKs Complementarios para Changan X7 Plus
Extrae paquetes .apkm/.xapk y organiza apks_listos_para_instalar para adb install-multiple.
"""
import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APKS_DIR = os.path.join(BASE_DIR, "apks")
READY_DIR = os.path.join(BASE_DIR, "apks_listos_para_instalar")

os.makedirs(READY_DIR, exist_ok=True)

# 1. Descomprimir .apkm de Magic Earth
apkm_file = None
for f in os.listdir(APKS_DIR):
    if f.endswith(".apkm"):
        apkm_file = os.path.join(APKS_DIR, f)
        break

if apkm_file:
    print(f"Descomprimiendo paquete APKM: {os.path.basename(apkm_file)}...")
    magic_out = os.path.join(READY_DIR, "magicearth_splits")
    os.makedirs(magic_out, exist_ok=True)
    with zipfile.ZipFile(apkm_file, 'r') as z:
        # Extract base and required splits for arm64 + es + xxhdpi
        target_splits = [
            "base.apk",
            "split_config.arm64_v8a.apk",
            "split_config.es.apk",
            "split_config.xxhdpi.apk"
        ]
        for item in z.namelist():
            if item in target_splits or item.endswith(".apk"):
                z.extract(item, magic_out)
                print(f"  -> Extraído: {item}")

# 2. Copiar APKs complementarios esenciales
essential_apks = [
    ("headunit_android_auto.apk", "headunit_android_auto.apk"),
    ("waze_gps_navegacion.apk", "waze_gps_navegacion.apk"),
    ("brave_arm64.apk", "brave_browser.apk"),
    ("tv_streaming_gratis.apk", "xuper_tv_streaming.apk"),
    ("smarttube_youtube_pro.apk", "smarttube_youtube_pro.apk"),
    ("NewPipe_v0.29.1.apk", "newpipe_youtube.apk"),
    ("organicmaps_gps_offline.apk", "organicmaps_gps_offline.apk"),
    ("taskbar_pantalla_dividida.apk", "taskbar_pantalla_dividida.apk"),
]

# Find RiMusic
for f in os.listdir(APKS_DIR):
    if "rimusic" in f.lower() and f.endswith(".apk"):
        essential_apks.append((f, "rimusic_musica_online_offline.apk"))
        break

print("\nCopiando APKs complementarios a 'apks_listos_para_instalar'...")
for src_name, dst_name in essential_apks:
    src_path = os.path.join(APKS_DIR, src_name)
    dst_path = os.path.join(READY_DIR, dst_name)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        sz_mb = os.path.getsize(dst_path) / (1024 * 1024)
        print(f"  [OK] {dst_name} ({sz_mb:.2f} MB)")
    else:
        print(f"  [SKIP] No se encontró {src_name}")

print(f"\n¡Listo! Directorio 'apks_listos_para_instalar' preparado con éxito.")
