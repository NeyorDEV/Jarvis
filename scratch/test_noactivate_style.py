import sys
import os
import time
import win32gui
import win32con
import win32process
import psutil
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

def apply_no_activate_to_deezer():
    # Find all Deezer process PIDs
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                deezer_pids.append(proc.info['pid'])
        except:
            pass

    if not deezer_pids:
        print("No Deezer processes found.")
        return []

    hwnds = []
    def enum_windows_callback(hwnd, extra):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in deezer_pids:
            # Check if it's a top-level visible window (or just any window)
            classname = win32gui.GetClassName(hwnd)
            if "Chrome_WidgetWin" in classname:
                hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(enum_windows_callback, None)
    
    modified_hwnds = []
    for hwnd in hwnds:
        try:
            # Get current ExStyle
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            # Add WS_EX_NOACTIVATE (0x08000000)
            if not (style & 0x08000000):
                new_style = style | 0x08000000
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
                # Apply changes
                win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | 
                                      win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED | 
                                      win32con.SWP_NOACTIVATE)
                print(f"Applied WS_EX_NOACTIVATE to HWND {hwnd} ({win32gui.GetWindowText(hwnd)})")
                modified_hwnds.append((hwnd, style))
            else:
                print(f"HWND {hwnd} already has WS_EX_NOACTIVATE")
        except Exception as e:
            print(f"Failed to apply style to HWND {hwnd}: {e}")
            
    return modified_hwnds

def restore_styles(modified_hwnds):
    for hwnd, old_style in modified_hwnds:
        try:
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, old_style)
            win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | 
                                  win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED | 
                                  win32con.SWP_NOACTIVATE)
            print(f"Restored style for HWND {hwnd}")
        except:
            pass

async def main():
    print("Step 1: Launching Deezer...")
    await deezer_ouvrir()
    print("Waiting 10 seconds for Deezer to load...")
    time.sleep(10)

    print("Step 2: Applying WS_EX_NOACTIVATE style...")
    modified = apply_no_activate_to_deezer()

    # Focus VS Code
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

    # Perform background search and play
    print("Performing background search (typing + click)...")
    
    deezer_ctrl = get_deezer_main_control()
    if not deezer_ctrl:
        print("❌ Deezer main control not found")
        restore_styles(modified)
        return
        
    _uia_taper_dans_recherche("c63 de werenoi")
    time.sleep(2)
    
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
        restore_styles(modified)
        return
        
    print(f"Found button to click: '{found_btn.Name}'")
    
    # Try legacy click
    try:
        pat = found_btn.GetLegacyIAccessiblePattern()
        if pat:
            pat.DoDefaultAction()
            print("Clicked play button.")
        else:
            print("LegacyIAccessible not supported, fallback to Invoke...")
            found_btn.GetInvokePattern().Invoke()
    except Exception as e:
        print(f"Click failed: {e}")

    time.sleep(3.0)
    
    active_after_noactivate = win32gui.GetForegroundWindow()
    print(f"Active window with NOACTIVATE style: {active_after_noactivate} (title: '{win32gui.GetWindowText(active_after_noactivate)}')")
    
    # Restore original styles
    print("Restoring styles...")
    restore_styles(modified)
    
    print("Sleeping 3 seconds to see if focus is stolen after style restoration...")
    time.sleep(3.0)
    
    active_after_restore = win32gui.GetForegroundWindow()
    print(f"Active window after restoring style: {active_after_restore} (title: '{win32gui.GetWindowText(active_after_restore)}')")
    
    if active_after_restore == active_before:
        print("✅ SUCCESS: Search and play worked 100% in the background! Focus was not stolen even after style restoration!")
    else:
        print("❌ FAILURE: Focus was stolen after style restoration!")
    
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
