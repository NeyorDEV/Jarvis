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
    deezer_ouvrir,
    prevent_focus_theft,
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
            time.sleep(2.0)
        except Exception as e:
            print(f"Failed to focus other window: {e}")
            
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before ShowWindow: {active_before} ({win32gui.GetWindowText(active_before)})")
    
    print("\nCalling ShowWindow(SW_SHOWNOACTIVATE) inside prevent_focus_theft...")
    with prevent_focus_theft():
        # Restore window shownoactivate
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        time.sleep(1.5)
        
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after: {active_after} ({win32gui.GetWindowText(active_after)})")
    print(f"Is Deezer visible? {win32gui.IsWindowVisible(hwnd)}")
    
    if active_after == active_before:
        print("SUCCESS: No focus theft occurred on ShowWindow(SW_SHOWNOACTIVATE)!")
    else:
        print("FAILURE: Focus was stolen on ShowWindow(SW_SHOWNOACTIVATE)!")
        
    # Let's see if we can search
    print("\nAttempting search...")
    res = _uia_taper_dans_recherche("Billie Jean")
    print(f"Search edit set value result: {res}")
    
    # Hide again to test SW_RESTORE under prevent_focus_theft
    print("\nHiding window again...")
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    time.sleep(1.5)
    
    if vscode_hwnd:
        win32gui.SetForegroundWindow(vscode_hwnd)
        time.sleep(1.0)
        
    active_before2 = win32gui.GetForegroundWindow()
    print(f"Active window before SW_RESTORE: {active_before2} ({win32gui.GetWindowText(active_before2)})")
    
    print("\nCalling ShowWindow(SW_RESTORE) inside prevent_focus_theft...")
    with prevent_focus_theft():
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(1.5)
        
    active_after2 = win32gui.GetForegroundWindow()
    print(f"Active window after SW_RESTORE: {active_after2} ({win32gui.GetWindowText(active_after2)})")
    print(f"Is Deezer visible? {win32gui.IsWindowVisible(hwnd)}")
    
    if active_after2 == active_before2:
        print("SUCCESS: No focus theft occurred on ShowWindow(SW_RESTORE)!")
    else:
        print("FAILURE: Focus was stolen on ShowWindow(SW_RESTORE)!")

if __name__ == "__main__":
    asyncio.run(main())
