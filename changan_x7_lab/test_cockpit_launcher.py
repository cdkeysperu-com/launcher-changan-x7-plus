import os
import sys
import subprocess
import time

ADB = r"C:\Users\axeln\AppData\Local\Android\Sdk\platform-tools\adb.exe"
DEV = "emulator-5554"
APK_PATH = r"C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1\apks\x7_cockpit_launcher.apk"
OUTPUT_DIR = r"c:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\changan_x7_lab\diagnostics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip()

def capture_screen(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    cmd = [ADB, "-s", DEV, "exec-out", "screencap", "-p"]
    with open(filepath, "wb") as f:
        subprocess.run(cmd, stdout=f)
    print(f"Captured screenshot to: {filepath} ({os.path.getsize(filepath)} bytes)")
    return filepath

def main():
    print("=== TESTING COCKPIT X7 LAUNCHER IN CHANGAN X7 LAB ===")

    # 1. Capture initial system home screen
    capture_screen("01_initial_home_screen.png")

    # 2. Check Display & Density
    size_out, _ = run_adb(["shell", "wm", "size"])
    density_out, _ = run_adb(["shell", "wm", "density"])
    print(f"Display: {size_out}")
    print(f"Density: {density_out}")

    # 3. Clear logcat
    run_adb(["logcat", "-c"])

    # 4. Install APK
    print(f"Installing APK: {APK_PATH}...")
    install_out, install_err = run_adb(["install", "-r", "-g", APK_PATH])
    print(f"Install stdout: {install_out}")
    if install_err:
        print(f"Install stderr: {install_err}")

    # 5. Launch MainActivity
    print("Launching com.changan.x7plus.launcher/.MainActivity...")
    launch_out, launch_err = run_adb(["shell", "am", "start", "-n", "com.changan.x7plus.launcher/.MainActivity"])
    print(f"Launch stdout: {launch_out}")
    if launch_err:
        print(f"Launch stderr: {launch_err}")

    # Give UI time to render webview
    time.sleep(3)

    # 6. Capture screenshot after launch
    capture_screen("02_cockpit_x7_launched.png")

    # 7. Dump window diagnostics
    dumpsys_out, _ = run_adb(["shell", "dumpsys", "window", "displays"])
    with open(os.path.join(OUTPUT_DIR, "dumpsys_window_displays.txt"), "w", encoding="utf-8") as f:
        f.write(dumpsys_out)

    dumpsys_win, _ = run_adb(["shell", "dumpsys", "window", "windows"])
    with open(os.path.join(OUTPUT_DIR, "dumpsys_window_windows.txt"), "w", encoding="utf-8") as f:
        f.write(dumpsys_win)

    # 8. Dump logcat
    logcat_out, _ = run_adb(["logcat", "-d"])
    with open(os.path.join(OUTPUT_DIR, "logcat_cockpit_test.txt"), "w", encoding="utf-8") as f:
        f.write(logcat_out)

    # 9. Extract focus and window bounds
    for line in dumpsys_win.splitlines():
        if "com.changan.x7plus.launcher" in line or "mCurrentFocus" in line or "mFocusedApp" in line:
            print("Focus/Window:", line.strip())

    print("\nTest run complete. All diagnostics saved in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
