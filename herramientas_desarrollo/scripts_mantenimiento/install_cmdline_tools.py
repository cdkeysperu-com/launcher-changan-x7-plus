import os
import sys
import urllib.request
import zipfile
import shutil

SDK_ROOT = r"C:\Users\axeln\AppData\Local\Android\Sdk"
CMDLINE_DIR = os.path.join(SDK_ROOT, "cmdline-tools")
LATEST_DIR = os.path.join(CMDLINE_DIR, "latest")
URL = "https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip"
ZIP_PATH = os.path.join(SDK_ROOT, "cmdline-tools.zip")

def download_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = downloaded / total_size * 100 if total_size > 0 else 0
    if block_num % 1000 == 0 or downloaded >= total_size:
        print(f"Downloading: {percent:.1f}% ({downloaded // (1024*1024)} MB / {total_size // (1024*1024)} MB)")

def setup_cmdline_tools():
    print(f"Downloading official Google Android cmdline-tools from {URL}...")
    urllib.request.urlretrieve(URL, ZIP_PATH, download_progress)
    print("Download complete. Extracting...")

    temp_extract = os.path.join(SDK_ROOT, "temp_cmdline")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(temp_extract)

    extracted_inner = os.path.join(temp_extract, "cmdline-tools")
    os.makedirs(CMDLINE_DIR, exist_ok=True)
    if os.path.exists(LATEST_DIR):
        shutil.rmtree(LATEST_DIR)

    shutil.move(extracted_inner, LATEST_DIR)
    shutil.rmtree(temp_extract)
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    sdkmanager_bat = os.path.join(LATEST_DIR, "bin", "sdkmanager.bat")
    print(f"Successfully installed cmdline-tools! sdkmanager is at: {sdkmanager_bat}")
    return os.path.exists(sdkmanager_bat)

if __name__ == "__main__":
    setup_cmdline_tools()
