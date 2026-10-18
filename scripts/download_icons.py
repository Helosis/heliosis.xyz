import os
import json
import urllib.request

ICONS_DIR = r"C:\Users\Helios\Desktop\heliosis.xyz\assets\icons"
os.makedirs(ICONS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

with open(r"C:\Users\Helios\Desktop\heliosis.xyz\scripts\iptv_links.json", "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    url = item.get("icon")
    title = item.get("title", "").strip().lower()
    # clean name
    safe_name = "".join(c if c.isalnum() else "_" for c in title).strip("_")
    filename = f"{safe_name}.png"
    filepath = os.path.join(ICONS_DIR, filename)
    
    if url and not os.path.exists(filepath):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(filepath, "wb") as out:
                    out.write(resp.read())
            print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed {filename}: {e}")

print("All icons processed.")
