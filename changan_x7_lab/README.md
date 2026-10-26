# CHANGAN X7 PLUS LAB — ENTORNO VIRTUAL DE DESARROLLO (COCKPIT X7)

Bienvenido al laboratorio virtual de desarrollo y pruebas para la unidad multimedia de la **Changan X7 Plus** (Plataforma F202_MCA / R202_MCA).

Este entorno permite desarrollar, instalar, probar y depurar la aplicación de launcher nativo `com.changan.x7plus.launcher` (**Cockpit X7**) directamente desde tu PC con Windows, reproduciendo con máxima fidelidad la resolución física, relación de aspecto, versión de Android y densidad de la pantalla del vehículo, sin necesidad de conectarse al auto físico ni arriesgar su firmware.

---

## 1. Especificaciones de Referencia del Laboratorio

| Parámetro | Unidad Multimedia Real (Vehículo) | Entorno Virtual (CHANGAN_X7_PLUS_LAB) |
| :--- | :--- | :--- |
| **Vehículo / Plataforma** | Changan X7 Plus / F202_MCA / R202_MCA | Changan_X7_Plus_API28_1920x720 |
| **Sistema Operativo** | Android 9.0 Pie (API 28) | Android 9.0 Pie (API 28, AOSP puro sin Google Play) |
| **Resolución de Pantalla** | **1920 × 720** píxeles | **1920 × 720** píxeles |
| **Relación de Aspecto** | **8:3** (aprox. 2.67:1 panorámica) | **8:3** nativa de hardware virtual |
| **Densidad de Pantalla** | 213 DPI (Referencia) / 160 DPI | 213 DPI (Referencia) y 160 DPI (Compatibilidad) |
| **Memoria RAM** | 4 GB | 4096 MB asignados |
| **Almacenamiento** | 32 GB eMMC | 32 GB partición de datos persistente |
| **Arquitectura de CPU** | MediaTek MT8666 (Octa-Core ARM64) | x86_64 con aceleración WHPX en AMD Ryzen |
| **Google Play Services** | No instalados de fábrica | No instalados (AOSP puro oficial) |
| **Persistencia** | Flash interna | Disco virtual persistente entre reinicios |

---

## 2. Estructura de Herramientas Creadas

El laboratorio se encuentra en la carpeta aislada `changan_x7_lab/` dentro de tu espacio de trabajo:

```text
c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\
│
├── changan_x7_lab\
│   ├── README.md                  # Esta guía completa
│   ├── check_environment.ps1      # Auditoría completa de SDK, AVD y aceleración
│   ├── start_emulator.bat         # Inicia el AVD en 1920x720 con aceleración WHPX
│   ├── install_launcher.bat       # Instala/actualiza Cockpit X7 con validación de seguridad
│   ├── capture_diagnostics.bat    # Genera reporte de resolución, ventanas y logcat
│   ├── capture_screenshot.bat     # Guarda captura PNG de la pantalla del emulador
│   ├── collect_logs.bat           # Descarga logcat completo y filtrado del launcher
│   ├── switch_density.bat         # Alterna en caliente entre 213 DPI y 160 DPI
│   ├── diagnostics\               # Capturas PNG y reportes de diagnóstico
│   └── logs\                      # Archivos de registro logcat
```

---

## 3. Guía Rápida de Uso

### Paso 1: Verificar el Entorno
Abre PowerShell o terminal y ejecuta:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File changan_x7_lab\check_environment.ps1
```
Verifica que todos los componentes (SDK, AVD, emulador, imagen API 28 y APK) muestren `[OK]`.

### Paso 2: Iniciar el Emulador
Haz doble clic en:
```text
start_emulator.bat
```
* O por línea de comandos para iniciar el perfil de referencia:
  `start_emulator.bat 213`
* O para iniciar el perfil de compatibilidad:
  `start_emulator.bat 160`

El emulador iniciará en una ventana panorámica nativa de **1920 × 720 píxeles** con aceleración por hardware WHPX en tu procesador AMD Ryzen 7 5700X.

### Paso 3: Instalar o Actualizar Cockpit X7
Con el emulador abierto, haz doble clic en:
```text
install_launcher.bat
```
* **Mecanismo de seguridad activo:** El script verifica que el dispositivo ADB sea estrictamente `emulator-5554`. Si conectas tu vehículo por cable USB a la laptop, el script **NUNCA** intentará instalar o modificar nada en el vehículo físico.

### Paso 4: Probar y Cambiar Densidad (213 DPI vs 160 DPI)
Para comparar cómo se escala la interfaz gráfica:
```text
switch_density.bat
```
* Opción 1: Aplica `wm density 213`
* Opción 2: Aplica `wm density 160`
* Opción 3: Restablece a la densidad de hardware original (`wm density reset`)

### Paso 5: Capturar Pantalla y Diagnósticos
* Para guardar una captura PNG instantánea:
  `capture_screenshot.bat`
* Para generar un reporte forense completo de ventanas y estado:
  `capture_diagnostics.bat`
* Para descargar los registros de errores:
  `collect_logs.bat`

---

## 4. Hallazgo Clave y Diagnóstico de las Franjas Negras

Durante la auditoría forense del proyecto y las pruebas en el emulador se compararon las capturas reales del vehículo (`scratch_car_screen.png`, `scratch_launcher_screen.png`) frente al emulador (`06_cockpit_clean.png`):

### ¿Por qué aparecen franjas negras en el auto físico?
1. **En el Emulador Virtual:**
   * La ventana de `MainActivity` ocupa el 100% de la superficie física (`mFrame=[0,0][1920,720]`).
   * El código HTML/CSS/JS de Cockpit X7 (`width: 100vw; height: 100vh`) llena **completamente** la pantalla sin ninguna franja negra.
   * **Conclusión 1:** El código de Cockpit X7 y su WebView **NO** generan franjas negras por sí mismos; su diseño es completamente adaptable y llena los 1920 píxeles horizontales.

2. **En la Unidad Multimedia Real del Vehículo (Changan X7 Plus):**
   * El sistema operativo del vehículo no es un Android AOSP puro, sino una versión personalizada por el fabricante con la interfaz **ChinaTSP / OnStyle 3.0.1**.
   * En las capturas forenses del auto (`scratch_launcher_screen.png` y `scratch_after_resize.png`), se observa claramente que las franjas laterales **no están vacías**:
     * **Franja izquierda:** Contiene los controles del sistema del auto: botón de cerrar ventana (`X`), botón volver (`<`), reloj (`19:56` / `20:03`), estado del climatizador/ventilador (`fan 00`) y botón físico de Inicio (`Home`).
     * **Franja derecha:** Contiene la barra de iconos de estado (DVR Cámara, Wi-Fi, Bluetooth) y en la parte inferior la pestaña de la tarea activa (`Cockpit X7...` con icono Android).
   * **Conclusión 2:** El gestor de ventanas (`WindowManager` / `SystemUI`) del firmware ChinaTSP del vehículo trata a las aplicaciones instaladas por ADB como **aplicaciones secundarias en modo ventana / huésped**, reservando ambos docks laterales (izquierdo y derecho) a menos que la aplicación posea permisos especiales OEM, esté firmada con la clave de plataforma del auto, o se integre con los servicios propietarios de ChinaTSP.

---

## 5. Diferencias entre el Entorno Virtual y el Firmware OEM

| Componente | Laboratorio Virtual (AOSP Genérico) | Radio Real (Firmware ChinaTSP) |
| :--- | :--- | :--- |
| **SystemUI** | Barra de estado y navegación estándar de Android | SystemUI personalizado ChinaTSP con dock lateral de controles y clima |
| **Gestión de Ventanas** | Pantalla completa inmersiva real (`1920x720`) | Multi-ventana con contenedor para aplicaciones de terceros |
| **Firma del Sistema** | Claves de prueba AOSP estándar | Clave privada OEM de Changan / ChinaTSP |
| **Módulos de Hardware** | Emulados (GPS genérico, Audio, GPU Vulkan/GLES) | Bus CAN automotriz, MCU SWC.2506, cámaras 360 AVM, DSP de audio |
| **Servicios Propietarios** | Ausentes (sin `com.chinatsp.*`) | Presentes (`com.chinatsp.vehiclecontrol`, `com.chinatsp.avmlive`, etc.) |

---

## 6. Próximos Pasos para Eliminar las Franjas Negras en el Vehículo

Con el laboratorio virtual completamente operativo y verificado, las siguientes líneas de investigación deben probarse en el laboratorio antes de llevarlas al auto:

1. **Declaración en `AndroidManifest.xml`:**
   * Agregar explícitamente:
     ```xml
     <meta-data android:name="android.max_aspect" android:value="2.67" />
     <supports-screens
         android:resizeable="true"
         android:smallScreens="true"
         android:normalScreens="true"
         android:largeScreens="true"
         android:xlargeScreens="true"
         android:anyDensity="true" />
     ```
   * En Android 9 (API 28), aplicaciones sin `resizeableActivity="true"` o sin `max_aspect` superior a 1.86 sufren encajonamiento ("letterboxing") por parte de ciertos gestores de ventanas OEM.

2. **Categoría HOME y Default Launcher:**
   * Verificar en el vehículo mediante ADB si el sistema permite seleccionar Cockpit X7 como el launcher predeterminado del sistema (`cmd package set-home-activity com.changan.x7plus.launcher/.MainActivity`). Al convertirse en el Home oficial reconocido, el gestor de ventanas OEM suele retirar los docks laterales de multi-ventana.

3. **Inmersión Profunda (`SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN`):**
   * Configurar flags avanzados de layout en `MainActivity.java` para solicitar a SystemUI la superficie completa sin insets decorativos.
