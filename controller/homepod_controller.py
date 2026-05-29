import asyncio
import pyatv
import os
from typing import Optional

# Configuration du HomePod
# Vous pouvez spécifier l'IP pour aller plus vite, sinon JARVIS le cherchera sur le réseau.
HOMEPOD_IP = os.getenv("HOMEPOD_IP", None)

async def find_homepod(identifier: Optional[str] = None):
    """Recherche un HomePod sur le réseau local."""
    print("[HOMEPOD] Recherche du HomePod sur le réseau...")
    discovered = await pyatv.scan(asyncio.get_event_loop(), timeout=5)
    
    for device in discovered:
        # On cherche un HomePod (souvent identifié comme tel ou par son nom)
        if identifier:
            if identifier.lower() in device.name.lower() or identifier == device.address:
                return device
        else:
            # Par défaut, on prend le premier HomePod trouvé
            return device
            
    return None

async def send_command(command: str, value: Optional[float] = None):
    """Envoie une commande au HomePod (play, pause, stop, volume)."""
    try:
        # Découverte ou utilisation de l'IP
        if HOMEPOD_IP:
            # On tente une connexion directe (plus rapide)
            # Note: pyatv.connect a besoin d'une configuration, le scan est plus sûr au début
            device = await find_homepod(HOMEPOD_IP)
        else:
            device = await find_homepod()

        if not device:
            print("[HOMEPOD] Aucun HomePod trouvé.")
            return False, "Aucun HomePod trouvé sur le réseau."

        print(f"[HOMEPOD] Connexion à {device.name} ({device.address})...")
        atv = await pyatv.connect(device, asyncio.get_event_loop())
        
        try:
            if command == "play":
                await atv.control.play()
            elif command == "pause":
                await atv.control.pause()
            elif command == "stop":
                await atv.control.stop()
            elif command == "next":
                await atv.control.next()
            elif command == "previous":
                await atv.control.previous()
            elif command == "volume" and value is not None:
                # pyatv utilise une échelle de 0 à 100 pour le volume
                await atv.audio.set_volume(value)
            
            return True, f"Commande {command} envoyée avec succès."
        finally:
            await asyncio.gather(*atv.close())
            
    except Exception as e:
        print(f"[HOMEPOD ERROR] {e}")
        return False, str(e)

if __name__ == "__main__":
    # Petit test de scan
    async def test():
        device = await find_homepod()
        if device:
            print(f"Trouvé : {device.name} à l'adresse {device.address}")
        else:
            print("Rien trouvé.")
            
    asyncio.run(test())
