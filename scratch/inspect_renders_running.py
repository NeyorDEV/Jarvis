import uiautomation as auto
import sys
import os
import win32gui
import win32process
import psutil
import time
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_ouvrir, _get_deezer_pids

async def main():
    print("Opening Deezer...")
    res = await deezer_ouvrir()
    print(f"deezer_ouvrir result: {res}")
    
    # Wait 5 seconds for full loading
    print("Sleeping 5 seconds for full load...")
    time.sleep(5)
    
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
        print(f"\n--- Checking Render HWND {r_hwnd} ---")
        try:
            ctrl = auto.ControlFromHandle(r_hwnd)
            print(f"Control: Name='{ctrl.Name}', Type={ctrl.ControlTypeName}, AutoId='{ctrl.AutomationId}'")
            
            # Print children recursive up to depth 3
            def dump_tree(c, depth=0):
                indent = "  " * depth
                print(f"{indent}- [{c.ControlTypeName}] Name='{c.Name}', AutoId='{c.AutomationId}'")
                if depth < 3:
                    for child in c.GetChildren():
                        dump_tree(child, depth + 1)
            dump_tree(ctrl)
            
        except Exception as e:
            print(f"Error checking render HWND {r_hwnd}: {e}")

asyncio.run(main())
