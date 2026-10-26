import os

def update_servers():
    paths = [
        r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\portable\server.py",
        r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\server.py"
    ]
    
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        old_aa_block = """    aa_apk = find_suite_apk("headunit_android_auto.apk")
    if aa_apk:
        install_single_apk(aa_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "gb.xxy.hr", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "pm", "grant", "gb.xxy.hr", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        steps.append({"title": "Headunit Reloaded (Android Auto Directo)", "status": "ok", "msg": "Android Auto nativo por cable USB instalado"})"""

        new_aa_block = """    aa_apk = find_suite_apk("headunit_android_auto.apk")
    if aa_apk:
        install_single_apk(aa_apk, timeout=90)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.ACCESS_COARSE_LOCATION"], timeout=5)
        run_adb(["shell", "pm", "grant", "com.andrerinas.headunitrevived", "android.permission.SYSTEM_ALERT_WINDOW"], timeout=5)
        run_adb(["shell", "appops", "set", "com.andrerinas.headunitrevived", "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "pm", "grant", "gb.xxy.hr", "android.permission.RECORD_AUDIO"], timeout=5)
        run_adb(["shell", "pm", "grant", "gb.xxy.hr", "android.permission.ACCESS_FINE_LOCATION"], timeout=5)
        run_adb(["shell", "appops", "set", "gb.xxy.hr", "SYSTEM_ALERT_WINDOW", "allow"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", "--es", "packageName", "com.andrerinas.headunitrevived", "--ei", "appCentered", "2"], timeout=5)
        run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", "--es", "packageName", "com.andrerinas.headunitrevived"], timeout=5)
        steps.append({"title": "Headunit Revived (Android Auto Widescreen)", "status": "ok", "msg": "Android Auto nativo panorámico 1920x720 instalado y configurado"})"""

        content = content.replace(old_aa_block, new_aa_block)
        
        # In execute_global_margin_fix, add broadcast for Headunit Revived
        old_margin_block = """    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", 
             "--es", "packageName", launcher_pkg, "--ei", "appCentered", "2"], timeout=5)"""
             
        new_margin_block = """    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", 
             "--es", "packageName", launcher_pkg, "--ei", "appCentered", "2"], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.chinatsp.systemui.ACTION_APP_INFO", 
             "--es", "packageName", "com.andrerinas.headunitrevived", "--ei", "appCentered", "2"], timeout=5)
    run_adb(["shell", "am", "broadcast", "-a", "com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR", 
             "--es", "packageName", "com.andrerinas.headunitrevived"], timeout=5)"""

        content = content.replace(old_margin_block, new_margin_block)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated server: {path}")

if __name__ == "__main__":
    update_servers()
