import os
import sys
import shutil

SRC_DIR = r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS"
PORTABLE_DIR = r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\portable"

def build_portable():
    print(f"=== Creando paquete PORTABLE Changan X7 Plus ===")
    print(f"Origen:      {SRC_DIR}")
    print(f"Destino:     {PORTABLE_DIR}\n")

    if os.path.exists(PORTABLE_DIR):
        print(f"[*] Limpiando carpeta portable existente...")
        shutil.rmtree(PORTABLE_DIR)
    os.makedirs(PORTABLE_DIR, exist_ok=True)

    # 1. Scripts batch y ejecutables principales
    root_files = [
        "0_ABRIR_MENU_CHANGAN.bat",
        "INICIAR_DASHBOARD_CHANGAN.bat",
        "INSTALAR_TODO_EN_EL_AUTO.bat",
        "DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat",
        "DETENER_DASHBOARD.bat",
        "server.py",
        "dashboard_state.json",
        "ChanganX7Plus_OEM_Launcher.apk",
        "INFORME_TECNICO_MAESTRO_CHANGAN.md"
    ]

    print("[1/6] Copiando scripts y servidor...")
    for f in root_files:
        sp = os.path.join(SRC_DIR, f)
        dp = os.path.join(PORTABLE_DIR, f)
        if os.path.exists(sp):
            shutil.copy2(sp, dp)
            size_mb = round(os.path.getsize(dp) / (1024*1024), 2)
            print(f"  + {f} ({size_mb} MB)")
        else:
            print(f"  ! ALERTA: No se encontró {f}")

    # 2. Carpeta Web (launcher_web)
    print("\n[2/6] Copiando interfaz Dashboard (launcher_web)...")
    web_src = os.path.join(SRC_DIR, "launcher_web")
    web_dst = os.path.join(PORTABLE_DIR, "launcher_web")
    if os.path.exists(web_src):
        shutil.copytree(web_src, web_dst)
        count = sum(len(files) for _, _, files in os.walk(web_dst))
        print(f"  + launcher_web/ ({count} archivos copiados)")

    # 3. Python Portable (runtime)
    print("\n[3/6] Copiando Python 3.11 embebido portable (runtime)...")
    rt_src = os.path.join(SRC_DIR, "runtime")
    rt_dst = os.path.join(PORTABLE_DIR, "runtime")
    if os.path.exists(rt_src):
        shutil.copytree(rt_src, rt_dst)
        count = sum(len(files) for _, _, files in os.walk(rt_dst))
        print(f"  + runtime/ ({count} archivos, ejecutable autónomo listo)")

    # 4. Herramientas ADB (tools) - SOLO ADB Y DLLs (sin JDK ni Android.jar pesados)
    print("\n[4/6] Copiando binarios ADB limpios (tools)...")
    tools_dst = os.path.join(PORTABLE_DIR, "tools")
    os.makedirs(tools_dst, exist_ok=True)
    adb_files = ["adb.exe", "AdbWinApi.dll", "AdbWinUsbApi.dll"]
    for af in adb_files:
        sp = os.path.join(SRC_DIR, "tools", af)
        dp = os.path.join(tools_dst, af)
        if os.path.exists(sp):
            shutil.copy2(sp, dp)
            print(f"  + tools/{af}")
        else:
            print(f"  ! ALERTA: No se encontró tools/{af}")

    # 5. APKs listos para instalar (apks y apks_listos_para_instalar)
    print("\n[5/6] Copiando suite completa de APKs optimizados...")
    apks_src = os.path.join(SRC_DIR, "apks_listos_para_instalar")
    apks_dst = os.path.join(PORTABLE_DIR, "apks_listos_para_instalar")
    if os.path.exists(apks_src):
        shutil.copytree(apks_src, apks_dst)
        count = sum(len(files) for _, _, files in os.walk(apks_dst))
        print(f"  + apks_listos_para_instalar/ ({count} archivos, incluye Magic Earth splits)")

    # Copiar también a apks/ para compatibilidad con cualquier script
    apks_plain_dst = os.path.join(PORTABLE_DIR, "apks")
    shutil.copytree(apks_dst, apks_plain_dst)
    print(f"  + apks/ (espejo de compatibilidad creado)")

    # 6. Carpetas de respaldo y diagnóstico
    print("\n[6/6] Configurando carpetas de respaldo y diagnóstico...")
    # oem_factory_backup
    oem_src = os.path.join(SRC_DIR, "oem_factory_backup")
    oem_dst = os.path.join(PORTABLE_DIR, "oem_factory_backup")
    os.makedirs(oem_dst, exist_ok=True)
    for f in ["F202_Launcher.apk", "F202_SystemUI.apk"]:
        sp = os.path.join(oem_src, f)
        dp = os.path.join(oem_dst, f)
        if os.path.exists(sp):
            shutil.copy2(sp, dp)
            print(f"  + oem_factory_backup/{f}")

    # diagnostics
    diag_dst = os.path.join(PORTABLE_DIR, "diagnostics")
    os.makedirs(diag_dst, exist_ok=True)
    # Copiar telemetría previa si existe
    diag_src = os.path.join(SRC_DIR, "diagnostics")
    if os.path.exists(diag_src):
        for f in os.listdir(diag_src):
            if f.endswith(".txt"):
                shutil.copy2(os.path.join(diag_src, f), os.path.join(diag_dst, f))
                print(f"  + diagnostics/{f}")

    # 7. Crear archivo LEEME_PRIMERO_EN_EL_AUTO.txt
    readme_path = os.path.join(PORTABLE_DIR, "LEEME_PRIMERO_EN_EL_AUTO.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("""===============================================================================
       GUÍA RÁPIDA: CONECTAR Y APLICAR MEJORAS EN TU CHANGAN X7 PLUS
===============================================================================

LLEVA ESTA CARPETA EN TU LAPTOP AL AUTO CON EL CABLE USB.

PASO 1: EN EL AUTO
-------------------------------------------------------------------------------
1. Enciende la radio de tu Changan X7 Plus.
2. Abre la aplicación de TELÉFONO (marcador de llamadas).
3. Escribe exactamente el código:
      **888
4. Se abrirán los Ajustes Ocultos de Desarrollador del auto.
5. Busca y MARCA la casilla: "Depuración por USB".
6. Conecta el cable USB de tu laptop al PUERTO USB FRONTAL de la radio.
7. En la pantalla del auto aparecerá una ventana emergente:
   -> Marca la casilla: "Permitir siempre desde este equipo"
   -> Presiona el botón: ACEPTAR

PASO 2: EN TU LAPTOP
-------------------------------------------------------------------------------
Opción A (Visual - Recomendada):
  - Haz doble clic en "INICIAR_DASHBOARD_CHANGAN.bat".
  - Se abrirá automáticamente tu navegador en http://localhost:5050.
  - Verás el estado "Changan X7 Plus Conectado".
  - Pulsa la Tarjeta 4 ("Extraer Telemetría") para guardar el log de tu auto.
  - Pulsa la Tarjeta 2 ("APLICAR TODAS LAS MEJORAS CON 1 CLIC").
  - ¡Listo! En 2 minutos tendrás todo configurado.

Opción B (Consola directa):
  - Haz doble clic en "INSTALAR_TODO_EN_EL_AUTO.bat".
  - El script hará todo el proceso por ti automáticamente.

SI ALGÚN DÍA QUIERES DEJAR EL AUTO 100% VIRGEN DE FÁBRICA:
-------------------------------------------------------------------------------
  - Haz doble clic en "DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat" o pulsa
    la Tarjeta 1 en el Dashboard. Tu auto volverá al OnStyle original intacto.
===============================================================================
""")
    print("  + LEEME_PRIMERO_EN_EL_AUTO.txt (Guía paso a paso generada)")

    # Auditoría final de tamaño
    total_size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                     for dirpath, _, filenames in os.walk(PORTABLE_DIR) 
                     for filename in filenames)
    total_files = sum(len(filenames) for _, _, filenames in os.walk(PORTABLE_DIR))

    print(f"\n=======================================================")
    print(f"✅ PAQUETE PORTABLE GENERADO CON ÉXITO")
    print(f"Ruta:        {PORTABLE_DIR}")
    print(f"Archivos:    {total_files}")
    print(f"Tamaño total:{round(total_size / (1024*1024), 2)} MB")
    print(f"=======================================================")

if __name__ == "__main__":
    build_portable()
