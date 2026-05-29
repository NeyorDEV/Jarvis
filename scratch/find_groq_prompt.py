file_path = r"n:\JARVIS\main2.py"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    lower_line = line.lower()
    if "groq" in lower_line or "grok" in lower_line or "llama" in lower_line:
        results.append(f"{i+1}: {line.strip()}")

with open(r"n:\JARVIS\scratch\groq_found.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("SUCCESS: Groq search completed!")
