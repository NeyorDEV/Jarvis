import sys
import os
import time
import win32gui
import win32con
import win32process
import psutil
import pyautogui

sys.stdout.reconfigure(encoding='utf-8')

# 1. Find Deezer PIDs
deezer_pids = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            deezer_pids.append(proc.info['pid'])
    except:
        pass

print(f"Deezer PIDs: {deezer_pids}")

# 2. Find HWNDs for these PIDs
deezer_hwnds = []
def enum_cb(hwnd, extra):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    if pid in deezer_pids:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        is_visible = win32gui.IsWindowVisible(hwnd)
        print(f"Found window HWND: {hwnd}, Title: '{title}', Class: '{class_name}', Visible: {is_visible}")
        if is_visible:
            deezer_hwnds.append(hwnd)
    return True

win32gui.EnumWindows(enum_cb, None)

if deezer_hwnds:
    hwnd = deezer_hwnds[0]
    print(f"Focusing HWND: {hwnd}")
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        print("SetForegroundWindow succeeded")
    except Exception as e:
        print(f"Failed to focus: {e}")
    time.sleep(1.0)
else:
    print("No visible Deezer HWNDs found")

# Take screenshot of the screen anyway
dest_dir = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"
os.makedirs(dest_dir, exist_ok=True)
dest_path = os.path.join(dest_dir, "deezer_focus_capture.png")

screenshot = pyautogui.screenshot()
screenshot.save(dest_path)
print(f"✔ Screenshot saved to: {dest_path}")
