import sys
import os
import asyncio
import time
import win32gui
import psutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_rechercher, deezer_ouvrir

async def main():
    print("Ensuring Deezer is open...")
    await deezer_ouvrir()
    time.sleep(4.0)
    
    print("\n--- TEST: Running search while Deezer is in the background ---")
    print("Please make sure VS Code / this terminal window is active.")
    print("Starting background search in 4 seconds...")
    time.sleep(4.0)
    
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")
    
    # Run background search
    res = await deezer_rechercher("c63 de werenoi")
    print(f"Result: {res}")
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after search: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")
    
    if active_after == active_before:
        print("\n✅ SUCCESS: Deezer performed search and play completely in the background! Focus was not stolen!")
    else:
        print("\n❌ FAILURE: Focus was stolen by Deezer!")

asyncio.run(main())
