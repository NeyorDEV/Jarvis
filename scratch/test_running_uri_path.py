import psutil
import subprocess
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

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

running_exe = get_running_deezer_exe()
print(f"Running Deezer Executable Path: {running_exe}")

if running_exe:
    uri = "deezer://track/3045111091" # Michael Jackson track
    print(f"Launching: {running_exe} {uri}")
    subprocess.Popen([running_exe, uri], shell=False)
    print("Launched successfully.")
else:
    print("Deezer is not running, launch it manually first.")
