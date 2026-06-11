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
        
    print("Searching for page_content with AutomationId='page_content' and searchDepth=5...")
    page_content = ctrl.GroupControl(searchDepth=5, AutomationId='page_content')
    if page_content.Exists(2.0):
        print(f"🎉 FOUND! Type={page_content.ControlTypeName}, AutomationId='{page_content.AutomationId}'")
        children = page_content.GetChildren()
        print(f"page_content children count: {len(children)}")
        for i, child in enumerate(children):
            print(f"  Child {i}: Name='{child.Name}', Type={child.ControlTypeName}, AutomationId='{child.AutomationId}'")
    else:
        print("❌ NOT FOUND page_content with AutomationId='page_content'")

asyncio.run(main())
