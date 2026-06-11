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

async def capture_thinking_packet():
    uri = "ws://localhost:8765"
    print("Connexion au WebSocket...", flush=True)
    try:
        async with websockets.connect(uri) as websocket:
            print("Connexion établie! Envoi du payload...", flush=True)
            # Envoyer la question
            payload = {
                "type": "mobile_command",
                "text": "Que penses-tu de l'intelligence artificielle ?"
            }
            await websocket.send(json.dumps(payload))
            print("Payload envoyé. Attente des messages...", flush=True)
            
            # Écouter 5 paquets
            count = 0
            while count < 6:
                packet = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(packet)
                if data.get("state") or data.get("status_text"):
                    print(f"[RECU SPECIFIQUE] : {json.dumps(data)}", flush=True)
                    count += 1
            return
    except Exception as e:
        print(f"Erreur : {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(capture_thinking_packet())
