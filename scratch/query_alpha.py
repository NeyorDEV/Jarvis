import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

url = "https://api.deezer.com/search?q=Alpha Werenoi"
resp = requests.get(url)
if resp.status_code == 200:
    data = resp.json()
    for track in data.get('data', [])[:5]:
        print(f"Track: '{track.get('title')}' | Album: '{track.get('album', {}).get('title')}'")
else:
    print(f"Error: {resp.status_code}")
