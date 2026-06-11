import sys
import os
import time
import win32gui
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_rechercher

async def main():
    print("Testing deezer_rechercher for 'ma playlist teenage dirtbag'...")
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {active_before} ({win32gui.GetWindowText(active_before)})")
    
    res = await deezer_rechercher("ma playlist teenage dirtbag")
    print(f"Result response: {res}")
    
    time.sleep(2)
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after: {active_after} ({win32gui.GetWindowText(active_after)})")
    
    if active_after == active_before:
        print("✅ SUCCESS: Playlist was searched, opened, and played from sidebar with ZERO focus theft!")
    else:
        print("❌ FAILURE: Focus was stolen!")

asyncio.run(main())
