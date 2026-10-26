import os
import sys
import subprocess
import time

SDK_ROOT = r"C:\Users\axeln\AppData\Local\Android\Sdk"
EMULATOR_BIN = os.path.join(SDK_ROOT, "emulator", "emulator.exe")
ADB_BIN = os.path.join(SDK_ROOT, "platform-tools", "adb.exe")

def is_emulator_running():
    try:
        res = subprocess.run([ADB_BIN, "devices"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if "emulator-" in line and "device" in line:
                return line.split()[0]
    except Exception as e:
        print("Error checking devices:", e)
    return None

def start_emulator(avd_name="Changan_X7_Plus_API28_1920x720", port=5554):
    device_id = f"emulator-{port}"
    running = is_emulator_running()
    if running:
        print(f"Emulator is already running: {running}")
        return running

    print(f"Starting emulator for AVD '{avd_name}' on port {port}...")
    cmd = [
        EMULATOR_BIN,
        "-avd", avd_name,
        "-port", str(port),
        "-gpu", "auto",
        "-accel", "on",
        "-no-boot-anim",
    ]
    # Launch detached process
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

    print("Emulator process launched. Waiting for ADB connection...")
    # Wait for device to appear in adb devices
    start_time = time.time()
    while time.time() - start_time < 90:
        res = subprocess.run([ADB_BIN, "devices"], capture_output=True, text=True)
        if device_id in res.stdout:
            print(f"Device {device_id} detected in ADB.")
            break
        time.sleep(2)
    else:
        print("Timeout waiting for emulator to appear in ADB.")
        return None

    # Wait for boot completion
    print("Waiting for Android OS to complete booting (sys.boot_completed=1)...")
    while time.time() - start_time < 180:
        res = subprocess.run([ADB_BIN, "-s", device_id, "shell", "getprop", "sys.boot_completed"], capture_output=True, text=True)
        if res.stdout.strip() == "1":
            print(f"Android OS boot completed on {device_id}!")
            break
        time.sleep(3)
    else:
        print("Timeout waiting for sys.boot_completed.")
        return None

    return device_id

if __name__ == "__main__":
    avd = sys.argv[1] if len(sys.argv) > 1 else "Changan_X7_Plus_API28_1920x720"
    dev = start_emulator(avd)
    if dev:
        print(f"SUCCESS: Emulator ready: {dev}")
    else:
        print("FAILED to start emulator.")
