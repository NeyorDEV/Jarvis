import ctypes
import sys
import time
import win32gui
import win32process
import psutil
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Find PIDs of Deezer
deezer_pids = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            deezer_pids.append(proc.info['pid'])
    except:
        pass

print(f"Deezer PIDs: {deezer_pids}")

# Find main Deezer window and all Chrome_RenderWidgetHostHWND windows
main_hwnd = None
render_hwnds = []

def enum_windows_callback(hwnd, extra):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    if pid in deezer_pids:
        title = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        if classname == "Chrome_WidgetWin_1" and "deezer" in title.lower():
            global main_hwnd
            main_hwnd = hwnd
            
        # Check all child windows recursively
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

print(f"Main Deezer HWND: {main_hwnd}")
print(f"Render HWNDs: {render_hwnds}")

if not main_hwnd:
    print("Main Deezer window not found.")
    sys.exit(1)

# Trigger accessibility on all render windows
for r_hwnd in render_hwnds:
    print(f"Sending WM_GETOBJECT (0x3D) with OBJID_CLIENT (0xFFFFFFFC) to render HWND {r_hwnd}...")
    # SendMessage / PostMessage to trigger accessibility
    win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
    win32gui.SendMessage(r_hwnd, 0x003D, 0, 0)

time.sleep(1.0)

# Bind to main window and dump tree
deezer_ctrl = auto.ControlFromHandle(main_hwnd)
print(f"Bound main window control: Name='{deezer_ctrl.Name}', Class='{deezer_ctrl.ClassName}'")

# Search for DocumentControl
doc = deezer_ctrl.DocumentControl(searchDepth=10)
if doc.Exists(1.0):
    print(f"🎉 DocumentControl found! Name='{doc.Name}'")
    # print first few children
    for child in doc.GetChildren()[:10]:
        print(f"  - [{child.ControlTypeName}] Name: '{child.Name}'")
else:
    print("❌ DocumentControl still not found on the main window.")
