import os
import sys
import zipfile
import subprocess

def main():
    print("=== AUDIT PC AND PROJECT ===")
    
    # 1. Project directory
    project_root = r"C:\Users\axeln\OneDrive\Desktop\X7 PLUS 2.1"
    workspace_root = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL"
    print(f"Project root found: {project_root} (Exists: {os.path.exists(project_root)})")
    print(f"Virtual Lab workspace: {workspace_root}")

    # 2. Inspect APKs
    apks_dir = os.path.join(project_root, "apks")
    if os.path.exists(apks_dir):
        for apk in os.listdir(apks_dir):
            if apk.endswith(".apk") and ("cockpit" in apk.lower() or "x7" in apk.lower()):
                apk_path = os.path.join(apks_dir, apk)
                with zipfile.ZipFile(apk_path, "r") as z:
                    names = z.namelist()
                    libs = [n for n in names if n.startswith("lib/")]
                    print(f"\nAPK: {apk}")
                    print(f"  Size: {os.path.getsize(apk_path)} bytes")
                    print(f"  Files: {len(names)}")
                    print(f"  Native libs (lib/): {libs if libs else 'None (Architecture-independent DEX/bytecode, runs 100% on x86, x86_64, arm64)'}")

    # 3. Android SDK inspection
    sdk_root = r"C:\Users\axeln\AppData\Local\Android\Sdk"
    print(f"\nAndroid SDK Root: {sdk_root} (Exists: {os.path.exists(sdk_root)})")
    
    tools = {
        "emulator.exe": os.path.join(sdk_root, "emulator", "emulator.exe"),
        "adb.exe": os.path.join(sdk_root, "platform-tools", "adb.exe"),
        "cmdline-tools": os.path.join(sdk_root, "cmdline-tools"),
        "system-images": os.path.join(sdk_root, "system-images"),
        "platforms": os.path.join(sdk_root, "platforms"),
        "build-tools": os.path.join(sdk_root, "build-tools")
    }
    for k, v in tools.items():
        print(f"  {k}: {os.path.exists(v)} ({v})")

    # 4. Check platforms installed
    platforms_dir = tools["platforms"]
    if os.path.exists(platforms_dir):
        print(f"  Platforms installed: {os.listdir(platforms_dir)}")

    # 5. Check cmdline-tools / sdkmanager
    # Check if sdkmanager exists anywhere
    print("\nChecking for sdkmanager:")
    found_sdkmanager = None
    for root, dirs, files in os.walk(r"C:\Program Files\Android\Android Studio"):
        if "sdkmanager.bat" in files or "sdkmanager.exe" in files or "sdkmanager" in files:
            found_sdkmanager = os.path.join(root, "sdkmanager.bat")
            break
    print(f"  In Android Studio: {found_sdkmanager}")

if __name__ == "__main__":
    main()
