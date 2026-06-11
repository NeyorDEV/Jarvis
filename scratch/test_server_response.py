import asyncio
import websockets
import json
import sys

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

async def debug_query():
    uri = "ws://localhost:8765"
    print("Connexion au WebSocket...", flush=True)
    try:
        async with websockets.connect(uri) as websocket:
            print("Connexion établie! Envoi du payload...", flush=True)
            payload = {
                "type": "mobile_command",
                "text": "Que penses-tu de l'intelligence artificielle ?"
            }
            await websocket.send(json.dumps(payload))
            print("Payload envoyé. Attente des paquets...", flush=True)
            
            # Écouter pendant 10 secondes
            try:
                while True:
                    packet = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(packet)
                    print(f"[PAQUET] : {json.dumps(data)}", flush=True)
            except asyncio.TimeoutError:
                print("Fin de capture (timeout).", flush=True)
    except Exception as e:
        print(f"Erreur : {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(debug_query())
