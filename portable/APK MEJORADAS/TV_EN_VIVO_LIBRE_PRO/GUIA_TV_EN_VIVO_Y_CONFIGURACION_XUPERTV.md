# GUÍA DEFINITIVA: TV EN VIVO LIBRE Y STREAMING HD (XUPERTV ALTERNATIVE)
## Open Source, Sin Anuncios, Sin Suscripciones y Pre-Configurado para Changan Oshan X7

---

### 1. ¿Por qué sustituir XuperTV / MagisTV por una solución Open Source?

Aplicaciones como **XuperTV**, **Magis TV** o **Tele Latino** presentan serios inconvenientes en radios automotrices:
* **Seguridad y Privacidad:** Son aplicaciones cerradas de origen desconocido que solicitan permisos excesivos y ejecutan servicios en segundo plano que ralentizan el procesador de la radio.
* **Bloqueos y Caídas:** Con frecuencia sufren caídas de servidores, cambios de dominio o exigen repentinamente membresías de pago o suscripciones VIP para continuar viendo canales.
* **Consumo de Recursos:** Provocan sobrecalentamiento en procesadores de infotainment como el Mediatek MT8666 al no contar con decodificación de hardware optimizada.

**Nuestra Solución de Código Abierto:**
100% gratuita, de código auditado, sin anuncios, sin malware, con decodificación por hardware nativa (**ExoPlayer + MPV**) y con una lista maestra de **más de 370 canales en vivo de Perú, Latinoamérica, Deportes y Cine** precargada directamente en la memoria del auto.

---

### 2. Las 2 Aplicaciones Incluidas en esta Carpeta

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SUITE DE ENTRETENIMIENTO LIBRE                            │
├──────────────────────────────────────────┬─────────────────────────────────────────────┤
│                 OWNTV v5.2.1             │             CLOUDSTREAM 3 v4.8.0            │
│         (El Cableoperador en Vivo)       │           (El "XuperTV Libre" Total)        │
├──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ • Especializado en TV en Vivo            │ • TV en Vivo + Películas + Series + Anime   │
│ • Cambio de canal ultra-rápido (< 1 seg) │ • Servidores de alta velocidad sin cortes   │
│ • Motor híbrido ExoPlayer + MPV          │ • Enlaces en Español Latino y Castellano    │
│ • 370+ Canales precargados localmente    │ • Sin publicidad ni suscripciones           │
│ • Guía EPG y favoritos para el volante   │ • Interfaz moderna adaptable a 1920x720     │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

### 3. Detalle y Configuración de Cada Aplicación

#### Opción 1: OwnTV v5.2.1 (Recomendado para zapping de TV tradicional)
* **¿Qué es?:** Es el reproductor de IPTV y televisión en vivo más avanzado y rápido del ecosistema de código abierto.
* **Lista Precargada:** El script de instalación ya transfirió automáticamente el archivo maestro `CANALES_VIP_LATAM_PERU_DEPORTES.m3u` a `/sdcard/IPTV/canales_vip.m3u`.
* **Cómo activarla al abrir OwnTV por primera vez:**
  1. Abre **OwnTV** en la pantalla de tu Changan X7.
  2. Toca en **"Añadir Lista"** (*Add Playlist*) o pulsa en **M3U**.
  3. Elige la opción **"Archivo Local"** (*Local File*) y selecciona el archivo `/sdcard/IPTV/canales_vip.m3u`.
  4. *(Opcional)* Si prefieres una URL auto-actualizable por internet, puedes pegar:
     `https://iptv-org.github.io/iptv/countries/pe.m3u`
  5. ¡Listo! Tendrás acceso a:
     * **Perú en Vivo:** América TV, ATV, Panamericana, Latina, TV Perú, Willax, Exitosa, RPP Noticias, etc.
     * **Deportes en Vivo:** Feeds de fútbol, automovilismo/F1, ESPN, Fox, TyC, Claro Sports, Red Bull TV.
     * **Noticias en Español:** DW Español, RT, France 24, Euronews, etc.
     * **Cine y Series:** Canales temáticos de acción, clásicos, comedias y series 24/7.

---

#### Opción 2: CloudStream 3 v4.8.0 (El "XuperTV Open Source")
* **¿Qué es?:** La plataforma libre más famosa del mundo para ver televisión en vivo, películas de cartelera, series y anime.
* **Cómo activar los proveedores en Español Latino con 1 solo toque:**
  CloudStream viene por seguridad sin extensiones de fábrica. Para activarle todo el catálogo latino en segundos:
  1. Abre **CloudStream** en la radio.
  2. Ve a **Ajustes** (icono de engranaje) -> **Extensiones** (*Extensions*).
  3. Toca en **"Añadir Repositorio"** (*Add Repository*).
  4. Ingresa el nombre: `Latino` y en la URL pega:
     ```
     https://raw.githubusercontent.com/Stormunblessed/stormunblessed-cs3/master/repo.json
     ```
  5. Toca en **Descargar/Instalar** en los módulos que desees (ej: *CineCalidad, PelisPlus, Cuevana, AnimeFLV, TV Latina*).
  6. A partir de ese momento tendrás una biblioteca infinita de películas, series y canales de televisión con audio latino y en alta definición.

---

### 4. Instalación Automatizada en el Changan Oshan X7

Para instalar todo de forma 100% asistida y con los permisos automotrices concedidos:

1. Conecta tu auto por USB (o Wi-Fi ADB).
2. Haz doble clic sobre:
   👉 `INSTALAR_TV_EN_EL_AUTO.bat`
3. El script automáticamente:
   - Crea la carpeta `/sdcard/IPTV/` y copia la lista de 370+ canales.
   - Instala la app que elijas (o ambas).
   - Otorga permisos de almacenamiento y ejecución sin restricciones de batería.
   - Envía el comando broadcast propietario de Changan (`appCentered 2`) para estirar la imagen y eliminar los bordes negros en el panel panorámico de 1920x720.

---

### 5. Consejos para una Transmisión Fluida en Carretera

* **Calidad de Video:** En OwnTV puedes seleccionar la resolución del flujo (1080p, 720p o 480p). Si vas en carretera con poca cobertura celular, selecciona 720p para evitar cualquier tipo de pausa o congelamiento.
* **Hotspot del Celular:** Cuando compartas internet desde tu celular hacia la radio del auto, activa la banda de **5 GHz** en la zona Wi-Fi para obtener la menor latencia de video posible.
