import uiautomation as auto
import sys
import os
import win32gui
import win32process
import psutil
import time
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    _focus_deezer
)

# Start Deezer if not running
deezer_running = False
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        deezer_running = True
        break
        
if not deezer_running:
    print("Starting Deezer...")
    DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
    DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
    subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility"], cwd=DEEZER_DIR, shell=False)
    time.sleep(8)

_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if main_ctrl:
    # Find the "open queuelist" button
    queue_btn = main_ctrl.ButtonControl(Name="open queuelist")
    if queue_btn.Exists(1.0):
        print("Clicking 'open queuelist' button...")
        # Try to click it
        queue_btn.Click(simulateMove=False)
        time.sleep(1.5)
        
        # Dump the elements in the window to see the queue list
        print("\nDumping queue list elements:")
        
        # Let's search for list items or elements in the queue panel
        # Typically the queue is a list of CustomControl or GroupControl elements containing track names
        tracks = []
        def find_queue_tracks(c, depth=0):
            # If it's a TextControl or other control in the queue panel
            name = c.Name or ""
            ctype = c.ControlTypeName or ""
            # Let's print anything that looks like a track or artist in the queue
            if name and ctype in ["TextControl", "HyperlinkControl", "CustomControl"]:
                if len(name) > 1 and not any(x in name for x in ["Accueil", "Explorer", "Bibliothèque", "Téléchargements", "Raccourcis", "Playlists"]):
                    print(f"{'  ' * depth}[{ctype}] '{name}'")
            for child in c.GetChildren():
                find_queue_tracks(child, depth + 1)
                
        find_queue_tracks(main_ctrl)
    else:
        print("'open queuelist' button not found.")
else:
    print("Main control not found.")
