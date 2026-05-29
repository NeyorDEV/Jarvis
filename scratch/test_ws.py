import asyncio
import websockets
import json

async def send_test():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connecté au serveur JARVIS!")
            
            # Message pour écrire "test" dans la barre de recherche YouTube
            msg = {
                "type": "dom_action",
                "action": "type",
                "selector": "input[name='search_query'], input#search",
                "text": "test manuel"
            }
            await websocket.send(json.dumps(msg))
            print("Message envoyé au serveur (qui va le broadcaster).")
            
    except Exception as e:
        print(f"Erreur: {e}")

asyncio.run(send_test())
