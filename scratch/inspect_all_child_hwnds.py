import win32gui
import win32process
import psutil
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("Finding all windows belonging to Deezer.exe processes...")

deezer_pids = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            deezer_pids.append(proc.info['pid'])
    except:
        pass

print(f"Deezer PIDs: {deezer_pids}")

def enum_windows_callback(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd) or True:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in deezer_pids:
            title = win32gui.GetWindowText(hwnd)
            classname = win32gui.GetClassName(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            print(f"HWND: {hwnd} | PID: {pid} | Title: '{title}' | Class: '{classname}' | Visible: {visible}")
            
            # List child windows
            children = []
            def child_callback(child_hwnd, _):
                c_title = win32gui.GetWindowText(child_hwnd)
                c_classname = win32gui.GetClassName(child_hwnd)
                children.append((child_hwnd, c_classname, c_title))
                return True
            try:
                win32gui.EnumChildWindows(hwnd, child_callback, None)
            except Exception as e:
                pass
            
            for c_hwnd, c_class, c_title in children:
                print(f"   -> Child HWND: {c_hwnd} | Class: '{c_class}' | Title: '{c_title}'")
    return True

win32gui.EnumWindows(enum_windows_callback, None)
