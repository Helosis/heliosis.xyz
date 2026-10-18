import re
import json

with open(r'scripts\iptvwire.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find every container with headers and links
# In Linktree, sections have <div ...><h3 ...>SECTION_NAME</h3></div>
# and links have <div data-testid="Link">...<a href="..." aria-label="...">...<img src="...">

# Let's write a python regex parser for Link items
blocks = re.split(r'(?=<div id="header-|<div data-testid="Link")', text)
current_section = "General"
data = []

for b in blocks:
    h_m = re.search(r'<h3[^>]*>(.*?)</h3>', b)
    if h_m:
        current_section = re.sub(r'<[^>]+>', '', h_m.group(1)).strip()
        continue
    
    a_m = re.search(r'<a[^>]+href="([^"]+)"[^>]*aria-label="([^"]+)"', b)
    if not a_m:
        a_m = re.search(r'<a[^>]*aria-label="([^"]+)"[^>]+href="([^"]+)"', b)
        if a_m:
            title, url = a_m.group(1), a_m.group(2)
        else:
            continue
    else:
        url, title = a_m.group(1), a_m.group(2)
    
    img_m = re.search(r'<img[^>]+src="([^"]+)"', b)
    img_src = img_m.group(1) if img_m else ""
    
    if "linktr.ee" in url and "iptvwire" not in url:
        continue
    
    data.append({
        "section": current_section,
        "title": title.replace('&#x27;', "'").replace('&amp;', '&'),
        "url": url.replace('&amp;', '&'),
        "icon": img_src
    })

print(f"Total extracted: {len(data)}")
for d in data:
    print(f"[{d['section']}] {d['title']} -> {d['url']}")

import json
with open(r'scripts\iptv_links.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
