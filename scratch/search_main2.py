import re
import sys

def search_main_restaurant():
    sys.stdout.reconfigure(errors="replace")
    filepath = r"N:\JARVIS8.5\main2.py"
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    print("=== MATCHES FOR 'restaurant' IN main2.py ===")
    for i, line in enumerate(lines, 1):
        if "restaurant" in line.lower():
            print(f"Line {i:4d}: {line.strip()[:140]}")

if __name__ == "__main__":
    search_main_restaurant()
