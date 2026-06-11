import win32gui
import win32process
import psutil
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def enum_cb(hwnd, results):
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    is_visible = win32gui.IsWindowVisible(hwnd)
    
    if "Chrome_WidgetWin" in class_name or "Deezer" in title or "Deezer" in class_name:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc_name = "unknown"
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
        except:
            pass
        results.append((hwnd, title, class_name, is_visible, pid, proc_name))
    return True

results = []
win32gui.EnumWindows(enum_cb, results)
print("Found windows:")
for hwnd, title, class_name, is_visible, pid, proc_name in results:
    print(f"HWND: {hwnd} | Title: '{title}' | Class: '{class_name}' | Visible: {is_visible} | PID: {pid} | Proc: {proc_name}")
