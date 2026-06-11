import subprocess
import time
import ctypes
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_windows_titles():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    
    titles = []
    def foreach_window(hwnd, lParam):
        length = GetWindowTextLength(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True
        
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return titles

def test_legacy():
    track_id = 66609426
    uri = f"deezer://track/{track_id}"
    
    print(f"🚀 Lancement de l'URI legacy : {uri}")
    subprocess.Popen(["explorer", uri], shell=False)
    
    print("⏳ Attente de 10 secondes...")
    time.sleep(10)
    
    after = [t for t in get_windows_titles() if "deezer" in t.lower() or "get lucky" in t.lower() or "daft punk" in t.lower()]
    print("\n--- ÉTAT DES FENÊTRES APRÈS LANCEMENT ---")
    print(after)

if __name__ == "__main__":
    test_legacy()
