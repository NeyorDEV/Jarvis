import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
lines = open('main2.py', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    if 'websocket' in l.lower() or 'async def' in l or '"action"' in l or "'action'" in l:
        print(f'{i}: {l.rstrip()}')
