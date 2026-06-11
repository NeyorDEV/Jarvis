import sys
import os
import time
import subprocess
import psutil
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, _focus_deezer

# Let's ensure Deezer is running and focused on the album page
deezer_running = False
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        deezer_running = True
        break

if not deezer_running:
    print("Launching Deezer with album...")
    DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
    DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
    subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://album/386771657"], cwd=DEEZER_DIR, shell=False)
    print("Waiting 8 seconds...")
    time.sleep(8)
else:
    # Navigate to album
    print("Deezer already running. Opening album URI...")
    DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
    subprocess.Popen([DEEZER_EXE, "deezer://album/386771657"], shell=False)
    time.sleep(4)

_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if not main_ctrl:
    print("Main control not found.")
    sys.exit(1)

# Find the "1809" track row
found_item = []
def find_track_row(c):
    name = c.Name or ""
    ctype = c.ControlTypeName or ""
    if "1809" in name and ctype in ["CustomControl", "DataItemControl", "GroupControl"]:
        found_item.append(c)
        return True
    for child in c.GetChildren():
        if find_track_row(child):
            return True
    return False

find_track_row(main_ctrl)

if not found_item:
    print("Track row '1809' not found.")
    sys.exit(1)

row = found_item[0]
print(f"Row: Name='{row.Name}', Type={row.ControlTypeName}, Rect={row.BoundingRectangle}")

# Dump row's tree recursively
def dump_tree(c, indent=0):
    name = c.Name or ""
    ctype = c.ControlTypeName or ""
    rect = c.BoundingRectangle
    print("  " * indent + f"- Type: {ctype} | Name: '{name}' | Rect: {rect.left},{rect.top},{rect.right},{rect.bottom}")
    for child in c.GetChildren():
        dump_tree(child, indent + 1)

print("Row Subtree:")
dump_tree(row)
