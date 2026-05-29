with open("n:\\JARVIS\\main2.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

search_words = ["prompt_actuel", "system_prompt", "consignes", "system_instruction"]
for i, line in enumerate(lines):
    for word in search_words:
        if word.lower() in line.lower():
            if "def " in line or "=" in line:
                print(f"Line {i+1}: {line.strip()}")
            break
