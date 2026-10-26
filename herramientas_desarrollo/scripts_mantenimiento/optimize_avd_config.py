import os

user_dir = os.path.expanduser("~")
avd_dir = os.path.join(user_dir, ".android", "avd")

avds = ["Changan_X7_Plus_API28_1920x720", "Changan_X7_Plus_API28_160DPI"]

for avd in avds:
    ini_path = os.path.join(avd_dir, f"{avd}.avd", "config.ini")
    if not os.path.exists(ini_path):
        continue

    # Read config
    lines = []
    with open(ini_path, "r", encoding="utf-8") as f:
        for line in f:
            line_s = line.strip()
            if line_s.startswith("showDeviceFrame"):
                lines.append("showDeviceFrame = no\n")
            elif line_s.startswith("skin.dynamic"):
                lines.append("skin.dynamic = yes\n")
            elif line_s.startswith("skin.path"):
                lines.append("skin.path = _no_skin\n")
            else:
                lines.append(line)

    with open(ini_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Updated {ini_path} (showDeviceFrame=no, skin.dynamic=yes)")

    # Clean lock files
    avd_folder = os.path.join(avd_dir, f"{avd}.avd")
    for f in os.listdir(avd_folder):
        if f.endswith(".lock"):
            try:
                os.remove(os.path.join(avd_folder, f))
                print(f"Removed stale lock: {f}")
            except Exception as e:
                print(f"Could not remove {f}: {e}")
