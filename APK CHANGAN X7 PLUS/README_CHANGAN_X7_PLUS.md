# 🚘 SISTEMA MAESTRO CHANGAN X7 PLUS (2026 / 2027)
## Dashboard Visual + Cockpit Fullscreen + GPS 100% Offline + Música & Descargas + Botón Deshacer

Este proyecto resuelve de forma definitiva todas las limitaciones de la pantalla multimedia de la **Changan X7 Plus** (Android 9 / MediaTek MT8666 Octa-core / Pantalla Ultrawide 1920x720).

---

## 🎯 1. Soluciones Exactas a Tus Requerimientos

### A. Dashboard Visual Completo (Estilo `api.changan-tools-global.com` / TikTok)
* **¿Qué es?** Un panel visual interactivo que corre en tu laptop conectado a la radio.
* **Archivo para iniciar**: 👉 **`INICIAR_DASHBOARD_CHANGAN.bat`** (se abre en tu navegador o ventana de escritorio en `http://localhost:5050`).
* **Funciones**:
  * Detección en vivo de la conexión con el vehículo (USB o Wi-Fi) y estado de memoria.
  * **Simulador Visual 1920x720**: Te permite probar el lanzador y ver cómo se renderizan las aplicaciones antes de instalarlas.
  * Botón maestro **"APLICAR TODO EN 1 CLIC"**.
  * Gestor para desinstalar apps limpiamente y herramientas de pantalla.

### B. Botón de "Deshacer Cambios / Restaurar de Fábrica" (100% Seguro)
Tienes **dos formas inmediatas** de volver a la interfaz oficial de fábrica:
1. **Desde el Dashboard Visual**: Haz clic en el botón superior amarillo **`↺ Deshacer Cambios (Fábrica)`**.
2. **Desde el archivo Batch directo**: Doble clic en 👉 **`DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat`**.
* **¿Qué hace el botón de deshacer?**
  * Restablece el Launcher oficial Changan OnStyle (`com.chinatsp.launcher`).
  * Quita el modo inmersivo forzado (`policy_control null`).
  * Restablece la resolución y densidad originales (`wm size reset`, `wm density reset`).
  * Detiene cualquier app de terceros. Ninguna partición del sistema es alterada.

### C. Navegación GPS 100% Offline (Cero Dependencia de Celular)
Para no depender de conectar el teléfono por cable ni compartir datos móviles constantemente:
* **Aplicación incluida**: [apks/organicmaps_gps_offline.apk](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/apks/organicmaps_gps_offline.apk) (**Organic Maps** - Open Source).
* **Alternativa instalada**: [apks/magicearth_splits](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/apks/magicearth_splits) (**Magic Earth**).
* **¿Cómo funciona?**
  * Descargas el mapa de tu país/región una sola vez (mediante Wi-Fi o USB) a los más de 6 GB libres de la radio.
  * Funciona **100% offline** utilizando la antena GPS integrada de la Changan X7 Plus.
  * Muestra tu posición en tiempo real, guía por voz paso a paso, radares y límites de velocidad sin consumir un solo mega de tu teléfono.

### D. Música Online con Descargador Local
* **Aplicación incluida**: [apks/rimusic_spotify_gratis.apk](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/apks/rimusic_spotify_gratis.apk) (**RiMusic**).
* **¿Cómo funciona?**
  * Escuchas música en streaming cuando estés conectado al Wi-Fi o hotspot.
  * Dispone de un **botón de descarga directa**: guarda canciones, listas de reproducción o álbumes en el almacenamiento interno de la radio para escucharlos en carretera sin conexión a internet.
  * Compatible con pantalla panorámica y mandos del volante.

### E. Por Qué las Apps no Ocupaban la Pantalla Completa y Cómo se Corrigió
* **La Causa**: En Android 9, las aplicaciones estándar limitan su relación de aspecto a 16:9 (`1.86`), provocando franjas negras laterales en la pantalla de la Changan (que es ultrawide 24:9 o `2.67`).
* **La Solución**:
  1. El instalador ejecuta `adb shell settings put global policy_control immersive.full=*`, eliminando tanto la barra superior como las barras laterales de Android en todas las aplicaciones.
  2. El lanzador `x7_cockpit_launcher.apk` incluye en su manifiesto `android.max_aspect = 3.0` y `android:resizeableActivity="true"`, obligando al motor gráfico a llenar el 100% del cristal de 1920x720.

---

## 🚀 2. Guía Rápida de Uso

1. Conecta tu laptop a la radio del auto con el cable USB frontal.
2. En la radio, abre el marcador telefónico y digita: `**888` para activar **Depuración por USB**.
3. En tu laptop tienes dos opciones:
   * **Modo Visual (Recomendado)**: Ejecuta `INICIAR_DASHBOARD_CHANGAN.bat`. Verás la pantalla conectada, el simulador interactivo y podrás presionar **"APLICAR TODO EN 1 CLIC"**.
   * **Modo Directo por Terminal**: Ejecuta `INSTALAR_TODO_EN_EL_AUTO.bat`.
4. Si alguna vez deseas volver a como vino de fábrica el auto, solo ejecuta `DESHACER_CAMBIOS_Y_RESTAURAR_FABRICA.bat`.
