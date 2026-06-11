import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

for track_id in [2070327887, 1560500402]:
    url = f"https://api.deezer.com/track/{track_id}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Track ID: {track_id} | Title: '{data.get('title')}' | Readable: {data.get('readable')}")
    else:
        print(f"Error {track_id}: {resp.status_code}")
