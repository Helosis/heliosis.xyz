import os
import sys
import json
import urllib.request
import urllib.error
import subprocess

def get_token():
    p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = p.communicate('protocol=https\nhost=github.com\n\n')
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    raise RuntimeError('Token not found')

def main():
    token = get_token()
    repo = 'helosis/heliosis.xyz'
    tag = 'v1.0-downloads'
    
    headers = {
        'Authorization': f'token {token}',
        'User-Agent': 'Heliosis-Deployer',
        'Accept': 'application/vnd.github.v3+json'
    }

    # 1. Fetch existing release for v1.0-downloads
    get_url = f'https://api.github.com/repos/{repo}/releases/tags/{tag}'
    req = urllib.request.Request(get_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode())
            print(f"Found release ID: {release['id']} (tag: {tag})")
    except urllib.error.HTTPError as e:
        print(f"Error fetching release: {e}")
        return

    release_id = release['id']

    def upload_file(filepath, filename):
        if not os.path.exists(filepath):
            print(f'Warning: {filepath} not found, skipping.')
            return
        
        size = os.path.getsize(filepath)
        print(f'Syncing {filename} ({size:,} bytes)...')
        
        # Check if asset already exists in release and delete ONLY this specific asset before re-uploading
        assets_req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/{release_id}/assets', headers=headers)
        with urllib.request.urlopen(assets_req) as aresp:
            current_assets = json.loads(aresp.read().decode())

        for ex in current_assets:
            if ex['name'] == filename:
                del_url = f'https://api.github.com/repos/{repo}/releases/assets/{ex["id"]}'
                dreq = urllib.request.Request(del_url, headers=headers, method='DELETE')
                try:
                    with urllib.request.urlopen(dreq):
                        print(f'  Deleted old version of {filename} ({ex["id"]})')
                except Exception as err:
                    print('  Delete err:', err)

        upload_url = f'https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={filename}'
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        ureq = urllib.request.Request(upload_url, data=file_data, headers={
            'Authorization': f'token {token}',
            'User-Agent': 'Heliosis-Deployer',
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(file_data))
        })
        with urllib.request.urlopen(ureq) as uresp:
            ures = json.loads(uresp.read().decode())
            print(f'  [SUCCESS] {filename} -> {ures["browser_download_url"]}')
            return ures['browser_download_url']

    # Update only HeliosisTV APKs
    apk_candidates = [
        r'C:\Users\Helios\Desktop\heliosis.xyz\heliosistv.apk',
        r'D:\heliosiptv\heliosistv.apk',
        r'c:\Users\Helios\Downloads\iptv\heliosistv.apk'
    ]
    apk_path = next((p for p in apk_candidates if os.path.exists(p)), None)
    if apk_path:
        upload_file(apk_path, 'heliosistv.apk')
        upload_file(apk_path, 'heliosis-iptv.apk')

    # Safety Guard: Ensure all 6 core tools are always present in the release
    backup_dir = r'C:\Users\Helios\Desktop\heliosis.xyz\binaries_backup'
    core_tools = [
        'Heliosis-M3U-Editor-v1.0.zip',
        'HeliosisTV-Setup-v1.0.0.zip',
        'iptv-smarters-pro.apk',
        'smart-iptv.apk',
        'tivimate-premium.apk',
        'xciptv-player.apk'
    ]
    
    assets_req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/{release_id}/assets', headers=headers)
    with urllib.request.urlopen(assets_req) as aresp:
        existing_names = {a['name'] for a in json.loads(aresp.read().decode())}

    for tool in core_tools:
        if tool not in existing_names:
            tool_path = os.path.join(backup_dir, tool)
            print(f'Safeguard triggered: Missing {tool}, restoring from backup...')
            upload_file(tool_path, tool)

    print('\nRelease sync completed with all assets intact!')

if __name__ == '__main__':
    main()
