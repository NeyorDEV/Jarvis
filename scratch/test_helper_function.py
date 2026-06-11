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
    """Trouve le DocumentControl (Chrome_RenderWidgetHostHWND) principal de Deezer."""
    if not auto:
        return None
    
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                deezer_pids.append(proc.info['pid'])
        except:
            pass
            
    if not deezer_pids:
        print("No Deezer processes running.")
        return None
        
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
    print(f"Render HWNDs: {render_hwnds}")
    
    best_ctrl = None
    max_buttons = -1
    
    for r_hwnd in render_hwnds:
        try:
            win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
        except:
            pass
            
        try:
            ctrl = auto.ControlFromHandle(r_hwnd)
            if ctrl and ctrl.Exists(0.2):
                # Count button controls
                buttons_count = 0
                def count_buttons(c):
                    nonlocal buttons_count
                    if c.ControlTypeName == "ButtonControl":
                        buttons_count += 1
                    for child in c.GetChildren():
                        count_buttons(child)
                count_buttons(ctrl)
                
                print(f"HWND {r_hwnd}: Name='{ctrl.Name}', Buttons={buttons_count}")
                if buttons_count > max_buttons:
                    max_buttons = buttons_count
                    best_ctrl = ctrl
        except Exception as e:
            print(f"Error binding HWND {r_hwnd}: {e}")
            
    return best_ctrl

main_ctrl = get_deezer_main_control()
if main_ctrl:
    print(f"🎉 Success! Best control: Name='{main_ctrl.Name}', Type={main_ctrl.ControlTypeName}")
    
    # Try to find page play button
    button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
    
    # Let's see if we can find buttons matching button_names
    buttons = []
    def collect_buttons(c):
        if c.ControlTypeName == "ButtonControl" and (c.Name in button_names or any(c.Name.startswith(b) for b in button_names)):
            buttons.append(c)
        for child in c.GetChildren():
            collect_buttons(child)
            
    collect_buttons(main_ctrl)
    print(f"Found {len(buttons)} play/pause/ecouter buttons:")
    for idx, btn in enumerate(buttons):
        w = btn.BoundingRectangle.right - btn.BoundingRectangle.left
        h = btn.BoundingRectangle.bottom - btn.BoundingRectangle.top
        print(f"  Button {idx}: Name='{btn.Name}', Size={w}x{h}, Rect={btn.BoundingRectangle}")
else:
    print("❌ Failed to find main control.")
