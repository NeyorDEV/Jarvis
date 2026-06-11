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

from controller.deezer_controller import deezer_ouvrir, get_deezer_main_control

async def main():
    await deezer_ouvrir()
    time.sleep(2)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer control not found.")
        return
        
    query_lower = "teenage dirtbag"
    
    print("\n--- Method 2: New Pruned Sidebar Search ---")
    t0 = time.time()
    elem_playlist_new = None
    def _find_sidebar_new(c, depth=0):
        nonlocal elem_playlist_new
        if elem_playlist_new or depth > 8:
            return
        try:
            rect = c.BoundingRectangle
            # Only prune if it is completely to the right or completely below
            if rect.left >= 350:
                return # Prune right side
            if rect.top >= 940:
                return # Prune bottom side
                
            name = c.Name or ""
            ctype = c.ControlTypeName or ""
            if ctype in ("DataItemControl", "TextControl", "HyperlinkControl"):
                if query_lower in name.lower():
                    # Double check it is actually in the sidebar (right < 350)
                    if rect.right < 350:
                        elem_playlist_new = c
                        return
        except:
            pass
        for child in c.GetChildren():
            _find_sidebar_new(child, depth + 1)
            
    _find_sidebar_new(ctrl)
    t_new = time.time() - t0
    print(f"New sidebar search took: {t_new:.4f}s (found: {elem_playlist_new.Name if elem_playlist_new else 'None'})")

asyncio.run(main())
