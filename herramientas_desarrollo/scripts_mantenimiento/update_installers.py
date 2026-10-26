# -*- coding: utf-8 -*-
import os

def update_instalar_todo_py():
    path = r"APK CHANGAN X7 PLUS/instalar_todo_x7_plus.py"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # Fix package name
    code = code.replace('launcher_pkg = "com.changan.x7plus.launcher"', 'launcher_pkg = "com.chinatsp.x7plus.launcher"')
    code = code.replace('com.changan.x7plus.launcher', 'com.chinatsp.x7plus.launcher')

    # Fix mock location to real GPS hardware in Phase 4
    old_gps_sec = '''    # E. Activación de GPS Satelital y Red
    log("Activando proveedores de ubicación en alta precisión (Modo 3: GPS + Network)...")
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"])
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])'''

    new_gps_sec = '''    # E. Activación de GPS Satelital Real MediaTek de Hardware (Zero Mock Hijacking)
    log("Activando GPS satelital nativo del vehículo en ultra-alta precisión (Modo 3)...")
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"])
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"])
    run_adb(["shell", "settings", "put", "secure", "mock_location", "0"])
    run_adb(["shell", "appops", "set", launcher_pkg, "android:mock_location", "deny"])
    run_adb(["shell", "appops", "set", launcher_pkg, "MOCK_LOCATION", "deny"])
    
    # E2. Habilitar FloatingBackService como AccessibilityService de Sistema
    log("Habilitando FloatingBackService para retroceso y Home flotante sin restricciones...")
    run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", "com.chinatsp.x7plus.launcher/.FloatingBackService"])
    run_adb(["shell", "settings", "put", "secure", "accessibility_enabled", "1"])'''

    code = code.replace(old_gps_sec, new_gps_sec)

    # Add InnerTune, Open Headunit Beta 5, YGPS to complementary list
    old_comp = '''        ("rimusic_musica_online_offline.apk", "RiMusic (Streaming & Descargas)"),'''
    new_comp = '''        ("vimusic_innertune_musica.apk", "InnerTune / ViMusic (Música Streaming & Descargas Offline)"),
        ("rimusic_musica_online_offline.apk", "RiMusic (Streaming Alternativo)"),'''
    if old_comp in code and "vimusic_innertune_musica" not in code:
        code = code.replace(old_comp, new_comp)

    # Add YGPS from OEM backup
    ygps_install = '''    # 3. MediaTek YGPS Satellite Diagnostics
    ygps_src = os.path.join(BASE_DIR, "oem_factory_backup", "full_backup_20261016_161339", "app", "YGPS", "YGPS.apk")
    if not os.path.exists(ygps_src):
        ygps_src = os.path.join(os.path.dirname(BASE_DIR), "portable", "oem_factory_backup", "full_backup_20261016_161339", "app", "YGPS", "YGPS.apk")
    if os.path.exists(ygps_src):
        log("Instalando Monitor Satelital MediaTek YGPS...")
        run_adb(["install", "-r", "-d", ygps_src])
        run_adb(["shell", "pm", "grant", "com.mediatek.ygps", "android.permission.ACCESS_FINE_LOCATION"])
'''
    if "MediaTek YGPS" not in code:
        code = code.replace('    # FASE 4:', ygps_install + '\n    # FASE 4:')

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("instalar_todo_x7_plus.py updated successfully!")

def update_bat(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix package name
    content = content.replace("com.changan.x7plus.launcher", "com.chinatsp.x7plus.launcher")

    # Fix mock location -> real GPS
    content = content.replace('tools\\adb.exe shell appops set com.chinatsp.x7plus.launcher android:mock_location allow', 'tools\\adb.exe shell appops set com.chinatsp.x7plus.launcher android:mock_location deny\ntools\\adb.exe shell appops set com.chinatsp.x7plus.launcher MOCK_LOCATION deny')
    
    # Add real GPS mode 3 and accessibility
    old_p4 = 'echo [4/5] INSTALANDO APLICACIONES COMPLEMENTARIAS Y ANDROID AUTO'
    gps_block = '''echo Configurando GPS Satelital Real MediaTek de Hardware (Modo 3)...
tools\\adb.exe shell settings put secure location_mode 3 >nul 2>&1
tools\\adb.exe shell settings put secure location_providers_allowed +gps,+network >nul 2>&1
tools\\adb.exe shell settings put secure mock_location 0 >nul 2>&1
tools\\adb.exe shell settings put secure enabled_accessibility_services com.chinatsp.x7plus.launcher/.FloatingBackService >nul 2>&1
tools\\adb.exe shell settings put secure accessibility_enabled 1 >nul 2>&1
echo [OK] GPS Satelital nativo y Boton Flotante activados.
echo.
'''
    if "FloatingBackService >nul 2>&1" not in content:
        content = content.replace(old_p4, gps_block + old_p4)

    # Add vimusic_innertune install
    inner_tune_block = '''REM InnerTune / ViMusic (Musica Streaming & Descargas Offline)
if exist "apks\\vimusic_innertune_musica.apk" (
    echo Instalando InnerTune / ViMusic...
    tools\\adb.exe install -r -d "apks\\vimusic_innertune_musica.apk"
    tools\\adb.exe shell pm grant com.zionhuang.music android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
    tools\\adb.exe shell pm grant com.zionhuang.music android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1
    tools\\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName "com.zionhuang.music" --ei appCentered 2 >nul 2>&1
    echo [OK] InnerTune instalado.
)

'''
    if "vimusic_innertune_musica.apk" not in content:
        content = content.replace('REM RiMusic (Musica Streaming & Descargas Hi-Fi)', inner_tune_block + 'REM RiMusic (Musica Streaming & Descargas Hi-Fi)')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {path}")

if __name__ == "__main__":
    update_instalar_todo_py()
    update_bat(r"portable/INSTALAR_TODO_EN_EL_AUTO.bat")
    update_bat(r"APK CHANGAN X7 PLUS/INSTALAR_TODO_EN_EL_AUTO.bat")
