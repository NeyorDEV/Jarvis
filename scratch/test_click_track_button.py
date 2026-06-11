import sys
import os
import time
import psutil
import subprocess
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, _focus_deezer, deezer_obtenir_titre_encours

# Launch Deezer with album 386771657
print("Launching Deezer...")
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://album/386771657"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds for Deezer to load...")
time.sleep(10)

# Ensure Deezer is focused
_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if not main_ctrl:
    print("Main control not found.")
    sys.exit(1)

# Search for the button with Name starting with 'Écouter 1809 par'
found_button = None
def find_button(c):
    global found_button
    ctype = c.ControlTypeName or ""
    name = c.Name or ""
    if ctype == "ButtonControl" and name.startswith("Écouter 1809 par"):
        found_button = c
        return True
    for child in c.GetChildren():
        if find_button(child):
            return True
    return False

find_button(main_ctrl)

if found_button:
    print(f"Found button: '{found_button.Name}' | Rect: {found_button.BoundingRectangle}")
    
    # Try Invoke pattern
    try:
        pattern = found_button.GetInvokePattern()
        if pattern:
            print("Invoking button via InvokePattern...")
            pattern.Invoke()
            print("Invoke successful.")
        else:
            print("InvokePattern not supported, clicking physically...")
            found_button.Click(simulateMove=False)
            print("Click successful.")
    except Exception as e:
        print(f"Error clicking button: {e}")
        print("Attempting physical Click fallback...")
        try:
            found_button.Click(simulateMove=False)
            print("Physical Click successful.")
        except Exception as ex:
            print(f"Physical Click failed: {ex}")
            
    print("Waiting 5 seconds...")
    time.sleep(5)
    print(f"Now playing: {deezer_obtenir_titre_encours()}")
else:
    print("Play button for 1809 not found.")
