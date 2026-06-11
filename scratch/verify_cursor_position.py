import uiautomation as auto
import sys
import os
import win32gui
import win32process
import psutil
import time
import subprocess
import pyautogui
from PIL import ImageDraw

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
    subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/2070327887"], cwd=DEEZER_DIR, shell=False)
    time.sleep(10)
else:
    # Navigate to 1809 track
    subprocess.Popen([r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe", "deezer://track/2070327887"], shell=False)
    time.sleep(4)

_focus_deezer()
time.sleep(1.0)

main_ctrl = get_deezer_main_control()
if main_ctrl:
    button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
    btn = find_page_play_button(main_ctrl, button_names)
    if btn:
        rect = btn.BoundingRectangle
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        print(f"Page play button: Rect={rect}, Center=({cx}, {cy})")
        
        # Move mouse there
        pyautogui.moveTo(cx, cy)
        time.sleep(1.0)
        
        # Capture screenshot
        dest_dir = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, "cursor_position.png")
        
        screenshot = pyautogui.screenshot()
        
        # Draw a red cross at the mouse position on the screenshot
        # Since pyautogui coordinates are logical, let's convert cx, cy if screen is scaled.
        # But let's first get the screen size to see if there's scaling.
        screen_w, screen_h = screenshot.size
        print(f"Screenshot size: {screen_w}x{screen_h}")
        
        # We can draw the cross at (cx, cy) but wait! If the screen has scaling, cx and cy are in logical pixels.
        # Let's get the logical screen size
        logical_w, logical_h = pyautogui.size()
        print(f"Logical screen size: {logical_w}x{logical_h}")
        
        scale_x = screen_w / logical_w
        scale_y = screen_h / logical_h
        
        px = int(cx * scale_x)
        py = int(cy * scale_y)
        print(f"Drawing cross at physical coordinates: ({px}, {py})")
        
        draw = ImageDraw.Draw(screenshot)
        draw.line((px - 20, py, px + 20, py), fill="red", width=3)
        draw.line((px, py - 20, px, py + 20), fill="red", width=3)
        
        screenshot.save(dest_path)
        print(f"✔ Screenshot saved to: {dest_path}")
    else:
        print("Page play button not found.")
else:
    print("Main control not found.")
