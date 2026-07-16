import re
import sys

def search_frontend():
    sys.stdout.reconfigure(errors="replace")
    
    keywords = ["vpn", "obsidian", "restaurant", "secure_browser", "browser", "deezer", "spotify", "youtube", "rap"]
    
    files = [
        r"N:\JARVIS8.5\frontend\index.html",
        r"N:\JARVIS8.5\frontend\src\main.ts"
    ]
    
    for filepath in files:
        print(f"\n==================================================")
        print(f"SEARCHING IN: {filepath}")
        print(f"==================================================")
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        lines = content.splitlines()
        
        for kw in keywords:
            matches = list(re.finditer(r'\b' + re.escape(kw) + r'\b', content, re.IGNORECASE))
            if matches:
                print(f"Keyword: {kw.upper()} ({len(matches)} matches)")
                found = 0
                for m in matches:
                    char_idx = m.start()
                    line_num = content[:char_idx].count('\n') + 1
                    line_content = lines[line_num - 1].strip()[:135]
                    print(f"  Line {line_num:4d}: {line_content}")
                    found += 1
                    if found >= 12:
                        print("  ... (truncated)")
                        break
                print()

if __name__ == "__main__":
    search_frontend()
