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

candidats = []
def foreach_window(hwnd, lParam):
    title = win32gui.GetWindowText(hwnd)
    classname = win32gui.GetClassName(hwnd)
    if classname == "Chrome_WidgetWin_1" and ("deezer" in title.lower() or title == ""):
        try:
            import win32process
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            import psutil
            proc = psutil.Process(pid)
            if "deezer" in proc.name().lower():
                candidats.append((hwnd, title, win32gui.IsWindowVisible(hwnd)))
        except:
            pass
    return True

win32gui.EnumWindows(foreach_window, 0)
print(f"Candidats: {candidats}")

if not candidats:
    print("No Deezer window found.")
    sys.exit(1)

hwnd, title, visible = candidats[0]
print(f"Showing and restoring window HWND={hwnd}...")
win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception as e:
    print(f"SetForegroundWindow failed: {e}")
time.sleep(1.0)

# Re-fetch visible state
print(f"Is visible now: {win32gui.IsWindowVisible(hwnd)}")

deezer_ctrl = auto.WindowControl(searchDepth=1, ClassName="Chrome_WidgetWin_1", Name="Deezer")
if not deezer_ctrl.Exists(1.0):
    # Try finding by class only
    print("WindowControl with Name='Deezer' not found, searching by ClassName only...")
    deezer_ctrl = auto.Control(searchDepth=1, ClassName="Chrome_WidgetWin_1")
    # check if it is indeed deezer
    found = False
    for child in auto.GetRootControl().GetChildren():
        if child.ClassName == "Chrome_WidgetWin_1" and child.Name == "Deezer":
            deezer_ctrl = child
            found = True
            break
    if not found:
        print("Could not bind Deezer control.")
        sys.exit(1)

print(f"Bound control Name: '{deezer_ctrl.Name}', Class: '{deezer_ctrl.ClassName}'")

# Dump all elements recursively
def dump_ctrl(control, depth=0):
    indent = "  " * depth
    name = control.Name or ""
    ctype = control.ControlTypeName or ""
    rect = control.BoundingRectangle
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    print(f"{indent}{ctype}: '{name}' (Size: {w}x{h})")
    for child in control.GetChildren():
        dump_ctrl(child, depth + 1)

dump_ctrl(deezer_ctrl)
