import subprocess
import time
import psutil

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

print("Launching Deezer...")
proc = subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility"], cwd=DEEZER_DIR, shell=False)

print("Waiting 10 seconds...")
time.sleep(10)

# Check processes
for p in psutil.process_iter(['pid', 'name']):
    if p.info['name'] and 'deezer' in p.info['name'].lower():
        print(f"Running: {p.info}")
