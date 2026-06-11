import sys
import os
import time
import asyncio
import ctypes
import win32gui

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, find_player_button

async def main():
    try:
        ctypes.windll.ole32.CoInitialize(None)
    except:
        pass
        
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Deezer not running")
        return
        
    # Get active window before
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")
    
    # Check Suivant button UIA patterns
    btn_next = find_player_button(ctrl, ["Suivant"])
    if btn_next:
        print(f"Suivant button name: '{btn_next.Name}'")
        try:
            pattern = btn_next.GetInvokePattern()
            if pattern:
                print("✔ InvokePattern supported on Suivant button!")
                # Call Invoke
                pattern.Invoke()
                print("✔ Invoke() called on Suivant!")
            else:
                print("❌ InvokePattern is None on Suivant")
        except Exception as e:
            print(f"❌ Invoke on Suivant failed: {e}")
    else:
        print("❌ Suivant button not found")
        
    # Wait a bit
    time.sleep(2.0)
    
    # Check active window after
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after Suivant: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("✅ SUCCESS: Suivant did not steal focus!")
    else:
        print("❌ FAILURE: Suivant stole focus!")

asyncio.run(main())
