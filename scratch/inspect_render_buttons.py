import uiautomation as auto
import sys
import win32gui
import win32process
import psutil
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Find the HWND of the Chrome_RenderWidgetHostHWND belonging to Deezer with the active song name
deezer_pids = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            deezer_pids.append(proc.info['pid'])
    except:
        pass

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

print(f"Render HWNDs: {render_hwnds}")

for r_hwnd in render_hwnds:
    # Send WM_GETOBJECT
    win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
    time.sleep(0.2)
    
    try:
        ctrl = auto.ControlFromHandle(r_hwnd)
        print(f"\n==========================================")
        print(f"Render HWND: {r_hwnd} | Name: '{ctrl.Name}' | Type: {ctrl.ControlTypeName}")
        print(f"==========================================")
        
        # Dump all button elements in this control
        buttons = []
        def find_buttons(c):
            if c.ControlTypeName == "ButtonControl":
                buttons.append(c)
            for child in c.GetChildren():
                find_buttons(child)
                
        find_buttons(ctrl)
        print(f"Found {len(buttons)} buttons in this control:")
        for idx, btn in enumerate(buttons):
            print(f"  Button {idx}: Name='{btn.Name}', Rect={btn.BoundingRectangle}")
            
    except Exception as e:
        print(f"Error: {e}")
