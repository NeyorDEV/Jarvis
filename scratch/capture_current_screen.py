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

from controller.deezer_controller import _focus_deezer

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

print("Waiting 12 seconds for Deezer to load and process URI...")
time.sleep(12)

# 3. Focus window
print("Focusing Deezer window...")
focused = _focus_deezer()
print(f"Focused: {focused}")
time.sleep(1.0)

# Take screenshot
dest_dir = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"
os.makedirs(dest_dir, exist_ok=True)
dest_path = os.path.join(dest_dir, "deezer_test_capture.png")

screenshot = pyautogui.screenshot()
screenshot.save(dest_path)
print(f"✔ Screenshot saved to: {dest_path}")
