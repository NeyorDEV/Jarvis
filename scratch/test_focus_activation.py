import sys
import os
import time
import win32gui
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control

def main():
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Deezer not running")
        return
        
    top = ctrl.GetTopLevelControl()
    hwnd_top = top.NativeWindowHandle
    print(f"Top window handle: {hwnd_top}, Name: '{top.Name}', Class: '{top.ClassName}'")
    
    # Check current active window
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")
    
    # Try UIA activation
    print("Activating top control via UIA...")
    top.SetActive()
    time.sleep(0.5)
    top.SetFocus()
    time.sleep(0.5)
    
    # Check current active window after UIA
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == hwnd_top:
        print("✅ SUCCESS: Deezer is now the active window!")
    else:
        print("❌ FAILURE: Deezer is not the active window!")

if __name__ == "__main__":
    main()
