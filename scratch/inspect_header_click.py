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
        
    header_added = auto.HeaderControl(searchFromControl=ctrl, Name="AJOUTÉ")
    if header_added.Exists(1.0):
        print(f"🎉 HeaderControl found: Name='{header_added.Name}', Type={header_added.ControlTypeName}, AutoId='{header_added.AutomationId}'")
        
        # Check patterns supported by header_added
        try:
            legacy = header_added.GetLegacyIAccessiblePattern()
            print(f"  Header LegacyIAccessiblePattern: {legacy is not None}")
        except Exception as e:
            print(f"  Header LegacyIAccessiblePattern error: {e}")
            
        try:
            invoke = header_added.GetInvokePattern()
            print(f"  Header InvokePattern: {invoke is not None}")
        except Exception as e:
            print(f"  Header InvokePattern error: {e}")
            
        # Check children of HeaderControl
        children = header_added.GetChildren()
        print(f"  Children of HeaderControl count: {len(children)}")
        for i, child in enumerate(children):
            print(f"    Child {i}: Name='{child.Name}', Type={child.ControlTypeName}, AutoId='{child.AutomationId}'")
            try:
                legacy = child.GetLegacyIAccessiblePattern()
                print(f"      LegacyIAccessiblePattern: {legacy is not None}")
            except Exception as e:
                print(f"      LegacyIAccessiblePattern error: {e}")
            try:
                invoke = child.GetInvokePattern()
                print(f"      InvokePattern: {invoke is not None}")
            except Exception as e:
                print(f"      InvokePattern error: {e}")
    else:
        print("❌ HeaderControl 'AJOUTÉ' not found.")

asyncio.run(main())
