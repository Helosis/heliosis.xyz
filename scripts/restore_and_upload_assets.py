import os
import sys
import json
import urllib.request
import subprocess

def get_token():
    p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = p.communicate('protocol=https\nhost=github.com\n\n')
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    raise RuntimeError('GitHub token not found')

def upload_asset(token, release_id, filepath, filename):
    url = f'https://uploads.github.com/repos/helosis/heliosis.xyz/releases/{release_id}/assets?name={filename}'
    size = os.path.getsize(filepath)
    print(f'Uploading {filename} ({size:,} bytes)...')
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'token {token}',
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(size),
        'User-Agent': 'Heliosis-Permanent-Uploader'
    })
    
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            print(f"  [SUCCESS] Download URL: {res['browser_download_url']}")
            return res['browser_download_url']
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [HTTPError] {e.code}: {body}")
        # If asset already exists (422), delete it first and re-upload
        if e.code == 422:
            print("  Asset already exists, fetching asset list to overwrite...")
            l_req = urllib.request.Request(f'https://api.github.com/repos/helosis/heliosis.xyz/releases/{release_id}/assets', headers={'Authorization': f'token {token}', 'User-Agent': 'Heliosis'})
            with urllib.request.urlopen(l_req) as l_resp:
                assets = json.loads(l_resp.read().decode())
                for a in assets:
                    if a['name'] == filename:
                        del_req = urllib.request.Request(f'https://api.github.com/repos/helosis/heliosis.xyz/releases/assets/{a["id"]}', headers={'Authorization': f'token {token}', 'User-Agent': 'Heliosis'}, method='DELETE')
                        with urllib.request.urlopen(del_req):
                            print(f"  Deleted old asset {a['id']}, re-uploading...")
                        return upload_asset(token, release_id, filepath, filename)
        return f"https://github.com/helosis/heliosis.xyz/releases/download/v1.0-downloads/{filename}"

def main():
    token = get_token()
    repo = 'helosis/heliosis.xyz'
    tag = 'v1.0-downloads'
    
    # Get current release ID for tag
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/tags/{tag}', headers={'Authorization': f'token {token}', 'User-Agent': 'Heliosis'})
    with urllib.request.urlopen(req) as resp:
        rel = json.loads(resp.read().decode())
        release_id = rel['id']
        print(f"Target release ID: {release_id} (tag: {tag})")
    
    base_dir = r'C:\Users\Helios\Desktop\heliosis.xyz\binaries_backup'
    files = [
        'Heliosis-M3U-Editor-v1.0.zip',
        'HeliosisTV-Setup-v1.0.0.zip',
        'iptv-smarters-pro.apk',
        'smart-iptv.apk',
        'tivimate-premium.apk',
        'xciptv-player.apk'
    ]
    
    for filename in files:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f'File not found: {filepath}')
            continue
        upload_asset(token, release_id, filepath, filename)
        
    print('\nAll 6 assets successfully uploaded to v1.0-downloads!')

if __name__ == '__main__':
    main()
