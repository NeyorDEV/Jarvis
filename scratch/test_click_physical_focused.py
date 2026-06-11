import sys
import os
import asyncio
import time
import subprocess
import psutil

# Add controller directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    deezer_rechercher,
    deezer_lecture_pause,
    deezer_stop,
    deezer_obtenir_titre_encours,
    get_deezer_main_control,
    find_page_play_button,
    _focus_deezer
)

# 1. Kill Deezer
print("Killing all Deezer processes...")
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try:
            proc.kill()
        except:
            pass
time.sleep(2.0)

# 2. Launch with 1809 track
print("Launching Deezer with track 2070327887...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/2070327887"], cwd=DEEZER_DIR, shell=False)

print("Waiting 8 seconds for Deezer to load...")
time.sleep(8)

# 3. Focus window
print("Focusing Deezer window...")
focused = _focus_deezer()
print(f"Focused: {focused}")
time.sleep(1.0)

# 4. Find main control
main_ctrl = get_deezer_main_control()
if not main_ctrl:
    print("Main control not found.")
    sys.exit(1)

print(f"Main control name: '{main_ctrl.Name}'")

# 5. Find page play button
button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
btn = find_page_play_button(main_ctrl, button_names)
if btn:
    print(f"Page play button found: Name='{btn.Name}'")
    # Click physically
    print("Clicking using physical click Click(simulateMove=False)...")
    btn.Click(simulateMove=False)
    
    print("Waiting 5 seconds for track to play...")
    time.sleep(5)
    
    # 6. Check playing track
    track_info = deezer_obtenir_titre_encours()
    print(f"Current playing track: {track_info}")
else:
    print("Page play button not found.")
