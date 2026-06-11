import sys
import os
import time
import pyautogui

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import _focus_deezer

print("Focusing Deezer window...")
focused = _focus_deezer()
print(f"Focused: {focused}")
time.sleep(1.0)

dest_dir = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"
os.makedirs(dest_dir, exist_ok=True)
dest_path = os.path.join(dest_dir, "deezer_current_state.png")

screenshot = pyautogui.screenshot()
screenshot.save(dest_path)
print(f"✔ Screenshot saved to: {dest_path}")
