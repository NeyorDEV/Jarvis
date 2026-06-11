import sys
import os
import time
import win32gui
import win32con
import ctypes
import asyncio
import psutil
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    DEEZER_EXE,
    DEEZER_DIR,
    get_deezer_main_control,
    prevent_focus_theft
)

async def main():
    print("Step 1: Closing existing Deezer processes...")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try:
                proc.kill()
            except:
                pass
    time.sleep(2.0)
    
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
    print(f"Active window before launch: {active_before} ({win32gui.GetWindowText(active_before)})")
    
    print("\nLaunching Deezer with SW_SHOWMINNOACTIVE...")
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = win32con.SW_SHOWMINNOACTIVE
    
    subprocess.Popen(
        [DEEZER_EXE, "--force-renderer-accessibility"],
        cwd=DEEZER_DIR,
        shell=False,
        startupinfo=startupinfo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Monitor active window for 10 seconds during launch
    t0 = time.time()
    focus_stolen = False
    while time.time() - t0 < 10.0:
        active = win32gui.GetForegroundWindow()
        if active != active_before and active != 0:
            title = win32gui.GetWindowText(active)
            if "Deezer" in title:
                print(f"FOCUS STOLEN by Deezer: {active} ({title})")
                focus_stolen = True
                break
        time.sleep(0.1)
        
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after launch monitor: {active_after} ({win32gui.GetWindowText(active_after)})")
    
    ctrl = get_deezer_main_control()
    if ctrl:
        top = ctrl.GetTopLevelControl()
        hwnd = top.NativeWindowHandle
        print(f"Deezer running, HWND: {hwnd}, Visible: {win32gui.IsWindowVisible(hwnd)}, Iconic: {win32gui.IsIconic(hwnd)}")
    else:
        print("Deezer control not found after 10s")
        
    if not focus_stolen:
        print("SUCCESS: Cold start in background succeeded without focus theft!")
    else:
        print("FAILURE: Focus was stolen during cold start!")

if __name__ == "__main__":
    asyncio.run(main())
