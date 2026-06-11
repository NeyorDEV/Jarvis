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
    find_page_play_button,
    _focus_deezer
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

# 2. Launch with C63 (track 3045111091)
print("Launching Deezer with C63 track...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/3045111091"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds...")
time.sleep(10)

_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if main_ctrl:
    button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
    btn = find_page_play_button(main_ctrl, button_names)
    if btn:
        print(f"Button found: Name='{btn.Name}'")
        
        # Check patterns
        print("Supported patterns:")
        for pattern_id in [
            auto.PatternId.InvokePattern,
            auto.PatternId.LegacyIAccessiblePattern,
            auto.PatternId.SelectionItemPattern,
            auto.PatternId.TogglePattern,
            auto.PatternId.ValuePattern
        ]:
            try:
                pattern = btn.GetPattern(pattern_id)
                if pattern:
                    print(f"  - {pattern_id}")
            except:
                pass
                
        # Check LegacyIAccessible details
        try:
            legacy = btn.GetLegacyIAccessiblePattern()
            if legacy:
                print(f"LegacyIAccessible details:")
                print(f"  ChildId: {legacy.ChildId}")
                print(f"  DefaultAction: '{legacy.DefaultAction}'")
                print(f"  Description: '{legacy.Description}'")
                print(f"  Help: '{legacy.Help}'")
                print(f"  KeyboardShortcut: '{legacy.KeyboardShortcut}'")
                print(f"  Name: '{legacy.Name}'")
                print(f"  Role: {legacy.Role}")
                print(f"  State: {legacy.State}")
                print(f"  Value: '{legacy.Value}'")
        except Exception as e:
            print(f"Error getting LegacyIAccessible: {e}")
            
    else:
        print("Page play button not found.")
else:
    print("Main control not found.")
