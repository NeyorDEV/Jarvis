import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from plugins.app_launcher_resolver import resoudre_apps_localement

async def main():
    # Test cases
    test_cases = [
        "joue ma playlist",
        "joue ma playlist teenage dirtbag",
        "mets de la musique",
        "mets la playlist teenage dirtbag",
        "lance ma playlist rock",
        "lance la musique"
    ]
    
    print("=== Testing local resolver for playlists ===")
    for cmd in test_cases:
        res = await resoudre_apps_localement(cmd)
        print(f"Command: '{cmd}' -> Resolved output: {res}")

asyncio.run(main())
