import sys
import os
import time
import win32gui
import win32process
import psutil

def get_pids_slow():
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                deezer_pids.append(proc.info['pid'])
        except:
            pass
    return deezer_pids

def get_pids_fast():
    deezer_pids = []
    def enum_pids(hwnd, extra):
        try:
            classname = win32gui.GetClassName(hwnd)
            if "Chrome_WidgetWin" in classname:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid not in deezer_pids:
                    try:
                        proc = psutil.Process(pid)
                        if 'deezer' in proc.name().lower():
                            deezer_pids.append(pid)
                    except:
                        pass
        except:
            pass
        return True
    win32gui.EnumWindows(enum_pids, None)
    return deezer_pids

def main():
    print("Benchmarking PID retrieval methods...")
    
    # Run slow method
    t0 = time.time()
    for _ in range(10):
        pids_slow = get_pids_slow()
    t_slow = (time.time() - t0) / 10.0
    print(f"Slow method (psutil.process_iter): {t_slow:.4f} seconds (found PIDs: {pids_slow})")
    
    # Run fast method
    t0 = time.time()
    for _ in range(10):
        pids_fast = get_pids_fast()
    t_fast = (time.time() - t0) / 10.0
    print(f"Fast method (EnumWindows + psutil.Process): {t_fast:.4f} seconds (found PIDs: {pids_fast})")
    
    speedup = t_slow / t_fast if t_fast > 0 else 0
    print(f"Speedup factor: {speedup:.2f}x")

if __name__ == "__main__":
    main()
