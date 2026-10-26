import os

def update_install_bats():
    paths = [
        r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\portable\INSTALAR_TODO_EN_EL_AUTO.bat",
        r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\INSTALAR_TODO_EN_EL_AUTO.bat"
    ]
    
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if "REM Headunit Reloaded" in line or "REM Headunit Revived" in line:
                # Skip until REM Waze GPS
                while i < len(lines) and "REM Waze GPS" not in lines[i]:
                    i += 1
                
                # Insert modern Headunit Revived and AutoKit blocks
                new_lines.append("REM Headunit Revived (Android Auto Oficial Widescreen 1920x720)\n")
                new_lines.append("if exist \"apks\\headunit_android_auto.apk\" (\n")
                new_lines.append("    echo Instalando Headunit Revived (Android Auto Nativo)...\n")
                new_lines.append("    tools\\adb.exe install -r -d \"apks\\headunit_android_auto.apk\"\n")
                new_lines.append("    tools\\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.RECORD_AUDIO >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.ACCESS_FINE_LOCATION >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.ACCESS_COARSE_LOCATION >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant com.andrerinas.headunitrevived android.permission.SYSTEM_ALERT_WINDOW >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell appops set com.andrerinas.headunitrevived SYSTEM_ALERT_WINDOW allow >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant gb.xxy.hr android.permission.RECORD_AUDIO >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant gb.xxy.hr android.permission.ACCESS_FINE_LOCATION >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell appops set gb.xxy.hr SYSTEM_ALERT_WINDOW allow >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName \"com.andrerinas.headunitrevived\" --ei appCentered 2 >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell am broadcast -a com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR --es packageName \"com.andrerinas.headunitrevived\" >nul 2>&1\n")
                new_lines.append("    echo [OK] Headunit Revived instalado con permisos y bypass de bordes negros.\n")
                new_lines.append(")\n\n")
                
                new_lines.append("REM AutoKit (Carlinkit CarPlay & Android Auto)\n")
                new_lines.append("if exist \"apks\\AutoKit.apk\" (\n")
                new_lines.append("    echo Instalando AutoKit (Carlinkit Dongle)...\n")
                new_lines.append("    tools\\adb.exe install -r -d \"apks\\AutoKit.apk\"\n")
                new_lines.append("    tools\\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.RECORD_AUDIO >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.ACCESS_FINE_LOCATION >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.READ_EXTERNAL_STORAGE >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell pm grant cn.manstep.phonemirrorBox android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1\n")
                new_lines.append("    tools\\adb.exe shell am broadcast -a com.chinatsp.systemui.ACTION_APP_INFO --es packageName \"cn.manstep.phonemirrorBox\" --ei appCentered 2 >nul 2>&1\n")
                new_lines.append("    echo [OK] AutoKit instalado con permisos y bypass.\n")
                new_lines.append(")\n\n")
                continue
            
            new_lines.append(line)
            i += 1
            
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Updated: {path}")

if __name__ == "__main__":
    update_install_bats()
