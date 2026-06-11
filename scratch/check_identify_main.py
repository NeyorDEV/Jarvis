import uiautomation as auto
import sys
import os
import time
import win32gui
import win32process
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from controller.deezer_controller import deezer_ouvrir, _get_deezer_pids

async def main():
    await deezer_ouvrir()
    time.sleep(2)
    
    deezer_pids = _get_deezer_pids()
    print(f"Deezer PIDs: {deezer_pids}")
    
    render_hwnds = []
    def enum_windows_callback(hwnd, extra):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in deezer_pids:
            def child_callback(child_hwnd, _):
                c_class = win32gui.GetClassName(child_hwnd)
                if c_class == "Chrome_RenderWidgetHostHWND":
                    render_hwnds.append(child_hwnd)
                return True
            try:
                win32gui.EnumChildWindows(hwnd, child_callback, None)
            except:
                pass
        return True

    win32gui.EnumWindows(enum_windows_callback, None)
    print(f"Render HWNDs found: {render_hwnds}")

    for r_hwnd in render_hwnds:
        win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
        time.sleep(0.1)
        ctrl = auto.ControlFromHandle(r_hwnd)
        if ctrl and ctrl.Exists(0.2):
            is_main = ctrl.GroupControl(searchDepth=3, AutomationId='dzr-app').Exists(0.1)
            is_header = ctrl.GroupControl(searchDepth=3, AutomationId='headerbar').Exists(0.1)
            print(f"HWND {r_hwnd}: is_main (dzr-app)={is_main}, is_header (headerbar)={is_header}")

asyncio.run(main())
