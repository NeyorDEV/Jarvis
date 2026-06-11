import uiautomation as auto
import sys
import time
import win32gui

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Find the HWNDs we saw
hwnds = [34549888, 2036352, 2101712]

# Let's find them dynamically in case HWNDs changed
import win32process
import psutil

deezer_pids = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            deezer_pids.append(proc.info['pid'])
    except:
        pass

widget_win_0_hwnds = []
def enum_windows_callback(hwnd, extra):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    if pid in deezer_pids:
        classname = win32gui.GetClassName(hwnd)
        if classname == "Chrome_WidgetWin_0":
            widget_win_0_hwnds.append(hwnd)
    return True

win32gui.EnumWindows(enum_windows_callback, None)
print(f"Dynamic Chrome_WidgetWin_0 HWNDs: {widget_win_0_hwnds}")

for hwnd in widget_win_0_hwnds:
    print(f"\n--- Checking HWND {hwnd} ---")
    try:
        # Send WM_GETOBJECT to trigger accessibility on children
        children = []
        def child_callback(child_hwnd, _):
            c_classname = win32gui.GetClassName(child_hwnd)
            if c_classname == "Chrome_RenderWidgetHostHWND":
                children.append(child_hwnd)
            return True
        win32gui.EnumChildWindows(hwnd, child_callback, None)
        
        for c_hwnd in children:
            print(f"Sending WM_GETOBJECT to child Chrome_RenderWidgetHostHWND {c_hwnd}...")
            # WM_GETOBJECT = 0x003D, OBJID_CLIENT = 0xFFFFFFFC
            win32gui.SendMessage(c_hwnd, 0x003D, 0, 0xFFFFFFFC)
            
        time.sleep(0.5)
        
        ctrl = auto.ControlFromHandle(hwnd)
        print(f"Control bound: Name='{ctrl.Name}', Type={ctrl.ControlTypeName}")
        
        def dump_ctrl(control, depth=0):
            indent = "  " * depth
            name = control.Name or ""
            ctype = control.ControlTypeName or ""
            print(f"{indent}{ctype}: '{name}'")
            # Don't go too deep if it's too large, but let's see
            children = control.GetChildren()
            for child in children:
                dump_ctrl(child, depth + 1)
                
        dump_ctrl(ctrl)
    except Exception as e:
        print(f"Error checking HWND {hwnd}: {e}")
