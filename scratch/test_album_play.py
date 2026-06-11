import sys
import os
import asyncio
import time
import subprocess
import psutil
import uiautomation as auto

# Add controller directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    _focus_deezer,
    deezer_obtenir_titre_encours
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

# 2. Launch with album Into The Dark (album 386771657)
print("Launching Deezer with album 386771657...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://album/386771657"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds to load album page...")
time.sleep(10)

_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if main_ctrl:
    found_item = []
    
    # Let's list all elements containing "1809" in their name to find the track row
    def find_track_row(c):
        name = c.Name or ""
        ctype = c.ControlTypeName or ""
        if "1809" in name and ctype in ["CustomControl", "DataItemControl", "TextControl", "GroupControl"]:
            # Check if this element is in a list or has parents in list
            print(f"Found candidate: Name='{name}', Type={ctype}")
            # If it's a TextControl, let's look at its parent to find the row
            if ctype == "TextControl":
                found_item.append(c.GetParentControl())
            else:
                found_item.append(c)
            return True
        for child in c.GetChildren():
            if find_track_row(child):
                return True
        return False
        
    find_track_row(main_ctrl)
    
    if found_item:
        track_item = found_item[0]
        print(f"Target track row found: Name='{track_item.Name}', Type={track_item.ControlTypeName}")
        # Let's double click the track row
        print("Double clicking the track row...")
        track_item.DoubleClick()
        
        print("Waiting 5 seconds...")
        time.sleep(5)
        print(f"Playing track: {deezer_obtenir_titre_encours()}")
    else:
        print("Track '1809' not found in album page.")
else:
    print("Main control not found.")
