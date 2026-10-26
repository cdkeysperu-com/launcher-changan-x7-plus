import re

target_file = r"C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1\build_launcher_apk.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update manifest_content
old_manifest_regex = r'manifest_content = """<\?xml.*?<\/manifest>\s*"""'
new_manifest = '''manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.changan.x7plus.launcher"
    android:versionCode="202611"
    android:versionName="2.2.0">

    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="28" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />

    <!-- Soporte completo para pantalla ultra-panorámica 8:3 y densidades automotrices -->
    <supports-screens
        android:resizeable="true"
        android:smallScreens="true"
        android:normalScreens="true"
        android:largeScreens="true"
        android:xlargeScreens="true"
        android:anyDensity="true" />

    <application
        android:label="@string/app_name"
        android:hardwareAccelerated="true"
        android:supportsRtl="true"
        android:resizeableActivity="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">

        <!-- Desbloqueo de aspecto ultra-ancho 8:3 (2.67:1) -->
        <meta-data android:name="android.max_aspect" android:value="2.67" />

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTask"
            android:stateNotNeeded="true"
            android:resizeableActivity="true"
            android:screenOrientation="landscape"
            android:configChanges="orientation|screenSize|keyboardHidden|smallestScreenSize|screenLayout|density">

            <!-- PRIORIDAD MAXIMA DE HOME LAUNCHER -->
            <intent-filter android:priority="1000">
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.HOME" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

    </application>
</manifest>
"""'''

content = re.sub(old_manifest_regex, new_manifest, content, flags=re.DOTALL)

# 2. Update MainActivity.java onCreate to include cutout & display surface mode
old_on_create = """        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        setImmersiveMode();"""

new_on_create = """        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        // Desbloqueo de superficie completa y cutout en Android 9 Pie (API 28)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
            getWindow().getAttributes().layoutInDisplayCutoutMode = 
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }

        setImmersiveMode();"""

content = content.replace(old_on_create, new_on_create)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated build_launcher_apk.py successfully.")
