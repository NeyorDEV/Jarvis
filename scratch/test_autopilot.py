import asyncio
import websockets
import json
import sys

# Forcer stdout en UTF-8 pour éviter les crashs d'encodage sur Windows cmd
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

async def send_command(command_text):
    uri = "ws://localhost:8765"
    print(f"Connexion au WebSocket : {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            payload = {
                "type": "mobile_command",
                "text": command_text
            }
            print(f"Envoi du payload : {payload}")
            await websocket.send(json.dumps(payload))
            
            print("Envoi réussi. En attente de réponses éventuelles pendant 10 secondes...")
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    # Impression sécurisée pour éviter les crashs d'encodage Windows
                    safe_data_str = json.dumps(data, ensure_ascii=True)
                    print(f"[RECU FROM WEBSOCKET] {safe_data_str}")
            except asyncio.TimeoutError:
                print("Fin de l'attente (timeout de 10s expiré).")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    cmd = "Jarvis, active le mode local"
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
    asyncio.run(send_command(cmd))
