import sys
import os
import asyncio
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

import uiautomation as auto
from controller.deezer_controller import get_deezer_main_control

def dump_sidebar():
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer not running")
        return
        
    print("Dumping UIA tree to find sidebar links...")
    
    # Let's search recursively for items that might be in the sidebar
    # The sidebar is usually on the left, let's list all elements in the main control
    # to look for "Coups de cœur" or "clara astier" or "Werenoi"
    found_elements = []
    
    def walk_tree(c, depth=0):
        if depth > 15:
            return
        name = c.Name or ""
        ctype = c.ControlTypeName or ""
        auto_id = c.AutomationId or ""
        
        # Check if the element name looks like a sidebar playlist item
        if "clara" in name.lower() or "werenoi" in name.lower() or "coups de" in name.lower() or "dirtbag" in name.lower() or "playlists" in name.lower():
            found_elements.append((depth, ctype, name, auto_id, c))
            
        for child in c.GetChildren():
            walk_tree(child, depth + 1)
            
    walk_tree(ctrl)
    
    print(f"\nFound {len(found_elements)} potential sidebar elements:")
    for depth, ctype, name, auto_id, c in found_elements:
        print(f"Depth {depth} | Type: {ctype} | Name: '{name}' | AutoId: '{auto_id}'")
        try:
            rect = c.BoundingRectangle
            print(f"  Rect: {rect.left}, {rect.top}, {rect.right}, {rect.bottom}")
        except:
            pass

dump_sidebar()
