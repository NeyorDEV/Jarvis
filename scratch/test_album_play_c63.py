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

# 1. Search API for c63 de werenoi
print("Searching API...")
url = "https://api.deezer.com/search?q=c63 de werenoi"
resp = requests.get(url)
if resp.status_code != 200:
    print("API error")
    sys.exit(1)

tracks = resp.json().get("data", [])
if not tracks:
    print("No tracks found")
    sys.exit(1)

track = tracks[0]
track_id = track.get("id")
track_title = track.get("title")
artist_name = track.get("artist", {}).get("name")
album_id = track.get("album", {}).get("id")

print(f"Track: '{track_title}' | Artist: '{artist_name}' | Album ID: {album_id}")

# 2. Launch Deezer with album
print("Launching Deezer with album...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

# Close Deezer first to ensure clean state
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try:
            proc.kill()
        except:
            pass
time.sleep(2.0)

subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", f"deezer://album/{album_id}"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds for album page to load...")
time.sleep(10)

_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if not main_ctrl:
    print("Main control not found")
    sys.exit(1)

# Find play button
found_button = None
def find_play_button(c):
    global found_button
    ctype = c.ControlTypeName or ""
    name = c.Name or ""
    # We want a button starting with "Écouter " and containing the track title
    if ctype == "ButtonControl" and name.startswith("Écouter") and track_title.lower() in name.lower():
        # Let's make sure it's not the main page "Écouter" button (which has a larger width/height ratio and contains no artist/track title)
        # The track row buttons are typically square (32x32) and contain the track name in the button name.
        found_button = c
        return True
    for child in c.GetChildren():
        if find_play_button(child):
            return True
    return False

find_play_button(main_ctrl)

if found_button:
    print(f"Found button: '{found_button.Name}' | Rect: {found_button.BoundingRectangle}")
    try:
        pattern = found_button.GetInvokePattern()
        if pattern:
            print("Invoking button via InvokePattern...")
            pattern.Invoke()
            print("Invoke success.")
        else:
            print("InvokePattern not supported, clicking physically...")
            found_button.Click(simulateMove=False)
    except Exception as e:
        print(f"Click failed: {e}")
        
    print("Waiting 5 seconds...")
    time.sleep(5)
    print(f"Now playing: {deezer_obtenir_titre_encours()}")
else:
    print(f"Play button for '{track_title}' not found on album page.")
