import sys
import os
import time
import subprocess
import psutil
import requests
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, _focus_deezer, deezer_obtenir_titre_encours

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

# 1. Search API for c63 de werenoi
print("Searching API...")
url = "https://api.deezer.com/search?q=c63 de werenoi"
resp = requests.get(url)
tracks = resp.json().get("data", [])
track = tracks[0]
track_id = track.get("id")
track_title = track.get("title")
artist_name = track.get("artist", {}).get("name")
album_id = track.get("album", {}).get("id")
print(f"Track: '{track_title}' | Artist: '{artist_name}' | Album ID: {album_id}")

# 2. Kill Deezer
print("Killing Deezer...")
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try:
            proc.kill()
        except:
            pass
time.sleep(2.5)

# 3. Launch Deezer with album page
print(f"Launching Deezer with album {album_id}...")
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", f"deezer://album/{album_id}"], cwd=DEEZER_DIR, shell=False)

# 4. Wait dynamically for the specific track button to appear (max 20s)
print(f"Waiting for button 'Écouter {track_title} par {artist_name}'...")
t0 = time.time()
found_button = None
timeout = 20

while time.time() - t0 < timeout:
    main_ctrl = get_deezer_main_control()
    if main_ctrl:
        def find_play_button(c, depth=0):
            if depth > 15:
                return None
            ctype = c.ControlTypeName or ""
            name = c.Name or ""
            if ctype == "ButtonControl" and name.startswith("Écouter") and track_title.lower() in name.lower():
                return c
            for child in c.GetChildren():
                res = find_play_button(child, depth + 1)
                if res:
                    return res
            return None
        
        btn = find_play_button(main_ctrl)
        if btn:
            elapsed = time.time() - t0
            print(f"Button found after {elapsed:.2f}s: '{btn.Name}'")
            found_button = btn
            break
    time.sleep(0.4)

if not found_button:
    print(f"Button for '{track_title}' not found within {timeout}s.")
    sys.exit(1)

# 5. Invoke the button
try:
    pattern = found_button.GetInvokePattern()
    if pattern:
        print("Invoking button via InvokePattern...")
        pattern.Invoke()
        print("Invoke success.")
    else:
        print("No InvokePattern, physical click...")
        found_button.Click(simulateMove=False)
except Exception as e:
    print(f"Error: {e}")

# 6. Wait and check
time.sleep(5)
playing = deezer_obtenir_titre_encours()
print(f"Now playing: {playing}")

if playing and playing.get("title", "").lower() == track_title.lower():
    print("✅ SUCCESS: Correct track is playing!")
else:
    print(f"❌ FAIL: Expected '{track_title}', got '{playing}'")
