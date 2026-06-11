import sys
import os
import time
import subprocess
import psutil
import pyautogui

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    find_page_play_button,
    _focus_deezer,
    deezer_obtenir_titre_encours
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

print("Waiting 12 seconds for Deezer to load...")
time.sleep(12)

# 3. Focus window
print("Focusing Deezer window...")
_focus_deezer()
time.sleep(1.0)

# 4. Find button coordinates using UIA
main_ctrl = get_deezer_main_control()
if main_ctrl:
    button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
    btn = find_page_play_button(main_ctrl, button_names)
    if btn:
        rect = btn.BoundingRectangle
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        print(f"Page play button found: Rect={rect}, Center=({cx}, {cy})")
        
        # Click using pyautogui
        print(f"Clicking at ({cx}, {cy}) using pyautogui...")
        pyautogui.click(cx, cy)
        
        print("Waiting 6 seconds...")
        time.sleep(6)
        
        track_info = deezer_obtenir_titre_encours()
        print(f"Current playing track: {track_info}")
    else:
        print("Page play button not found.")
else:
    print("Main control not found.")
