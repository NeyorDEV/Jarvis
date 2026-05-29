file_path = r"n:\JARVIS\main2.py"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "port" in line.lower() or "server" in line.lower() or "ws_url" in line.lower() or "8000" in line or "8765" in line:
        print(f"{i+1}: {line.strip()}")
