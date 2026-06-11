import asyncio
import websockets
import json
import sys

# Force output to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

async def send_and_wait(command_text):
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
            
            print("Envoi réussi. En attente de la réponse de JARVIS...")
            
            # Attendre spécifiquement la réponse textuelle
            found_response = False
            try:
                while not found_response:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data = json.loads(response)
                    action = data.get("action")
                    
                    if action == "jarvis_text":
                        print(f"\n[JARVIS PARLE] : {data.get('text')}\n")
                        found_response = True
                    elif action == "ctx_card":
                        print(f"\n[CARTE HUD] {data.get('title')} : {data.get('text')} [{data.get('type')}]\n")
                    elif action == "os_agent_status":
                        print(f"\n[HUD STATUS] Active: {data.get('active')} | Log: {data.get('log')}\n")
                        if not data.get("active") and "termi" in data.get("log", "").lower():
                            # Fin de l'autopilote
                            found_response = True
            except asyncio.TimeoutError:
                print("Délai d'attente dépassé (15 secondes).")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
    else:
        cmd = "Salut Jarvis, comment ça va aujourd'hui ?"
    asyncio.run(send_and_wait(cmd))
