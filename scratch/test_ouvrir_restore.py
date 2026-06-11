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

from controller.deezer_controller import get_deezer_main_control, deezer_ouvrir

async def main():
    print("Launching Deezer...")
    await deezer_ouvrir()
    time.sleep(5)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Deezer main control not found")
        return
        
    top = ctrl.GetTopLevelControl()
    hwnd = top.NativeWindowHandle
    print(f"HWND: {hwnd}")
    
    # Hide window
    print("Hiding window...")
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    time.sleep(2)
    print(f"Is visible? {win32gui.IsWindowVisible(hwnd)}")
    
    # Call deezer_ouvrir() and see what it does
    print("\nCalling deezer_ouvrir()...")
    res = await deezer_ouvrir()
    print(f"Result of deezer_ouvrir: {res}")
    
    # Check if visible now
    print(f"Is visible now? {win32gui.IsWindowVisible(hwnd)}")
    
    # Restore window
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

if __name__ == "__main__":
    asyncio.run(main())
