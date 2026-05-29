import re

with open("n:\\JARVIS\\main2.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

search_words = ["Client", "genai", "system_instruction", "time.strftime", "datetime", "modelflash"]
for i, line in enumerate(lines):
    for word in search_words:
        if word.lower() in line.lower():
            print(f"Line {i+1}: {line.strip()}")
            break
