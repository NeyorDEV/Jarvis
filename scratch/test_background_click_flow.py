import sys
import os
import time
import win32gui
import win32con
import win32api
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

def post_click_background(hwnd, client_x, client_y):
    # Prepare lParam (y is in high word, x is in low word)
    lParam = (client_y << 16) | (client_x & 0xFFFF)
    # Post WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

async def main():
    print("Step 1: Launching Deezer...")
    await deezer_ouvrir()
    print("Waiting 10 seconds for Deezer to load...")
    time.sleep(10)

    # Find the main control
    deezer_ctrl = get_deezer_main_control()
    if not deezer_ctrl:
        print("❌ Deezer main control not found")
        return
        
    r_hwnd = deezer_ctrl.NativeWindowHandle
    if not r_hwnd:
        print("❌ NativeWindowHandle not found")
        return
    print(f"Deezer HWND: {r_hwnd}")

    print("Step 2: Searching for track 'c63 de werenoi' in background...")
    # This will set the search text using ValuePattern (which is focus-safe)
    _uia_taper_dans_recherche("c63 de werenoi")
    time.sleep(3)

    # Let's find the track button
    found_btn = None
    def _find_btn(c):
        nonlocal found_btn
        if c.ControlTypeName == "ButtonControl" and c.Name and "Écouter" in c.Name and "Werenoi" in c.Name:
            try:
                rect = c.BoundingRectangle
                if rect.right - rect.left > 0:
                    found_btn = c
                    return True
            except:
                pass
        for child in c.GetChildren():
            if _find_btn(child):
                return True
        return False
        
    _find_btn(deezer_ctrl)
    if not found_btn:
        print("❌ Track play button not found on screen. Try searching manual.")
        return
    print(f"Found button to click: '{found_btn.Name}'")
    
    # Get coordinates
    rect = found_btn.BoundingRectangle
    screen_x = (rect.left + rect.right) // 2
    screen_y = (rect.top + rect.bottom) // 2
    client_x, client_y = win32gui.ScreenToClient(r_hwnd, (screen_x, screen_y))
    print(f"Screen coordinates: {screen_x}, {screen_y} -> Client: {client_x}, {client_y}")

    # Step 3: Find and focus VS Code (original window) to simulate user playing a game
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
            # Simulation Alt key to bypass SetForegroundWindow restriction
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
            win32gui.ShowWindow(vscode_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(vscode_hwnd)
            time.sleep(2.0)
        except Exception as e:
            print(f"Failed to focus VS Code: {e}")

    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before background click: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")

    # Step 4: Perform background click
    print("Performing background click...")
    post_click_background(r_hwnd, client_x, client_y)
    
    # Wait to see if focus changed
    time.sleep(3.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after background click: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("✅ SUCCESS: Background click worked without stealing focus!")
    else:
        print("❌ FAILURE: Focus was stolen!")
        
    # Let's wait a bit and close Deezer so we clean up
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
