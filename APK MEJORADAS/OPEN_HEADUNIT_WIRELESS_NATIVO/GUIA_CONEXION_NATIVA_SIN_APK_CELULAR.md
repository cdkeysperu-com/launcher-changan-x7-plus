# GUÍA DEFINITIVA: ANDROID AUTO INALÁMBRICO 100% NATIVO
## Open Headunit v3.5.0 — Conexión Wi-Fi / Wi-Fi Direct SIN APK EN EL CELULAR

---

### 1. ¿Por qué NO necesitas ninguna APK en tu celular?

En versiones antiguas y en aplicaciones comerciales cerradas (como Headunit Reloaded), se solía utilizar una app complementaria llamada *"WiFi Launcher"* o *"Wireless Helper"* en el teléfono para "despertar" la conexión.

**En Open Headunit v3.5.0 esto ya NO es necesario:**
Android 10, 11, 12, 13, 14, 15 y 16 incluyen de fábrica el protocolo **WPP (Wireless Projection Protocol)** dentro de los Servicios de Google Play y de la app oficial de Android Auto. Open Headunit implementa directamente el apretón de manos (*handshake*) y la capa de transporte nativa del estándar de la **Open Automotive Alliance (OAA)**. 

Tu teléfono inteligente reconoce a la radio de tu **Changan Oshan X7** como si fuera una radio OEM de fábrica (como un vehículo BMW, Audi o Honda con Android Auto inalámbrico de serie).

---

### 2. Los 3 Métodos de Conexión 100% Nativos (Cero APKs en el Teléfono)

Tienes 3 formas sencillas de conectarte, todas **sin instalar nada en tu celular**:

```
                              ┌─────────────────────────────────────────┐
                              │     CELULAR ANDROID (Sin ninguna APK)   │
                              │       Android Auto Oficial de Google    │
                              └────────────────────┬────────────────────┘
                                                   │
                  ┌────────────────────────────────┼────────────────────────────────┐
                  │                                │                                │
                  ▼                                ▼                                ▼
           [ MÉTODO 1 ]                     [ MÉTODO 2 ]                     [ MÉTODO 3 ]
       AUTOMÁTICO TOTAL              EMPAREJAMIENTO POR QR              SERVIDOR NATIVO AA
  Bluetooth + Wi-Fi Direct         Deep Link Oficial Google           Headunit Server (Wi-Fi)
  ─────────────────────────        ─────────────────────────         ─────────────────────────
  1. Conecta Bluetooth normal      1. Radio muestra Código QR         1. En celular: Activa Servidor
  2. Radio negocia por RFCOMM      2. Escaneas con la cámara             desarrollador de AA (1 toque)
  3. Salta Android Auto solo       3. Celular guarda el auto          2. En radio: Pulsas "WiFi"
  4. 100% automático al entrar     4. Conecta por Wi-Fi Direct        3. Conexión directa a 60 FPS
```

---

### MÉTODO 1: Automático Total (Bluetooth + Wi-Fi Direct) — Recomendado

Este es el método idéntico al de los autos nuevos de agencia:

1. **En la Radio del Auto (Open Headunit):**
   * Abre Open Headunit y ve a **Settings (Ajustes)**.
   * En **General -> Connection mode**: Deja marcado **WiFi**.
   * En **Wireless Connection -> Wireless Mode**: Selecciona **Native** (Nativo).
   * En **Network transport**: Selecciona **WiFi Direct (P2P)**.
   * Guarda los cambios pulsando **Save**.

2. **Vinculación Inicial por Bluetooth:**
   * Enciende el Bluetooth de tu teléfono y emparéjalo con la radio de tu auto como haces normalmente para manos libres.
   * Abre Open Headunit en la radio.

3. **Conexión Automática:**
   * Open Headunit utiliza el canal de servicio oficial de Android Auto (`UUID: 4de17a00-52cb-11e6-bdf4-0800200c9a66`) sobre el Bluetooth.
   * La radio le envía las credenciales seguras de Wi-Fi Direct a tu teléfono.
   * Tu teléfono enciende su Wi-Fi en segundo plano, se vincula al grupo Wi-Fi Direct de la radio y **Android Auto se proyecta automáticamente a pantalla completa**.
   * A partir de este momento, cada vez que subas a tu auto y se conecte el Bluetooth, Android Auto arrancará solo.

---

### MÉTODO 2: Emparejamiento por Código QR Nativo de Android Auto

*Úsalo si el Bluetooth de tu radio tiene un chip propietario serie/UART que Android no expone a las apps:*

Google Android Auto tiene un receptor nativo de enlaces de configuración: `https://androidauto.com/projection/setup?...`. Open Headunit v3.5.0 aprovecha este sistema para provisionar el vehículo en 3 segundos.

1. **En Open Headunit:**
   * En **Settings -> Wireless Connection -> Wireless Mode -> Native**.
   * Selecciona transporte **Headunit Hotspot** (Punto de acceso del auto) o **WiFi Direct**.
   * Toca en **Show Setup QR Code (Mostrar código QR de emparejamiento)**.
2. **En tu Celular:**
   * Abre la app de **Cámara normal** o **Google Lens**.
   * Apunta al código QR que aparece en la pantalla del auto.
   * Te saldrá una notificación emergente del sistema: *"Configurar Android Auto con este vehículo"*.
   * Tócala para aceptar. Android Auto guardará el nombre de la red Wi-Fi y el puerto de proyección en la lista de *"Autos Conectados"*.
3. ¡Listo! Se iniciará la proyección inalámbrica de inmediato sin instalar absolutamente nada.

---

### MÉTODO 3: Servidor de Desarrollador Oficial de Android Auto (Headunit Server)

*El método más veloz, directo y a prueba de fallos para redes Wi-Fi compartidas o punto de acceso móvil:*

El Android Auto oficial que ya tienes instalado en tu teléfono cuenta con un servidor de transmisión interno oculto por Google para ingenieros automotrices.

1. **Desbloquear el menú en tu celular (Se hace una sola vez):**
   * En tu teléfono, ve a **Ajustes** -> busca **Android Auto**.
   * Desplázate hacia abajo hasta el final de la pantalla, donde dice **Versión**.
   * **Toca la palabra "Versión" 10 veces seguidas**.
   * Te preguntará: *"¿Deseas permitir los ajustes de desarrollo?"* -> Pulsa **Aceptar**.
2. **Iniciar la Conexión:**
   * En esa misma pantalla de Android Auto en tu celular, pulsa el botón de los **3 puntos** (arriba a la derecha).
   * Toca en **"Iniciar servidor de unidad principal"** (*Start headunit server*).
   * Asegúrate de que el celular y la radio estén en la misma red Wi-Fi (por ejemplo, el celular conectado al Hotspot del auto, o el auto conectado a la zona Wi-Fi del celular).
3. **En la Radio del Auto:**
   * Abre Open Headunit y pulsa sobre el botón grande **WiFi** en la pantalla principal.
   * En 1 segundo se conectará a 60 FPS con fluidez total.

---

### 3. Ajustes de Rendimiento para Changan Oshan X7 (Aceleración GPU y Coolwalk)

Para que la pantalla del Changan X7 (1920x720 / 1280x720 panorámica) se vea como un vehículo de gama alta:

| Parámetro | Valor Recomendado | Motivo / Beneficio |
| :--- | :--- | :--- |
| **Video Codec** | **H.264** | Máxima aceleración por hardware en SoC Mediatek. Cero tirones ni calentamiento. |
| **Resolution** | **1280x720** o **1920x720** | 1280x720 = Ultra ligera a 60 FPS. 1920x720 = Llena el 100% del panel panorámico. |
| **Pixel Density (DPI)**| **160 DPI** o **180 DPI** | **Clave**: Activa la interfaz **Coolwalk dividida** (Mapa grande a la izquierda + Spotify a la derecha). |
| **Frame Rate** | **60 FPS** | Fluidez absoluta en animaciones de Waze / Google Maps. |
| **Pause Wi-Fi Scans** | **Activado (On)** | Evita que Android escanee redes en carretera, eliminando micro-cortes de video. |
| **Audio Sink** | **Activado (On)** | El sonido de la música y del navegador sale directo por los parlantes del Changan. |
| **Audio Engine** | **AAudio (Low Latency)**| Reduce el desfase de sonido a prácticamente cero. |

---

### 4. Solución a Problemas Frecuentes

* **"El celular se desconecta a los pocos segundos":**
  * En tu celular, entra a *Ajustes de Wi-Fi* -> *Ajustes avanzados*. Desactiva la opción **"Asistente Wi-Fi"** o **"Cambiar a datos móviles si no hay internet"**. Como la red Wi-Fi Direct de la radio es solo para video y no tiene internet propio, el celular intenta desconectarse creyendo que la red falló.
* **"La pantalla se queda en negro":**
  * Entra a los ajustes de Open Headunit y verifica que el **Video Codec** esté en **H.264** y no en H.265.
* **"¿Puedo usar los botones del volante del auto?":**
  * Sí. En Open Headunit ve a **Settings -> Keymap** y presiona las teclas de tu volante (Siguiente, Anterior, Volumen, Voz) para asociarlas nativamente a Android Auto.
