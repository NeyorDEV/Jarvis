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

# Find PIDs of Deezer
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
print(f"Render HWNDs found: {render_hwnds}")

for r_hwnd in render_hwnds:
    print(f"\n--- Checking Render HWND {r_hwnd} ---")
    # Send WM_GETOBJECT to make sure accessibility is active
    win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
    time.sleep(0.5)
    
    try:
        ctrl = auto.ControlFromHandle(r_hwnd)
        print(f"Control bound: Name='{ctrl.Name}', Type={ctrl.ControlTypeName}, AutoId='{ctrl.AutomationId}'")
        
        # Check if we can find DocumentControl
        doc = ctrl.DocumentControl(searchDepth=5)
        if doc.Exists(0.5):
            print(f"🎉 DocumentControl found inside render HWND! Name='{doc.Name}'")
            # Dump first few elements
            for child in doc.GetChildren()[:10]:
                print(f"  - [{child.ControlTypeName}] Name: '{child.Name}'")
        else:
            print("❌ DocumentControl not found inside this render HWND.")
            
        # Dump direct children of the render control
        print("Direct children of render control:")
        for child in ctrl.GetChildren():
            print(f"  - [{child.ControlTypeName}] Name: '{child.Name}' | Class: '{child.ClassName}'")
            
    except Exception as e:
        print(f"Error checking render HWND {r_hwnd}: {e}")
