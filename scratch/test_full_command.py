import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main2 import resoudre_commandes_locales

async def main():
    import main2
    async def mock_deezer_rechercher(query):
        return f"MOCKED DEEZER SEARCH FOR: '{query}'"
    main2.deezer_rechercher = mock_deezer_rechercher
    
    cmd1 = "joue ma playlist"
    print(f"Testing command: '{cmd1}'")
    res1 = await resoudre_commandes_locales(cmd1)
    print(f"Result: {res1}")
    
    cmd2 = "joue ma playlist teenage dirtbag"
    print(f"\nTesting command: '{cmd2}'")
    res2 = await resoudre_commandes_locales(cmd2)
    print(f"Result: {res2}")

asyncio.run(main())
