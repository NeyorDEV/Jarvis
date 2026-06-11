import sys
import os
import asyncio
import time
import win32gui
import win32con
import ctypes

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_rechercher, deezer_ouvrir

def force_foreground(hwnd):
    try:
        # Trick 1: Simulate Alt key press to unlock SetForegroundWindow
        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0) # Alt Down
        time.sleep(0.01)
        ctypes.windll.user32.keybd_event(0x12, 0, 2, 0) # Alt Up
        
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print(f"Force foreground via Alt failed: {e}")
        
    try:
        # Trick 2: AttachThreadInput
        fore_hwnd = win32gui.GetForegroundWindow()
        import win32process
        _, fore_tid = win32process.GetWindowThreadProcessId(fore_hwnd)
        curr_tid = ctypes.windll.kernel32.GetCurrentThreadId()
        
        if fore_tid != curr_tid:
            ctypes.windll.user32.AttachThreadInput(curr_tid, fore_tid, True)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.SetActiveWindow(hwnd)
            ctypes.windll.user32.AttachThreadInput(curr_tid, fore_tid, False)
            return True
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
    except Exception as e:
        print(f"Force foreground via AttachThreadInput failed: {e}")
        
    return False

async def main():
    print("Ensuring Deezer is open...")
    await deezer_ouvrir()
    time.sleep(3)
    
    # Programmatically focus VS Code / Antigravity
    print("Finding and focusing VS Code...")
    vscode_hwnd = None
    def _cb(hwnd, _):
        nonlocal vscode_hwnd
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if "Visual Studio Code" in t or "Researching Miso" in t:
                vscode_hwnd = hwnd
    win32gui.EnumWindows(_cb, None)
    
    if vscode_hwnd:
        print(f"VS Code window found: {vscode_hwnd} (title: '{win32gui.GetWindowText(vscode_hwnd)}')")
        force_foreground(vscode_hwnd)
        time.sleep(2.0)
    else:
        print("❌ VS Code window not found!")
        
    hwnd_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {hwnd_before} (title: '{win32gui.GetWindowText(hwnd_before)}')")
    
    # Run search (C63)
    res = await deezer_rechercher("c63 de werenoi")
    print(f"Result: {res}")
    
    active_now = win32gui.GetForegroundWindow()
    if active_now != hwnd_before and hwnd_before != 0:
        print(f"Focus was stolen by: {active_now} (title: '{win32gui.GetWindowText(active_now)}')")
        print(f"Restoring focus to: {hwnd_before}...")
        ok = force_foreground(hwnd_before)
        print(f"Restore result: {ok}")
            
    time.sleep(1.0)
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after restoration: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == hwnd_before:
        print("\n✅ SUCCESS: Focus restored successfully!")
    else:
        print("\n❌ FAILURE: Could not restore focus!")

asyncio.run(main())
