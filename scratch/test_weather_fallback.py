import sys
import os
import asyncio
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main2 import get_raw_weather

async def main():
    print("Testing get_raw_weather for Monistrol-sur-Loire...")
    t0 = time.time()
    res = await get_raw_weather(45.2933, 4.1728, "Monistrol-sur-Loire")
    elapsed = time.time() - t0
    print(f"\nExecution time: {elapsed:.2f}s")
    if res:
        print("🎉 Success! Weather data returned:")
        import json
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("❌ Failed to get weather data.")

asyncio.run(main())
