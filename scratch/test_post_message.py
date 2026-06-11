import sys
import os
import time
import win32gui
import win32con

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, deezer_obtenir_titre_encours

def main():
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer not running")
        return
        
    top = ctrl.GetTopLevelControl()
    hwnd = top.NativeWindowHandle
    if not hwnd:
        print("Top window handle not found")
        return
        
    print(f"Top HWND: {hwnd}")
    
    # Check current track before
    playing_before = deezer_obtenir_titre_encours()
    print(f"Before: {playing_before}")
    
    # Send APPCOMMAND_MEDIA_NEXTTRACK (11)
    WM_APPCOMMAND = 0x0319
    APPCOMMAND_MEDIA_NEXTTRACK = 11
    lParam = APPCOMMAND_MEDIA_NEXTTRACK << 16
    
    print("Posting WM_APPCOMMAND NEXTTRACK...")
    win32gui.PostMessage(hwnd, WM_APPCOMMAND, hwnd, lParam)
    
    time.sleep(2.0)
    
    # Check current track after
    playing_after = deezer_obtenir_titre_encours()
    print(f"After: {playing_after}")
    
    if playing_after != playing_before:
        print("SUCCESS: Track changed successfully!")
    else:
        print("FAILURE: Track did not change.")

if __name__ == "__main__":
    main()
