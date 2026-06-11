import subprocess
import time
import ctypes
import os
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

def test_direct_url():
    exe_path = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
    url = "https://www.deezer.com/track/66609426"
    
    print(f"🚀 Lancement direct avec URL standard : {exe_path} {url}")
    subprocess.Popen([exe_path, url], shell=False)
    
    print("⏳ Attente de 10 secondes...")
    time.sleep(10)
    
    print("\n--- TOUS LES TITRES DE FENÊTRES CONCERNÉS ---")
    titles = get_windows_titles()
    deezer_titles = [t for t in titles if "deezer" in t.lower() or "get lucky" in t.lower() or "daft punk" in t.lower()]
    print(deezer_titles)
    
if __name__ == "__main__":
    test_direct_url()
