import sys
import os
import time
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from controller.deezer_controller import get_deezer_main_control

def main():
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Could not get Deezer main control!")
        return
        
    out_path = os.path.join(os.path.dirname(__file__), "buttons_dump.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Main control: Name='{ctrl.Name}', Type='{ctrl.ControlTypeName}'\n\n")
        
        def dump_buttons(c, depth=0):
            name = c.Name or ""
            ctype = c.ControlTypeName or ""
            auto_id = c.AutomationId or ""
            
            w, h = 0, 0
            try:
                rect = c.BoundingRectangle
                w = rect.right - rect.left
                h = rect.bottom - rect.top
            except:
                pass
                
            if w > 0 and h > 0:
                indent = "  " * depth
                f.write(f"{indent}- [{ctype}] Name: '{name}' | ID: '{auto_id}' | Size: {w}x{h}\n")
                
            for child in c.GetChildren():
                dump_buttons(child, depth + 1)
                
        dump_buttons(ctrl)
    print(f"✔ Done. Saved to {out_path}")

if __name__ == "__main__":
    main()
