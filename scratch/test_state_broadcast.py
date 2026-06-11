import asyncio
import websockets
import json
import sys

# UTF-8 Console output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

async def capture_packets():
    uri = "ws://localhost:8765"
    print(f"Connexion au WebSocket : {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            # Envoyer la question
            payload = {
                "type": "mobile_command",
                "text": "Salut Jarvis, comment ça va ?"
            }
            await websocket.send(json.dumps(payload))
            print("Message envoyé. Capture des paquets pendant 5 secondes...")
            
            # Écouter les paquets pendant 5 secondes
            try:
                while True:
                    packet = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(packet)
                    # Afficher uniquement les paquets liés au statut, texte ou cartes
                    if "state" in data or "status_text" in data or "action" in data:
                        safe_str = json.dumps(data, ensure_ascii=True)
                        print(f"[PAQUET DEBOGAGE] : {safe_str}")
            except asyncio.TimeoutError:
                print("Capture terminée.")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    asyncio.run(capture_packets())
