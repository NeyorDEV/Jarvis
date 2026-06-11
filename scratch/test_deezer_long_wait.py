import subprocess
import time
import ctypes
import sys
try:
    import pyautogui
except ImportError:
    pyautogui = None

sys.stdout.reconfigure(encoding='utf-8')

def get_windows_titles_with_hwnd():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    
    windows = []
    def foreach_window(hwnd, lParam):
        length = GetWindowTextLength(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            windows.append((hwnd, buff.value))
        return True
        
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return windows

def focus_window_by_title(title_query):
    import win32gui, win32con
    for hwnd, title in get_windows_titles_with_hwnd():
        if title_query.lower() in title.lower():
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                return True
            except Exception as e:
                pass
    return False

def test_long_wait():
    track_id = 66609426
    uri = f"deezer://www.deezer.com/track/{track_id}"
    
    print(f"🚀 Lancement de l'URI : {uri}")
    subprocess.Popen(["explorer", uri], shell=False)
    
    print("⏳ Attente de 12 secondes pour un chargement complet de l'application...")
    time.sleep(12)
    
    print("🎯 Focus de la fenêtre Deezer...")
    focused = focus_window_by_title("Deezer")
    if not focused:
        print("❌ Impossible de trouver et focus la fenêtre Deezer.")
        return
        
    if pyautogui:
        print("⌨ Envoi de la touche 'space'...")
        pyautogui.press('space')
        time.sleep(3)
        
        print("\n--- FENÊTRES APRÈS ESPACE ---")
        after = [t for hwnd, t in get_windows_titles_with_hwnd() if "deezer" in t.lower()]
        print(after)
        
        print("⌨ Envoi de la touche 'enter' en fallback...")
        pyautogui.press('enter')
        time.sleep(3)
        
        after2 = [t for hwnd, t in get_windows_titles_with_hwnd() if "deezer" in t.lower()]
        print("Après ENTRÉE :", after2)
        
    else:
        print("❌ pyautogui non disponible.")

if __name__ == "__main__":
    test_long_wait()
