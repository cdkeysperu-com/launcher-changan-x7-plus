# -*- coding: utf-8 -*-
"""
Generador y Compilador de WebApps Nativas Automotrices 1920x720:
- kick_streaming_live.apk (Kick Live Streaming via Brave Fullscreen)
- youtube_web_pro.apk (YouTube Premium via Brave Fullscreen sin anuncios)
"""

import os
import sys
import shutil
import subprocess
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "tools")
AAPT2 = os.path.join(TOOLS_DIR, "aapt2.exe")
ANDROID_JAR = os.path.join(TOOLS_DIR, "android.jar")
JAVAC = os.path.join(TOOLS_DIR, "jdk", "bin", "javac.exe")
JAVA = os.path.join(TOOLS_DIR, "jdk", "bin", "java.exe")
R8_JAR = os.path.join(TOOLS_DIR, "r8.jar")
JARSIGNER = os.path.join(TOOLS_DIR, "jdk", "bin", "jarsigner.exe")
KEYSTORE = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "launcher_android", "release.keystore")

def build_app(app_id, pkg_name, app_name, start_url, icon_type, out_filename):
    print(f"\n==================================================")
    print(f" Compilando {app_name} ({pkg_name})...")
    print(f"==================================================")

    build_dir = os.path.join(BASE_DIR, "build_scratch", app_id)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    res_dir = os.path.join(build_dir, "res")
    layout_dir = os.path.join(res_dir, "layout")
    values_dir = os.path.join(res_dir, "values")
    drawable_dir = os.path.join(res_dir, "drawable")
    src_dir = os.path.join(build_dir, "src")
    gen_dir = os.path.join(build_dir, "gen")
    classes_dir = os.path.join(build_dir, "classes")
    bin_dir = os.path.join(build_dir, "bin")

    for d in [layout_dir, values_dir, drawable_dir, gen_dir, classes_dir, bin_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. AndroidManifest.xml
    manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{pkg_name}"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:label="{app_name}"
        android:icon="@drawable/ic_launcher"
        android:hardwareAccelerated="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">

        <meta-data android:name="android.max_aspect" android:value="3.5" />
        <meta-data android:name="com.chinatsp.systemui.fullscreen" android:value="true" />

        <activity
            android:name=".MainActivity"
            android:label="{app_name}"
            android:screenOrientation="landscape"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    manifest_path = os.path.join(build_dir, "AndroidManifest.xml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest_content)

    # 2. Strings
    strings_content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
</resources>
"""
    with open(os.path.join(values_dir, "strings.xml"), "w", encoding="utf-8") as f:
        f.write(strings_content)

    # 3. Create high quality icon using Pillow
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (192, 192), color=(8, 12, 20, 255))
    draw = ImageDraw.Draw(img)

    if icon_type == "kick":
        # Green neon Kick brand style
        draw.rounded_rectangle([12, 12, 180, 180], radius=36, fill=(15, 23, 42), outline=(83, 252, 24), width=4)
        # Draw "K"
        draw.rectangle([54, 46, 76, 146], fill=(83, 252, 24))
        draw.polygon([(76, 96), (132, 46), (146, 58), (94, 102)], fill=(83, 252, 24))
        draw.polygon([(88, 98), (138, 146), (120, 146), (76, 106)], fill=(83, 252, 24))
    else:
        # YouTube red brand style
        draw.rounded_rectangle([12, 12, 180, 180], radius=36, fill=(15, 23, 42), outline=(255, 0, 0), width=4)
        draw.rounded_rectangle([38, 54, 154, 138], radius=24, fill=(255, 0, 0))
        # White play triangle
        draw.polygon([(82, 74), (122, 96), (82, 118)], fill=(255, 255, 255))

    img.save(os.path.join(drawable_dir, "ic_launcher.png"))

    # 4. Java Source Code
    pkg_subpath = pkg_name.replace(".", os.sep)
    java_pkg_dir = os.path.join(src_dir, pkg_subpath)
    os.makedirs(java_pkg_dir, exist_ok=True)

    java_code = f"""package {pkg_name};

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;

public class MainActivity extends Activity {{

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);

        // Bypass Changan F202 Fullscreen Status Bar
        try {{
            Intent auth = new Intent("com.chinatsp.systemui.ACTION_APP_INFO");
            auth.putExtra("packageName", "com.brave.browser");
            auth.putExtra("appCentered", 2);
            sendBroadcast(auth);

            Intent hide = new Intent("com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR");
            hide.putExtra("packageName", "com.brave.browser");
            sendBroadcast(hide);
        }} catch (Exception ignored) {{}}

        // Iniciar directamente en Brave Browser Fullscreen
        try {{
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("{start_url}"));
            intent.setPackage("com.brave.browser");
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        }} catch (Exception e) {{
            try {{
                Intent generic = new Intent(Intent.ACTION_VIEW, Uri.parse("{start_url}"));
                generic.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(generic);
            }} catch (Exception ignored) {{}}
        }}

        finish();
    }}
}}
"""
    with open(os.path.join(java_pkg_dir, "MainActivity.java"), "w", encoding="utf-8") as f:
        f.write(java_code)

    # 5. aapt2 compile
    compiled_res = os.path.join(build_dir, "compiled_res.zip")
    subprocess.run([AAPT2, "compile", "--dir", res_dir, "-o", compiled_res], check=True)

    # 6. aapt2 link
    base_apk = os.path.join(bin_dir, "base.apk")
    subprocess.run([
        AAPT2, "link",
        "-I", ANDROID_JAR,
        "--manifest", manifest_path,
        "--java", gen_dir,
        "-o", base_apk,
        "--auto-add-overlay",
        compiled_res
    ], check=True)

    # 7. javac
    java_files = [os.path.join(java_pkg_dir, "MainActivity.java")]
    for root, _, files in os.walk(gen_dir):
        for fl in files:
            if fl.endswith(".java"):
                java_files.append(os.path.join(root, fl))

    subprocess.run([
        JAVAC,
        "-encoding", "UTF-8",
        "-cp", ANDROID_JAR,
        "-d", classes_dir
    ] + java_files, check=True)

    # 8. R8 / D8 dex compiler
    class_files = []
    for root, _, files in os.walk(classes_dir):
        for fl in files:
            if fl.endswith(".class"):
                class_files.append(os.path.join(root, fl))

    dex_dir = os.path.join(build_dir, "dex")
    os.makedirs(dex_dir, exist_ok=True)
    d8_cmd = [
        JAVA, "-cp", R8_JAR,
        "com.android.tools.r8.D8",
        "--min-api", "28",
        "--output", dex_dir,
        "--lib", ANDROID_JAR
    ] + class_files
    subprocess.run(d8_cmd, check=True)

    # 9. Add classes.dex to base.apk
    classes_dex = os.path.join(dex_dir, "classes.dex")
    unsigned_apk = os.path.join(bin_dir, "unsigned.apk")
    shutil.copy2(base_apk, unsigned_apk)
    with zipfile.ZipFile(unsigned_apk, "a") as z:
        z.write(classes_dex, "classes.dex")

    # 10. Sign APK
    signed_apk = os.path.join(bin_dir, "signed.apk")
    sign_cmd = [
        JARSIGNER,
        "-keystore", KEYSTORE,
        "-storepass", "changan2026",
        "-keypass", "changan2026",
        "-digestalg", "SHA-256",
        "-sigalg", "SHA256withRSA",
        "-signedjar", signed_apk,
        unsigned_apk,
        "changan_x7"
    ]
    subprocess.run(sign_cmd, check=True)

    # 11. Copy to portable & ready
    dest_portable = os.path.join(BASE_DIR, "portable", "apks", out_filename)
    dest_ready = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "apks_listos_para_instalar", out_filename)
    dest_local_apks = os.path.join(BASE_DIR, "APK CHANGAN X7 PLUS", "apks", out_filename)

    for dst in [dest_portable, dest_ready, dest_local_apks]:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(signed_apk, dst)
    print(f"[OK] Creado e instalado: {dest_portable} ({os.path.getsize(dest_portable)} bytes)")

def main():
    # 1. YouTube Premium Web Pro
    build_app(
        app_id="youtube_web",
        pkg_name="com.changan.youtube",
        app_name="YouTube Premium",
        start_url="https://m.youtube.com",
        icon_type="youtube",
        out_filename="youtube_web_pro.apk"
    )

    # 2. Kick Live Streaming
    build_app(
        app_id="kick_live",
        pkg_name="com.changan.kick",
        app_name="Kick Live",
        start_url="https://kick.com",
        icon_type="kick",
        out_filename="kick_streaming_live.apk"
    )

    print("\n¡APKs nativas de YouTube y Kick compiladas y firmadas con éxito!")

if __name__ == "__main__":
    main()
