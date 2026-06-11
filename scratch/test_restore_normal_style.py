import sys
import os
import time
import win32gui
import win32con
import ctypes
import asyncio
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    deezer_ouvrir,
    _uia_taper_dans_recherche
)

async def main():
    print("Step 1: Ensuring Deezer is open...")
    await deezer_ouvrir()
    time.sleep(3)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer not running")
        return
        
    top = ctrl.GetTopLevelControl()
    hwnd = top.NativeWindowHandle
    print(f"Deezer HWND: {hwnd}")
    
    # Hide window (simulating tray)
    print("Hiding Deezer window...")
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    time.sleep(1.5)
    
    # Focus VS Code
    vscode_hwnd = None
    def _cb(h, _):
        nonlocal vscode_hwnd
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if "Visual Studio Code" in t or "Researching Miso" in t or "antigravity" in t:
                vscode_hwnd = h
    win32gui.EnumWindows(_cb, None)
    if vscode_hwnd:
        try:
            print(f"Focusing VS Code (HWND: {vscode_hwnd})")
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
            win32gui.ShowWindow(vscode_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(vscode_hwnd)
            time.sleep(1.5)
        except Exception as e:
            print(f"Focus VS Code failed: {e}")
        
    print("\nRunning asyncio.to_thread requests.get (simulating deezer_rechercher)...")
    url = f"https://api.deezer.com/search?q=c63%20werenoi"
    resp = await asyncio.to_thread(requests.get, url, timeout=5)
    print(f"Web request done, status: {resp.status_code}")
    
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before ShowWindow: {active_before} ({win32gui.GetWindowText(active_before)})")
    
    print("\nCalling ShowWindow(SW_SHOWNOACTIVATE) with NORMAL style...")
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
    time.sleep(2.0)
        
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after ShowWindow: {active_after} ({win32gui.GetWindowText(active_after)})")
    print(f"Is Deezer visible? {win32gui.IsWindowVisible(hwnd)}")
    
    # Let's see if we can search
    print("\nAttempting search...")
    res = _uia_taper_dans_recherche("Billie Jean")
    print(f"Search edit set value result: {res}")

if __name__ == "__main__":
    asyncio.run(main())
