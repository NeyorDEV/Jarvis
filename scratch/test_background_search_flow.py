import sys
import os
import time
import win32gui
import win32con
import ctypes
import asyncio
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    deezer_ouvrir,
    deezer_rechercher
)

async def main():
    print("Step 1: Launching Deezer...")
    await deezer_ouvrir()
    print("Waiting 10 seconds for Deezer to load...")
    time.sleep(10)

    # Focus VS Code (simulating user active window like a game)
    vscode_hwnd = None
    def _cb(hwnd, _):
        nonlocal vscode_hwnd
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if "Visual Studio Code" in t or "Researching Miso" in t:
                vscode_hwnd = hwnd
    win32gui.EnumWindows(_cb, None)
    if vscode_hwnd:
        print(f"Focusing VS Code window (HWND: {vscode_hwnd})")
        try:
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
            win32gui.ShowWindow(vscode_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(vscode_hwnd)
            time.sleep(2.0)
        except Exception as e:
            print(f"Failed to focus VS Code: {e}")

    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before background search: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")

    # Step 2: Perform background search and play
    print("Performing background search...")
    res = await deezer_rechercher("c63 de werenoi")
    print(f"Result: {res}")
    
    time.sleep(3.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after background search: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("✅ SUCCESS: Search and play worked entirely in the background without stealing focus!")
    else:
        print("❌ FAILURE: Focus was stolen!")
        
    print("Closing Deezer processes...")
    import psutil
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
