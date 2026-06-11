import sys
import os
import time
import win32gui

try:
    import pyautogui
except ImportError:
    pyautogui = None

sys.stdout.reconfigure(encoding='utf-8')

def main():
    if not pyautogui:
        print("❌ pyautogui not installed")
        return
        
    print("Please keep VS Code active.")
    print("Sending global media key 'nexttrack' in 3 seconds...")
    time.sleep(3.0)
    
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")
    
    # Send media key
    pyautogui.press('nexttrack')
    time.sleep(1.0)
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("✅ SUCCESS: Media key did not steal focus!")
    else:
        print("❌ FAILURE: Focus was stolen!")

if __name__ == "__main__":
    main()
