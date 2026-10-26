# -*- coding: utf-8 -*-
"""
====================================================================
SIMULADOR Y VALIDADOR DE REGLAS DE VENTANA: F202_SystemUI
====================================================================
Simula y valida en PC las reglas exactas extraídas de F202_SystemUI.apk
(Changan X7 Plus - 1920x720 @ 213 DPI, Android 9 Pie)

Reglas Forenses Implementadas:
- com.chinatsp.custom.PageChangeHandler.isSystemAPP()
- com.chinatsp.custom.view.NavigationBarLeft (320px ancho, #000000)
- com.chinatsp.custom.view.NavigationBarRight (320px ancho, #000000)
- PullExpanedView / PullExpandedRightView (Gestos y paneles CarAuto)
- Broadcasts: ACTION_APP_INFO (appCentered=2), ACTION_HIDE_CUSTOM_STATUS_BAR
"""
import os
import sys
import subprocess
import zipfile
import re
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS")
AAPT2 = os.path.join(PROJECT_DIR, "tools", "aapt2.exe")

# Listas oficiales extraídas de classes.dex de F202_SystemUI.apk
OEM_WHITELIST = [
    "com.incall.apps.softmanager",
    "com.cepreitr.ibv.android.catechche",
    "tv.newtv.vcar",
    "com.changan.os.wechatsendcar",
    "com.oushang.weather",
    "com.huawei.hicar.demoapp",
    "com.eryanet.vlink",
    "com.baidu.bodyguard",
    "com.changba.sd",
    "com.chinatsp.dvrcamera",
    "com.os.airconditioner",
    "com.autonavi.amapauto",
    "com.baidu.BaiduMap.auto",
    "com.baidu.naviauto",
    "com.ximalaya.ting.android.car"
]

OEM_FULLSCREEN_LIST = [
    "com.baidu.BaiduMap.auto",
    "com.autonavi.amapauto",
    "com.changba.sd",
    "com.qiyi.video.pad"
]

class F202SystemUISimulator:
    def __init__(self, apk_path):
        self.apk_path = os.path.abspath(apk_path)
        self.package_name = ""
        self.version_name = ""
        self.is_system_app = False
        self.is_third_app_for_screen = False
        self.is_fullscreen_unlocked = False
        self.reasons = []
        self.broadcasts_sent = []
        self.has_overlay_perm = False
        
    def analyze_apk(self):
        print(f"\n[F202 SIMULATOR] Analizando APK: {self.apk_path}")
        if not os.path.exists(self.apk_path):
            raise FileNotFoundError(f"No existe el archivo {self.apk_path}")

        # 1. Extraer Package Name y Permisos con AAPT2
        p = subprocess.run([AAPT2, "dump", "badging", self.apk_path], capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in p.stdout.splitlines():
            if line.startswith("package:"):
                # package: name='com.chinatsp.launcher'
                m = re.search(r"name='([^']+)'", line)
                if m:
                    self.package_name = m.group(1)
                m2 = re.search(r"versionName='([^']+)'", line)
                if m2:
                    self.version_name = m2.group(1)
            if "SYSTEM_ALERT_WINDOW" in line or "SYSTEM_OVERLAY_WINDOW" in line:
                self.has_overlay_perm = True

        # 2. Analizar DEX para Broadcasts y APIs Changan
        with zipfile.ZipFile(self.apk_path, "r") as z:
            for n in z.namelist():
                if n.endswith(".dex"):
                    data = z.read(n)
                    for action in [
                        b"com.chinatsp.systemui.ACTION_APP_INFO",
                        b"com.chinatsp.activity.onpostresume",
                        b"com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR",
                        b"com.chinatsp.action.FULL_SCREEN"
                    ]:
                        if action in data:
                            self.broadcasts_sent.append(action.decode())

        # 3. Evaluar Reglas F202_SystemUI
        self.evaluate_systemui_rules()
        
    def evaluate_systemui_rules(self):
        pkg = self.package_name
        self.reasons = []
        
        # Regla 1: Prefijo com.chinatsp
        if pkg.startswith("com.chinatsp"):
            self.is_system_app = True
            self.reasons.append("COINCIDENCIA OEM 1: El paquete inicia con 'com.chinatsp' (Reconocido automáticamente como Changan Native System App).")
            
        # Regla 2: Prefijo com.android
        elif pkg.startswith("com.android"):
            self.is_system_app = True
            self.reasons.append("COINCIDENCIA OEM 2: El paquete inicia con 'com.android' (AOSP Whitelist).")

        # Regla 3: Whitelist específica
        elif pkg in OEM_WHITELIST:
            self.is_system_app = True
            self.reasons.append(f"COINCIDENCIA OEM 3: Paquete presente en mWhiteList de SystemUI ({pkg}).")

        # Regla 4: Broadcast de Whitelist Dinámica ACTION_APP_INFO con appCentered == 2
        elif "com.chinatsp.systemui.ACTION_APP_INFO" in self.broadcasts_sent:
            self.is_system_app = True
            self.reasons.append("COINCIDENCIA OEM 4: El APK transmite 'ACTION_APP_INFO' (appCentered=2) que programa la persistencia en SharePrefrecenceUtil de SystemUI.")

        # Regla 5: Modo Overlay
        elif self.has_overlay_perm:
            self.reasons.append("COINCIDENCIA OEM 5: Permiso SYSTEM_ALERT_WINDOW detectado (capaz de superponerse a SystemUI).")

        # Verificación de confinamiento
        if pkg in OEM_FULLSCREEN_LIST:
            self.is_third_app_for_screen = True
            self.reasons.append("ADVERTENCIA: Paquete incluido en mFullScreenList de F202 (requiere control de marcos).")
            
        # Veredicto final de Pantalla Completa
        if self.is_system_app and not self.is_third_app_for_screen:
            self.is_fullscreen_unlocked = True
        else:
            self.is_fullscreen_unlocked = False

    def render_simulation_canvas(self, output_img_path):
        W, H = 1920, 720
        img = Image.new("RGB", (W, H), (10, 15, 24))
        draw = ImageDraw.Draw(img)

        # Cargar fuentes estándar
        try:
            font_title = ImageFont.truetype("arial.ttf", 36)
            font_sub = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
            font_hud = ImageFont.truetype("cour.ttf", 20)
        except:
            font_title = font_sub = font_small = font_hud = ImageFont.load_default()

        if not self.is_fullscreen_unlocked:
            # ==========================================================
            # ESTADO: BLOQUEADO (MARCOS Y BARRAS NEGRAS ACTIVOS)
            # ==========================================================
            # 1. Barra Negra Izquierda: Ancho 320px
            draw.rectangle([(0, 0), (320, H)], fill=(0, 0, 0))
            draw.line([(320, 0), (320, H)], fill=(50, 50, 50), width=2)
            draw.text((20, 30), "< Volver", fill=(180, 180, 180), font=font_sub)
            draw.text((20, 200), "12:00", fill=(255, 255, 255), font=font_title)
            draw.text((20, 300), "Right slide to\nvehicle control", fill=(130, 130, 130), font=font_sub)
            draw.text((20, 650), "[O] Inicio Changan", fill=(180, 180, 180), font=font_sub)

            # 2. Barra Negra Derecha: Ancho 320px (de 1600 a 1920)
            draw.rectangle([(1600, 0), (W, H)], fill=(0, 0, 0))
            draw.line([(1600, 0), (1600, H)], fill=(50, 50, 50), width=2)
            draw.text((1620, 30), "[X] Cerrar", fill=(180, 180, 180), font=font_sub)
            draw.text((1620, 300), "Down slide to\nshortcut", fill=(130, 130, 130), font=font_sub)
            draw.text((1620, 650), "200 M / Flujo", fill=(100, 150, 255), font=font_sub)

            # 3. Marco Inferior CarAuto (Altura 90px de 320 a 1600)
            draw.rectangle([(320, 630), (1600, H)], fill=(5, 8, 15))
            draw.line([(320, 630), (1600, 630)], fill=(0, 120, 200), width=2)
            carauto_msg = "Connect phone with CarAuto to use more functions"
            draw.text((450, 655), carauto_msg, fill=(0, 210, 255), font=font_sub)

            # 4. Área Confinada de la App (1280 x 630)
            draw.rectangle([(320, 0), (1600, 630)], fill=(15, 22, 35))
            draw.rectangle([(325, 5), (1595, 625)], outline=(255, 50, 50), width=3)
            
            # Texto de advertencia en pantalla
            draw.text((360, 60), "ESTADO: BLOQUEADO POR F202_SystemUI", fill=(255, 80, 80), font=font_title)
            draw.text((360, 120), f"Paquete detectado: {self.package_name}", fill=(255, 255, 255), font=font_sub)
            draw.text((360, 160), f"Resolución efectiva útil: 1280 x 630 px (¡Pérdida de 640px laterales!)", fill=(255, 200, 80), font=font_sub)
            draw.text((360, 220), "Causa del bloqueo extraída de PageChangeHandler.java:", fill=(200, 200, 200), font=font_sub)
            draw.text((360, 260), "- isSystemAPP() = false (El paquete no inicia con 'com.chinatsp')", fill=(255, 120, 120), font=font_hud)
            draw.text((360, 300), "- addNavigationBar() invocó NavigationBarLeft (320px) + NavigationBarRight (320px)", fill=(255, 120, 120), font=font_hud)
            draw.text((360, 340), "- showThirdAppFullScreen() confinó el Launcher en el marco CarAuto", fill=(255, 120, 120), font=font_hud)

        else:
            # ==========================================================
            # ESTADO: DESBLOQUEADO (100% FULLSCREEN 1920x720)
            # ==========================================================
            # Dibujar el diseño del Cockpit a pantalla completa
            draw.rectangle([(0, 0), (W, H)], fill=(8, 12, 18))
            draw.rectangle([(4, 4), (W-4, H-4)], outline=(0, 230, 255), width=4)

            # Sidebar lateral integrado del Launcher (80px estilo boceto OEM)
            draw.rectangle([(0, 0), (84, H)], fill=(12, 16, 24))
            draw.rectangle([(6, 120), (78, 200)], fill=(0, 100, 220), outline=(0, 230, 255), width=2)
            draw.text((22, 145), "HOME", fill=(255, 255, 255), font=font_small)

            # Contenido principal
            draw.text((120, 40), "F202_SystemUI: BYPASS EXITOSO - 100% FULL SCREEN", fill=(0, 255, 180), font=font_title)
            draw.text((120, 100), f"Paquete OEM Activo: {self.package_name} (v{self.version_name})", fill=(255, 255, 255), font=font_sub)
            draw.text((120, 140), "Resolución Activa: 1920 x 720 px reales | DPI: 213 TVDPI", fill=(0, 220, 255), font=font_sub)

            # Panel de Diagnóstico Forense
            draw.rectangle([(120, 200), (1800, 660)], fill=(14, 20, 30), outline=(0, 160, 220), width=2)
            draw.text((140, 220), "=== CERTIFICACIÓN DE REGLAS DE EJECUCIÓN (AOSP F202) ===", fill=(0, 255, 200), font=font_sub)

            y_pos = 270
            for r in self.reasons:
                draw.text((140, y_pos), f"[APROBADO] {r}", fill=(180, 255, 180), font=font_hud)
                y_pos += 40

            draw.text((140, y_pos + 10), "[APROBADO] hideNaviBar() ejecutado: NavigationBarLeft (320px) = REMOVIDA", fill=(0, 255, 150), font=font_hud)
            draw.text((140, y_pos + 45), "[APROBADO] hideNaviBar() ejecutado: NavigationBarRight (320px) = REMOVIDA", fill=(0, 255, 150), font=font_hud)
            draw.text((140, y_pos + 80), "[APROBADO] hideThirdAppFullScreen() ejecutado: Panel CarAuto = DESACTIVADO", fill=(0, 255, 150), font=font_hud)
            draw.text((140, y_pos + 120), "[VEREDICTO] La unidad multimedia entregará los 1920x720 píxeles nativos al Launcher.", fill=(255, 255, 0), font=font_sub)

        img.save(output_img_path)
        print(f"[F202 SIMULATOR] Simulación visual guardada en: {output_img_path}")
        return img

    def print_verdict(self):
        print("\n" + "="*70)
        print("RESULTADO DE EVALUACIÓN F202_SystemUI:")
        print("="*70)
        print(f"  Paquete: {self.package_name}")
        print(f"  isSystemAPP(): {self.is_system_app}")
        print(f"  isThirdAppForScreen: {self.is_third_app_for_screen}")
        print(f"  Broadcasts de Bypass detectados: {self.broadcasts_sent}")
        print(f"  ESTADO FULLSCREEN (1920x720): {'DESBLOQUEADO (100% Pantalla Completa)' if self.is_fullscreen_unlocked else 'BLOQUEADO (Barras negras activas)'}")
        print("  Razones:")
        for r in self.reasons:
            print(f"    - {r}")
        print("="*70 + "\n")

if __name__ == "__main__":
    target_apk = os.path.join(PROJECT_DIR, "ChanganX7Plus_OEM_Launcher.apk")
    if len(sys.argv) > 1:
        target_apk = sys.argv[1]

    simulator = F202SystemUISimulator(target_apk)
    simulator.analyze_apk()
    simulator.print_verdict()
    out_img = os.path.join(BASE_DIR, "simulador_f202_resultado.png")
    simulator.render_simulation_canvas(out_img)
