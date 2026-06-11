import sys
import os
import uiautomation as auto

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control

def main():
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer not running")
        return
        
    print("Dumping elements with right coordinate < 350 (Sidebar area)...")
    
    sidebar_elements = []
    
    def walk(c, depth=0):
        if depth > 18:
            return
        try:
            rect = c.BoundingRectangle
            # Check if it's on the left side
            if rect.right > 0 and rect.right < 350:
                name = c.Name or ""
                ctype = c.ControlTypeName or ""
                auto_id = c.AutomationId or ""
                sidebar_elements.append((depth, ctype, name, auto_id, rect))
        except:
            pass
            
        for child in c.GetChildren():
            walk(child, depth + 1)
            
    walk(ctrl)
    
    print(f"\nFound {len(sidebar_elements)} elements in the sidebar area:")
    for depth, ctype, name, auto_id, rect in sidebar_elements:
        if name or auto_id:
            print(f"Depth {depth} | {ctype} | Name: '{name}' | AutoId: '{auto_id}' | Rect: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")

if __name__ == "__main__":
    main()
