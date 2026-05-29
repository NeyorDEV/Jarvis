file_path = r"n:\JARVIS\main2.py"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "def construire_system_prompt" in line:
        start_line = max(1, i - 2)
        end_line = min(len(lines), i + 200)
        for j in range(start_line, end_line):
            results.append(f"{j+1}: {lines[j].strip()}")
        break

with open(r"n:\JARVIS\scratch\system_prompt.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("SUCCESS: system prompt found!")
