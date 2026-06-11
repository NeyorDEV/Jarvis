import sys
import os
import win32gui
import win32process
import psutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from controller.deezer_controller import _get_deezer_pids

def main():
    pids = _get_deezer_pids()
    print(f"Deezer PIDs: {pids}")
    
    hwnd = None
    if pids:
        def enum_windows_callback(h, extra):
            nonlocal hwnd
            _, pid = win32process.GetWindowThreadProcessId(h)
            classname = win32gui.GetClassName(h)
            title = win32gui.GetWindowText(h)
            parent = win32gui.GetParent(h)
            is_visible = win32gui.IsWindowVisible(h)
            
            if pid in pids:
                print(f"HWND {h} | Class: {classname} | Title: '{title}' | Parent: {parent} | Visible: {is_visible}")
                if "Chrome_WidgetWin" in classname:
                    if not parent:
                        print(f"  --> MATCHED as top-level: {h}")
                        hwnd = h
                        # Let's not return False immediately so we see all windows
            return True
            
        win32gui.EnumWindows(enum_windows_callback, None)
        
    print(f"\nFinal detected HWND: {hwnd}")

if __name__ == "__main__":
    main()
