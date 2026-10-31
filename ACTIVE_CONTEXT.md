# 📍 ACTIVE_CONTEXT: Oshan X7 Virtual (Suite Infotainment Changan)
> Última Actualización: 2026-10-31 | Versión: v3.6.0 Laptop Migration & 5G Hotspot Ready | Estado: ✅ LISTO PARA MIGRACIÓN Y PRUEBAS EN VEHÍCULO

---

## 1. 🚦 Estado Actual Inmediato
- **Hardware Objetivo:** Changan Oshan X7 Plus (F202_MCA) · SoC MediaTek MT8666 · Pantalla 1920x720 213 DPI (Android 9 Pie / API 28).
- **Entorno Limpio y Descarte de `portable/`:** La carpeta `portable/` (runtime incrustado de 100MB+ y archivos duplicados) ha sido eliminada por completo. El proyecto corre ahora de forma nativa en cualquier PC/laptop con Python instalado.
- **Suite HMI / Cockpit:** Servidor backend `APK CHANGAN X7 PLUS/server.py` (puerto 5050) y cockpit táctil panorámico (`launcher_web/cockpit.html`, `launcher_web/index.html`).
- **Conectividad Dual (Cable USB + Wi-Fi Hotspot 5G):** Soporte completo para conexión mediante cable USB frontal o inalámbrica a través de ADB sobre TCP/IP (`adb connect <IP>:5555`).
- **Menú Maestro Unificado:** `0_ABRIR_MENU_CHANGAN.bat` en raíz permite gestionar arranque de dashboard, conexión Wi-Fi, mapeo de teclas, restauración de fábrica y restablecimiento satelital GPS en 1 clic.

---

## 2. 💻 Guía de Migración a Laptop (Requisitos y Setup)

### A. Software a Instalar en la Laptop
1. **Python 3.10+ (Recomendado 3.11, 3.12 o 3.14):**
   - Descargar e instalar desde [python.org](https://www.python.org).
   - ⚠️ **IMPORTANTE:** Marcar la casilla *"Add python.exe to PATH"* durante la instalación.
   - *Nota:* Todos los scripts del proyecto (`server.py`, `capturar_telemetria_avanzada.py`, etc.) fueron diseñados exclusivamente sobre la biblioteca estándar de Python (`http.server`, `urllib`, `subprocess`, `json`, `threading`). **No requieren instalar librerías pesadas con `pip`.**
2. **Android Platform Tools (ADB):**
   - El proyecto ya incluye los binarios listos en `APK CHANGAN X7 PLUS\tools\adb.exe`, por lo que los scripts `.bat` funcionarán sin configuración previa.
   - Opcional recomendado: Descargar [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) y agregar su ruta al PATH del sistema para poder usar `adb` desde cualquier terminal de Windows.
3. **Git para Windows:**
   - Instalar desde [gitforwindows.org](https://gitforwindows.org) para clonar y sincronizar cambios con GitHub.
4. **Navegador Web:**
   - Chrome, Brave o Edge para interactuar con el Dashboard HMI en `http://localhost:5050` o `http://localhost:5050/cockpit.html`.
5. **IDE / Asistente:**
   - Google Antigravity o VS Code.

---

### B. Skills de Antigravity / Gemini a Instalar en la Laptop
En la laptop, las skills deben ubicarse en la carpeta global de configuración:
`%USERPROFILE%\.gemini\config\skills\` (ejemplo: `C:\Users\<TuUsuario>\.gemini\config\skills\`)

#### Lista de Skills Fundamentales:
1. **`project-memory`** *(Crítica y Obligatoria)*:
   - Protocolo estricto de memoria viva en `ACTIVE_CONTEXT.md`, control git, prohibición de reportes acumulativos redundantes.
2. **`harness-engineering`**:
   - Arquitectura de arnés de pruebas, ciclos de verificación de agentes y boundaries seguros.
3. **`ponytail`**:
   - Modo programador senior minimalista (resolución directa, mínimo código efectivo, sin sobreingeniería).
4. **`cybersecurity`**:
   - Auditoría de seguridad, permisos de red automotriz y comprobación de interfaces ADB.
5. **`diagram-design`**:
   - Generación de esquemas limpios para diagramar topologías CAN, flujos de red y mapas de audio/pantalla.

> **Tip de Transferencia:** Puedes copiar directamente la carpeta `.gemini\config\skills` desde tu equipo actual a tu laptop para tener exactamente la misma configuración y herramientas de agentes.

---

## 3. 🌐 Protocolo de Conexión al Auto con Hotspot 5G

```
                ┌──────────────────────────────────┐
                │   Celular / Módem Hotspot 5G     │
                │   (Zona Wi-Fi Compartida)        │
                └─────────────────┬────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌──────────────────────┐        ┌──────────────────────┐
       │ Radio Changan Oshan  │        │   Laptop / Antigravity│
       │ IP: 192.168.43.X:5555│◄───────┤ Conexión ADB Wi-Fi   │
       └──────────────────────┘        └──────────────────────┘
```

### Paso a Paso para Conectar por 5G en el Auto:
1. **Encender el Hotspot 5G** en tu celular o módem móvil.
2. **Conectar ambos equipos al mismo Hotspot:**
   - Conectar la radio de la Changan X7 Plus al Wi-Fi del Hotspot.
   - Conectar la laptop al mismo Wi-Fi del Hotspot.
3. **Obtener la IP de la Radio:**
   - En la radio: Ajustes de Sistema > Wi-Fi > Ver detalles de conexión (anotar la IP, ej: `192.168.43.15`).
   - O mediante el marcador de teléfono del auto escribiendo `**888` para abrir el menú de ingeniería / depuración.
4. **Habilitar y Conectar ADB Inalámbrico:**
   - Abre `0_ABRIR_MENU_CHANGAN.bat` en la laptop.
   - Elige la opción `[9] Conectar al Auto por Wi-Fi / Hotspot 5G`.
   - Si es la primera vez que se enciende el vehículo: conecta el cable USB unos segundos y presiona `[2]` (`adb tcpip 5555`). Desconecta el cable USB.
   - Presiona `[1]` e introduce la IP de la radio (`192.168.43.X`).
   - El script mostrará `connected to 192.168.43.X:5555`.
5. **Realizar Comprobaciones en Ruta:**
   - Opción `[1]`: Lanza el Dashboard en el navegador con telemetría en tiempo real.
   - Opción `[M]`: Prueba y monitoreo en vivo de pulsaciones del volante multimedia.
   - Opción `[G]`: Restablece el GPS físico satelital nativo para Waze y Magic Earth si fuera necesario.
   - Opción `[7]`: Extrae un diagnóstico completo de salud térmica y estado de Android.

---

## 4. 🧠 Base de Conocimiento de Errores (Caminos Resueltos vs Descartados)

### ✅ Errores Resueltos Definitivamente (No volver a diagnosticar)
1. **GPS Congelado en 0 Satélites:**
   - *Causa:* Intentar usar ubicaciones simuladas (`mock_location 1`) desconectaba el hardware GPS de MediaTek en Android.
   - *Solución:* Restablecimiento de antena satelital física nativa (`mock_location 0`, `location_mode 3`, permisos en tiempo de ejecución otorgados en `RESTABLECER_GPS_FISICO_NATIVO.bat`).
2. **Superposición de SystemUI sobre el Engranaje de SimpMusic:**
   - *Causa:* `F202_SystemUI` interceptaba toques en la franja superior de 48px en apps de terceros.
   - *Solución:* Broadcast propietario de Changan (`am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName com.maxrave.simpmusic --ei appCentered 2`) y modo inmersivo forzado (`policy_control immersive.full`).
3. **Congelamiento de Dashboard en Mapeo de Teclas:**
   - *Causa:* `KeymapMonitor` ejecutaba llamadas síncronas bloqueantes a `dumpsys window windows` en cada pulsación.
   - *Solución:* Desacople del foco a un hilo en caché en segundo plano (`_focus_updater_loop()`) cada 2.5s.
4. **Mandos del Timón Lado Izquierdo (No envían keycodes a Android):**
   - *Causa Raíz:* Los botones izquierdos (Control Crucero / Pantalla del Odómetro) pertenecen al CAN-Bus de Dinámica Vehicular / ECU. **No viajan al SoC MT8666 por diseño automotriz.** Los botones del lado derecho (multimedia) sí operan al 100% como teclas de Android.
5. **Redundancia y Peso de la Carpeta `portable/`:**
   - *Causa:* Mantener un runtime de Python 3.11 incrustado de más de 650 archivos duplicados sobrecargaba el repositorio y el control de versiones.
   - *Solución:* Descarte total de `portable/`, preservación del backup OEM en `APK CHANGAN X7 PLUS/oem_factory_backup/` y delegación limpia al runtime de la laptop.

### ❌ Caminos Técnicos Descartados (Prohibido reintentar)
- **Descartado Definitivamente:** Ubicaciones simuladas (Mock Location) para Waze o Maps en este vehículo (deja la antena en 0 satélites).
- **Descartado Definitivamente:** Intentar capturar eventos de teclado de Android para los mandos de crucero del timón izquierdo.
- **Descartado Definitivamente:** Reintroducir runtimes embebidos o carpetas portables pesadas dentro del repositorio Git.

---

## 5. 📋 Tareas Pendientes y Roadmap Inmediato
- [ ] Clonar el repositorio en la laptop y validar ejecución de `0_ABRIR_MENU_CHANGAN.bat`.
- [ ] Copiar las skills a `%USERPROFILE%\.gemini\config\skills\` en la laptop.
- [ ] Enlace de prueba con Hotspot 5G en el vehículo (validar conexión inalámbrica por `adb connect`).
- [ ] Verificación de estabilidad del dashboard HMI durante conducción prolongada.

---

## 6. 🔗 Referencias Rápidas
- **Punto de Entrada Principal:** `0_ABRIR_MENU_CHANGAN.bat` (Menú interactivo con soporte USB y Wi-Fi 5G).
- **Backend Servidor:** `APK CHANGAN X7 PLUS/server.py` (Puerto 5050).
- **GPS Fix Script:** `RESTABLECER_GPS_FISICO_NATIVO.bat` (Directo en raíz).
- **Paquetes OEM Changan:** Radio (`com.edog.car.changanoushang`), Cámara AVM (`com.chinatsp.avmlive/.MainActivity`), Launcher Original (`com.chinatsp.launcher`).
