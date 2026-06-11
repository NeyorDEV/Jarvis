import requests
import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

url = "https://api.deezer.com/search?q=1809 menace santana"
resp = requests.get(url)
if resp.status_code == 200:
    data = resp.json()
    tracks = data.get("data", [])
    if tracks:
        track = tracks[0]
        print(json.dumps(track, indent=2))
    else:
        print("No tracks found")
else:
    print(f"Error: {resp.status_code}")
