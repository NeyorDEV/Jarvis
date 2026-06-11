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
        
    page_content = ctrl.GroupControl(searchDepth=5, AutomationId='page_content')
    if page_content.Exists(2.0):
        print("🎉 page_content found!")
        # Let's find child CustomControls directly using uiautomation's WalkControl or GetChildren
        # Let's print the descendant elements under page_content up to depth 4
        def dump_descendants(c, depth=0):
            indent = "  " * depth
            name = c.Name or ""
            auto_id = c.AutomationId or ""
            ctype = c.ControlTypeName or ""
            # Print only relevant details
            if "écouter" in name.lower() or ctype in ("CustomControl", "ListControl", "ListItemControl"):
                print(f"{indent}- [{ctype}] Name='{name[:50]}', AutomationId='{auto_id}'")
            for child in c.GetChildren():
                dump_descendants(child, depth + 1)
        
        dump_descendants(page_content)
    else:
        print("❌ NOT FOUND page_content")

asyncio.run(main())
