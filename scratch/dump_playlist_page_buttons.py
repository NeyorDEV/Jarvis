import uiautomation as auto
import sys
import time
import subprocess
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

print("Launching Deezer with playlist/10487355742...")
subprocess.Popen([DEEZER_EXE, "deezer://playlist/10487355742"], cwd=DEEZER_DIR, shell=False)

print("Waiting 6 seconds for page to load...")
time.sleep(6)

deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

buttons = []
def scan_buttons(control):
    if control.ControlTypeName == "ButtonControl":
        buttons.append(control)
    for child in control.GetChildren():
        scan_buttons(child)

scan_buttons(deezer_ctrl)
print(f"Found {len(buttons)} buttons on playlist page:")
for idx, btn in enumerate(buttons):
    name = btn.Name or ""
    if "écoute" in name.lower() or "pause" in name.lower() or "play" in name.lower():
        print(f"Button {idx}: Name='{name}', Rect={btn.BoundingRectangle}")
