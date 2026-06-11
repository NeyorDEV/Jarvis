import uiautomation as auto
import sys
import os
import time
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_ouvrir, get_deezer_main_control, _ouvrir_uri_deezer

async def main():
    await deezer_ouvrir()
    time.sleep(2)
    _ouvrir_uri_deezer("deezer://playlist/1890860542")
    time.sleep(4)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer control not found.")
        return
        
    print("\n--- Method 2: New Optimized Depth-limited page_content Search ---")
    t0 = time.time()
    tracks_new = []
    page_content = ctrl.GroupControl(searchDepth=5, AutomationId='page_content')
    if page_content.Exists(0.5):
        def find_tracks_new(c, depth=0):
            if depth > 10 or len(tracks_new) >= 15:
                return
            ctype = c.ControlTypeName or ""
            name = c.Name or ""
            if ctype == "CustomControl" and name:
                if "écouter" in name.lower() or "afficher le menu" in name.lower():
                    tracks_new.append((name, depth))
            for child in c.GetChildren():
                find_tracks_new(child, depth + 1)
        find_tracks_new(page_content)
    t_new = time.time() - t0
    print(f"New method took: {t_new:.4f}s (found {len(tracks_new)} tracks)")
    for name, depth in tracks_new[:5]:
        print(f"  - Depth {depth}: {name[:60]}")

asyncio.run(main())
