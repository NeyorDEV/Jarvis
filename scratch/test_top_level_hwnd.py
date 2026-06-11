import sys
import os
import time
import win32gui
import win32con
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, deezer_ouvrir

async def main():
    print("Ensuring Deezer is open...")
    await deezer_ouvrir()
    time.sleep(5)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ main control not found")
        return
        
    print(f"ctrl: Name='{ctrl.Name}', Type={ctrl.ControlTypeName}, HWND={ctrl.NativeWindowHandle}")
    
    # Let's inspect ancestors
    curr = ctrl
    while curr:
        print(f"Ancestor: Name='{curr.Name}', Type={curr.ControlTypeName}, HWND={curr.NativeWindowHandle}")
        curr = curr.GetParentControl()
        
    top = ctrl.GetTopLevelControl()
    if top:
        print(f"GetTopLevelControl(): Name='{top.Name}', Type={top.ControlTypeName}, HWND={top.NativeWindowHandle}")
        hwnd = top.NativeWindowHandle
        if hwnd:
            print(f"IsWindowVisible(hwnd): {win32gui.IsWindowVisible(hwnd)}")
            print("Hiding window...")
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            time.sleep(1)
            print(f"IsWindowVisible(hwnd) after hide: {win32gui.IsWindowVisible(hwnd)}")
            
            print("Restoring...")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
