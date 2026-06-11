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

from controller.deezer_controller import deezer_rechercher

async def main():
    # 1. Kill Deezer to start clean
    print("=== Killing Deezer... ===")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try: proc.kill()
            except: pass
    time.sleep(2.0)

    # 2. Focus a non-Deezer window (e.g. this terminal / VS Code window)
    # We will find the window of the terminal or just wait for the user to keep VS Code active.
    print("Please keep VS Code / this terminal active and do not touch the keyboard/mouse.")
    print("Starting search in 4 seconds...")
    time.sleep(4.0)
    
    active_before = win32gui.GetForegroundWindow()
    print(f"Active window before: {active_before} (title: '{win32gui.GetWindowText(active_before)}')")
    
    # 3. Call deezer_rechercher for the album
    print("\nRunning deezer_rechercher...")
    res = await deezer_rechercher("joue l'album invincible de michael jackson")
    print(f"Result: {res}")
    
    active_after = win32gui.GetForegroundWindow()
    print(f"Active window after search: {active_after} (title: '{win32gui.GetWindowText(active_after)}')")

asyncio.run(main())
