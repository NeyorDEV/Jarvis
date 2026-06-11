import sys
import os
import asyncio
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_suivant, deezer_precedent, get_deezer_main_control, find_player_button

async def main():
    print("Testing player button identification...")
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Deezer not running / not accessible")
        return
        
    btn_prev = find_player_button(ctrl, ["Précédent"])
    if btn_prev:
        print(f"✔ Found Précédent button: Name='{btn_prev.Name}', Size={btn_prev.BoundingRectangle.right - btn_prev.BoundingRectangle.left}x{btn_prev.BoundingRectangle.bottom - btn_prev.BoundingRectangle.top}")
        if btn_prev.BoundingRectangle.right - btn_prev.BoundingRectangle.left == 33:
            print("✅ Correct track previous button (33x33) identified!")
        else:
            print("❌ Wrong button (not 33x33) identified!")
    else:
        print("❌ Précédent button not found!")
        
    btn_next = find_player_button(ctrl, ["Suivant"])
    if btn_next:
        print(f"✔ Found Suivant button: Name='{btn_next.Name}', Size={btn_next.BoundingRectangle.right - btn_next.BoundingRectangle.left}x{btn_next.BoundingRectangle.bottom - btn_next.BoundingRectangle.top}")
    else:
        print("❌ Suivant button not found!")

    print("\nExecuting track next...")
    res1 = await deezer_suivant()
    print(f"Result: {res1}")
    
    print("\nWaiting 2 seconds...")
    time.sleep(2)
    
    print("\nExecuting track previous...")
    res2 = await deezer_precedent()
    print(f"Result: {res2}")

asyncio.run(main())
