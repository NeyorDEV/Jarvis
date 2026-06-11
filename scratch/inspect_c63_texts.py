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
    print(f"Main control name: '{main_ctrl.Name}'")
    # Let's dump all TextControl, HeaderControl, or TitleBarControl elements
    print("Dumping all elements with type containing Text, Title, Header or having a non-empty name:")
    elements = []
    def collect_elements(c, depth=0):
        name = c.Name or ""
        ctype = c.ControlTypeName or ""
        if name and (ctype in ["TextControl", "HeaderControl", "TitleBarControl", "HyperlinkControl", "CustomControl"] or "c63" in name.lower() or "werenoi" in name.lower()):
            elements.append((depth, ctype, name))
        for child in c.GetChildren():
            collect_elements(child, depth + 1)
            
    collect_elements(main_ctrl)
    for depth, ctype, name in elements[:50]:
        print(f"{'  ' * depth}- [{ctype}] '{name}'")
else:
    print("Main control not found.")
