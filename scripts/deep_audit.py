import urllib.request
import re
import ssl
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://heliosis.xyz/?t=check'
print(f"Fetching {url}...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        html = r.read().decode('utf-8')
except Exception as e:
    print(f"Failed to fetch heliosis.xyz: {e}")
    sys.exit(1)

print(f"Fetched HTML, length: {len(html)}")

matches = re.findall(r'id:\s*["\']([^"\']+)["\'],\s*title:\s*["\']([^"\']+)["\'],[\s\S]*?url:\s*["\']([^"\']+)["\']', html)
print(f"Total app items found in JS: {len(matches)}")

dead = []
ok = []

for app_id, title, target_url in matches:
    print(f"\n[{app_id}] {title}")
    print(f" Target: {target_url}")
    try:
        # Standard browser GET request without range first, or with small range
        req_item = urllib.request.Request(
            target_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        # Open and read up to 1024 bytes
        with urllib.request.urlopen(req_item, timeout=15, context=ctx) as resp:
            data = resp.read(1024)
            final_url = resp.geturl()
            ctype = resp.headers.get('Content-Type', '')
            status = resp.status
            
            is_html = b'<!DOCTYPE html>' in data or b'<html' in data or b'404 Not Found' in data or 'text/html' in ctype.lower()
            is_zip = data.startswith(b'PK')
            
            print(f" Status: {status}, Content-Type: {ctype}, Bytes read: {len(data)}")
            print(f" Final URL: {final_url}")
            print(f" Header: {data[:8]}")
            
            if is_html:
                print(f" !!! DEAD (Received HTML landing/error page)")
                dead.append((title, target_url, "HTML/Error page returned", final_url))
            elif is_zip or 'application' in ctype.lower():
                print(f" >>> OK (Valid binary file)")
                ok.append((title, target_url))
            else:
                print(f" ??? UNCERTAIN (Non-ZIP binary or unknown format)")
                ok.append((title, target_url))
    except Exception as e:
        print(f" !!! FAILED: {e}")
        dead.append((title, target_url, str(e), ""))

print("\n" + "="*60)
print(f"AUDIT SUMMARY: {len(ok)} OK, {len(dead)} DEAD")
print("="*60)
for title, url, reason, fin in dead:
    print(f"DEAD: {title}\n  URL: {url}\n  Reason: {reason}\n  Final: {fin}\n")
