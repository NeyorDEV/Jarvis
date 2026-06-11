import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Search Werenoi artist ID
print("--- Werenoi Top Tracks ---")
url = "https://api.deezer.com/search/artist?q=werenoi"
resp = requests.get(url)
if resp.status_code == 200:
    artists = resp.json().get('data', [])
    if artists:
        artist_id = artists[0].get('id')
        print(f"Artist ID: {artist_id} | Name: '{artists[0].get('name')}'")
        
        # Get top tracks
        top_url = f"https://api.deezer.com/artist/{artist_id}/top"
        resp2 = requests.get(top_url)
        if resp2.status_code == 200:
            for idx, track in enumerate(resp2.json().get('data', [])[:5]):
                print(f"  Track {idx+1}: '{track.get('title')}' (ID: {track.get('id')})")
                
print("\n--- Menace Santana Top Tracks ---")
url = "https://api.deezer.com/search/artist?q=menace Santana"
resp = requests.get(url)
if resp.status_code == 200:
    artists = resp.json().get('data', [])
    if artists:
        artist_id = artists[0].get('id')
        print(f"Artist ID: {artist_id} | Name: '{artists[0].get('name')}'")
        
        # Get top tracks
        top_url = f"https://api.deezer.com/artist/{artist_id}/top"
        resp2 = requests.get(top_url)
        if resp2.status_code == 200:
            for idx, track in enumerate(resp2.json().get('data', [])[:5]):
                print(f"  Track {idx+1}: '{track.get('title')}' (ID: {track.get('id')})")
