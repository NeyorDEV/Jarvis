import sys
import os
import time
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, deezer_ouvrir

async def main():
    print("Opening Deezer...")
    await deezer_ouvrir()
    time.sleep(3)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("❌ Deezer main control not found")
        return
        
    def _find_edit(c, depth=0):
        if c.ControlTypeName == 'EditControl' and depth < 10:
            return c
        if depth < 10:
            for child in c.GetChildren():
                res = _find_edit(child, depth + 1)
                if res:
                    return res
        return None
        
    search_edit = _find_edit(ctrl)
    if not search_edit:
        print("❌ Search edit control not found")
        return
        
    print(f"✔ Search edit found: Name='{search_edit.Name}', Type='{search_edit.ControlTypeName}'")
    
    # Try using ValuePattern
    try:
        val_pat = search_edit.GetValuePattern()
        if val_pat:
            print("✔ ValuePattern supported!")
            val_pat.SetValue("1809 Menace Santana")
            print("✔ ValuePattern.SetValue('1809 Menace Santana') called!")
            
            # Check the new value
            time.sleep(1.0)
            print(f"Current Value in EditControl: '{search_edit.GetValuePattern().Value}'")
        else:
            print("❌ ValuePattern is None")
    except Exception as e:
        print(f"❌ ValuePattern failed: {e}")

asyncio.run(main())
