import psutil
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("--- Running Deezer.exe process command lines ---")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            print(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Cmd: {proc.info['cmdline']}")
    except Exception as e:
        print(f"Error reading PID {proc.pid}: {e}")
