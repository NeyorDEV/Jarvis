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
    get_deezer_main_control,
    deezer_ouvrir,
    _uia_taper_dans_recherche
)

async def main():
    print("Step 1: Launching Deezer...")
    await deezer_ouvrir()
    print("Waiting 10 seconds for Deezer to load...")
    time.sleep(10)

    deezer_ctrl = get_deezer_main_control()
    if not deezer_ctrl:
        print("❌ Deezer main control not found")
        return
        
    print("Step 2: Searching for track 'c63 de werenoi'...")
    _uia_taper_dans_recherche("c63 de werenoi")
    time.sleep(3)

    found_btn = None
    def _find_btn(c):
        nonlocal found_btn
        if c.ControlTypeName == "ButtonControl" and c.Name and "Écouter" in c.Name and "Werenoi" in c.Name:
            found_btn = c
            return True
        for child in c.GetChildren():
            if _find_btn(child):
                return True
        return False
        
    _find_btn(deezer_ctrl)
    if not found_btn:
        print("❌ Track play button not found on screen.")
        return
    print(f"Found button: '{found_btn.Name}'")

    # Step 3: Focus VS Code
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
    print(f"Active window before UIA Invoke: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")

    # Step 4: Perform UIA Invoke
    print("Performing UIA Invoke...")
    try:
        pattern = found_btn.GetInvokePattern()
        if pattern:
            pattern.Invoke()
            print("Invoke called successfully.")
        else:
            print("❌ InvokePattern not supported on this button.")
    except Exception as e:
        print(f"❌ InvokePattern failed: {e}")
    
    time.sleep(3.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after UIA Invoke: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("✅ SUCCESS: UIA Invoke worked without stealing focus!")
    else:
        print("❌ FAILURE: Focus was stolen by UIA Invoke!")
        
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
