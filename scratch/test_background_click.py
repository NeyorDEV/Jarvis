import sys
import os
import time
import win32gui
import win32con
import win32api
import ctypes
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, deezer_ouvrir

def post_click_background(hwnd, client_x, client_y):
    # Prepare lParam (y is in high word, x is in low word)
    lParam = (client_y << 16) | (client_x & 0xFFFF)
    # Post WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

def main():
    # Ensure Deezer is open and search for a track first
    print("Finding Deezer control...")
    deezer_ctrl = get_deezer_main_control()
    if not deezer_ctrl:
        print("❌ Deezer not running")
        return
        
    # We find the child window HWND of the control
    r_hwnd = None
    # Let's find r_hwnd from get_deezer_main_control
    # In get_deezer_main_control, it uses auto.ControlFromHandle(r_hwnd), so we can get it via NativeWindowHandle
    r_hwnd = deezer_ctrl.NativeWindowHandle
    if not r_hwnd:
        print("❌ NativeWindowHandle not found")
        return
        
    print(f"Child HWND: {r_hwnd}")
    
    # Let's search for a track button to click (must be visible on screen)
    found_btn = None
    def _find_btn(c):
        nonlocal found_btn
        if c.ControlTypeName == "ButtonControl" and c.Name and "Écouter" in c.Name and "par" in c.Name:
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
        print("❌ Visible track play button not found on screen. Please search for a track first.")
        return
        
    print(f"Found button to click: '{found_btn.Name}'")
    
    # Get screen coordinates
    rect = found_btn.BoundingRectangle
    screen_x = (rect.left + rect.right) // 2
    screen_y = (rect.top + rect.bottom) // 2
    print(f"Screen coordinates: {screen_x}, {screen_y}")
    
    # Map to client coordinates
    client_x, client_y = win32gui.ScreenToClient(r_hwnd, (screen_x, screen_y))
    print(f"Client coordinates for HWND {r_hwnd}: {client_x}, {client_y}")
    
    # Focus VS Code first
    vscode_hwnd = None
    def _cb(hwnd, _):
        nonlocal vscode_hwnd
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if "Visual Studio Code" in t or "Researching Miso" in t:
                vscode_hwnd = hwnd
    win32gui.EnumWindows(_cb, None)
    if vscode_hwnd:
        try:
            win32gui.ShowWindow(vscode_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(vscode_hwnd)
            time.sleep(2.0)
        except Exception as e:
            print(f"Failed to focus VS Code: {e}")
            
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before background click: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")
    
    # Perform background click
    print("Performing background click...")
    post_click_background(r_hwnd, client_x, client_y)
    
    time.sleep(3.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after background click: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("✅ SUCCESS: Background click worked without stealing focus!")
    else:
        print("❌ FAILURE: Focus was stolen!")

if __name__ == "__main__":
    main()
