# -*- coding: utf-8 -*-
"""
APLICACIÓN DEL BYPASS FULLSCREEN (F202_SystemUI)
1. Migra package name a com.chinatsp.x7plus.launcher
2. Añade broadcasts y hooks de desbloqueo nativo OEM en MainActivity.java
3. Actualiza activity_main.xml
4. Actualiza AndroidManifest.xml
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS")
LAUNCHER_DIR = os.path.join(PROJECT_DIR, "launcher_android")
SRC_DIR = os.path.join(LAUNCHER_DIR, "src")
OLD_PKG_DIR = os.path.join(SRC_DIR, "com", "changan", "x7plus", "launcher")
NEW_PKG_DIR = os.path.join(SRC_DIR, "com", "chinatsp", "x7plus", "launcher")
MANIFEST_PATH = os.path.join(LAUNCHER_DIR, "AndroidManifest.xml")
LAYOUT_PATH = os.path.join(LAUNCHER_DIR, "res", "layout", "activity_main.xml")

print("====================================================================")
print("APLICANDO BYPASS DEFINITIVO: com.chinatsp.x7plus.launcher")
print("====================================================================")

# 1. Crear nuevo directorio de fuentes
os.makedirs(NEW_PKG_DIR, exist_ok=True)

# 2. Mover y actualizar archivos Java
java_files = [f for f in os.listdir(OLD_PKG_DIR) if f.endswith(".java")]
for jf in java_files:
    old_file = os.path.join(OLD_PKG_DIR, jf)
    new_file = os.path.join(NEW_PKG_DIR, jf)
    with open(old_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Reemplazar package
    content = content.replace("package com.changan.x7plus.launcher;", "package com.chinatsp.x7plus.launcher;")
    content = content.replace("import com.changan.x7plus.launcher.", "import com.chinatsp.x7plus.launcher.")
    content = content.replace("com.changan.x7plus.launcher", "com.chinatsp.x7plus.launcher")

    # Si es MainActivity.java, inyectar el método de desbloqueo F202
    if jf == "MainActivity.java":
        if "unlockChanganF202Fullscreen" not in content:
            unlock_method = """
    /**
     * BYPASS FORENSE F202_SystemUI:
     * Transmite los Broadcasts y propiedades exactas para eliminar las barras laterales (320px)
     * y liberar los 1920x720 pixeles nativos de la pantalla Changan X7 Plus.
     */
    private void unlockChanganF202Fullscreen() {
        try {
            // 1. Broadcast de Autorización Dinámica a PageChangeHandler$6 (appCentered = 2)
            Intent authIntent = new Intent("com.chinatsp.systemui.ACTION_APP_INFO");
            authIntent.putExtra("packageName", getPackageName());
            authIntent.putExtra("appCentered", 2);
            sendBroadcast(authIntent);

            // 2. Broadcast de Ocultación de Barra de Estado Propietaria
            Intent hideBarIntent = new Intent("com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR");
            hideBarIntent.putExtra("packageName", getPackageName());
            sendBroadcast(hideBarIntent);

            // 3. Notificación de Actividad Reanudada para forzar hideNaviBar() y hideThirdAppFullScreen()
            Intent resumeIntent = new Intent("com.chinatsp.activity.onpostresume");
            resumeIntent.putExtra("packageName", getPackageName());
            sendBroadcast(resumeIntent);
            
            android.util.Log.i("ChanganCockpit", "[F202_BYPASS] Broadcasts de desbloqueo transmitidos exitosamente a F202_SystemUI");
        } catch (Exception e) {
            android.util.Log.e("ChanganCockpit", "[F202_BYPASS] Error transmitiendo broadcasts", e);
        }
    }
"""
            # Insertar método antes del final de la clase
            last_brace = content.rfind("}")
            content = content[:last_brace] + unlock_method + "\n}\n"

            # Inyectar llamada en onCreate y onResume
            content = content.replace("enforceFullScreenBounds();", "enforceFullScreenBounds();\n        unlockChanganF202Fullscreen();")
            content = content.replace("setImmersiveMode();\n        registerHardwareKeyReceiver();", "setImmersiveMode();\n        unlockChanganF202Fullscreen();\n        registerHardwareKeyReceiver();")

    with open(new_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Migrado {jf} -> com.chinatsp.x7plus.launcher")

# Eliminar carpeta antigua de fuentes si ya se copiaron todos
if os.path.exists(OLD_PKG_DIR):
    shutil.rmtree(OLD_PKG_DIR)
    # Limpiar directorios vacios de changan
    parent = os.path.dirname(OLD_PKG_DIR)
    if os.path.exists(parent) and not os.listdir(parent):
        shutil.rmtree(parent)
    parent2 = os.path.dirname(parent)
    if os.path.exists(parent2) and not os.listdir(parent2):
        shutil.rmtree(parent2)

# 3. Actualizar AndroidManifest.xml
with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest_content = f.read()

manifest_content = manifest_content.replace('package="com.changan.x7plus.launcher"', 'package="com.chinatsp.x7plus.launcher"')
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    f.write(manifest_content)
print("  [OK] AndroidManifest.xml actualizado con package='com.chinatsp.x7plus.launcher'")

# 4. Actualizar activity_main.xml
with open(LAYOUT_PATH, "r", encoding="utf-8") as f:
    layout_content = f.read()

layout_content = layout_content.replace("com.changan.x7plus.launcher.FullScreenVideoView", "com.chinatsp.x7plus.launcher.FullScreenVideoView")
with open(LAYOUT_PATH, "w", encoding="utf-8") as f:
    f.write(layout_content)
print("  [OK] activity_main.xml actualizado con com.chinatsp.x7plus.launcher.FullScreenVideoView")

print("\n¡Migración de código fuente completada exitosamente!")
