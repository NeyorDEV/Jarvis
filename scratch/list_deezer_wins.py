import ctypes
import sys
import psutil

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Find running processes containing 'deezer'
print("--- Processes containing 'deezer' ---")
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'deezer' in proc.info['name'].lower():
            print(f"PID: {proc.info['pid']}, Name: {proc.info['name']}")
    except:
        pass

# Find windows containing 'deezer'
print("\n--- Windows containing 'deezer' ---")
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetClassName = ctypes.windll.user32.GetClassNameW

def foreach_window(hwnd, lParam):
    length = GetWindowTextLength(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        title = buff.value
        
        class_buff = ctypes.create_unicode_buffer(256)
        GetClassName(hwnd, class_buff, 256)
        classname = class_buff.value
        
        if 'deezer' in title.lower() or 'deezer' in classname.lower() or 'chrome_widgetwin_1' in classname.lower():
            import win32gui
            visible = win32gui.IsWindowVisible(hwnd)
            print(f"HWND: {hwnd}, Title: '{title}', Class: '{classname}', Visible: {visible}")
    return True
    
EnumWindows(EnumWindowsProc(foreach_window), 0)
