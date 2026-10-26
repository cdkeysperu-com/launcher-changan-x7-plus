import os
import sys
import subprocess

SDK_ROOT = r"C:\Users\axeln\AppData\Local\Android\Sdk"
AVDMANAGER = os.path.join(SDK_ROOT, "cmdline-tools", "latest", "bin", "avdmanager.bat")
JBR_HOME = r"C:\Program Files\Android\Android Studio\jbr"
USER_HOME = os.path.expanduser("~")
AVD_BASE_DIR = os.path.join(USER_HOME, ".android", "avd")

def create_and_configure_avd(avd_name, density, ram_mb=4096, disk_size="32G"):
    env = os.environ.copy()
    env["JAVA_HOME"] = JBR_HOME
    env["PATH"] = os.path.join(JBR_HOME, "bin") + ";" + env["PATH"]
    env["ANDROID_HOME"] = SDK_ROOT
    env["ANDROID_SDK_ROOT"] = SDK_ROOT

    print(f"\n--- Creating AVD: {avd_name} (Density: {density} DPI) ---")
    cmd = [
        AVDMANAGER, "create", "avd",
        "-n", avd_name,
        "-k", "system-images;android-28;default;x86_64",
        "--force"
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
    out, err = p.communicate(input="no\n")
    print("AVDManager output:", out.strip())
    if err.strip():
        print("AVDManager stderr:", err.strip())

    avd_dir = os.path.join(AVD_BASE_DIR, f"{avd_name}.avd")
    config_ini_path = os.path.join(avd_dir, "config.ini")
    
    if not os.path.exists(config_ini_path):
        print(f"ERROR: {config_ini_path} not found!")
        return False

    # Read existing config
    config = {}
    with open(config_ini_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()

    # Apply target specs for Changan X7 Plus Head Unit
    custom_settings = {
        "hw.lcd.width": "1920",
        "hw.lcd.height": "720",
        "hw.lcd.density": str(density),
        "hw.ramSize": str(ram_mb),
        "disk.dataPartition.size": disk_size,
        "vm.heapSize": "512",
        "hw.gpu.enabled": "yes",
        "hw.gpu.mode": "auto",
        "hw.keyboard": "yes",
        "hw.battery": "no",          # Automotive unit powered by vehicle 12V ACC, not battery
        "hw.gps": "yes",              # Automotive GPS
        "hw.audioInput": "yes",
        "hw.mainKeys": "no",
        "hw.dPad": "no",
        "skin.name": "1920x720",
        "hw.initialOrientation": "landscape",
    }
    config.update(custom_settings)

    with open(config_ini_path, "w", encoding="utf-8") as f:
        for k in sorted(config.keys()):
            f.write(f"{k} = {config[k]}\n")

    print(f"Configured {config_ini_path} successfully:")
    for k in ["hw.lcd.width", "hw.lcd.height", "hw.lcd.density", "hw.ramSize", "disk.dataPartition.size", "hw.gpu.mode"]:
        print(f"  {k} = {config.get(k)}")
    return True

if __name__ == "__main__":
    os.makedirs(AVD_BASE_DIR, exist_ok=True)
    # 1. Reference AVD (213 DPI)
    create_and_configure_avd("Changan_X7_Plus_API28_1920x720", density=213)
    # 2. Compatibility AVD (160 DPI)
    create_and_configure_avd("Changan_X7_Plus_API28_160DPI", density=160)
