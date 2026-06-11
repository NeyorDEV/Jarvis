import sys
import os
import time
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control

async def main():
    print("Getting main control...")
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Could not get Deezer main control!")
        return
        
    print(f"✔ Main control found: Name='{ctrl.Name}', Type='{ctrl.ControlTypeName}'")
    
    print("\nDumping ALL visible buttons in the window:")
    def dump_buttons(c, path=""):
        name = c.Name or ""
        ctype = c.ControlTypeName or ""
        
        # Check size
        w, h = 0, 0
        try:
            rect = c.BoundingRectangle
            w = rect.right - rect.left
            h = rect.bottom - rect.top
        except:
            pass
            
        if w > 0 and h > 0:
            current_path = f"{path} > {ctype}('{name}')" if path else f"{ctype}('{name}')"
            if ctype == "ButtonControl":
                print(f"- Button: Name='{name}', Size={w}x{h}, Path={current_path}")
            
            for child in c.GetChildren():
                dump_buttons(child, current_path)
        else:
            for child in c.GetChildren():
                dump_buttons(child, path)
            
    dump_buttons(ctrl)

import asyncio
asyncio.run(main())
