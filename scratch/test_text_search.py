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

def has_text_in_tree(control, text_to_find, max_depth=12):
    text_lower = text_to_find.lower().strip()
    
    def _search(c, depth):
        if depth > max_depth:
            return False
        name = c.Name or ""
        if text_lower in name.lower():
            # Skip if it is the top-level DocumentControl name (which is the currently playing track, not the page content)
            if depth == 1 and c.ControlTypeName == "DocumentControl":
                pass
            else:
                print(f"Match found at depth {depth}: '{name}' ({c.ControlTypeName})")
                return True
        for child in c.GetChildren():
            if _search(child, depth + 1):
                return True
        return False
        
    return _search(control, 1)

main_ctrl = get_deezer_main_control()
if main_ctrl:
    t0 = time.time()
    found = has_text_in_tree(main_ctrl, "c63", max_depth=12)
    t1 = time.time()
    print(f"Search for 'c63' took {t1-t0:.4f}s. Found: {found}")
    
    t0 = time.time()
    found = has_text_in_tree(main_ctrl, "werenoi", max_depth=12)
    t1 = time.time()
    print(f"Search for 'werenoi' took {t1-t0:.4f}s. Found: {found}")
    
    t0 = time.time()
    found = has_text_in_tree(main_ctrl, "xyz123abc", max_depth=12)
    t1 = time.time()
    print(f"Search for non-existent took {t1-t0:.4f}s. Found: {found}")
else:
    print("Main control not found.")
