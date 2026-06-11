import ctypes
import sys
import time
import win32gui
import win32con
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Find window with class Chrome_WidgetWin_1 and title containing 'Deezer'
candidats = []
def foreach_window(hwnd, lParam):
    if win32gui.IsWindowVisible(hwnd) or True: # Check all
        title = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        if classname == "Chrome_WidgetWin_1" and ("deezer" in title.lower() or title == ""):
            # Let's verify process name
            try:
                import win32process
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                import psutil
                proc = psutil.Process(pid)
                if "deezer" in proc.name().lower():
                    candidats.append((hwnd, title, win32gui.IsWindowVisible(hwnd)))
            except Exception as e:
                pass
    return True

win32gui.EnumWindows(foreach_window, 0)
print(f"Found candidats: {candidats}")

if candidats:
    # Try to restore and focus the first one
    hwnd, title, visible = candidats[0]
    print(f"Restoring HWND {hwnd} with title '{title}', visible={visible}...")
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"SetForegroundWindow failed: {e}")
    time.sleep(1.0)
    
    # Try UIA lookup
    deezer_ctrl = auto.WindowControl(searchDepth=1, ClassName="Chrome_WidgetWin_1")
    # Wait, we can find by ClassName, but let's list all Chrome_WidgetWin_1 windows
    for win in auto.GetRootControl().GetChildren():
        if win.ClassName == "Chrome_WidgetWin_1":
            print(f"Root child: Name='{win.Name}', Class='{win.ClassName}'")
            # Let's inspect its children
            children = win.GetChildren()
            print(f"  Number of children: {len(children)}")
            for child in children:
                print(f"    Child: Name='{child.Name}', Type='{child.ControlTypeName}'")
                if child.ControlTypeName in ("DocumentControl", "CustomControl", "PaneControl"):
                    print(f"      This looks like the main window!")
                    
else:
    print("No candidatos found.")
