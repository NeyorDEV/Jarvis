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

# 2. Launch with MaDrug (track 1999313427)
print("Launching Deezer with track 1999313427...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/1999313427"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds to load track 1999313427...")
time.sleep(10)

_focus_deezer()
time.sleep(1.0)

# Play it
ctrl = get_deezer_main_control()
btn = find_page_play_button(ctrl, ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"])
if btn:
    print(f"Clicking play on track 1999313427 page...")
    _clic_control(btn)
    time.sleep(5)
    print(f"Playing track: {deezer_obtenir_titre_encours()}")
else:
    print("Play button for 1999313427 not found.")
