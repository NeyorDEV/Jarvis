import psutil
import subprocess
import time
import win32gui
import win32process
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def kill_deezer():
    print("Killing all Deezer processes...")
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                proc.kill()
        except:
            pass
    time.sleep(2)

def get_running_deezer_exe():
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                exe = proc.info['exe']
                if exe and os.path.exists(exe):
                    return exe
        except:
            pass
    return None

def get_deezer_windows():
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                deezer_pids.append(proc.info['pid'])
        except:
            pass
            
    windows = []
    def _cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in deezer_pids:
                title = win32gui.GetWindowText(hwnd)
                classname = win32gui.GetClassName(hwnd)
                windows.append((hwnd, pid, title, classname))
        return True
    win32gui.EnumWindows(_cb, None)
    return windows

# 1. Reset
kill_deezer()

# 2. Launch default protocol handler (UWP version)
print("Launching Deezer via explorer...")
subprocess.Popen(["explorer", "deezer://"], shell=False)
time.sleep(6)

# 3. Get running EXE and windows
running_exe = get_running_deezer_exe()
print(f"Running Executable: {running_exe}")
wins_before = get_deezer_windows()
print("Windows BEFORE:")
for w in wins_before:
    print(f"  HWND: {w[0]} | PID: {w[1]} | Title: '{w[2]}' | Class: {w[3]}")

if running_exe:
    # 4. Launch URI using the running exe
    uri = "deezer://track/3045111091"
    print(f"Launching URI '{uri}' using {running_exe}...")
    subprocess.Popen([running_exe, uri], shell=False)
    time.sleep(4)
    
    # 5. Check windows again
    wins_after = get_deezer_windows()
    print("Windows AFTER:")
    for w in wins_after:
        print(f"  HWND: {w[0]} | PID: {w[1]} | Title: '{w[2]}' | Class: {w[3]}")
        
    print(f"Window count before: {len(wins_before)} | after: {len(wins_after)}")
else:
    print("Failed to detect running Deezer process.")
