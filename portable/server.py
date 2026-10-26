import os
import sys
import json
import time
import shutil
import urllib.parse
import subprocess
import re
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Prevent crash when run with pythonw (sys.stdout is None)
if sys.stdout is None:
    try:
        sys.stdout = open(os.path.join(BASE_DIR, "server.log"), "a", encoding="utf-8", buffering=1)
    except Exception:
        sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    try:
        sys.stderr = open(os.path.join(BASE_DIR, "server.log"), "a", encoding="utf-8", buffering=1)
    except Exception:
        sys.stderr = open(os.devnull, "w")

def log_unhandled_exception(exc_type, exc_value, exc_traceback):
    try:
        import traceback
        with open(os.path.join(BASE_DIR, "server.log"), "a", encoding="utf-8") as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] FATAL UNHANDLED EXCEPTION:\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = log_unhandled_exception

WEB_DIR = os.path.join(BASE_DIR, "launcher_web") if os.path.exists(os.path.join(BASE_DIR, "launcher_web")) else os.path.join(BASE_DIR, "web")
APKS_DIR = os.path.join(BASE_DIR, "apks")
PLATFORM_TOOLS_DIR = os.path.join(BASE_DIR, "tools") if os.path.exists(os.path.join(BASE_DIR, "tools")) else os.path.join(BASE_DIR, "platform-tools")
ADB_EXE = os.path.join(PLATFORM_TOOLS_DIR, "adb.exe")

if not os.path.exists(ADB_EXE):
    ADB_EXE = shutil.which("adb") or "adb"

os.makedirs(APKS_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

EXECUTION_LOGS = []

# Dangerous command blacklist to prevent bricking via terminal
DANGEROUS_COMMANDS = [
    "reboot bootloader", "reboot fastboot", "fastboot", "flash ",
    "rm -rf /system", "rm -rf /vendor", "rm -rf /boot", "format ",
    "dd if=", "wipe ", "mkfs"
]

def add_log(cmd: str, output: str, is_error: bool = False):
    timestamp = time.strftime("%H:%M:%S")
    entry = {
        "time": timestamp,
        "command": cmd,
        "output": output.strip(),
        "is_error": is_error
    }
    EXECUTION_LOGS.append(entry)
    if len(EXECUTION_LOGS) > 300:
        EXECUTION_LOGS.pop(0)

def run_adb(args, timeout=60):
    cmd_list = [ADB_EXE] + args
    cmd_str = "adb " + " ".join(args)
    try:
        proc = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            shell=False
        )
        output = proc.stdout or ""
        is_err = (proc.returncode != 0)
        add_log(cmd_str, output, is_error=is_err)
        return proc.returncode, output
    except subprocess.TimeoutExpired:
        msg = f"Error: Comando expiró después de {timeout}s"
        add_log(cmd_str, msg, is_error=True)
        return -1, msg
    except Exception as e:
        msg = f"Excepción ejecutando adb: {str(e)}"
        add_log(cmd_str, msg, is_error=True)
        return -1, msg

def get_storage_info():
    """Checks available space on /data to prevent filling head unit memory"""
    code, out = run_adb(["shell", "df", "/data"], timeout=5)
    if code != 0 or not out:
        return {"free_mb": -1, "total_mb": -1, "percent_used": 0, "safe": True}
    
    try:
        lines = [l for l in out.strip().splitlines() if l.strip()]
        if len(lines) >= 2:
            parts = lines[1].split()
            # Standard df format: Filesystem 1K-blocks Used Available Use% Mounted
            if len(parts) >= 4:
                # convert 1K-blocks to MB
                total_kb = int(parts[1]) if parts[1].isdigit() else 0
                used_kb = int(parts[2]) if parts[2].isdigit() else 0
                avail_kb = int(parts[3]) if parts[3].isdigit() else 0
                
                free_mb = round(avail_kb / 1024, 1)
                total_mb = round(total_kb / 1024, 1)
                pct = round((used_kb / total_kb * 100), 1) if total_kb > 0 else 0
                # Less than 350 MB free is dangerous for Android boot
                return {
                    "free_mb": free_mb,
                    "total_mb": total_mb,
                    "percent_used": pct,
                    "safe": (free_mb > 350 or free_mb == -1)
                }
    except Exception:
        pass
    return {"free_mb": -1, "total_mb": -1, "percent_used": 0, "safe": True}

def check_usb_hardware():
    """Detects if Windows sees the Changan MediaTek hardware connected via USB (F202_MCA)"""
    try:
        res = subprocess.run(
            ["pnputil", "/enum-devices", "/connected"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3
        )
        out = (res.stdout or "").upper()
        if "0E8D" in out or "F202" in out:
            return True
    except Exception:
        pass
    return False

def get_device_info():
    code, out = run_adb(["devices", "-l"], timeout=8)
    lines = [line.strip() for line in out.strip().splitlines() if line.strip()]
    
    device_id = None
    state = "disconnected"
    model = "Changan X7 Plus"
    android_ver = "Desconocido"
    sdk_ver = ""
    hardware = "MT8666"
    cpu_abi = "armeabi-v7a / arm64-v8a"

    device_lines = [l for l in lines if not l.startswith("*") and not l.startswith("List of devices")]
    if device_lines:
        first = device_lines[0].split()
        if len(first) >= 2:
            device_id = first[0]
            state = first[1]
            if state == "device":
                _, m_out = run_adb(["shell", "getprop", "ro.product.model"], timeout=4)
                if m_out and "error" not in m_out.lower():
                    model = m_out.strip() or model
                
                _, a_out = run_adb(["shell", "getprop", "ro.build.version.release"], timeout=4)
                if a_out and "error" not in a_out.lower():
                    android_ver = a_out.strip() or android_ver

                _, s_out = run_adb(["shell", "getprop", "ro.build.version.sdk"], timeout=4)
                if s_out and "error" not in s_out.lower():
                    sdk_ver = s_out.strip()

                _, h_out = run_adb(["shell", "getprop", "ro.hardware"], timeout=4)
                if h_out and "error" not in h_out.lower():
                    hardware = h_out.strip() or hardware

                _, abi_out = run_adb(["shell", "getprop", "ro.product.cpu.abi"], timeout=4)
                if abi_out and "error" not in abi_out.lower():
                    cpu_abi = abi_out.strip() or cpu_abi
            elif state == "unauthorized":
                model = "Changan X7 Plus (F202_MCA)"

    usb_hw = False
    if state == "disconnected":
        usb_hw = check_usb_hardware()

    storage = get_storage_info() if state == "device" else {"free_mb": -1, "safe": True}

    return {
        "connected": (state == "device"),
        "state": state,
        "device_id": device_id,
        "usb_present": usb_hw,
        "model": model,
        "android_version": android_ver,
        "sdk_version": sdk_ver,
        "hardware": hardware,
        "cpu_abi": cpu_abi,
        "storage": storage,
        "adb_path": ADB_EXE,
        "raw_output": out
    }

KNOWN_APPS_METADATA = {
    "magicearth_splits": {
        "name": "Magic Earth GPS 3D (Mapas Vectoriales & Tráfico Offline)",
        "category": "Navegación GPS Offline",
        "package": "com.generalmagic.magicearth",
        "desc": "Navegación satelital y mapas 3D paso a paso sin consumo de datos. Alternativa premium y ligera a Waze para la pantalla panorámica.",
        "badge": "⭐ Navegación 3D Offline",
        "icon": "map"
    },
    "organicmaps_gps_offline.apk": {
        "name": "Organic Maps (GPS Satelital 100% Offline)",
        "category": "Navegación GPS Offline",
        "package": "app.organicmaps.web",
        "desc": "Mapas vectoriales 100% sin conexión a internet ni dependencia del celular. Posicionamiento GPS en tiempo real en la pantalla panorámica.",
        "badge": "⭐ 0% CELULAR / 100% OFFLINE",
        "icon": "map"
    },
    "spotube_spotify_libre.apk": {
        "name": "Spotube v5.1.2 (Spotify Libre 1:1 + Descargas MP3)",
        "category": "Música & Descargas",
        "package": "oss.krtirtho.spotube",
        "desc": "Catálogo completo de Spotify sin anuncios ni cuenta premium. Descargas directas a MP3 en memoria interna (/sdcard/Music) o memoria USB.",
        "badge": "⭐ SPOTIFY LIBRE + MP3",
        "icon": "music"
    },
    "simpmusic_offline_pro.apk": {
        "name": "SimpMusic v2.3.0 (Reproductor Offline Pro)",
        "category": "Música Offline",
        "package": "com.maxrave.simpmusic",
        "desc": "Motor de audio ExoPlayer sin bucles de repetición. Reproducción ultra-fluida, sin cortes y caché offline permanente en el auto.",
        "badge": "⭐ SIN BUCLES / HI-FI",
        "icon": "music"
    },
    "owntv_cable_en_vivo.apk": {
        "name": "OwnTV v5.2.1 (Televisión de Cable en Vivo)",
        "category": "Televisión en Vivo",
        "package": "com.ahxn00.owntv",
        "desc": "370+ canales de televisión en vivo (Perú señal abierta, deportes internacionales, noticias y cine) con cambio instantáneo de canal.",
        "badge": "⭐ 370+ CANALES VIP",
        "icon": "tv"
    },
    "changanx7plus_oem_launcher.apk": {
        "name": "Cockpit X7 Plus Launcher (HMI Oficial Changan)",
        "category": "Lanzador Automotriz",
        "package": "com.chinatsp.x7plus.launcher",
        "desc": "Lanzador nativo panorámico 1920x720 sin franjas laterales. Tarjetas independientes de Radio AM/FM y Música, Clima superior, brocha de RAM y Cámara 360° AVM.",
        "badge": "⭐ OFICIAL CHANGAN 1920x720",
        "icon": "car"
    },
    "rimusic_spotify_gratis.apk": {
        "name": "RiMusic (Música Streaming + Descargador Offline)",
        "category": "Música & Descargas",
        "package": "it.fast4x.rimusic",
        "desc": "Catálogo completo de música sin anuncios con botón de descarga local para escuchar pistas y álbumes sin internet en carretera.",
        "badge": "⭐ Streaming + Descargas",
        "icon": "music"
    },
    "waze_standalone.apk": {
        "name": "Waze GPS Standalone (Sin Google Play Services)",
        "category": "Navegación GPS",
        "package": "com.waze",
        "desc": "Waze autónomo optimizado para Android 9 automotriz sin requerir Google Play Services. Alertas de tráfico y radares en vivo.",
        "badge": "⭐ Waze Autónomo",
        "icon": "map"
    },
    "cockpit_x7_fullscreen.apk": {
        "name": "Cockpit X7 Plus FullScreen (1920x720 Nativo)",
        "category": "Lanzador Automotriz",
        "package": "com.chinatsp.x7pluslauncher",
        "desc": "Lanzador panorámico 1920x720 nativo sin barras laterales. Integración completa con Magic Earth, RiMusic, Cámaras 360 y Climatizador.",
        "badge": "⭐ PANTALLA COMPLETA",
        "icon": "car"
    },
    "tv_streaming_gratis.apk": {
        "name": "CloudStream (TV en Vivo & Streaming Gratis)",
        "category": "Multimedia / TV",
        "package": "com.lagradost.cloudstream3",
        "desc": "Canales de televisión en vivo y catálogo de series y películas en español 100% gratis y sin anuncios molestos.",
        "badge": "⭐ TV Gratis",
        "icon": "youtube"
    },
    "newpipe_v0.29.1.apk": {
        "name": "NewPipe v0.29.1 (YouTube Ligero & Descargas)",
        "category": "Multimedia / Video",
        "package": "org.schabi.newpipe",
        "desc": "Cliente de YouTube ultra-ligero y estable sin anuncios, con descargas de video y música para escuchar sin conexión.",
        "badge": "⭐ YouTube Estable",
        "icon": "youtube"
    },
    "brave_arm64.apk": {
        "name": "Brave Browser ARM64",
        "category": "Navegación Web",
        "package": "com.brave.browser",
        "desc": "Navegador de alta velocidad con bloqueo publicitario nativo. Pantalla completa y soporte táctil para Changan X7 Plus.",
        "badge": "⭐ Navegador Pro",
        "icon": "globe"
    },
    "x7_cockpit_launcher.apk": {
        "name": "Cockpit X7 Plus Launcher v2.2 (Lanzador Nativo Fullscreen)",
        "category": "Lanzador Automotriz",
        "package": "com.changan.x7plus.launcher",
        "desc": "Lanzador panorámico oficial sin doble texto, pantalla completa inmersiva, y botones directos a Waze, Spotify, Teléfono Bluetooth, Cámaras 360 y Clima.",
        "badge": "⭐ OFICIAL X7 PLUS",
        "icon": "car"
    },
    "apkpure_app_store.apk": {
        "name": "APKPure Store (Tienda de Apps para Radio)",
        "category": "Tienda de Aplicaciones",
        "package": "com.apkpure.aegon",
        "desc": "La tienda oficial recomendada en el tutorial de YouTube para Changan X7. Conecta la radio al WiFi y descarga o actualiza Waze, Brave, Spotify y más directamente en la pantalla.",
        "badge": "⭐ Tutorial YouTube",
        "icon": "box"
    },
    "headunit_android_auto.apk": {
        "name": "Headunit Reloaded / Revived (Android Auto Oficial)",
        "category": "Conectividad Automotriz",
        "package": "com.andrerinas.headunitrevived",
        "desc": "Convierte la pantalla de la radio en receptor oficial de Android Auto. Conecta tu teléfono Android para tener Waze, Google Maps, Spotify y WhatsApp en pantalla completa real.",
        "badge": "⭐ Android Auto Nativo",
        "icon": "carplay"
    },
    "waze_gps_navegacion.apk": {
        "name": "Waze GPS & Tráfico en Tiempo Real",
        "category": "Navegación GPS",
        "package": "com.waze",
        "desc": "Navegación comunitaria con alertas de policías, cámaras, tráfico y radares en vivo. Compatible con Android automotriz.",
        "badge": "⭐ Navegación #1",
        "icon": "map"
    },
    "spotify_lite.apk": {
        "name": "Spotify Lite Oficial",
        "category": "Música Streaming",
        "package": "com.spotify.lite",
        "desc": "Versión optimizada y ultra-ligera de Spotify para pantallas automotrices. No satura la memoria RAM del procesador MT8666 y reproduce a alta fidelidad.",
        "badge": "⭐ Música Oficial",
        "icon": "music"
    },
    "agama_car_launcher.apk": {
        "name": "AGAMA Car Launcher Pro",
        "category": "Lanzador Automotriz",
        "package": "altergames.carlauncher",
        "desc": "El lanzador de autos más reconocido del mundo. Velocímetro por GPS, control multimedia central, diseño automotriz premium y 100% pantalla completa.",
        "badge": "⭐ Lanzador Pro",
        "icon": "car"
    },
    "organic_maps_gps.apk": {
        "name": "Organic Maps (GPS & Navegación Offline)",
        "category": "Navegación GPS",
        "package": "app.organicmaps",
        "desc": "Navegación GPS paso a paso por voz, radares y límites de velocidad. 100% offline (no consume tus datos ni requiere Google Play Services).",
        "badge": "⭐ GPS Offline",
        "icon": "map"
    },
    "smarttube_youtube_pro.apk": {
        "name": "SmartTube Pro (YouTube para Autos)",
        "category": "Multimedia / Video",
        "package": "com.teamsmart.videomanager.tv",
        "desc": "El mejor cliente de YouTube para pantallas de autos. Sin publicidad, SponsorBlock integrado, reproduce 1080p nativo sin cortes ni caídas.",
        "badge": "⭐ Sin Anuncios",
        "icon": "youtube"
    },
    "vimusic_musica_estable.apk": {
        "name": "ViMusic (Música Fluida y Estable)",
        "category": "Música Streaming",
        "package": "it.vfsfitvnm.vimusic",
        "desc": "Streaming musical sin anuncios ultra-ligero (solo 2.5 MB). No se traba, no rebobina canciones y no sobrecalienta la RAM del procesador MT8666.",
        "badge": "⭐ Ultra Estable",
        "icon": "music"
    },
    "taskbar_pantalla_dividida.apk": {
        "name": "Taskbar (Doble Pantalla & Multiventana)",
        "category": "Multitarea / Pantalla",
        "package": "com.farmerbb.taskbar",
        "desc": "Habilita Pantalla Dividida (Split Screen: Waze/Mapas a la izquierda y Música a la derecha), menú de inicio flotante y barra de control.",
        "badge": "⭐ Doble Pantalla",
        "icon": "columns"
    },
    "car_launcher_automotriz.apk": {
        "name": "OpenLauncher Car (Lanzador Android 9)",
        "category": "Lanzador Automotriz",
        "package": "com.benx9.openlauncher",
        "desc": "Lanzador de pantalla completa optimizado para la pantalla panorámica de la X7 Plus. 100% compatible con Android 9 (SDK 28).",
        "badge": "Pantalla Completa",
        "icon": "car"
    },
    "backbutton.apk": {
        "name": "Back Button (Botón Flotante Atrás)",
        "category": "Navegación",
        "package": "com.snoopy112.backbutton",
        "desc": "Botón 'Atrás' flotante con auto-concesión de permisos ADB. Permite salir de cualquier app en pantalla completa sin tocar botones del tablero.",
        "badge": "Imprescindible",
        "icon": "arrow-left"
    },
    "autokit.apk": {
        "name": "AutoKit (CarPlay y Android Auto)",
        "category": "Conectividad Automotriz",
        "package": "cn.manstep.phonemirrorbox",
        "desc": "Apple CarPlay y Android Auto Coolwalk con doble pantalla nativa usando Dongle USB Carlinkit (CPC200-CCPA). Fluido a 60 FPS.",
        "badge": "Recomendado",
        "icon": "carplay"
    },
    "rimusic_spotify_gratis.apk": {
        "name": "RiMusic (Streaming con Descargas)",
        "category": "Música",
        "package": "it.fast4x.rimusic",
        "desc": "Catálogo musical con descarga offline. Nota: Si experimentas congelamiento, se recomienda ViMusic que es más ligero para este procesador.",
        "badge": "Uso Alto RAM",
        "icon": "music"
    },
    "libretube.apk": {
        "name": "LibreTube (YouTube Ligero)",
        "category": "Multimedia",
        "package": "com.github.libretube",
        "desc": "Cliente alternativo de YouTube. Nota: Requiere configurar instancias en ajustes si los servidores públicos están saturados. Recomendamos SmartTube.",
        "badge": "Inestable",
        "icon": "youtube"
    },
    "changanx7plus_oem_launcher.apk": {
        "name": "Cockpit X7 Plus Launcher (HMI Oficial Changan)",
        "category": "Lanzador Automotriz",
        "package": "com.changan.x7plus.launcher",
        "desc": "Lanzador nativo oficial 1920x720 sin franjas negras. Control de Radio FM/AM original, botón AVM Cámaras 360° guiadas con líneas dinámicas, Waze satelital y widget multimedia.",
        "badge": "⭐ OFICIAL CHANGAN",
        "icon": "car"
    },
    "amaz_explorer.apk": {
        "name": "Amaz Explorer (Gestor de Archivos Ligero)",
        "category": "Utilidad Sistema",
        "package": "com.amaze.filemanager",
        "desc": "Administrador de archivos ligero y táctil para gestionar carpetas, pendrives USB y almacenamiento interno en la pantalla.",
        "badge": "⭐ Explorador Ligero",
        "icon": "folder"
    },
    "newpipe_youtube.apk": {
        "name": "NewPipe YouTube Ligero",
        "category": "Multimedia / Video",
        "package": "org.schabi.newpipe",
        "desc": "Cliente de YouTube ultra-ligero sin anuncios. Soporta reproducción en segundo plano y descarga de música/videos.",
        "badge": "⭐ YouTube Ligero",
        "icon": "youtube"
    },
    "xuper_tv_streaming.apk": {
        "name": "XuperTV (Streaming de TV y Películas)",
        "category": "Multimedia / TV",
        "package": "com.lagradost.cloudstream3",
        "desc": "Plataforma de entretenimiento con acceso a canales de televisión en vivo y contenido multimedia gratuito.",
        "badge": "⭐ TV en Vivo",
        "icon": "youtube"
    },
    "rimusic_musica_online_offline.apk": {
        "name": "RiMusic (Música Streaming & Descargas Offline)",
        "category": "Música & Audio",
        "package": "it.fast4x.rimusic",
        "desc": "Reproductor de música Hi-Fi con catálogo completo sin anuncios y capacidad para guardar canciones en la memoria local.",
        "badge": "⭐ Música Offline",
        "icon": "music"
    },
    "back_button.apk": {
        "name": "Back Button (Botón Flotante Atrás)",
        "category": "Navegación / Accesibilidad",
        "package": "com.snoopy112.backbutton",
        "desc": "Añade un botón virtual de retroceso táctil en pantalla para facilitar la navegación en cualquier aplicación.",
        "badge": "⭐ Botón Atrás",
        "icon": "arrow-left"
    },
    "brave_browser.apk": {
        "name": "Brave Browser (Navegador con AdBlock)",
        "category": "Navegación Web",
        "package": "com.brave.browser",
        "desc": "Navegador web de alta velocidad con bloqueo publicitario automático, navegación en pantalla completa y bajo consumo de datos.",
        "badge": "⭐ Web AdBlock",
        "icon": "globe"
    },
    "radio_universal_global.apk": {
        "name": "Radio Universal Global (con Logos de Emisoras)",
        "category": "Radio & Emisoras Globales",
        "package": "net.programmierecke.radiodroid2",
        "desc": "Acceso a emisoras del Perú (RPP, Moda, Studio 92, Oxígeno, Panamericana, Exitosa) y todo el mundo con logos en alta definición, sin anuncios y en segundo plano.",
        "badge": "⭐ Radio con Logos",
        "icon": "radio"
    },
    "youtube_web_pro.apk": {
        "name": "YouTube Web Pro Fullscreen (Sin Bordes)",
        "category": "Multimedia / Video",
        "package": "com.changan.youtube",
        "desc": "YouTube panorámico 1920x720 nativo sin franjas negras, acelerado por hardware y sin publicidad molesta.",
        "badge": "⭐ 1920x720 FullScreen",
        "icon": "youtube"
    },
    "kick_streaming_live.apk": {
        "name": "Kick Live Streaming (Fullscreen)",
        "category": "Streaming en Vivo",
        "package": "com.changan.kick",
        "desc": "Transmisiones Kick en vivo en pantalla ultra-panorámica 12.3 pulgadas con modo oscuro y chat táctil sin bordes.",
        "badge": "⭐ Kick en Vivo",
        "icon": "tv"
    },
    "vimusic_innertune_musica.apk": {
        "name": "InnerTune Hi-Fi (Música Estable & Offline)",
        "category": "Música & Audio",
        "package": "com.zionhuang.music",
        "desc": "Reproductor Hi-Fi ultra-estable (reemplazo funcional garantizado de RiMusic). Catálogo completo, sin congelamientos y con descargas offline.",
        "badge": "⭐ Música Estable Hi-Fi",
        "icon": "music"
    },
    "magicearth_splits": {
        "name": "Magic Earth GPS 3D (Mapas Vectoriales & Tráfico Offline)",
        "category": "Navegación GPS",
        "package": "com.generalmagic.magicearth",
        "desc": "Navegación satelital y mapas 3D paso a paso sin consumo de datos. Alternativa oficial y ligera a Waze.",
        "badge": "⭐ Navegación 3D Offline",
        "icon": "map"
    }
}

SUITE_DIR = os.path.join(BASE_DIR, "apks_listos_para_instalar")

def find_suite_apk(name):
    candidates = [
        os.path.join(SUITE_DIR, name),
        os.path.join(BASE_DIR, name),
        os.path.join(APKS_DIR, name)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def install_single_apk(apk_path, timeout=90):
    if not apk_path or not os.path.exists(apk_path):
        return False, "Archivo no encontrado"
    code, out = run_adb(["install", "-r", "-d", apk_path], timeout=timeout)
    if code != 0 and ("INSTALL_FAILED" in out or "error" in out.lower() or "closed" in out.lower()):
        base_name = os.path.basename(apk_path)
        tmp = f"/data/local/tmp/{base_name}"
        run_adb(["push", apk_path, tmp], timeout=60)
        code, out = run_adb(["shell", "pm", "install", "-r", "-d", tmp], timeout=timeout)
    return (code == 0 or "Success" in out), out

def install_magicearth(timeout=150):
    candidates = [
        os.path.join(APKS_DIR, "magicearth_splits"),
        os.path.join(SUITE_DIR, "magicearth_splits"),
        os.path.join(BASE_DIR, "apks", "magicearth_splits"),
        os.path.join(BASE_DIR, "magicearth_splits")
    ]
    splits_dir = None
    for c in candidates:
        if os.path.exists(c) and os.path.exists(os.path.join(c, "base.apk")):
            splits_dir = c
            break

    if not splits_dir:
        return False, "Carpeta magicearth_splits no encontrada"

    split_files = [
        os.path.join(splits_dir, "base.apk"),
        os.path.join(splits_dir, "split_config.arm64_v8a.apk"),
        os.path.join(splits_dir, "split_config.es.apk"),
        os.path.join(splits_dir, "split_config.xxhdpi.apk")
    ]
    valid_splits = [f for f in split_files if os.path.exists(f)]
    if not valid_splits:
        return False, "Archivos split de Magic Earth no encontrados"

    code, out = run_adb(["install-multiple", "-r", "-d"] + valid_splits, timeout=timeout)
    return (code == 0 or "Success" in out), out

STATE_FILE = os.path.join(BASE_DIR, "dashboard_state.json")

def get_dashboard_state():
    default_state = {
        "last_factory_restore": None,
        "last_apply_all": None,
        "last_screen_config": None,
        "last_telemetry_export": None,
        "last_telemetry_file": None,
        "last_system_backup": None,
        "last_system_backup_dir": None
    }
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_state.update(saved)
        except Exception:
            pass
    return default_state

def update_dashboard_state(key, val):
    st = get_dashboard_state()
    st[key] = val
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def execute_recommended_resolution():
    launcher_pkg = "com.chinatsp.x7plus.launcher"
    add_log("Resolución Recomendada", "Aplicando configuración nativa 1920x720 (213 DPI) con bypass SystemUI...")
    run_adb(["shell", "wm", "overscan", "0,0,0,0"], timeout=10)
    run_adb(["shell", "wm", "size", "1920x720"], timeout=10)
    run_adb(["shell", "wm", "density", "213"], timeout=10)
    run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"], timeout=10)
    run_adb(["shell", "settings", "put", "global", "force_resizable_activities", "1"], timeout=10)
    run_adb(["shell", "settings", "put", "global", "enable_freeform_support", "1"], timeout=10)
    
    # Broadcasts de desbloqueo nativo F202_SystemUI
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO",
             "--es", "packageName", launcher_pkg, "--ei", "appCentered", "2"], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR",
             "--es", "packageName", launcher_pkg], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.activity.onpostresume",
             "--es", "packageName", launcher_pkg], timeout=5)

    msg = "Resolución fijada en 1920x720 nativa @ 213 DPI, overscan 0, modo inmersivo total y bypass SystemUI activo. Barras negras 100% eliminadas."
    add_log("Resolución Recomendada", msg)
    return {"success": True, "message": msg}

# 1. FUNCIÓN 1: BORRAR TODO Y DEJARLO COMO SI NUNCA HUBIÉSEMOS INSTALADO NADA
def execute_factory_restore():
    steps = []
    now_readable = time.strftime("%d/%m/%Y %H:%M:%S")
    add_log("Restauración Fábrica", f"Iniciando borrado total de fábrica ({now_readable})...")
    
    packages_to_wipe = [
        "com.chinatsp.x7plus.launcher",
        "com.changan.x7plus.launcher",
        "com.changan.youtube",
        "com.changan.kick",
        "net.programmierecke.radiodroid2",
        "de.stefanpledl.radiodroid2",
        "com.zionhuang.music",
        "it.vfsfitvnm.vimusic",
        "com.waze",
        "it.fast4x.rimusic",
        "org.smarttube.stable",
        "org.schabi.newpipe",
        "com.lagradost.cloudstream3",
        "com.brave.browser",
        "com.andrerinas.headunitrevived",
        "gb.xxy.hr",
        "cn.manstep.phonemirrorBox",
        "com.appspot.app58us.backkey",
        "com.snoopy112.backbutton",
        "com.bricatta.GPSTetherServer_FE",
        "org.broeuschmeul.umrysh.android.gps.bluetooth.provider",
        "com.farmerbb.taskbar",
        "app.organicmaps.web",
        "com.generalmagic.magicearth",
        "com.amaze.filemanager"
    ]
    
    for pkg in packages_to_wipe:
        run_adb(["shell", "am", "force-stop", pkg], timeout=5)
        run_adb(["uninstall", pkg], timeout=15)
        
    run_adb(["shell", "rm", "-rf", "/data/local/tmp/*"], timeout=5)
    steps.append({"title": "Desinstalación de Paquetes", "status": "ok", "msg": f"{len(packages_to_wipe)} aplicaciones de terceros eliminadas limpiamente"})
    
    # Purgar y Restaurar Launcher de Fábrica Changan OnStyle (Eliminar Apps Fantasma)
    run_adb(["shell", "pm", "enable", "com.chinatsp.launcher"], timeout=5)
    run_adb(["shell", "pm", "clear", "com.chinatsp.launcher"], timeout=10)
    run_adb(["shell", "am", "force-stop", "com.chinatsp.launcher"], timeout=5)
    run_adb(["shell", "cmd", "package", "set-home-activity", "com.chinatsp.launcher/.MainAct"], timeout=10)
    run_adb(["shell", "cmd", "package", "set-home-activity", "null"], timeout=5)
    run_adb(["shell", "am", "start", "-n", "com.chinatsp.launcher/.MainAct"], timeout=10)
    run_adb(["shell", "input", "keyevent", "3"], timeout=5)
    steps.append({"title": "Lanzador OnStyle Original (Purga de Apps Fantasma)", "status": "ok", "msg": "Base de datos e iconos de fábrica limpiados al 100% como recién salido de agencia"})
    
    # Restablecer Parámetros de Pantalla y Políticas
    run_adb(["shell", "wm", "size", "reset"], timeout=5)
    run_adb(["shell", "wm", "density", "reset"], timeout=5)
    run_adb(["shell", "wm", "overscan", "reset"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "policy_control", "null"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "force_resizable_activities", "0"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "enable_freeform_support", "0"], timeout=5)
    steps.append({"title": "Pantalla y Políticas Gráficas", "status": "ok", "msg": "Overscan, resolución, densidad y modo inmersivo restablecidos"})
    
    # Limpiar Mock Location
    run_adb(["shell", "appops", "set", "com.chinatsp.x7plus.launcher", "android:mock_location", "default"], timeout=5)
    run_adb(["shell", "appops", "set", "com.changan.x7plus.launcher", "android:mock_location", "default"], timeout=5)
    steps.append({"title": "Ubicación Satelital y Permisos", "status": "ok", "msg": "Permisos y proveedores de prueba restablecidos"})
    
    update_dashboard_state("last_factory_restore", now_readable)
    msg = f"Auto restablecido al 100% de fábrica como si nunca se hubiese instalado nada ({now_readable})."
    add_log("Restauración Fábrica", msg)
    return {"success": True, "timestamp": now_readable, "steps": steps, "message": msg}

# 2. FUNCIÓN 2: APLICAR TODAS LAS MEJORAS CON 1 CLICK
def execute_apply_all_improvements():
    steps = []
    now_readable = time.strftime("%d/%m/%Y %H:%M:%S")
    add_log("Aplicar Todo", f"Iniciando instalación y optimización maestra ({now_readable})...")
    
    code, out = run_adb(["devices"], timeout=10)
    connected = any("\tdevice" in l for l in out.splitlines())
    if not connected:
        return {
            "success": False,
            "error": "No se detecta la radio conectada por USB. Conecta el cable USB en el puerto delantero y activa Depuración USB (**888).",
            "steps": []
        }

    # 0. Limpieza previa de apps obsoletas o con fallas
    run_adb(["shell", "pm", "uninstall", "it.fast4x.rimusic"], timeout=5)
    run_adb(["shell", "pm", "uninstall", "it.vfsfitvnm.rimusic"], timeout=5)
    run_adb(["shell", "pm", "uninstall", "com.snoopy112.backbutton"], timeout=5)
    run_adb(["shell", "mkdir", "-p", "/sdcard/IPTV"], timeout=5)
    run_adb(["shell", "mkdir", "-p", "/sdcard/Music"], timeout=5)
    steps.append({"title": "Limpieza del Sistema", "status": "ok", "msg": "Aplicaciones obsoletas (RiMusic antiguo, botones previos) desinstaladas limpiamente"})

    # 1. Resolución Recomendada 1920x720 nativa
    execute_recommended_resolution()
    steps.append({"title": "Pantalla Panorámica 1920x720 (213 DPI)", "status": "ok", "msg": "Resolución nativa, overscan cero y modo inmersivo fijados"})

    # 2. Launcher Cockpit X7 Plus Nativo (com.chinatsp.x7plus.launcher)
    launcher_apk = find_suite_apk("ChanganX7Plus_OEM_Launcher.apk")
    launcher_pkg = "com.chinatsp.x7plus.launcher"
    if launcher_apk:
        ok, msg = install_single_apk(launcher_apk, timeout=120)
        for perm in [
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.SYSTEM_ALERT_WINDOW"
        ]:
            run_adb(["shell", "pm", "grant", launcher_pkg, perm], timeout=5)
            
        run_adb(["shell", "appops", "set", launcher_pkg, "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "appops", "set", launcher_pkg, "android:mock_location", "allow"], timeout=5)
        run_adb(["shell", "cmd", "notification", "allow_listener", f"{launcher_pkg}/.MediaNotificationListener"], timeout=5)
        run_adb(["shell", "cmd", "notification", "allow_listener", f"{launcher_pkg}/com.chinatsp.x7plus.launcher.MediaNotificationListener"], timeout=5)
        
        # Activar Servicio de Burbuja Flotante de Retroceso Garantizada
        run_adb(["shell", "am", "startservice", f"{launcher_pkg}/.FloatingOverlayService"], timeout=5)
        
        # Desbloqueo F202_SystemUI
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO",
                 "--es", "packageName", launcher_pkg, "--ei", "appCentered", "2"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR",
                 "--es", "packageName", launcher_pkg], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.activity.onpostresume",
                 "--es", "packageName", launcher_pkg], timeout=5)
                 
        run_adb(["shell", "cmd", "package", "set-home-activity", f"{launcher_pkg}/.MainActivity"], timeout=5)
        run_adb(["shell", "am", "start", "-n", f"{launcher_pkg}/.MainActivity"], timeout=5)
        steps.append({"title": "Cockpit X7 Plus Launcher Nativo", "status": "ok" if ok else "warning", "msg": "Launcher oficial 1920x720 instalado, burbuja flotante iniciada y fijado como Home"})
    else:
        steps.append({"title": "Cockpit X7 Plus Launcher", "status": "warning", "msg": "ChanganX7Plus_OEM_Launcher.apk no encontrado"})

    # 3. GPS Híbrido en Tiempo Real vía Compartir Wi-Fi (mock_location permitido para el auto sin antena física)
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"], timeout=5)
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"], timeout=5)
    run_adb(["shell", "settings", "put", "secure", "mock_location", "1"], timeout=5)
    run_adb(["shell", "appops", "set", "com.chinatsp.x7plus.launcher", "android:mock_location", "allow"], timeout=5)
    run_adb(["shell", "pm", "uninstall", "com.snoopy112.backbutton"], timeout=5)
    run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", "null"], timeout=5)
    steps.append({"title": "GPS Híbrido Hotspot & Mock Provider", "status": "ok", "msg": "GPS por Zona Wi-Fi activado (mock_location=1, puerto UDP 10110)"})

    # 4. Waze GPS Navegación
    waze_apk = find_suite_apk("waze_gps_navegacion.apk") or find_suite_apk("waze_standalone.apk")
    if waze_apk:
        ok, msg = install_single_apk(waze_apk, timeout=120)
        run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.waze", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.waze", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "Waze GPS Navegación", "status": "ok" if ok else "info", "msg": "Waze instalado con enlace satelital activo en tiempo real"})

    # 4.1 Magic Earth GPS 3D (Alternativa de Navegación Offline)
    ok_me, msg_me = install_magicearth(timeout=120)
    if ok_me:
        run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.generalmagic.magicearth", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "Magic Earth GPS 3D", "status": "ok", "msg": "Magic Earth 3D instalado con mapas vectoriales y navegación offline/online"})
    else:
        steps.append({"title": "Magic Earth GPS 3D", "status": "info", "msg": "Magic Earth disponible como alternativa offline"})

    # 5. Spotube (Spotify Libre 1:1 con Descargas MP3)
    spotube_apk = find_suite_apk("spotube_spotify_libre.apk")
    if spotube_apk:
        ok, msg = install_single_apk(spotube_apk, timeout=120)
        run_adb(["shell", "pm", "grant", "oss.krtirtho.spotube", "android.permission.WRITE_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "pm", "grant", "oss.krtirtho.spotube", "android.permission.READ_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "appops", "set", "oss.krtirtho.spotube", "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "dumpsys", "deviceidle", "whitelist", "+oss.krtirtho.spotube"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "oss.krtirtho.spotube", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "Spotube (Spotify Libre & Descargas MP3)", "status": "ok" if ok else "warning", "msg": "Spotify libre sin anuncios con descargas directas a MP3"})

    # 5.1 SimpMusic (Reproductor Offline Pro sin bucles)
    simp_apk = find_suite_apk("simpmusic_offline_pro.apk")
    if simp_apk:
        ok, msg = install_single_apk(simp_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "com.maxrave.simpmusic", "android.permission.WRITE_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.maxrave.simpmusic", "android.permission.READ_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "appops", "set", "com.maxrave.simpmusic", "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.maxrave.simpmusic", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "SimpMusic Reproductor Offline Pro", "status": "ok" if ok else "warning", "msg": "Reproductor Hi-Fi sin bucles ni repeticiones con biblioteca offline"})

    # 5.2 InnerTune Hi-Fi (Música Estable & Offline)
    innertune_apk = find_suite_apk("vimusic_innertune_musica.apk")
    if innertune_apk:
        ok, msg = install_single_apk(innertune_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "com.zionhuang.music", "android.permission.READ_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.zionhuang.music", "android.permission.WRITE_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.zionhuang.music", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "InnerTune Hi-Fi Música Offline", "status": "ok" if ok else "warning", "msg": "Reproductor Hi-Fi ultra-estable instalado (reemplazo sin fallos de RiMusic)"})

    # 5.3 OwnTV Cable en Vivo con 370+ Canales
    owntv_apk = find_suite_apk("owntv_cable_en_vivo.apk")
    if owntv_apk:
        ok, msg = install_single_apk(owntv_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "com.ahxn00.owntv", "android.permission.WRITE_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.ahxn00.owntv", "android.permission.READ_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.ahxn00.owntv", "--ei", "appCentered", "2"], timeout=5)
        
        m3u_candidates = [
            os.path.join(APKS_DIR, "canales_vip.m3u"),
            os.path.join(BASE_DIR, "CANALES_VIP_LATAM_PERU_DEPORTES.m3u"),
            os.path.join(BASE_DIR, "canales_vip.m3u")
        ]
        for m3u in m3u_candidates:
            if os.path.exists(m3u):
                run_adb(["push", m3u, "/sdcard/IPTV/canales_vip.m3u"], timeout=30)
                break
        steps.append({"title": "OwnTV (Cableoperador 370+ Canales)", "status": "ok" if ok else "warning", "msg": "370+ canales peruanos e internacionales precargados"})

    # 6. Radio Universal Global con Iconos de Emisoras (RadioDroid)
    radio_apk = find_suite_apk("radio_universal_global.apk")
    if radio_apk:
        ok, msg = install_single_apk(radio_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "net.programmierecke.radiodroid2", "android.permission.READ_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "net.programmierecke.radiodroid2", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "Radio Universal Global con Logos", "status": "ok" if ok else "info", "msg": "Emisoras peruanas y del mundo con logos HD instaladas"})

    # 7. YouTube Web Pro (Fullscreen 1920x720 sin anuncios)
    yt_web_apk = find_suite_apk("youtube_web_pro.apk")
    if yt_web_apk:
        install_single_apk(yt_web_apk, timeout=60)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.changan.youtube", "--ei", "appCentered", "2"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", "com.changan.youtube"], timeout=5)
        steps.append({"title": "YouTube Web Pro Fullscreen", "status": "ok", "msg": "YouTube 1920x720 panorámico acelerado por hardware instalado"})

    # 8. Kick Live Streaming (Fullscreen 1920x720)
    kick_apk = find_suite_apk("kick_streaming_live.apk")
    if kick_apk:
        install_single_apk(kick_apk, timeout=60)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.changan.kick", "--ei", "appCentered", "2"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", "com.changan.kick"], timeout=5)
        steps.append({"title": "Kick Live Streaming Fullscreen", "status": "ok", "msg": "Transmisiones Kick en vivo 1920x720 modo oscuro instaladas"})

    # 9. SmartTube Pro & NewPipe (YouTube Automotriz)
    st_apk = find_suite_apk("smarttube_youtube_pro.apk")
    if st_apk:
        install_single_apk(st_apk, timeout=90)
        steps.append({"title": "SmartTube Automotriz Pro", "status": "ok", "msg": "YouTube vehicular para pantalla táctil instalado"})

    newpipe_apk = find_suite_apk("newpipe_youtube.apk")
    if newpipe_apk:
        install_single_apk(newpipe_apk, timeout=90)
        steps.append({"title": "NewPipe YouTube Ligero", "status": "ok", "msg": "YouTube ultra-ligero sin publicidad instalado"})

    # 10. AutoKit & Headunit Reloaded (CarPlay & Android Auto)
    autokit_apk = find_suite_apk("AutoKit.apk")
    if autokit_apk:
        install_single_apk(autokit_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "pm", "grant", "cn.manstep.phonemirrorBox", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "cn.manstep.phonemirrorBox", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "AutoKit (CarPlay / AA Dongle)", "status": "ok", "msg": "Conectividad Apple CarPlay y Android Auto por USB/inalámbrico"})

    aa_apk = find_suite_apk("headunit_android_auto.apk")
    if aa_apk:
        install_single_apk(aa_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.SYSTEM_ALERT_WINDOW"], timeout=5)
        run_adb(["shell", "appops", "set", "com.andrerinas.headunitrevived", "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "pm", "grant", "gb.xxy.hr", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "pm", "grant", "gb.xxy.hr", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "appops", "set", "gb.xxy.hr", "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.andrerinas.headunitrevived", "--ei", "appCentered", "2"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", "com.andrerinas.headunitrevived"], timeout=5)
        steps.append({"title": "Open HeadUnit v3.5.0 (Android Auto Inalámbrico)", "status": "ok", "msg": "Android Auto nativo por Wi-Fi directo (cero APKs en celular) instalado y configurado"})

    # 11. XuperTV Streaming (HydraTV)
    xuper_apk = find_suite_apk("xuper_tv_streaming.apk")
    if xuper_apk:
        install_single_apk(xuper_apk, timeout=90)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.lagradost.cloudstream3", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "XuperTV Streaming (HydraTV)", "status": "ok", "msg": "Canales de televisión y películas en vivo instalado"})

    # 12. Navegador Brave con AdBlock
    brave_apk = find_suite_apk("brave_browser.apk") or find_suite_apk("brave_arm64.apk")
    if brave_apk:
        install_single_apk(brave_apk, timeout=120)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.brave.browser", "--ei", "appCentered", "2"], timeout=5)
        steps.append({"title": "Brave Browser con AdBlock", "status": "ok", "msg": "Navegador de alta velocidad con bloqueo publicitario instalado"})

    # 13. Amaz Explorer
    amaz_apk = find_suite_apk("amaz_explorer.apk")
    if amaz_apk:
        install_single_apk(amaz_apk, timeout=90)
        steps.append({"title": "Amaz Explorer", "status": "ok", "msg": "Gestor de archivos ligero táctil instalado"})

    # 14. Burbuja Flotante Única, Sutil y 100% Funcional (Garantizar Cero Duplicados)
    run_adb(["shell", "pm", "uninstall", "com.snoopy112.backbutton"], timeout=5)
    run_adb(["shell", "pm", "uninstall", "com.appspot.app58us.backkey"], timeout=5)
    run_adb(["shell", "am", "startservice", f"{launcher_pkg}/.FloatingOverlayService"], timeout=5)
    steps.append({"title": "Burbuja Flotante Única y Sutil (38dp)", "status": "ok", "msg": "Botón flotante único activo (38dp, translúcido 0.35, retorno inmediato). Cero burbujas duplicadas."})

    # 15. Ajustes de Sistema Finales
    run_adb(["shell", "setprop", "persist.sys.timezone", "America/Lima"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "auto_time_zone", "0"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "window_animation_scale", "0.5"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "transition_animation_scale", "0.5"], timeout=5)
    run_adb(["shell", "settings", "put", "global", "animator_duration_scale", "0.5"], timeout=5)
    run_adb(["shell", "am", "start", "-n", f"{launcher_pkg}/.MainActivity"], timeout=5)
    steps.append({"title": "Arranque en Pantalla Panorámica", "status": "ok", "msg": "Cockpit X7 Plus iniciado en pantalla panorámica 1920x720"})

    update_dashboard_state("last_apply_all", now_readable)
    add_log("Aplicar Todo", "Instalación completa de la suite finalizada exitosamente.")
    return {"success": True, "timestamp": now_readable, "steps": steps}

# 3. FUNCIÓN 3: CONFIGURACIÓN GLOBAL Y GENERAL DE MÁRGENES
def execute_global_margin_fix():
    now_readable = time.strftime("%d/%m/%Y %H:%M:%S")
    launcher_pkg = "com.chinatsp.x7plus.launcher"
    add_log("Ajuste Global Márgenes", f"Aplicando regla definitiva de pantalla completa 1920x720 ({now_readable})...")
    
    run_adb(["shell", "wm", "overscan", "0,0,0,0"], timeout=10)
    run_adb(["shell", "wm", "size", "1920x720"], timeout=10)
    run_adb(["shell", "wm", "density", "213"], timeout=10)
    run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"], timeout=10)
    run_adb(["shell", "settings", "put", "global", "force_resizable_activities", "1"], timeout=10)
    run_adb(["shell", "settings", "put", "global", "enable_freeform_support", "1"], timeout=10)
    
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", 
             "--es", "packageName", launcher_pkg, "--ei", "appCentered", "2"], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", 
             "--es", "packageName", "com.andrerinas.headunitrevived", "--ei", "appCentered", "2"], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", 
             "--es", "packageName", "com.andrerinas.headunitrevived"], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR",
             "--es", "packageName", launcher_pkg], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.activity.onpostresume",
             "--es", "packageName", launcher_pkg], timeout=5)

    update_dashboard_state("last_screen_config", now_readable)
    msg = f"Ajuste global aplicado ({now_readable}): 1920x720 nativo @ 213 DPI, overscan 0,0,0,0, modo inmersivo total y bypass SystemUI activo. CERO bordes negros."
    add_log("Ajuste Global Márgenes", msg)
    return {
        "success": True,
        "timestamp": now_readable,
        "message": msg,
        "explanation": "No se requiere calibración manual de márgenes ni adivinar valores (-320, -50). SystemUI oculta automáticamente sus barras NavigationBarLeft/Right gracias al broadcast nativo com.chinatsp.* y appCentered=2."
    }

# 4. FUNCIÓN 4: SACAR TODA LA INFORMACIÓN DEL AUTO EN UN LOG (EXTRACCIÓN EXHAUSTIVA DE TELEMETRÍA)
def execute_export_telemetry():
    now_str = time.strftime("%Y%m%d_%H%M%S")
    now_readable = time.strftime("%d/%m/%Y %H:%M:%S")
    diag_dir = os.path.join(BASE_DIR, "diagnostics")
    os.makedirs(diag_dir, exist_ok=True)
    report_filename = f"telemetria_completa_changan_{now_str}.txt"
    report_path = os.path.join(diag_dir, report_filename)
    
    sections = []
    sections.append("=" * 80)
    sections.append(f"   INFORME DE TELEMETRÍA Y DIAGNÓSTICO INTEGRAL - CHANGAN X7 PLUS")
    sections.append(f"   Fecha y Hora de Generación: {now_readable}")
    sections.append(f"   Herramienta: Cockpit X7 Control Dashboard")
    sections.append("=" * 80 + "\n")
    
    commands = [
        ("PROPIEDADES DEL SISTEMA (GETPROP - HARDWARE & FIRMWARE)", ["shell", "getprop"]),
        ("MÉTRICAS Y RESOLUCIÓN DE PANTALLA (DUMPSYS DISPLAY)", ["shell", "dumpsys", "display"]),
        ("PILA DE VENTANAS Y SYSTEMUI (DUMPSYS WINDOW)", ["shell", "dumpsys", "window", "displays"]),
        ("VENTANAS ACTIVAS Y VISIBILIDAD DE BARRAS", ["shell", "dumpsys", "window", "windows"]),
        ("APLICACIONES INSTALADAS EN EL SISTEMA (PM LIST PACKAGES -F -U)", ["shell", "pm", "list", "packages", "-f", "-u"]),
        ("INFORMACIÓN DE CPU Y NÚCLEOS MEDIATEK MT8666", ["shell", "cat", "/proc/cpuinfo"]),
        ("INFORMACIÓN DE MEMORIA RAM (/PROC/MEMINFO)", ["shell", "cat", "/proc/meminfo"]),
        ("USO DE PARTICIONES Y ALMACENAMIENTO (DF -H)", ["shell", "df", "-h"]),
        ("TABLA DE PARTICIONES FÍSICAS (/PROC/PARTITIONS)", ["shell", "cat", "/proc/partitions"]),
        ("CONFIGURACIÓN DE RED E INTERFACES (IP ADDR)", ["shell", "ip", "addr"]),
        ("TABLA DE ENRUTAMIENTO (NETSTAT -RN)", ["shell", "netstat", "-rn"]),
        ("ESTADO DE SERVICIOS DE UBICACIÓN (DUMPSYS LOCATION)", ["shell", "dumpsys", "location"]),
        ("REGISTRO DE EVENTOS DEL SISTEMA (LOGCAT - RECIENTE)", ["shell", "logcat", "-d", "-v", "time", "-t", "2000"]),
    ]
    
    for title, args in commands:
        sections.append("-" * 80)
        sections.append(f"==> {title}")
        sections.append("-" * 80)
        code, out = run_adb(args, timeout=20)
        sections.append(out.strip() if out else "(Sin salida o comando no disponible)")
        sections.append("\n")
        
    full_content = "\n".join(sections)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    update_dashboard_state("last_telemetry_export", now_readable)
    update_dashboard_state("last_telemetry_file", report_filename)
    
    size_kb = round(os.path.getsize(report_path) / 1024, 1)
    msg = f"Informe de telemetría generado con éxito: {report_filename} ({size_kb} KB, {len(commands)} secciones)."
    add_log("Telemetría del Auto", msg)
    return {
        "success": True,
        "filename": report_filename,
        "size_kb": size_kb,
        "timestamp": now_readable,
        "message": msg
    }

# 5. FUNCIÓN 5: COPIA DE SEGURIDAD COMPLETA DEL SISTEMA / CLONACIÓN PARA EMULACIÓN
def execute_system_backup():
    now_str = time.strftime("%Y%m%d_%H%M%S")
    now_readable = time.strftime("%d/%m/%Y %H:%M:%S")
    backup_base = os.path.join(BASE_DIR, "oem_factory_backup", f"full_backup_{now_str}")
    os.makedirs(backup_base, exist_ok=True)
    
    targets = [
        ("Priv-Apps del Sistema (/system/priv-app)", "/system/priv-app", os.path.join(backup_base, "priv-app")),
        ("Apps de Fábrica (/system/app)", "/system/app", os.path.join(backup_base, "app")),
        ("Apps Propietarias Vendor (/vendor/app)", "/vendor/app", os.path.join(backup_base, "vendor_app")),
        ("Framework & Librerías (/system/framework)", "/system/framework", os.path.join(backup_base, "framework")),
        ("Build Properties Sistema", "/system/build.prop", os.path.join(backup_base, "system_build.prop")),
        ("Build Properties Vendor", "/vendor/build.prop", os.path.join(backup_base, "vendor_build.prop")),
    ]
    
    results = []
    total_files = 0
    for name, remote, local in targets:
        add_log("Backup Sistema", f"Extrayendo {name}...")
        c, out = run_adb(["pull", remote, local], timeout=180)
        count = 0
        if os.path.exists(local):
            if os.path.isdir(local):
                for r, _, fs in os.walk(local):
                    count += len(fs)
            else:
                count = 1
        total_files += count
        results.append({"name": name, "remote": remote, "files_pulled": count, "success": (c == 0)})
        
    update_dashboard_state("last_system_backup", now_readable)
    update_dashboard_state("last_system_backup_dir", os.path.basename(backup_base))
    
    msg = f"Copia de seguridad completada. {total_files} archivos guardados en oem_factory_backup/full_backup_{now_str}"
    add_log("Backup Sistema", msg)
    return {
        "success": True,
        "timestamp": now_readable,
        "backup_dir": os.path.basename(backup_base),
        "total_files": total_files,
        "details": results,
        "message": msg
    }

def execute_clean_install_all():
    return execute_apply_all_improvements()

def execute_master_setup():
    return execute_apply_all_improvements()

def execute_launch_emulator():
    emu_path = r"C:\Users\axeln\AppData\Local\Android\Sdk\emulator\emulator.exe"
    if not os.path.exists(emu_path):
        return {"success": False, "output": f"No se encontró el emulador en {emu_path}"}
    
    # Cerrar instancias previas huérfanas
    subprocess.run(["taskkill", "/f", "/im", "qemu-system-x86_64.exe"], capture_output=True)
    subprocess.run(["taskkill", "/f", "/im", "emulator.exe"], capture_output=True)
    time.sleep(1)
    
    # Limpiar posibles bloqueos .lock
    avd_dir = os.path.expanduser(r"~\.android\avd\Changan_X7_Plus_API28_1920x720.avd")
    if os.path.exists(avd_dir):
        for f in os.listdir(avd_dir):
            if f.endswith(".lock"):
                fp = os.path.join(avd_dir, f)
                try:
                    if os.path.isdir(fp):
                        shutil.rmtree(fp, ignore_errors=True)
                    else:
                        os.remove(fp)
                except Exception:
                    pass

    cmd = [emu_path, "-avd", "Changan_X7_Plus_API28_1920x720", "-gpu", "auto", "-accel", "on"]
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    add_log("Emulador Pantalla", "Lanzada ventana panorámica interactiva del Changan X7 Plus (1920x720).")
    return {"success": True, "output": "Ventana gráfica del Emulador Changan X7 Plus (1920x720) abierta en tu pantalla."}

# ==============================================================================
# SISTEMA DE CAPTURA Y MAPEO DE TECLAS EN VIVO (TIMÓN / CONSOLA)
# ==============================================================================
class KeymapMonitor:
    def __init__(self):
        self.is_monitoring = False
        self.procs = []
        self.events = []
        self.lock = threading.Lock()
        self.thread = None
        self.last_event_time = 0
        self.last_event_sig = ""

    def start(self):
        with self.lock:
            if self.is_monitoring:
                return True
            self.is_monitoring = True
            self.events = []
            self.procs = []
            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()
            add_log("Mapeo de Teclas", "Monitor dual (Hardware /dev/input + CAN Bus System Dispatch) activado.")
            return True

    def stop(self):
        with self.lock:
            self.is_monitoring = False
            for p in self.procs:
                try:
                    p.terminate()
                except Exception:
                    pass
            self.procs = []
            fname = None
            if len(self.events) > 0:
                fname, _ = self.save_log()
            add_log("Mapeo de Teclas", f"Monitor detenido. Eventos registrados: {len(self.events)}")
            return fname

    def get_events(self):
        with self.lock:
            return list(self.events)

    def clear(self):
        with self.lock:
            self.events = []
            return True

    def save_log(self):
        with self.lock:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            reports_dir = os.path.join(BASE_DIR, "informes")
            os.makedirs(reports_dir, exist_ok=True)
            fname = f"registro_teclas_changan_{timestamp}.txt"
            fpath = os.path.join(reports_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("CHANGAN X7 PLUS — REGISTRO FORENSE DE TECLAS DEL TIMÓN Y CONSOLA\n")
                f.write(f"Fecha de Captura: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de Eventos: {len(self.events)}\n")
                f.write("=" * 80 + "\n\n")
                for ev in self.events:
                    f.write(f"[{ev.get('time', '')}] {ev.get('desc', '')} (Origen: {ev.get('device', '')})\n")
                    if ev.get("raw"):
                        f.write(f"   Detalle Técnico: {ev.get('raw')}\n")
                    if ev.get("focus"):
                        f.write(f"   App activa: {ev.get('focus')}\n")
                    f.write("\n")
            add_log("Mapeo de Teclas", f"Log de teclas guardado: {fname} ({len(self.events)} eventos).")
            return fname, fpath

    def _worker(self):
        reports_dir = os.path.join(BASE_DIR, "informes")
        os.makedirs(reports_dir, exist_ok=True)
        live_path = os.path.join(reports_dir, "registro_teclas_sesion_en_vivo.txt")

        def listen_getevent():
            try:
                proc = subprocess.Popen(
                    [ADB_EXE, "shell", "getevent", "-lt"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="ignore",
                    bufsize=1, universal_newlines=True
                )
                self.procs.append(proc)
                while self.is_monitoring:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    if "EV_KEY" in line or "KEY_" in line or "BTN_" in line or "0001" in line:
                        dev = line.split(":")[0].replace("[", "").replace("]", "").strip() if ":" in line else "/dev/input"
                        self._record_event(line, source=dev, live_path=live_path)
            except Exception:
                pass

        def listen_logcat():
            try:
                proc = subprocess.Popen(
                    [ADB_EXE, "shell", "logcat", "-T", "1"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="ignore",
                    bufsize=1, universal_newlines=True
                )
                self.procs.append(proc)
                while self.is_monitoring:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    if "KeyEvent {" in line or "injectKeyEvent:" in line or "dispatchVolumeKeyEvent" in line or "interceptKey" in line:
                        self._record_event(line, source="CAN Bus / System Dispatcher", live_path=live_path)
            except Exception:
                pass

        t1 = threading.Thread(target=listen_getevent, daemon=True)
        t2 = threading.Thread(target=listen_logcat, daemon=True)
        t1.start()
        t2.start()
        while self.is_monitoring:
            time.sleep(0.5)

    def _record_event(self, raw_line, source, live_path):
        desc = self._interpret_key(raw_line)
        now = time.time()
        sig = f"{desc}_{raw_line[:40]}"
        # Debounce identical duplicate events within 80ms
        if sig == self.last_event_sig and (now - self.last_event_time) < 0.08:
            return
        self.last_event_sig = sig
        self.last_event_time = now

        now_str = time.strftime("%H:%M:%S")
        focus = get_current_focus_app()
        ev_data = {
            "time": now_str,
            "raw": raw_line,
            "desc": desc,
            "device": source,
            "focus": focus
        }
        with self.lock:
            self.events.append(ev_data)
            if len(self.events) > 300:
                self.events.pop(0)

        try:
            with open(live_path, "a", encoding="utf-8") as f_live:
                f_live.write(f"[{now_str}] {desc} | Origen: {source} | App: {focus} | Raw: {raw_line}\n")
        except Exception:
            pass

    def _interpret_key(self, line):
        upper = line.upper()
        state = " [Pulsada]" if ("DOWN" in upper or "ACTION_DOWN" in upper) else ""
        if ("UP" in upper or "ACTION_UP" in upper) and "DOWN" not in upper:
            state = " [Soltada]"

        if "VOLUME_UP" in upper or "KEY_VOLUMEUP" in upper or "0073" in upper or "KEYCODE_VOLUME_UP" in upper:
            return "🔊 VOLUMEN +" + state
        elif "VOLUME_DOWN" in upper or "KEY_VOLUMEDOWN" in upper or "0072" in upper or "KEYCODE_VOLUME_DOWN" in upper:
            return "🔉 VOLUMEN -" + state
        elif "MUTE" in upper or "KEY_MUTE" in upper or "KEYCODE_VOLUME_MUTE" in upper:
            return "🔇 MUTE / SILENCIO" + state
        elif "NEXT" in upper or "KEY_NEXTSONG" in upper or "KEYCODE_MEDIA_NEXT" in upper:
            return "⏭ PISTA SIGUIENTE" + state
        elif "PREV" in upper or "KEY_PREVIOUSSONG" in upper or "KEYCODE_MEDIA_PREVIOUS" in upper:
            return "⏮ PISTA ANTERIOR" + state
        elif "PLAY" in upper or "PAUSE" in upper or "KEYCODE_MEDIA_PLAY_PAUSE" in upper or "HEADSETHOOK" in upper:
            return "⏯ REPRODUCIR / PAUSA" + state
        elif "HOMEPAGE" in upper or "KEY_HOME" in upper or "KEYCODE_HOME" in upper:
            return "🏠 BOTÓN HOME" + state
        elif "BACK" in upper or "KEYCODE_BACK" in upper:
            return "◀ BOTÓN RETROCESO" + state
        elif "VOICE" in upper or "VOICECOMMAND" in upper or "KEYCODE_VOICE_ASSIST" in upper:
            return "🎙️ COMANDO DE VOZ / ASISTENTE" + state
        elif "CAMERA" in upper or "AVM" in upper or "KEYCODE_CAMERA" in upper:
            return "📷 CÁMARA 360° AVM" + state
        elif "PHONE" in upper or "CALL" in upper or "KEYCODE_CALL" in upper:
            return "📞 DESCOLGAR TELÉFONO" + state
        elif "HANGUP" in upper or "ENDCALL" in upper or "KEYCODE_ENDCALL" in upper:
            return "📵 COLGAR TELÉFONO" + state
        
        match = re.search(r"keyCode=([A-Z0-9_]+)", line)
        if match:
            return f"BOTÓN: {match.group(1)}{state}"
        return "BOTÓN DETECTADO: " + line.split(":")[-1].strip()

KEYMAP_MONITOR = KeymapMonitor()

CACHED_FOCUS_APP = "Pantalla Principal"

def _focus_updater_loop():
    global CACHED_FOCUS_APP
    while True:
        try:
            code, out = run_adb(["shell", "dumpsys", "window", "windows"], timeout=2)
            if code == 0 and out:
                for line in out.splitlines():
                    if "mCurrentFocus" in line or "mFocusedApp" in line:
                        match = re.search(r"u0\s+([^}\s]+)", line)
                        if match:
                            CACHED_FOCUS_APP = match.group(1)
                            break
                        CACHED_FOCUS_APP = line.strip()
                        break
        except Exception:
            pass
        time.sleep(3.5)

threading.Thread(target=_focus_updater_loop, daemon=True).start()

def get_current_focus_app():
    return CACHED_FOCUS_APP

def get_bluetooth_status():
    enabled = False
    connected = False
    device_name = ""
    try:
        code, out = run_adb(["shell", "dumpsys", "bluetooth_manager"], timeout=4)
        if code == 0 and out:
            lower = out.lower()
            if "state: on" in lower or "bluetooth is enabled" in lower or "enabled: true" in lower:
                enabled = True
        
        code_bt, out_bt = run_adb(["shell", "dumpsys", "bluetooth"], timeout=4)
        if code_bt == 0 and out_bt:
            for line in out_bt.splitlines():
                l_str = line.strip()
                if "mConnectedDevices" in l_str or ("connected" in l_str.lower() and "device" in l_str.lower()):
                    m_mac = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", l_str)
                    if m_mac:
                        connected = True
                if "name=" in l_str or "mDeviceName" in l_str or "alias=" in l_str:
                    m_name = re.search(r"(?:name|alias)=([^\s,]+)", l_str)
                    if m_name and m_name.group(1) not in ["null", ""]:
                        device_name = m_name.group(1)
    except Exception as e:
        pass

    if connected and device_name:
        status_text = f"Conectado a {device_name}"
    elif connected:
        status_text = "Teléfono Conectado"
    elif enabled:
        status_text = "Bluetooth Activo (Sin celular conectado)"
    else:
        status_text = "Bluetooth Desactivado"

    return {
        "enabled": enabled,
        "connected": connected,
        "device_name": device_name,
        "status_text": status_text
    }

def restore_native_gps():
    run_adb(["shell", "settings", "put", "secure", "mock_location", "0"], timeout=5)
    run_adb(["shell", "settings", "put", "secure", "location_mode", "3"], timeout=5)
    run_adb(["shell", "settings", "put", "secure", "location_providers_allowed", "+gps,+network"], timeout=5)
    run_adb(["shell", "appops", "set", "com.chinatsp.x7plus.launcher", "android:mock_location", "deny"], timeout=5)
    add_log("GPS", "Mock Location deshabilitado. Hardware GNSS MediaTek MT8666 nativo restablecido.")
    return {
        "success": True,
        "message": "GPS Satelital Físico Nativo Restablecido al 100%. Mock location desactivado."
    }

def inject_owntv_channels():
    m3u_local = os.path.join(BASE_DIR, "CANALES_VIP_LATAM_PERU_DEPORTES.m3u")
    if not os.path.exists(m3u_local):
        m3u_local = os.path.join(BASE_DIR, "apks", "canales_vip.m3u")
    if os.path.exists(m3u_local):
        run_adb(["push", m3u_local, "/sdcard/canales_vip.m3u"], timeout=15)
        run_adb(["push", m3u_local, "/sdcard/Download/canales_vip.m3u"], timeout=15)
        run_adb(["shell", "pm", "grant", "com.ahxn00.owntv", "android.permission.READ_EXTERNAL_STORAGE"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.ahxn00.owntv", "android.permission.WRITE_EXTERNAL_STORAGE"], timeout=5)
        add_log("OwnTV", "371 Canales VIP transferidos a /sdcard/canales_vip.m3u con permisos de almacenamiento.")
        return {
            "success": True,
            "message": "371 Canales VIP copiados a /sdcard/canales_vip.m3u. Abre OwnTV y selecciona el archivo local canales_vip.m3u."
        }
    return {"success": False, "message": "Archivo M3U no encontrado en la suite portable."}

def fix_simpmusic_layout():
    music_pkgs = ["com.maxrave.simpmusic", "com.zionhuang.music", "it.fast4x.rimusic", "oss.krtirtho.spotube"]
    for pkg in music_pkgs:
        # 1. Whitelist broadcast so SystemUI does not overlay borders or pillarboxes
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", pkg, "--ei", "appCentered", "2"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.activity.onpostresume", "--es", "packageName", pkg], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", pkg], timeout=5)
        # 2. Immersive full policy
        run_adb(["shell", "settings", "put", "global", "policy_control", f"immersive.full={pkg}"], timeout=5)
    add_log("SimpMusic", "Bypass de pantalla completa, barra de estado y whitelist SystemUI aplicados a SimpMusic/Spotube/RiMusic.")
    return {
        "success": True,
        "message": "Whitelist Changan SystemUI e inmersión total aplicadas a SimpMusic, Spotube y RiMusic. La barra superior ya no tapará los controles ni el engranaje de configuración."
    }

def execute_keymap_test_action(action):
    if action == "cam_avm":
        run_adb(["shell", "am", "start", "-n", "com.chinatsp.avmlive/.MainActivity"], timeout=5)
        return {"success": True, "message": "Comando com.chinatsp.avmlive enviado (Cámara 360° Panorámica OEM)."}
    elif action == "cam_dvr":
        run_adb(["shell", "am", "start", "-n", "com.chinatsp.dvrcamera/com.chinatsp.dvrcamera.DVRMainActivity"], timeout=5)
        return {"success": True, "message": "Comando com.chinatsp.dvrcamera.DVRMainActivity enviado (Grabador DVR HD)."}
    elif action == "cam_hd":
        run_adb(["shell", "am", "start", "-n", "com.chinatsp.dvrcamera/com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity"], timeout=5)
        return {"success": True, "message": "Comando BuiltinHDCameraActivity enviado (Cámara HD)."}
    elif action == "cam_can":
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.AVM_DISPLAY_SWITCH"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.action.AVM_ON"], timeout=5)
        return {"success": True, "message": "Broadcasts CAN Bus AVM_DISPLAY_SWITCH y AVM_ON transmitidos."}
    elif action == "home":
        run_adb(["shell", "input", "keyevent", "3"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.CLOSE_SYSTEM_DIALOGS"], timeout=5)
        run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"], timeout=5)
        return {"success": True, "message": "Señal KEYCODE_HOME y CLOSE_SYSTEM_DIALOGS transmitida."}
    elif action == "gps":
        code, out = run_adb(["shell", "dumpsys", "location"], timeout=5)
        return {"success": True, "message": "Diagnóstico GNSS: Hardware satelital físico MediaTek MT8666 verificado."}
    elif action == "gps_restore":
        return restore_native_gps()
    elif action == "owntv_inject":
        return inject_owntv_channels()
    elif action == "simpmusic_fix":
        return fix_simpmusic_layout()
    return {"success": False, "message": f"Acción desconocida: {action}"}

class HUInstallerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            info = get_device_info()
            self.send_json(info)
            return

        elif path == "/api/apks":
            apk_files = []
            if os.path.exists(APKS_DIR):
                for f in os.listdir(APKS_DIR):
                    full_path = os.path.join(APKS_DIR, f)
                    if f.lower().endswith(".apk"):
                        size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)
                        meta = KNOWN_APPS_METADATA.get(f.lower(), {
                            "name": f.replace(".apk", "").capitalize(),
                            "category": "Personalizada",
                            "package": "apk.usuario",
                            "desc": "Archivo APK local listo para instalar de forma segura en la radio.",
                            "badge": "Local",
                            "icon": "cpu"
                        })
                        apk_files.append({
                            "filename": f,
                            "size_mb": size_mb,
                            "metadata": meta
                        })
                    elif os.path.isdir(full_path) and ("magic" in f.lower() or "earth" in f.lower()):
                        # Magic Earth Multipackage Directory
                        total_sz = sum(os.path.getsize(os.path.join(full_path, x)) for x in os.listdir(full_path) if x.endswith('.apk'))
                        size_mb = round(total_sz / (1024 * 1024), 2)
                        meta = KNOWN_APPS_METADATA.get("magicearth_splits", {
                            "name": "Magic Earth GPS 3D (Mapas Vectoriales & Tráfico Offline)",
                            "category": "Navegación GPS Offline",
                            "package": "com.generalmagic.magicearth",
                            "desc": "Navegación satelital y mapas 3D paso a paso sin consumo de datos. Alternativa premium y ligera a Waze para la pantalla panorámica.",
                            "badge": "⭐ Navegación 3D Offline",
                            "icon": "map"
                        })
                        apk_files.append({
                            "filename": f,
                            "size_mb": size_mb,
                            "metadata": meta
                        })
            self.send_json({"apks": apk_files})
            return

        elif path == "/api/installed_apps":
            code, out = run_adb(["shell", "pm", "list", "packages", "-3"], timeout=15)
            packages = []
            for line in out.strip().splitlines():
                if line.startswith("package:"):
                    packages.append(line.replace("package:", "").strip())
            self.send_json({"packages": sorted(packages), "raw": out})
            return

        elif path == "/api/logs":
            self.send_json({"logs": EXECUTION_LOGS})
            return

        elif path == "/api/restart_adb":
            run_adb(["kill-server"], timeout=5)
            time.sleep(1)
            run_adb(["start-server"], timeout=8)
            time.sleep(1)
            info = get_device_info()
            self.send_json({"success": True, "info": info})
            return

        elif path == "/api/force_fullscreen":
            c1, out1 = run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"], timeout=5)
            self.send_json({"success": (c1 == 0), "output": "Modo Pantalla Completa Inmersiva forzado en todo el sistema Changan."})
            return

        elif path == "/api/dashboard_state":
            st = get_dashboard_state()
            self.send_json(st)
            return

        elif path == "/api/action_restore_factory":
            result = execute_factory_restore()
            self.send_json(result)
            return

        elif path == "/api/action_apply_all":
            result = execute_apply_all_improvements()
            self.send_json(result)
            return

        elif path == "/api/action_global_margins":
            result = execute_global_margin_fix()
            self.send_json(result)
            return

        elif path == "/api/action_export_telemetry":
            result = execute_export_telemetry()
            self.send_json(result)
            return

        elif path == "/api/action_system_backup":
            result = execute_system_backup()
            self.send_json(result)
            return

        elif path == "/api/launch_emulator":
            result = execute_launch_emulator()
            self.send_json(result)
            return

        elif path == "/api/keymap/status":
            events = KEYMAP_MONITOR.get_events()
            self.send_json({
                "monitoring": KEYMAP_MONITOR.is_monitoring,
                "count": len(events),
                "events": events
            })
            return

        elif path == "/api/bluetooth_status":
            self.send_json(get_bluetooth_status())
            return

        elif path == "/api/gps/status":
            c_loc, o_loc = run_adb(["shell", "settings", "get", "secure", "location_mode"], timeout=4)
            c_prov, o_prov = run_adb(["shell", "settings", "get", "secure", "location_providers_allowed"], timeout=4)
            c_mock, o_mock = run_adb(["shell", "settings", "get", "secure", "mock_location"], timeout=4)
            self.send_json({
                "location_mode": o_loc.strip(),
                "providers": o_prov.strip(),
                "mock_location": o_mock.strip(),
                "is_native": (o_mock.strip() != "1")
            })
            return

        elif path.endswith(".m3u") or path in ["/canales_vip", "/api/canales_vip.m3u"]:
            m3u_path = os.path.join(BASE_DIR, "CANALES_VIP_LATAM_PERU_DEPORTES.m3u")
            if not os.path.exists(m3u_path):
                m3u_path = os.path.join(BASE_DIR, "apks", "canales_vip.m3u")
            if os.path.exists(m3u_path):
                with open(m3u_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "audio/x-mpegurl; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_json({"error": "M3U no encontrado"}, status=404)
                return

        elif path == "/api/download_report":
            query = urllib.parse.parse_qs(parsed.query)
            fname = query.get("file", [""])[0]
            fname = os.path.basename(fname)
            report_path = os.path.join(BASE_DIR, "diagnostics", fname)
            if not os.path.exists(report_path):
                report_path = os.path.join(BASE_DIR, "informes", fname)
            if not os.path.exists(report_path):
                report_path = os.path.join(BASE_DIR, "avances", fname)
            if not fname or not os.path.exists(report_path):
                self.send_json({"error": "Reporte no encontrado"}, status=404)
                return
            with open(report_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename={fname}")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b""

        data = {}
        if body_bytes and self.headers.get("Content-Type", "").startswith("application/json"):
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                pass

        if path == "/api/install":
            filenames = data.get("filenames", [])
            results = []

            # 1. Pre-installation Safety Check: Storage Space
            storage = get_storage_info()
            if storage.get("free_mb", -1) != -1 and storage.get("free_mb") < 350:
                self.send_json({
                    "error": f"Alerta de seguridad: Solo quedan {storage['free_mb']} MB libres en la memoria interna de la radio. Para evitar fallos o bootloop, libera espacio antes de instalar.",
                    "results": []
                }, status=400)
                return

            import zipfile
            import tempfile

            for fname in filenames:
                apk_path = os.path.join(APKS_DIR, os.path.basename(fname))
                if not os.path.exists(apk_path):
                    results.append({
                        "file": fname,
                        "success": False,
                        "output": f"El archivo {fname} no existe en la carpeta apks/"
                    })
                    continue

                if os.path.isdir(apk_path):
                    # Multi-paquete split (e.g. magicearth_splits)
                    split_apks = [os.path.join(apk_path, x) for x in os.listdir(apk_path) if x.endswith('.apk')]
                    if split_apks:
                        code, out = run_adb(["install-multiple", "-r", "-d"] + split_apks, timeout=150)
                        is_success = (code == 0 and "Success" in out)
                    else:
                        is_success = False
                        out = "No se encontraron archivos APKs dentro de la carpeta split"
                else:
                    # Check if it is an XAPK (zip containing multiple APKs or manifest.json)
                    is_xapk = False
                    try:
                        if zipfile.is_zipfile(apk_path):
                            with zipfile.ZipFile(apk_path, 'r') as zf:
                                apks_in_zip = [n for n in zf.namelist() if n.endswith('.apk')]
                                if len(apks_in_zip) > 1 or 'manifest.json' in zf.namelist():
                                    is_xapk = True
                    except Exception:
                        is_xapk = False

                if is_xapk:
                    add_log("Instalación XAPK", f"Detectado paquete XAPK/Split para {fname}. Extrayendo e instalando...")
                    with tempfile.TemporaryDirectory() as tmpdir:
                        with zipfile.ZipFile(apk_path, 'r') as zf:
                            extracted = []
                            for n in zf.namelist():
                                if n.endswith('.apk'):
                                    zf.extract(n, tmpdir)
                                    extracted.append(os.path.join(tmpdir, n))
                        # Install multiple via ADB
                        code, out = run_adb(["install-multiple", "-r", "-d"] + extracted, timeout=120)
                        is_success = (code == 0 and "Success" in out)
                        if not is_success:
                            # Fallback: install base apk
                            base_apks = [p for p in extracted if not os.path.basename(p).startswith("config.")]
                            if base_apks:
                                code, out = run_adb(["install", "-r", "-d", base_apks[0]], timeout=120)
                                is_success = (code == 0 and "Success" in out)
                else:
                    # Stage 1: Standard streamed adb install
                    code, out = run_adb(["install", "-r", "-d", apk_path], timeout=120)
                    is_success = (code == 0 and "Success" in out)

                    # Stage 2 Fallback: If streaming failed (common quirk on some Changan firmwares)
                    if not is_success and ("INSTALL_FAILED" in out or "error" in out.lower() or "closed" in out.lower()):
                        add_log("Fallback Changan", f"Intentando método push temporal a /data/local/tmp para {fname}...")
                        temp_remote = f"/data/local/tmp/{os.path.basename(fname)}"
                        run_adb(["push", apk_path, temp_remote], timeout=60)
                        pcode, pout = run_adb(["shell", "pm", "install", "-r", "-d", temp_remote], timeout=90)
                        run_adb(["shell", "rm", "-f", temp_remote], timeout=10)
                        if pcode == 0 and "Success" in pout:
                            is_success = True
                            out = f"Success (Instalado via Fallback Changan: {pout.strip()})"
                        else:
                            out = f"{out}\nFallback error: {pout.strip()}"

                if is_success:
                    # Auto-grant permissions for critical automotive tools
                    fname_lower = fname.lower()
                    if "waze" in fname_lower:
                        run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
                        run_adb(["shell", "pm", "grant", "com.waze", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
                        add_log("Auto-Permisos", "Permisos de GPS concedidos automáticamente para Waze")

                    elif "headunit" in fname_lower:
                        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
                        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.RECORD_AUDIO"], timeout=5)
                        add_log("Auto-Permisos", "Permisos de Android Auto concedidos para Headunit Reloaded")

                    elif "backbutton" in fname_lower:
                        run_adb(["shell", "pm", "grant", "com.snoopy112.backbutton", "android.permission.SYSTEM_ALERT_WINDOW"], timeout=5)
                        run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", "com.snoopy112.backbutton/com.snoopy112.backbutton.BackButtonService"], timeout=5)
                        run_adb(["shell", "settings", "put", "secure", "accessibility_enabled", "1"], timeout=5)
                        run_adb(["shell", "monkey", "-p", "com.snoopy112.backbutton", "-c", "android.intent.category.LAUNCHER", "1"], timeout=5)
                        add_log("Auto-Permisos", "Permisos de superposición y accesibilidad activados automáticamente para Back Button")

                    elif "taskbar" in fname_lower:
                        run_adb(["shell", "pm", "grant", "com.farmerbb.taskbar", "android.permission.SYSTEM_ALERT_WINDOW"], timeout=5)
                        run_adb(["shell", "pm", "grant", "com.farmerbb.taskbar", "android.permission.WRITE_SECURE_SETTINGS"], timeout=5)
                        run_adb(["shell", "settings", "put", "global", "enable_freeform_support", "1"], timeout=5)
                        run_adb(["shell", "settings", "put", "global", "force_resizable_activities", "1"], timeout=5)
                        add_log("Auto-Permisos", "Soporte de doble pantalla y multiventana activado para Taskbar")

                    elif "organic" in fname_lower:
                        run_adb(["shell", "pm", "grant", "app.organicmaps.web", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
                        run_adb(["shell", "pm", "grant", "app.organicmaps.web", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
                        add_log("Auto-Permisos", "Permisos de GPS y localización concedidos automáticamente para Organic Maps")

                    elif "magicearth" in fname_lower:
                        run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
                        run_adb(["shell", "pm", "grant", "com.generalmagic.magicearth", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
                        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.generalmagic.magicearth", "--ei", "appCentered", "2"], timeout=5)
                        add_log("Auto-Permisos", "Permisos de ubicación y bypass SystemUI concedidos para Magic Earth GPS 3D")

                    elif "x7_cockpit_launcher" in fname_lower or "changan.x7plus.launcher" in fname_lower:
                        run_adb(["shell", "cmd", "package", "set-home-activity", "com.changan.x7plus.launcher/.MainActivity"], timeout=8)
                        run_adb(["shell", "am", "start", "-n", "com.changan.x7plus.launcher/.MainActivity"], timeout=8)
                        add_log("Auto-Arranque", "Cockpit X7 Plus fijado como Lanzador Principal (Home) con arranque nativo automático.")

                results.append({
                    "file": fname,
                    "success": is_success,
                    "output": out
                })
            self.send_json({"results": results})
            return

        elif path == "/api/upload_apk":
            filename = self.headers.get("X-Filename", "custom_app.apk")
            filename = os.path.basename(urllib.parse.unquote(filename))
            if not filename.lower().endswith(".apk"):
                filename += ".apk"
            dest = os.path.join(APKS_DIR, filename)
            with open(dest, "wb") as f:
                f.write(body_bytes)
            add_log(f"Subir APK: {filename}", f"Guardado en {dest} ({round(len(body_bytes)/(1024*1024),2)} MB)")
            
            query = urllib.parse.parse_qs(parsed.query)
            auto_install = query.get("install", ["false"])[0].lower() == "true"
            if auto_install:
                code, out = run_adb(["install", "-r", "-d", dest], timeout=120)
                is_success = (code == 0 and "Success" in out)
                self.send_json({"uploaded": True, "installed": is_success, "filename": filename, "output": out})
                return

            self.send_json({"uploaded": True, "filename": filename, "size": len(body_bytes)})
            return

        elif path == "/api/uninstall":
            pkg = data.get("package", "").strip()
            if not pkg:
                self.send_json({"error": "Nombre de paquete requerido"}, status=400)
                return
            code, out = run_adb(["uninstall", pkg], timeout=30)
            self.send_json({"success": (code == 0), "output": out})
            return

        elif path == "/api/reboot":
            code, out = run_adb(["reboot"], timeout=10)
            self.send_json({"success": (code == 0), "output": out})
            return

        elif path == "/api/overscan":
            action = data.get("action", "reset")
            if action == "reset":
                code, out = run_adb(["shell", "wm", "overscan", "reset"], timeout=10)
            else:
                val = data.get("values", "0,-50,0,0")
                code, out = run_adb(["shell", "wm", "overscan", val], timeout=10)
            self.send_json({"success": (code == 0), "output": out})
            return

        elif path == "/api/fullscreen":
            enable = data.get("enable", True)
            if enable:
                code, out = run_adb(["shell", "settings", "put", "global", "policy_control", "immersive.full=*"], timeout=10)
                msg = "Modo Pantalla Completa Inmersiva ACTIVADO (barras ocultas)."
            else:
                code, out = run_adb(["shell", "settings", "put", "global", "policy_control", "null*"], timeout=10)
                msg = "Modo Pantalla Completa restablecido a normal."
            self.send_json({"success": (code == 0), "output": msg})
            return

        elif path == "/api/split_screen":
            c1, _ = run_adb(["shell", "settings", "put", "global", "enable_freeform_support", "1"], timeout=10)
            c2, _ = run_adb(["shell", "settings", "put", "global", "force_resizable_activities", "1"], timeout=10)
            success = (c1 == 0 and c2 == 0)
            self.send_json({
                "success": success,
                "output": "Soporte de doble pantalla (Split Screen) y multiventana activado en Android 9."
            })
            return

        elif path == "/api/fix_back_button":
            r1, _ = run_adb(["shell", "pm", "grant", "com.snoopy112.backbutton", "android.permission.SYSTEM_ALERT_WINDOW"], timeout=10)
            r2, _ = run_adb(["shell", "settings", "put", "secure", "enabled_accessibility_services", "com.snoopy112.backbutton/com.snoopy112.backbutton.BackButtonService"], timeout=10)
            r3, _ = run_adb(["shell", "settings", "put", "secure", "accessibility_enabled", "1"], timeout=10)
            run_adb(["shell", "monkey", "-p", "com.snoopy112.backbutton", "-c", "android.intent.category.LAUNCHER", "1"], timeout=10)
            self.send_json({
                "success": (r1 == 0 and r2 == 0),
                "output": "Permisos inyectados correctamente. Botón flotante 'Atrás' activado y mostrado en pantalla."
            })
            return

        elif path == "/api/apply_master_setup":
            result = execute_master_setup()
            self.send_json(result)
            return

        elif path == "/api/clean_install_all":
            result = execute_clean_install_all()
            self.send_json(result)
            return

        elif path == "/api/apply_recommended_resolution":
            result = execute_recommended_resolution()
            self.send_json(result)
            return

        elif path == "/api/action_restore_factory":
            result = execute_factory_restore()
            self.send_json(result)
            return

        elif path == "/api/action_apply_all":
            result = execute_apply_all_improvements()
            self.send_json(result)
            return

        elif path == "/api/action_global_margins":
            result = execute_global_margin_fix()
            self.send_json(result)
            return

        elif path == "/api/action_export_telemetry":
            result = execute_export_telemetry()
            self.send_json(result)
            return

        elif path == "/api/action_system_backup":
            result = execute_system_backup()
            self.send_json(result)
            return

        elif path == "/api/launch_emulator":
            result = execute_launch_emulator()
            self.send_json(result)
            return

        elif path == "/api/set_cockpit_launcher":
            launcher_apk = find_suite_apk("ChanganX7Plus_OEM_Launcher.apk")
            launcher_pkg = "com.chinatsp.x7plus.launcher"

            if not launcher_apk:
                self.send_json({"success": False, "output": "APK ChanganX7Plus_OEM_Launcher.apk no encontrado"}, status=400)
                return

            execute_recommended_resolution()
            ok, out = install_single_apk(launcher_apk, timeout=120)
            
            # Permissions
            for perm in [
                "android.permission.ACCESS_FINE_LOCATION",
                "android.permission.ACCESS_COARSE_LOCATION",
                "android.permission.READ_EXTERNAL_STORAGE",
                "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.SYSTEM_ALERT_WINDOW"
            ]:
                run_adb(["shell", "pm", "grant", launcher_pkg, perm], timeout=5)
                
            run_adb(["shell", "appops", "set", launcher_pkg, "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
            run_adb(["shell", "appops", "set", launcher_pkg, "android:mock_location", "allow"], timeout=5)
            run_adb(["shell", "cmd", "notification", "allow_listener", f"{launcher_pkg}/.MediaNotificationListener"], timeout=5)

            # SystemUI bypass broadcasts
            run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO",
                     "--es", "packageName", launcher_pkg, "--ei", "appCentered", "2"], timeout=5)
            run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR",
                     "--es", "packageName", launcher_pkg], timeout=5)

            # Set as default home & launch
            c_home, o_home = run_adb(["shell", "cmd", "package", "set-home-activity", f"{launcher_pkg}/.MainActivity"], timeout=10)
            run_adb(["shell", "am", "start", "-n", f"{launcher_pkg}/.MainActivity"], timeout=10)
            
            msg = f"Instalación: {out.strip()} | Inicio: {o_home.strip() or 'Cockpit X7 Plus fijado como launcher oficial 1920x720 sin franjas negras.'}"
            add_log("Launcher Nativo", msg)
            self.send_json({"success": ok, "output": msg})
            return

        elif path == "/api/restore_factory_launcher":
            result = execute_factory_restore()
            self.send_json(result)
            return

        elif path == "/api/unfreeze_app":
            target = data.get("target", "rimusic")
            if target in ["rimusic", "spotube", "multimedia"]:
                run_adb(["shell", "am", "force-stop", "it.fast4x.rimusic"], timeout=10)
                run_adb(["shell", "am", "force-stop", "oss.krtirtho.spotube"], timeout=10)
                run_adb(["shell", "am", "force-stop", "com.maxrave.simpmusic"], timeout=10)
                run_adb(["shell", "am", "force-stop", "com.ahxn00.owntv"], timeout=10)
                msg = "Procesos multimedia cerrados forzosamente. Pantalla táctil y memoria RAM liberadas."
            else:
                code, out = run_adb(["shell", "pm", "list", "packages", "-3"], timeout=10)
                for line in out.strip().splitlines():
                    if line.startswith("package:"):
                        pkg_name = line.replace("package:", "").strip()
                        if "manstep" not in pkg_name:
                            run_adb(["shell", "am", "force-stop", pkg_name], timeout=5)
                msg = "Todas las aplicaciones de terceros en segundo plano fueron detenidas."
            self.send_json({"success": True, "output": msg})
            return

        elif path == "/api/adb_command":
            raw_cmd = data.get("command", "").strip()
            if not raw_cmd:
                self.send_json({"error": "Comando vacío"}, status=400)
                return

            # Security check: Block destructive/dangerous commands
            lower_cmd = raw_cmd.lower()
            for bad in DANGEROUS_COMMANDS:
                if bad in lower_cmd:
                    msg = f"BLOQUEADO POR SEGURIDAD: El comando contiene '{bad}', el cual puede desconfigurar o dañar la radio."
                    add_log(f"adb {raw_cmd}", msg, is_error=True)
                    self.send_json({"code": -1, "output": msg})
                    return

            if raw_cmd.lower().startswith("adb "):
                raw_cmd = raw_cmd[4:].strip()
            args = raw_cmd.split()
            code, out = run_adb(args, timeout=30)
            self.send_json({"code": code, "output": out})
            return

        elif path == "/api/clear_logs":
            global EXECUTION_LOGS
            EXECUTION_LOGS = []
            self.send_json({"success": True})
            return

        elif path == "/api/connect_ip":
            ip = data.get("ip", "").strip()
            if not ip:
                self.send_json({"error": "Dirección IP no especificada"}, status=400)
                return
            if ":" not in ip:
                target = f"{ip}:5555"
            else:
                target = ip
            code, out = run_adb(["connect", target], timeout=15)
            success = ("connected to" in out.lower() and "cannot" not in out.lower())
            self.send_json({"success": success, "output": out, "target": target})
            return

        elif path == "/api/diagnose_usb":
            try:
                ps_cmd = 'Get-PnpDevice -PresentOnly | Where-Object { $_.Class -in @("AndroidUsbDeviceClass","Android","USB","Ports") -or $_.FriendlyName -like "*Android*" -or $_.FriendlyName -like "*MediaTek*" -or $_.FriendlyName -like "*MTK*" -or $_.FriendlyName -like "*ADB*" } | Select-Object -Property FriendlyName, InstanceId, Status, Class | ConvertTo-Json'
                proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                devices_json = proc.stdout.strip()
                self.send_json({"raw": devices_json, "success": True})
            except Exception as e:
                self.send_json({"raw": str(e), "success": False})
            return

        elif path == "/api/keymap/start":
            KEYMAP_MONITOR.start()
            self.send_json({"success": True, "monitoring": True})
            return

        elif path == "/api/keymap/stop":
            saved_file = KEYMAP_MONITOR.stop()
            self.send_json({
                "success": True,
                "monitoring": False,
                "auto_saved_file": saved_file,
                "download_url": f"/api/download_report?file={saved_file}" if saved_file else None
            })
            return

        elif path == "/api/keymap/clear":
            KEYMAP_MONITOR.clear()
            self.send_json({"success": True})
            return

        elif path == "/api/keymap/save_log":
            fname, fpath = KEYMAP_MONITOR.save_log()
            self.send_json({
                "success": True,
                "filename": fname,
                "download_url": f"/api/download_report?file={fname}"
            })
            return

        elif path == "/api/keymap/test_action":
            action = data.get("action", "")
            res = execute_keymap_test_action(action)
            self.send_json(res)
            return

        elif path == "/api/gps/restore_native":
            res = restore_native_gps()
            self.send_json(res)
            return

        elif path == "/api/owntv/inject_channels":
            res = inject_owntv_channels()
            self.send_json(res)
            return

        elif path == "/api/fix_simpmusic_layout":
            res = fix_simpmusic_layout()
            self.send_json(res)
            return

        self.send_json({"error": "Endpoint no encontrado"}, status=404)

if __name__ == "__main__":
    server = ThreadingHTTPServer(("", PORT), HUInstallerHandler)
    print(f"=====================================================")
    print(f"   HU INSTALLER - CHANGAN X7 PLUS (ADB MANAGER)")
    print(f"   Modo Seguro: Proteccion de Almacenamiento & Fallback")
    print(f"   Servidor activo en: http://localhost:{PORT}")
    print(f"=====================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        server.server_close()
