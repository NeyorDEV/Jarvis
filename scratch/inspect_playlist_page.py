import uiautomation as auto
import sys
import os
import win32gui
import win32process
import psutil
import time
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_ouvrir, _get_deezer_pids, get_deezer_main_control, _ouvrir_uri_deezer

async def main():
    await deezer_ouvrir()
    time.sleep(2)
    
    print("Navigating to playlist...")
    _ouvrir_uri_deezer("deezer://playlist/1890860542")
    time.sleep(3) # Wait for page to load
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer control not found.")
        return
        
    page_content = ctrl.GroupControl(AutoId='page_content')
    if not page_content.Exists(2.0):
        print("page_content not found.")
        return
        
    print("Dumping page_content child controls...")
    def dump_content(c, depth=0):
        indent = "  " * depth
        name = c.Name or ""
        auto_id = c.AutomationId or ""
        ctype = c.ControlTypeName or ""
        # Limit print to prevent huge logs
        print(f"{indent}- [{ctype}] Name='{name}', AutoId='{auto_id}'")
        if depth < 4:
            for child in c.GetChildren():
                dump_content(child, depth + 1)
                
    dump_content(page_content)

asyncio.run(main())
