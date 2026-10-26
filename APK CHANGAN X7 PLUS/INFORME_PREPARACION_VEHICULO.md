# INFORME TÉCNICO Y GUÍA DE EJECUCIÓN — CHANGAN X7 PLUS (HMI COCKPIT v3.1.0)
**Proyecto:** Modernización Multimedia, Launcher Cockpit FullScreen y Navegación Offline / Tethering  
**Vehículo:** Changan X7 Plus (F202_MCA, SoC MT8666 / MT6771, 1920x720 px @ 213 DPI)  
**Launcher Nativo Oficial:** `ChanganX7Plus_OEM_Launcher.apk` (**26.87 MB**) firmado con Keystore Oficial  
**Fecha de Actualización:** 15 de Octubre de 2026  
**Estado:** APK 100% Compilado, Simulador Activo en PC, Puente GPS y Scripts Listos para Conexión USB en Vivo  

---

## 1. SIMULADOR EN VIVO EN LA LAPTOP (ANTES DE INSTALAR)

Puedes interactuar con el launcher y ver cómo lucirá exactamente en la pantalla de la radio:
* **Enlace web directo:** [http://localhost:5050/cockpit.html](http://localhost:5050/cockpit.html) *(Servidor local activo en segundo plano)*.
* **Desde el menú principal:** Ejecuta `0_ABRIR_MENU_CHANGAN.bat` y selecciona la opción `[2]`.
* **Captura de verificación (1920x720 px):** Se guardó la captura de pantalla oficial en [cockpit_preview_final.png](file:///c:/Users/Danna/OneDrive/Escritorio/APK%20CHANGAN%20X7%20PLUS/cockpit_preview_final.png).

---

## 2. RESOLUCIÓN DE LOS 6 PUNTOS CRÍTICOS

1. **Corrección Visual Milimétrica:**
   - Barra lateral izquierda de 105 px con 6 botones proporcionales (Inicio destacado con recuadro azul redondeado y barra neón vertical de 4 px).
   - Reloj de 78 px en tiempo real y fecha dinámica en español ("Viernes, 09 de octubre").
   - Widget de música horizontal a la izquierda (ancho ~600 px / 43%, carátula cuadrada, títulos dinámicos y controles `|<`, `||`, `>|`).
   - Mitad superior derecha totalmente despejada: la SUV Changan X7 Plus se luce completa sin elementos superpuestos.
   - Fila de 6 tarjetas casi cuadradas (altura ~230 px, proporción 1.12:1), sin recuadros anidados ni subtítulos celestes.
   - Barra inferior "FAVORITOS |" oscura con 5 píldoras uniformes (Radio, Reproductor de música, Teléfono Bluetooth, Brave, + Agregar acceso directo).
2. **Pantalla Completa 1920x720 Real (Sin marcos CarAuto):**
   - Categorías `HOME`, `DEFAULT`, `LAUNCHER`, metadatos ChinaTSP y elevación directa al stack raíz (`cmd package set-home-activity` + `input keyevent 3`).
   - Política inmersiva forzada (`policy_control immersive.full=*` y `wm overscan 0,0,0,0`).
3. **Video de Inicio TikTok con Skip y Mute:**
   - Video `intro_video.mp4` integrado en `res/raw/` del APK.
   - Volumen sutil bajo (18%), botón flotante "Omitir ⏭", botón "🔇 Silenciar" y toque en cualquier parte de la pantalla para quitarlo instantáneamente.
4. **Control Vehicular, Modo de Manejo y Hora:**
   - Zona horaria blindada a `America/Lima` en formato 24h.
   - Enlaces nativos a `com.chinatsp.vehiclecontrol`, `com.os.airconditioner` y `com.edog.car.changanoushang`.
   - Modal de Control Rápido Changan con memoria de modo de manejo (**ECO**, **CONFORT**, **SPORT**), Cámara 360°, Modo Nocturno (pantalla negra despierta al toque), Ecualizador y botón de retorno al launcher OnStyle original.
5. **Widget de Música Dinámico y Selector de Apps:**
   - Conectado a `MediaNotificationListener` y `AudioManager.dispatchMediaKeyEvent`.
   - Selector rápido para alternar entre Música OEM Bluetooth/USB, SmartTube, NewPipe, Spotify o RiMusic.
6. **Puente GPS sin Google Play Services:**
   - Servicio `MockLocationService` incorporado que inyecta coordenadas en `LocationManager.GPS_PROVIDER` recibidas por Wi-Fi o cable.
   - Permisos completos otorgados a Headunit Reloaded (`gb.xxy.hr`).

---

## 3. ¿CÓMO FUNCIONA EL PUENTE GPS POR WI-FI O CABLE?

El sistema no requiere servicios de Google (GMS/MicroG):
* **Por Wi-Fi Hotspot (Recomendado):**
  1. Activas el punto de acceso (Hotspot) de tu teléfono celular.
  2. Conectas la radio del Changan a ese Wi-Fi.
  3. Tu teléfono emite la señal satelital mediante la app complementaria (`gps_tether.apk` o `bluetooth_gps_provider.apk`) hacia los puertos UDP 5000/10110 o TCP 5000.
  4. El `MockLocationService` del launcher toma las tramas NMEA/JSON e inyecta la ubicación directamente en el sistema Android de la radio.
  5. Waze, Magic Earth 3D y Android Auto navegan con precisión satelital inmediata.
* **Por Cable USB:**
  - Al conectar el teléfono por USB con "Compartir conexión por USB" (USB Tethering) o Headunit Reloaded, las coordenadas viajan sobre la interfaz de red local simulada directamente al puerto 5000.

---

## 4. CHECKLIST PARA LA PRÓXIMA SESIÓN (CONEXIÓN EN VIVO POR USB)

Cuando estés conectado al auto:
1. Conecta el cable USB de la laptop al **puerto multimedia frontal** de la Changan (ícono de pantalla/datos).
2. En la radio Changan, abre el teléfono y marca:
   ```
   **888
   ```
3. Activa la casilla **"Depuración por USB"**.
4. Cuando aparezca el mensaje en la pantalla del auto, marca **"Permitir siempre desde este equipo"** y presiona **ACEPTAR**.
5. Ejecuta en tu laptop:
   ```bat
   INSTALAR_TODO_EN_EL_AUTO.bat
   ```
   *(o ejecuta `runtime\python.exe instalar_todo_x7_plus.py`)*

Todo el proceso de instalación, permisos inmersivos, zona horaria y despliegue del Launcher Cockpit se ejecutará de forma automática y desatendida.
