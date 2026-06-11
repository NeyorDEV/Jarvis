import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

search_url = "https://api.deezer.com/search/album?q=Pyramide 2 Werenoi"
resp = requests.get(search_url)
if resp.status_code == 200:
    albums = resp.json().get('data', [])
    if albums:
        album_id = albums[0].get('id')
        print(f"Album ID: {album_id} | Title: '{albums[0].get('title')}'")
        
        tracks_url = f"https://api.deezer.com/album/{album_id}/tracks"
        resp2 = requests.get(tracks_url)
        if resp2.status_code == 200:
            tracks = resp2.json().get('data', [])
            for idx, track in enumerate(tracks):
                print(f"  Track {idx+1}: ID: {track.get('id')} | Title: '{track.get('title')}'")
        else:
            print(f"Error getting tracks: {resp2.status_code}")
else:
    print(f"Error searching album: {resp.status_code}")
