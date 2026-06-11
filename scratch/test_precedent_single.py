import sys
import os
import time
import win32gui
import win32process
import psutil
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from controller.deezer_controller import (
    get_deezer_main_control,
    deezer_ouvrir,
    deezer_rechercher,
    deezer_obtenir_titre_encours
)

async def test_precedent():
    print("Ensuring Deezer is running and playing a track...")
    await deezer_ouvrir()
    time.sleep(2)
    
    # Play a specific track to test
    print("Playing 'c63 de werenoi'...")
    await deezer_rechercher("c63 de werenoi")
    time.sleep(8) # Let it play for 8 seconds (clearly > 3 seconds)
    
    playing_now = deezer_obtenir_titre_encours()
    print(f"Playing now: {playing_now}")
    
    # Get HWND
    ctrl = get_deezer_main_control()
    top = ctrl.GetTopLevelControl() if ctrl else None
    hwnd = top.NativeWindowHandle if top else None
    if not hwnd:
        print("Could not find HWND")
        return
        
    print("Sending previous command ONCE...")
    WM_APPCOMMAND = 0x0319
    APPCOMMAND_MEDIA_PREVTRACK = 12
    lParam = APPCOMMAND_MEDIA_PREVTRACK << 16
    win32gui.PostMessage(hwnd, WM_APPCOMMAND, hwnd, lParam)
    
    time.sleep(4)
    playing_after = deezer_obtenir_titre_encours()
    print(f"Playing after single previous: {playing_after}")

asyncio.run(test_precedent())
