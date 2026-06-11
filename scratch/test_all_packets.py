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

async def capture_all():
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
            print("Payload envoyé. Attente de tous les paquets...", flush=True)
            
            # Écouter pendant 8 secondes et tout imprimer
            try:
                while True:
                    packet = await asyncio.wait_for(websocket.recv(), timeout=8.0)
                    data = json.loads(packet)
                    print(f"[RECU RAPPORT] : {json.dumps(data)}", flush=True)
            except asyncio.TimeoutError:
                print("Fin de capture (timeout de 8s).", flush=True)
    except Exception as e:
        print(f"Erreur : {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(capture_all())
