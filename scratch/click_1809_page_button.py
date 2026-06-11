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
if not main_ctrl:
    print("Main control not found.")
    sys.exit(1)

print(f"Main control name: '{main_ctrl.Name}'")

# Find the page play button
button_names = ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"]
buttons = []
def collect_buttons(c):
    if c.ControlTypeName == "ButtonControl" and (c.Name in button_names or any(c.Name.startswith(b) for b in button_names)):
        buttons.append(c)
    for child in c.GetChildren():
        collect_buttons(child)
        
collect_buttons(main_ctrl)
print(f"All matching buttons:")
for idx, btn in enumerate(buttons):
    w = btn.BoundingRectangle.right - btn.BoundingRectangle.left
    h = btn.BoundingRectangle.bottom - btn.BoundingRectangle.top
    print(f"  Button {idx}: Name='{btn.Name}', Size={w}x{h}, Rect={btn.BoundingRectangle}")

# Filter for the page button (w/h ratio > 1.3, not in bottom player bar)
page_btn = None
for btn in buttons:
    try:
        rect = btn.BoundingRectangle
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w > 0 and h > 0:
            ratio = w / h
            if ratio < 1.3:
                continue
        else:
            continue
            
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
    except:
        continue

if page_btn:
    print(f"🎯 Target page button found: Name='{page_btn.Name}', Size={page_btn.BoundingRectangle.right - page_btn.BoundingRectangle.left}x{page_btn.BoundingRectangle.bottom - page_btn.BoundingRectangle.top}")
    print("Clicking the page button...")
    # Invoke
    pattern = page_btn.GetInvokePattern()
    if pattern:
        pattern.Invoke()
    else:
        page_btn.Click(simulateMove=False)
        
    print("Waiting 3 seconds...")
    time.sleep(3)
    
    # Re-fetch main control and print currently playing track
    main_ctrl2 = get_deezer_main_control()
    if main_ctrl2:
        print(f"Active song now: '{main_ctrl2.Name}'")
else:
    print("Page button not found.")
