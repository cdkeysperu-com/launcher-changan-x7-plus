import os
import sys
import subprocess

SDK_ROOT = r"C:\Users\axeln\AppData\Local\Android\Sdk"
SDKMANAGER = os.path.join(SDK_ROOT, "cmdline-tools", "latest", "bin", "sdkmanager.bat")
JBR_HOME = r"C:\Program Files\Android\Android Studio\jbr"

def install_packages():
    env = os.environ.copy()
    env["JAVA_HOME"] = JBR_HOME
    env["PATH"] = os.path.join(JBR_HOME, "bin") + ";" + env["PATH"]
    env["ANDROID_HOME"] = SDK_ROOT
    env["ANDROID_SDK_ROOT"] = SDK_ROOT

    # 1. Accept licenses
    print("Accepting licenses...")
    p = subprocess.Popen([SDKMANAGER, "--licenses"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
    out, err = p.communicate(input="y\n" * 50)
    print("Licenses output completed.")

    # 2. Install platform 28 and system image
    packages = ["platforms;android-28", "system-images;android-28;default;x86_64"]
    print(f"Installing packages: {packages}...")
    p = subprocess.Popen([SDKMANAGER] + packages, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
    out, err = p.communicate(input="y\n" * 10)
    print("Install output:")
    print(out[-1000:] if len(out) > 1000 else out)
    if err:
        print("Install error / warning:")
        print(err[-500:] if len(err) > 500 else err)

if __name__ == "__main__":
    install_packages()
