import subprocess
import time
import ctypes
import os
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

def capture_deezer():
    track_id = 66609426
    uri = f"deezer://www.deezer.com/track/{track_id}"
    
    print(f"🚀 Lancement de l'URI : {uri}")
    subprocess.Popen(["explorer", uri], shell=False)
    
    print("⏳ Attente de 6 secondes pour le chargement...")
    time.sleep(6)
    
    print("🎯 Focus de la fenêtre Deezer...")
    focus_window_by_title("Deezer")
    
    if pyautogui:
        print("📸 Capture d'écran...")
        dest_dir = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, "deezer_screenshot.png")
        
        screenshot = pyautogui.screenshot()
        screenshot.save(dest_path)
        print(f"✔ Capture d'écran sauvegardée sous : {dest_path}")
    else:
        print("❌ pyautogui indisponible pour faire la capture.")

if __name__ == "__main__":
    capture_deezer()
