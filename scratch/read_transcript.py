import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec\.system_generated\logs\transcript.jsonl"
found = []
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        step = json.loads(line)
        content = str(step.get('content', ''))
        if "Erreur fetch" in content or "Tentative de repli" in content:
            found.append(step)

print(f"Found {len(found)} matching steps.")
for step in found[10:30]:
    print(f"Step {step.get('step_index')} (Source: {step.get('source')}, Type: {step.get('type')})")
    print(f"Content: {step.get('content')[:500]}...")
    print("-" * 40)

