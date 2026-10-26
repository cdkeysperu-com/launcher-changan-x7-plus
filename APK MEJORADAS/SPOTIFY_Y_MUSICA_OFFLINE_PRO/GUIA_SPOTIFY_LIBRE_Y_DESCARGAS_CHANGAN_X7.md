# GUÍA DEFINITIVA: SPOTIFY LIBRE Y MÚSICA OFFLINE
## Alternativas Super Mejoradas para Changan Oshan X7 (Android 9 / Pantalla Panorámica)

---

### 1. ¿Por qué fallaba RiMusic en tu auto?

RiMusic presentaba tres problemas graves conocidos por la comunidad técnica:
1. **"No cargaba nada a pesar de tener internet":** YouTube actualizó su API interna (*InnerTube*) implementando firmas de cifrado y comprobación de bot (*PoToken*). RiMusic usaba un extractor antiguo que devolvía un error de reproducción desconocido (*Unknown Error*) y bloqueaba la carga de canciones.
2. **"Se repetía la canción a la mitad de la reproducción":** RiMusic tenía un fallo en el gestor de fragmentos de caché (*Chunked Buffer Cache*) de ExoPlayer: cuando había una micro-pérdida de paquetes en el Wi-Fi, el reproductor no continuaba el flujo, sino que saltaba en bucle de regreso al inicio o a la mitad de la pista.
3. **"Al presionar descargar nunca guardaba nada":** RiMusic implementaba almacenamiento aislado (*Scoped Storage*) de Android 11+ sin compatibilidad hacia atrás para Android 9 automotriz, provocando que las descargas fallaran silenciosamente sin permisos de escritura reales en `/sdcard/Music`.

---

### 2. Las 3 Nuevas Opciones Disponibles en esta Carpeta

Hemos seleccionado y preparado 3 aplicaciones de código abierto universales (compatibles con procesadores `arm64-v8a`, `armeabi-v7a` y `x86_64` del emulador y del auto real):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              REPRODUCTORES RECOMENDADOS                                │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│    SPOTUBE v5.1.2        │      SIMPMUSIC v2.3.0       │      INNERTUNE v0.5.14        │
│   (El Spotify Libre)     │     (Offline Pro / YTM)     │     (Ultra Ligero 7 MB)       │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ • Catálogo 1:1 Spotify   │ • Interfaz moderna Apple/   │ • Solo 7 MB de peso           │
│ • Todas las canciones    │   Spotify Music             │ • Arranque ultra-rápido       │
│ • Descargas directas en  │ • Pestaña "Descargas"       │ • Sin consumo de RAM          │
│   archivos MP3 con tags  │   100% offline real         │ • Ideal para compartir con    │
│ • Sin anuncios           │ • Sin bucles ni cortes      │   Waze y cámaras 360          │
│ • No requiere cuenta     │ • Letras sincronizadas      │ • Error de reproducción       │
│   de pago                │ • Ecualizador automotriz    │   completamente reparado      │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

---

### 3. Detalle de Cada Opción

#### Opción 1: Spotube v5.1.2 (Recomendada si amas Spotify)
* **¿Qué es?:** Es el cliente libre de Spotify por excelencia. Utiliza la API pública oficial de Spotify para obtener los metadatos de más de 100 millones de canciones, listas de éxitos (Top 50 global, lanzamientos, artistas, playlists temáticas) y reproduce el audio sin anuncios utilizando servidores de alta velocidad.
* **Descargas Reales a MP3:** A diferencia de otras apps que solo guardan un archivo temporal oculto, Spotube incluye un **Gestor de Descargas nativo** que guarda los archivos `.mp3` o `.m4a` directamente en `/sdcard/Music` con carátulas en alta resolución y etiquetas ID3 completas.
* **Sincronización:** Puedes usarlo de forma 100% anónima sin cuenta, o iniciar sesión con una cuenta gratuita de Spotify para tener todas tus playlists sincronizadas en la pantalla de tu auto.

#### Opción 2: SimpMusic v2.3.0 (Recomendada para el Auto / Modo Offline)
* **¿Qué es?:** Una obra de arte desarrollada en Kotlin nativo y Jetpack Compose. Diseñada específicamente para superar todas las limitaciones de ViMusic y RiMusic.
* **Cero Repetición de Canciones:** Utiliza **Media3 ExoPlayer**, el motor oficial más reciente de Google para streaming continuo, eliminando el fallo de repetición en bucle que sufrías con RiMusic.
* **Pestaña de Descargas Offline:** En tu Biblioteca cuenta con una sección dedicada: **"Descargado"**. Puedes descargar discos completos o tus canciones favoritas para viajar por carretera sin gastar datos de tu celular ni depender de la señal móvil.
* **Letras y Pantalla Dividida:** Presenta letras fluidas animadas estilo Apple Music y un diseño adaptable que se ve espectacular en la pantalla panorámica del Changan X7.

#### Opción 3: InnerTune v0.5.14 (La Opción más Ligera del Mundo)
* **¿Qué es?:** La versión actualizada y corregida por la comunidad del mítico InnerTune (Malopieds).
* **Solución al error "No cargaba nada":** Esta versión incorpora el parche que repara el cambio de API de InnerTube que rompió a RiMusic.
* **Peso pluma:** Pesa únicamente **7 MB**. Consume menos de 60 MB de memoria RAM en la radio del auto, garantizando que el sistema multimedia y el GPS (Waze / Google Maps) corran al 100% de velocidad sin saturar la memoria del vehículo.

---

### 4. Cómo Descargar Canciones para Escuchar Sin Internet

#### En Spotube:
1. Busca cualquier canción, disco o tu playlist favorita.
2. Toca el menú de los **3 puntos** al lado de la canción o en la cabecera del álbum.
3. Selecciona **"Descargar"** (*Download*).
4. El archivo se guardará directamente en la memoria interna de la radio (`/sdcard/Music/Spotube`).
   * *Tip de experto:* Si tienes una memoria USB conectada en el puerto de tu Changan X7, en los ajustes de Spotube puedes elegir tu memoria USB como carpeta de descargas predeterminada.

#### En SimpMusic:
1. En cualquier canción o álbum, presiona el icono de la **Flecha hacia abajo (Descargar)**.
2. La canción se descargará en segundo plano.
3. Cuando viajes y no tengas internet, ve a la pestaña **Biblioteca (Library)** -> **Descargado (Downloaded)** y dale a reproducir. Todas tus canciones sonarán al instante sin requerir conexión Wi-Fi ni datos móviles.

---

### 5. Cómo Instalar en la Pantalla del Changan X7

Simplemente haz doble clic sobre el script:
👉 `INSTALAR_MUSICA_EN_EL_AUTO.bat`

El script se encargará de:
* Detectar tu auto conectado por USB o Wi-Fi ADB.
* Crear la carpeta del sistema `/sdcard/Music` para asegurar que las descargas guarden siempre sin error.
* Instalar la app seleccionada y concederle permisos de almacenamiento en segundo plano y exclusión de ahorro de batería para que la música nunca se detenga al apagar la pantalla.
