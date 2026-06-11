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
    get_deezer_main_control,
    find_page_play_button,
    _focus_deezer,
    deezer_obtenir_titre_encours,
    _clic_control
)

# 1. Kill Deezer
print("Killing Deezer...")
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try:
            proc.kill()
        except:
            pass
time.sleep(2.0)

# 2. Launch with Quand le soleil se levera à l'ouest ! (track 1560500402)
print("Launching Deezer with track 1560500402...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/1560500402"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds to load track 1560500402...")
time.sleep(10)

_focus_deezer()
time.sleep(1.0)

# Play it
ctrl = get_deezer_main_control()
btn = find_page_play_button(ctrl, ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"])
if btn:
    print(f"Clicking play on track 1560500402 page...")
    _clic_control(btn)
    time.sleep(5)
    print(f"Playing track: {deezer_obtenir_titre_encours()}")
else:
    print("Play button for 1560500402 not found.")
    sys.exit(1)

# 3. Now open C63 (track 3045111091)
print("\nOpening C63 (track 3045111091)...")
subprocess.Popen([DEEZER_EXE, "deezer://track/3045111091"], cwd=DEEZER_DIR, shell=False)
time.sleep(6)

_focus_deezer()
time.sleep(1.0)

# Play C63
ctrl2 = get_deezer_main_control()
btn2 = find_page_play_button(ctrl2, ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"])
if btn2:
    print(f"Clicking play on C63 page (Button Name: '{btn2.Name}')...")
    _clic_control(btn2)
    time.sleep(5)
    print(f"Playing track now: {deezer_obtenir_titre_encours()}")
else:
    print("Play button for C63 not found.")
