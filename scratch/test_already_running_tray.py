import sys
import os
import time
import win32gui
import win32con
import ctypes
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    deezer_rechercher,
    deezer_obtenir_titre_encours
)

async def main():
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Deezer is not running! Please run Deezer, interact with it, and minimize/close it to tray first.")
        return
        
    top = ctrl.GetTopLevelControl()
    hwnd = top.NativeWindowHandle
    print(f"Deezer Window HWND: {hwnd}")
    print(f"Is visible? {win32gui.IsWindowVisible(hwnd)}, Is iconic? {win32gui.IsIconic(hwnd)}")

    # Find active window (VS Code or CMD)
    vscode_hwnd = None
    def _cb(h, _):
        nonlocal vscode_hwnd
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if "Visual Studio Code" in t or "Researching Miso" in t or "antigravity" in t:
                vscode_hwnd = h
    win32gui.EnumWindows(_cb, None)
    if vscode_hwnd:
        print(f"Focusing other window: {vscode_hwnd} ({win32gui.GetWindowText(vscode_hwnd)})")
        try:
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
            win32gui.ShowWindow(vscode_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(vscode_hwnd)
            time.sleep(1.0)
        except Exception as e:
            print(f"Failed to focus: {e}")

    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before search: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")

    # Perform search
    print("Performing search...")
    res = await deezer_rechercher("joue c63 de werenoi")
    print(f"Result: {res}")
    
    time.sleep(6.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after search: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    playing = deezer_obtenir_titre_encours()
    print(f"En écoute : {playing}")
    
    if active_after == active_before:
        print("✅ SUCCESS: Deezer window was restored and track played without stealing focus!")
    else:
        print("❌ FAILURE: Focus was stolen!")

if __name__ == "__main__":
    asyncio.run(main())
