import sys
import ctypes
import time
import win32gui
import win32con

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def get_child_windows(parent_hwnd):
    children = []
    def _cb(hwnd, _):
        class_name = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        children.append((hwnd, class_name, title))
        return True
    try:
        win32gui.EnumChildWindows(parent_hwnd, _cb, None)
    except:
        pass
    return children

def main():
    print("🔍 Searching for Deezer window...")
    # Trouver la fenêtre Deezer
    parent_hwnd = 0
    def _find_deezer(hwnd, _):
        nonlocal parent_hwnd
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if "Deezer" in title and class_name == "Chrome_WidgetWin_1":
            parent_hwnd = hwnd
            return False # Stop enumeration
        return True
    
    win32gui.EnumWindows(_find_deezer, None)
    
    if not parent_hwnd:
        print("❌ Deezer window not found.")
        return
        
    print(f"✔ Deezer found! HWND: {parent_hwnd}")
    
    # Lister les enfants
    children = get_child_windows(parent_hwnd)
    print(f"Total child windows: {len(children)}")
    render_hwnd = None
    for hwnd, cname, title in children:
        print(f" - HWND: {hwnd} | Class: '{cname}' | Title: '{title}'")
        if cname == "Chrome_RenderWidgetHostHWND":
            render_hwnd = hwnd
            
    if render_hwnd:
        print(f"⭐ Found Chrome_RenderWidgetHostHWND: {render_hwnd}")
        
        # Envoyer WM_GETOBJECT avec OBJID_CLIENT (0xFFFFFFFC) ou 1
        # WM_GETOBJECT = 0x003D
        # OBJID_CLIENT = 0xFFFFFFFC
        print("⚡ Sending WM_GETOBJECT to trigger accessibility...")
        
        # Envoyer avec OBJID_CLIENT
        win32gui.SendMessage(render_hwnd, 0x003D, 0, 0xFFFFFFFC)
        time.sleep(1.0)
        
        # Vérifier si l'accessibilité s'est activée dans uiautomation
        try:
            import uiautomation as auto
            deezer_ctrl = auto.ControlFromHandle(parent_hwnd)
            print("🌳 Inspecting tree after WM_GETOBJECT:")
            for child in deezer_ctrl.GetChildren():
                print(f" - [{child.ControlTypeName}] Name: '{child.Name}'")
                if child.ControlTypeName == "DocumentControl":
                    print("🎉 SUCCESS! DocumentControl is visible!")
                    return
        except Exception as e:
            print(f"Error checking tree: {e}")
            
    else:
        print("❌ Chrome_RenderWidgetHostHWND child window not found.")

if __name__ == "__main__":
    main()
