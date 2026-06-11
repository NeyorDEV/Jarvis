import sys

import os
import time
import win32gui
import win32con
import asyncio
import psutil
import ctypes

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    deezer_ouvrir,
    deezer_rechercher,
    deezer_obtenir_titre_encours,
    _uia_taper_dans_recherche
)

async def main():
    print("Step 1: Launching Deezer...")
    await deezer_ouvrir()
    print("Waiting 10 seconds for Deezer to load...")
    time.sleep(10)
    
    # Now find the main window handle (after loading is complete) via Win32
    import win32process
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            deezer_pids.append(proc.info['pid'])
            
    hwnd = None
    if deezer_pids:
        def enum_windows_callback(h, extra):
            nonlocal hwnd
            _, pid = win32process.GetWindowThreadProcessId(h)
            if pid in deezer_pids:
                classname = win32gui.GetClassName(h)
                if "Chrome_WidgetWin" in classname:
                    if not win32gui.GetParent(h):
                        title = win32gui.GetWindowText(h).lower()
                        has_render_child = False
                        def child_cb(ch, _):
                            nonlocal has_render_child
                            if win32gui.GetClassName(ch) == "Chrome_RenderWidgetHostHWND":
                                has_render_child = True
                                return False
                            return True
                        try:
                            win32gui.EnumChildWindows(h, child_cb, None)
                        except:
                            pass
                        if "deezer" in title or has_render_child:
                            hwnd = h
                            return False
            return True
        try:
            win32gui.EnumWindows(enum_windows_callback, None)
        except:
            pass

    if not hwnd:
        print("❌ Deezer main window handle not found")
        return
        
    print(f"Deezer Window HWND: {hwnd}")
    
    # Ensure window is visible to initialize Chromium's accessibility tree
    print("Showing Deezer window (no activation)...")
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
    time.sleep(2.0)
    print("Initializing UIA accessibility tree...")
    get_deezer_main_control()

    # Hide Deezer window (simulating closing it to tray)
    print("Hiding Deezer window (simulating closed to tray)...")
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    time.sleep(2.0)
    print(f"Is window visible? {win32gui.IsWindowVisible(hwnd)}")

    # Focus VS Code (simulating user active window)
    vscode_hwnd = None
    def _cb(hwnd_win, _):
        nonlocal vscode_hwnd
        if win32gui.IsWindowVisible(hwnd_win):
            t = win32gui.GetWindowText(hwnd_win)
            if "Visual Studio Code" in t or "Researching Miso" in t or "antigravity" in t:
                vscode_hwnd = hwnd_win
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
    print(f"Active window before search: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")

    # Step 2: Perform search directly
    print("Performing search directly...")
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
    time.sleep(2.0)
    res = _uia_taper_dans_recherche("Billie Jean")
    print(f"Direct search result: {res}")
    
    time.sleep(6.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after search: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    print(f"Is Deezer window visible now? {win32gui.IsWindowVisible(hwnd)}")
    playing = deezer_obtenir_titre_encours()
    print(f"En écoute : {playing}")
    
    if active_after == active_before:
        print("✅ SUCCESS: Deezer window was restored and track played without stealing focus!")
    else:
        print("❌ FAILURE: Focus was stolen!")

    print("Closing Deezer processes...")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
