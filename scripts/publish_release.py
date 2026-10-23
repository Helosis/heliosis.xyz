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

    # 1. Get or create release with tag 'v1.0-downloads'
    get_url = f'https://api.github.com/repos/{repo}/releases/tags/{tag}'
    req = urllib.request.Request(get_url, headers=headers)
    release = None

    try:
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode())
            print('Found existing release ID:', release['id'])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print('Release not found, creating new release v1.0-downloads...')
            create_url = f'https://api.github.com/repos/{repo}/releases'
            payload = json.dumps({
                'tag_name': tag,
                'name': 'HeliosisTV App & Tools Downloads v1.0',
                'body': 'Official downloads for HeliosisTV Android TV APK and Desktop tools.',
                'draft': False,
                'prerelease': False
            }).encode('utf-8')
            creq = urllib.request.Request(create_url, data=payload, headers={**headers, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(creq) as cresp:
                release = json.loads(cresp.read().decode())
                print('Created new release ID:', release['id'])
        else:
            raise

    release_id = release['id']

    def upload_file(filepath, filename):
        print(f'Checking {filename}...')
        # Check if asset already exists in release
        assets = release.get('assets', [])
        for ex in assets:
            if ex['name'] == filename:
                del_url = f'https://api.github.com/repos/{repo}/releases/assets/{ex["id"]}'
                dreq = urllib.request.Request(del_url, headers=headers, method='DELETE')
                try:
                    with urllib.request.urlopen(dreq):
                        print(f'  Deleted old asset {filename} ({ex["id"]})')
                except Exception as err:
                    print('  Delete err:', err)

        upload_url = f'https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={filename}'
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        ureq = urllib.request.Request(upload_url, data=file_data, headers={
            'Authorization': f'token {token}',
            'User-Agent': 'Heliosis-Deployer',
            'Content-Type': 'application/vnd.android.package-archive',
            'Content-Length': str(len(file_data))
        })
        with urllib.request.urlopen(ureq) as uresp:
            ures = json.loads(uresp.read().decode())
            print(f'  [SUCCESS] {filename} -> {ures["browser_download_url"]}')
            return ures['browser_download_url']

    apk_path = r'C:\Users\Helios\Desktop\heliosis.xyz\heliosistv.apk'
    upload_file(apk_path, 'heliosistv.apk')
    upload_file(apk_path, 'heliosis-iptv.apk')

    print('\nAll APK uploads completed successfully!')

if __name__ == '__main__':
    main()
