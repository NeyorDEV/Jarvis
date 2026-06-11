import sys
import os
import time
import win32gui
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import (
    get_deezer_main_control,
    deezer_ouvrir,
    prevent_focus_theft,
    _clic_control,
    _uia_clic_bouton_page_dynamique
)

def _trouver_playlist_sidebar(deezer_ctrl, query):
    query_lower = query.lower().strip()
    found_elem = None
    
    def _search_sidebar(control):
        nonlocal found_elem
        if found_elem:
            return
            
        try:
            rect = control.BoundingRectangle
            if rect.right > 0 and rect.right < 350:
                name = control.Name or ""
                ctype = control.ControlTypeName or ""
                
                if ctype in ("DataItemControl", "TextControl", "HyperlinkControl"):
                    if query_lower in name.lower():
                        # Exclure le lecteur du bas
                        if rect.top < 940:
                            found_elem = control
                            return
        except:
            pass
            
        for child in control.GetChildren():
            _search_sidebar(child)
            
    _search_sidebar(deezer_ctrl)
    return found_elem

async def main():
    print("Ensuring Deezer is open...")
    await deezer_ouvrir()
    time.sleep(2)
    
    ctrl = get_deezer_main_control()
    if not ctrl:
        print("Deezer not running")
        return
        
    print("Looking for playlist 'teenage dirtbag' in the sidebar...")
    elem = _trouver_playlist_sidebar(ctrl, "teenage dirtbag")
    if elem:
        print(f"✅ Found sidebar element: '{elem.Name}' ({elem.ControlTypeName}) at rect {elem.BoundingRectangle}")
        
        # Click it
        with prevent_focus_theft():
            active_before = win32gui.GetForegroundWindow()
            print(f"Active window before: {active_before} ({win32gui.GetWindowText(active_before)})")
            
            print("Clicking sidebar playlist item...")
            _clic_control(elem)
            time.sleep(1.5)
            
            active_after = win32gui.GetForegroundWindow()
            print(f"Active window after: {active_after} ({win32gui.GetWindowText(active_after)})")
            
            if active_after == active_before:
                print("✅ Clicked without stealing focus!")
            else:
                print("❌ Focus was stolen!")
                
            # Click play on page
            print("Clicking play on page...")
            ok = _uia_clic_bouton_page_dynamique(
                ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"],
                12, wait_for_title="teenage dirtbag"
            )
            print(f"Play result: {ok}")
            time.sleep(1.5)
    else:
        print("❌ Playlist 'teenage dirtbag' not found in sidebar")

asyncio.run(main())
