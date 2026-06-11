import uiautomation as auto
import sys
import win32gui
import win32process
import psutil
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def get_deezer_main_control():
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                deezer_pids.append(proc.info['pid'])
        except:
            pass
            
    render_hwnds = []
    def enum_windows_callback(hwnd, extra):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in deezer_pids:
            def child_callback(child_hwnd, _):
                c_class = win32gui.GetClassName(child_hwnd)
                if c_class == "Chrome_RenderWidgetHostHWND":
                    render_hwnds.append(child_hwnd)
                return True
            try:
                win32gui.EnumChildWindows(hwnd, child_callback, None)
            except:
                pass
        return True

    win32gui.EnumWindows(enum_windows_callback, None)
    
    best_ctrl = None
    max_buttons = -1
    for r_hwnd in render_hwnds:
        try:
            win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
        except:
            pass
        try:
            ctrl = auto.ControlFromHandle(r_hwnd)
            if ctrl and ctrl.Exists(0.1):
                buttons_count = 0
                def count_buttons(c):
                    nonlocal buttons_count
                    if c.ControlTypeName == "ButtonControl":
                        buttons_count += 1
                    for child in c.GetChildren():
                        count_buttons(child)
                count_buttons(ctrl)
                if buttons_count > max_buttons:
                    max_buttons = buttons_count
                    best_ctrl = ctrl
        except:
            pass
    return best_ctrl

main_ctrl = get_deezer_main_control()
if main_ctrl:
    button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
    buttons = []
    def collect_buttons(c):
        if c.ControlTypeName == "ButtonControl" and (c.Name in button_names or any(c.Name.startswith(b) for b in button_names)):
            buttons.append(c)
        for child in c.GetChildren():
            collect_buttons(child)
            
    collect_buttons(main_ctrl)
    
    # Filter for the page button
    page_btn = None
    for btn in buttons:
        rect = btn.BoundingRectangle
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w > 0 and h > 0:
            ratio = w / h
            if ratio >= 1.3:
                # Check if it has player bar siblings
                is_player_bar = False
                curr = btn
                for _ in range(3):
                    curr = curr.GetParentControl()
                    if not curr:
                        break
                    descendants = []
                    def get_descendant_names(ctrl):
                        if ctrl.ControlTypeName == "ButtonControl":
                            descendants.append(ctrl.Name or "")
                        for child in ctrl.GetChildren():
                            get_descendant_names(child)
                    get_descendant_names(curr)
                    if "Précédent" in descendants or "Suivant" in descendants:
                        is_player_bar = True
                        break
                if not is_player_bar:
                    page_btn = btn
                    break
                    
    if page_btn:
        print("Page button details:")
        print(f"  Name: '{page_btn.Name}'")
        print(f"  AutomationId: '{page_btn.AutomationId}'")
        print(f"  ClassName: '{page_btn.ClassName}'")
        print(f"  ControlTypeName: '{page_btn.ControlTypeName}'")
        print(f"  BoundingRectangle: {page_btn.BoundingRectangle}")
        print(f"  IsEnabled: {page_btn.IsEnabled}")
        print(f"  IsKeyboardFocusable: {page_btn.IsKeyboardFocusable}")
        print(f"  HasKeyboardFocus: {page_btn.HasKeyboardFocus}")
        
        # Print parent hierarchy
        print("\nParent hierarchy:")
        curr = page_btn
        for i in range(5):
            curr = curr.GetParentControl()
            if not curr:
                break
            print(f"  Parent {i+1}: Name='{curr.Name}', Type={curr.ControlTypeName}, Class='{curr.ClassName}'")
            
    else:
        print("Page button not found.")
else:
    print("Main control not found.")
