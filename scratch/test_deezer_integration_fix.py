import sys
import os
import asyncio
import time

# Add controller directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    deezer_rechercher,
    deezer_lecture_pause,
    deezer_stop,
    deezer_obtenir_titre_encours,
    get_deezer_main_control
)

async def test_flow():
    print("1. Testing get_deezer_main_control()...")
    ctrl = get_deezer_main_control()
    if ctrl:
        print(f"🎉 Success! Found main control: Name='{ctrl.Name}', Type={ctrl.ControlTypeName}")
    else:
        print("❌ Failed to find main control. Make sure Deezer is running.")
        
    print("\n2. Getting current playing track...")
    track_info = deezer_obtenir_titre_encours()
    print(f"Current track: {track_info}")

    print("\n3. Launching 'c63 de werenoi' via deezer_rechercher...")
    res = await deezer_rechercher("c63 de werenoi")
    print(f"Result: {res}")
    
    print("\nWaiting 5 seconds for track to play...")
    await asyncio.sleep(5)
    
    print("\n4. Getting current playing track...")
    track_info = deezer_obtenir_titre_encours()
    print(f"Current track: {track_info}")
    
    print("\n5. Toggling play/pause (pausing)...")
    res = await deezer_lecture_pause()
    print(f"Result: {res}")
    
    print("\nWaiting 3 seconds...")
    await asyncio.sleep(3)
    
    print("\n6. Toggling play/pause (resuming)...")
    res = await deezer_lecture_pause()
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(test_flow())
