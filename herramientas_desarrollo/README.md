# HERRAMIENTAS DE DESARROLLO, INGENIERÍA INVERSA Y DIAGNÓSTICO
## Changan Oshan X7 Plus (Plataforma F202 / R202)

Esta carpeta almacena todas las utilidades técnicas, desensamblados y scripts forenses generados durante la ingeniería inversa del sistema original de la Changan X7 Plus.

---

### Estructura de Subcarpetas:

1. **`ingenieria_inversa/`**
   - Scripts de descompilación y análisis estático de `F202_SystemUI.apk` y `F202_Launcher.apk`.
   - Extracción de bytecode Dalvik DEX (`classes.dex` en `systemui_extracted/`).
   - Lógica de detección de `PageChangeHandler.java`, `isSystemAPP()` y receptores de broadcast.

2. **`dumps_y_dex/`**
   - Desensamblados de métodos smali (`PageChangeHandler_full_methods.txt`, `PageChangeHandler_disassembly.txt`).
   - Tabla de cadenas del sistema (`systemui_all_strings.txt`, `launcher_strings.txt`).
   - Volcados forenses de métodos de broadcast (`onReceive_full.txt`).

3. **`capturas_evidencia/`**
   - Capturas de pantalla generadas durante las pruebas unitarias y de emulación.
   - Evidencias de pantalla completa 1920x720, eliminación de barras de 320px y pruebas de burbuja.

4. **`scripts_mantenimiento/`**
   - Scripts de parchado previo (`apply_fullscreen_bypass.py`, `apply_headunit_updates.py`, etc.).
   - Herramientas de auditoría previa y emulación de imágenes Android (`install_android28_image.py`, `create_avds.py`).
   - Compilador de WebApps automotrices (`build_webapp_apks.py`).

5. **`instalador_web/`**
   - Interfaz HTML/JS con WebUSB para flasheo directo desde navegadores Chromium (`changan_tools_index.html`, `changan_catalog.json`).
