import sys
import os
import time
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import get_deezer_main_control, deezer_ouvrir, _uia_clic_bouton_piste_album

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
        
    # Clear and set value via UIA ValuePattern
    val_pat = search_edit.GetValuePattern()
    print("Setting value via ValuePattern...")
    val_pat.SetValue("1809 Menace Santana")
    
    # Check if we can find the track button
    print("Checking if track button appears in UIA tree (sleeping 3s)...")
    time.sleep(3.0)
    
    # Look for button named containing "1809"
    found_btn = None
    def _find_btn(c):
        nonlocal found_btn
        if c.ControlTypeName == "ButtonControl" and c.Name and "1809" in c.Name:
            found_btn = c
            return True
        for child in c.GetChildren():
            if _find_btn(child):
                return True
        return False
        
    _find_btn(ctrl)
    if found_btn:
        print(f"✅ SUCCESS: Found track button: '{found_btn.Name}'!")
    else:
        print("❌ FAILURE: Track button did not appear. Search results did not update.")

asyncio.run(main())
