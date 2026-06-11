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
        
    print("\n--- Method 3: Ultra Optimized ListControl Search ---")
    t0 = time.time()
    tracks_new = []
    page_content = ctrl.GroupControl(searchDepth=5, AutomationId='page_content')
    if page_content.Exists(0.5):
        list_ctrl = page_content.ListControl(searchDepth=4)
        if list_ctrl.Exists(0.5):
            for item in list_ctrl.GetChildren():
                c = item.CustomControl(searchDepth=3)
                if c.Exists(0.1):
                    name = c.Name
                    if name and ("écouter" in name.lower() or "afficher le menu" in name.lower()):
                        tracks_new.append(name)
                        if len(tracks_new) >= 15:
                            break
    t_new = time.time() - t0
    print(f"Ultra method took: {t_new:.4f}s (found {len(tracks_new)} tracks)")
    for name in tracks_new[:5]:
        print(f"  - {name[:60]}")

asyncio.run(main())
