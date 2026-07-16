import os
import re
import sys

def search_specific():
    base_dir = r"N:\JARVIS8.5"
    keywords = ["obsidian", "vpn", "restaurant", "secure_browser", "deezer"]
    
    sys.stdout.reconfigure(errors="replace")
    print(f"Scanning all python files in {base_dir} for specific keywords...\n")
    
    py_files = []
    for root, dirs, files in os.walk(base_dir):
        if "venv" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
                
    for kw in keywords:
        print(f"==================================================")
        print(f"KEYWORD: {kw.upper()}")
        print(f"==================================================")
        found_total = 0
        for filepath in py_files:
            filename = os.path.basename(filepath)
            if filename in ["search_all.py", "compare_versions.py", "search_main2.py"]:
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                matches = list(re.finditer(r'\b' + re.escape(kw) + r'\b', content, re.IGNORECASE))
                if matches:
                    print(f"\nFile: {os.path.relpath(filepath, base_dir)}")
                    lines = content.splitlines()
                    found_in_file = 0
                    for m in matches:
                        char_idx = m.start()
                        line_num = content[:char_idx].count('\n') + 1
                        line_content = lines[line_num - 1].strip()[:130]
                        print(f"  Line {line_num:4d}: {line_content}")
                        found_in_file += 1
                        found_total += 1
                        if found_in_file >= 15:
                            print("  ... (more matches)")
                            break
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
        if found_total == 0:
            print("(none)")
        print()

if __name__ == "__main__":
    search_specific()
