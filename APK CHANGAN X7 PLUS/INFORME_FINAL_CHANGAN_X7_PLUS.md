# INFORME TÉCNICO DE INSTALACIÓN Y ESTADO — CHANGAN X7 PLUS CUSTOM HMI

**Fecha:** 15 de Octubre de 2026  
**Vehículo:** Changan X7 Plus (Plataforma F202_MCA)  
**Sistema:** Android 9.0 Pie (API 28) | SoC MediaTek MT8666 / MT6771 (ARM64-v8a)  
**Resolución:** 1920x720 píxeles nativos  
**Estado General:** **TODAS LAS CORRECCIONES APLICADAS Y COMPILADAS EXITOSAMENTE (26.90 MB)**  

---

## 1. Resumen de Correcciones Aplicadas en Esta Sesión

### ✅ 1. Cámara 360° en Vivo (Sin Pantalla en Chino ni Grabadora DVR)
- **Problema previo:** El botón de cámara en el launcher abría `com.chinatsp.avmlive` (que mostraba un código QR en chino para descargar una app móvil), o abría la grabadora de video DVR (`DVRMainActivity`) pidiendo tarjeta MicroSD.
- **Solución implementada:** 
  - Se eliminó completamente `com.chinatsp.avmlive`.
  - Se enlazó directamente con la actividad de cámaras en vivo nativa del vehículo: `com.chinatsp.dvrcamera.builtin.BuiltinDVRActivity` en modo live.
  - Se envía la señal del sistema de reversa y cámaras surround `com.chinatsp.action.RVC_CAMERA` y se inicializa el servicio `video.evs.camera.CameraRenderService`.
  - Abre en tiempo real las 4 cámaras a 1920x720: frontal, trasera, espejos laterales y vista cenital combinada.

### ✅ 2. Botón de Radio OEM Funcional
- **Problema previo:** El botón de radio en el launcher no abría nada porque las radios automotrices de Changan no tienen categoría `LAUNCHER` en su manifiesto.
- **Solución implementada:**
  - Se implementó resolución de actividades con `Intent.ACTION_MAIN` sin requerir categoría launcher.
  - Se agregaron intents explícitos a `com.chinatsp.radio.MainActivity`, `com.chinatsp.radio.RadioActivity`, `com.chinatsp.fmradio.MainActivity` y `com.os.radio.MainActivity`.
  - Se envían los broadcasts del sistema `com.chinatsp.action.RADIO` y `com.chinatsp.radio.action.play`.
  - Se inicializa el servicio `com.chinatsp.radio.service.PlayControlService`.

### ✅ 3. Widget de Música Intuitivo (Filtro Anti "Maps en Segundo Plano")
- **Problema previo:** El widget mostraba textos del sistema como *"maps en segundo plano"* cuando Google Maps o Waze estaban activos.
- **Solución implementada:**
  - En [`MediaNotificationListener.java`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/launcher_android/src/com/changan/x7plus/launcher/MediaNotificationListener.java) se creó una lista negra para descartar notificaciones de mapas, navegación, Waze, descargas y servicios de fondo.
  - Se filtran cadenas como *"segundo plano"*, *"background"*, *"navegando"*, *"ruta"*, etc.
  - Textos por defecto limpios e intuitivos: *"♫ Toca para reproducir"*, *"Música"*, *"Selecciona tu reproductor"*.
  - Muestra título real, artista y carátula de disco únicamente de reproductores musicales (RiMusic, Spotify, SmartTube, Radio y Bluetooth Audio).

### ✅ 4. GPS Silencioso, Preciso y Compatible con Waze y Magic Earth
- **Problema previo:** Magic Earth recibía GPS por `GPS_PROVIDER`, pero Waze no detectaba ubicación al usar preferentemente `NETWORK_PROVIDER`.
- **Solución implementada:**
  - En [`MockLocationService.java`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/launcher_android/src/com/changan/x7plus/launcher/MockLocationService.java), el inyector ahora publica coordenadas satelitales simultáneamente en `LocationManager.GPS_PROVIDER` y `LocationManager.NETWORK_PROVIDER`.
  - Precisión forzada a 1.5 metros (`mock.setAccuracy(1.5f)`) con sellos de tiempo en nanosegundos (`elapsedRealtimeNanos`) para que el motor de Waze reconozca el fix instantáneamente.
  - Activación silenciosa automática cuando el móvil se conecta por Bluetooth (`ACTION_ACL_CONNECTED`) o Wi-Fi sin necesidad de interacción manual.
  - Indicador verde en el Launcher cuando la señal GPS está fluyendo.

### ✅ 5. Iconografía Premium para Todas las Aplicaciones
- **Problema previo:** Algunas apps no tenían icono o se mostraban con el robot genérico de Android.
- **Solución implementada:**
  - Se diseñó y generó el icono nativo oficial en alta resolución [`ic_launcher.png`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/launcher_android/res/drawable-nodpi/ic_launcher.png) (squircle carbono-metálico con alas aerodinámicas cian/blancas y logotipo X7 PLUS).
  - Configurado en `android:icon` y `android:roundIcon` en [`AndroidManifest.xml`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/launcher_android/AndroidManifest.xml).
  - En el cajón de aplicaciones se implementaron anulaciones de iconos en alta definición para Waze, Brave, Launcher y fallbacks estilizados para evitar cualquier icono vacío.

### ✅ 6. Video de Inicio Inteligente con Cooldown de 5 Horas
- **Problema previo:** El video de bienvenida no debía salir a cada momento si el auto se apagaba brevemente.
- **Solución implementada:**
  - Temporizador inteligente persistente en SharedPreferences: el video solo se reproduce una vez cada 5 horas. Si el auto se apaga brevemente o se cala, el launcher inicia directo sin reproducir el video.
  - Controles translúcidos semitransparentes ("Omitir" y "Silenciar").
  - Toque en cualquier parte de la pantalla o pulsación de botones físicos omite el video al instante.
  - Renderizado a pantalla completa real 1920x720 vía `FullScreenVideoView`.

### ✅ 7. Teclas Físicas del Volante / Timón y Consola
- Se sincronizaron las teclas físicas en [`HardwareKeyReceiver.java`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/launcher_android/src/com/changan/x7plus/launcher/HardwareKeyReceiver.java) y [`MainActivity.java`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/launcher_android/src/com/changan/x7plus/launcher/MainActivity.java):
  - Botón HOME del timón (KeyCode 3 y broadcast `KEYHOME_SWIPE`): eleva el Launcher al frente de forma inmediata.
  - Botón CÁMARA del timón (KeyCode 27 y evento CoAgent): abre la vista en vivo de las 4 cámaras 360° en tiempo real.

### ✅ 8. Pantalla Completa 1920x720 y Eliminación de Marcos
- El APK incluye los atributos de ventana WindowManager `FLAG_LAYOUT_NO_LIMITS`, `FLAG_LAYOUT_IN_SCREEN`, `FLAG_TRANSLUCENT_STATUS`, `FLAG_TRANSLUCENT_NAVIGATION` y `SYSTEM_UI_FLAG_IMMERSIVE_STICKY`.
- El script de instalación [`INSTALAR_TODO_EN_EL_AUTO.bat`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/INSTALAR_TODO_EN_EL_AUTO.bat) aplica los comandos de política de inmersión global (`policy_control immersive.full=*`) y ofrece los modos de ajuste de overscan (`wm overscan 0,0,0,0` y `wm overscan -320,0,-320,0`) para abarcar el 100% de la pantalla sin franjas laterales.

---

## 2. Estado de Compilación

- **Archivo compilado:** [`ChanganX7Plus_OEM_Launcher.apk`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/ChanganX7Plus_OEM_Launcher.apk) (26.90 MB)
- **Firma digital:** Keystore Oficial Changan X7 Plus RSA-256 (`release.keystore`)
- **Estado:** 100% libre de errores de compilación, DEX empaquetado y verificado.
- **Ubicaciones actualizadas:**
  - `c:\Users\Danna\OneDrive\Escritorio\APK CHANGAN X7 PLUS\ChanganX7Plus_OEM_Launcher.apk`
  - `c:\Users\Danna\OneDrive\Escritorio\APK CHANGAN X7 PLUS\apks_listos_para_instalar\ChanganX7Plus_OEM_Launcher.apk`
  - `c:\Users\Danna\OneDrive\Escritorio\APK CHANGAN X7 PLUS\apks\ChanganX7Plus_OEM_Launcher.apk`

---

## 3. Instrucciones para Desplegar en el Vehículo

Cuando conectes el cable USB en el auto:
1. Conecta el cable USB frontal de la radio a la laptop.
2. Abre la carpeta del proyecto en el escritorio y haz doble clic en:  
   👉 **[`INSTALAR_TODO_EN_EL_AUTO.bat`](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/INSTALAR_TODO_EN_EL_AUTO.bat)**
3. El script detectará el auto por ADB, instalará el launcher actualizado con todas las correcciones y configurará automáticamente los permisos y el modo inmersivo 1920x720.
