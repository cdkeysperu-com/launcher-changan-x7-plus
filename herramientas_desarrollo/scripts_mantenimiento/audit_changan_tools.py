# -*- coding: utf-8 -*-
import urllib.request
import re
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://api.changan-tools-global.com/'
print(f"Auditing: {url}")

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='replace')

with open('changan_tools_index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML saved (len={len(html)} bytes)")

# Find script URLs
scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
print("JavaScript files found:")
for s in scripts:
    if s.startswith('/'):
        s = 'https://api.changan-tools-global.com' + s
    print(f"  -> {s}")

# Download and analyze the JavaScript bundles
for s in scripts:
    full_url = s if s.startswith('http') else ('https://api.changan-tools-global.com/' + s.lstrip('/'))
    print(f"\nAnalyzing bundle: {full_url}")
    try:
        req_js = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_js, timeout=10, context=ctx) as r_js:
            js_code = r_js.read().decode('utf-8', errors='replace')
            print(f"  Downloaded {len(js_code)} bytes.")
            
            # Search for technical keywords: X7, overscan, size, density, chinatsp, SystemUI, broadcast, window, fullscreen
            keywords = ["x7", "overscan", "chinatsp", "fullscreen", "1920", "720", "density", "policy_control", "immersive", "adb", "shell", "navigation"]
            found = set()
            for kw in keywords:
                matches = re.findall(r'.{0,60}' + kw + r'.{0,60}', js_code, re.IGNORECASE)
                if matches:
                    print(f"    Matches for '{kw}' ({len(matches)}):")
                    for m in matches[:5]:
                        clean_m = m.replace('\n', ' ').strip()
                        print(f"      {clean_m}")
    except Exception as e:
        print(f"  Error downloading {full_url}: {e}")
