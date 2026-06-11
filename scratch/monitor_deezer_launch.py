import subprocess
import time
import psutil
import win32gui
import win32process
import pyautogui
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

print("Launching Deezer...")
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility"], cwd=DEEZER_DIR, shell=False)

dest_dir = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"
os.makedirs(dest_dir, exist_ok=True)

for i in range(1, 16):
    time.sleep(1)
    # Check processes
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                pids.append(proc.info['pid'])
        except:
            pass
            
    # Check windows
    windows = []
    def enum_cb(hwnd, extra):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in pids:
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            windows.append((hwnd, title, class_name, is_visible))
        return True
    win32gui.EnumWindows(enum_cb, None)
    
    print(f"Second {i}: PIDs={pids}, Windows={windows}")
    
    # Save a screenshot at second 5 and 10
    if i in (5, 10, 15):
        screenshot = pyautogui.screenshot()
        screenshot.save(os.path.join(dest_dir, f"deezer_launch_sec_{i}.png"))
        print(f"Saved screenshot for second {i}")
