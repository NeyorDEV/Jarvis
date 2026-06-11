import sys
import os
import win32gui
import win32process
import psutil
import time
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
    
    for r_hwnd in render_hwnds:
        rect = win32gui.GetWindowRect(r_hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        print(f"HWND {r_hwnd}: dimensions={width}x{height}, rect={rect}")

asyncio.run(main())
