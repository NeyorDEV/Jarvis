import asyncio
import subprocess
import time
import sys
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

sys.stdout.reconfigure(encoding='utf-8')

async def test_winsdk_play():
    track_id = 66609426
    uri = f"deezer://www.deezer.com/track/{track_id}"
    
    print(f"🚀 Lancement de l'URI : {uri}")
    subprocess.Popen(["explorer", uri], shell=False)
    
    print("⏳ Attente de 6 secondes pour le chargement...")
    await asyncio.sleep(6)
    
    print("🔎 Requête du gestionnaire de sessions média de Windows...")
    manager = await MediaManager.request_async()
    
    # Récupérer toutes les sessions actives pour voir ce qui est détecté
    sessions = manager.get_sessions()
    print(f"Nombre de sessions média actives détectées par Windows : {len(sessions)}")
    
    deezer_session = None
    for session in sessions:
        source_id = session.source_app_user_model_id
        print(f" - Session détectée : '{source_id}'")
        if "deezer" in source_id.lower():
            deezer_session = session
            
    # Si on ne trouve pas de session explicite Deezer, on prend la session active par défaut
    if not deezer_session:
        deezer_session = manager.get_current_session()
        if deezer_session:
            print(f"🎯 Utilisation de la session active par défaut : '{deezer_session.source_app_user_model_id}'")
            
    if deezer_session:
        print(f"🔊 Envoi de la commande native 'PLAY' à la session : '{deezer_session.source_app_user_model_id}'")
        
        # Récupérer les propriétés avant play pour info
        try:
            props = await deezer_session.try_get_media_properties_async()
            print(f"   [Avant Play] Titre : {props.title} | Artiste : {props.artist}")
        except Exception as e:
            print(f"   Impossible de lire les propriétés : {e}")
            
        # Tenter de lancer la lecture
        success = await deezer_session.try_play_async()
        print(f"✔ Résultat de try_play_async() : {success}")
        
        print("⏳ Attente de 4 secondes...")
        await asyncio.sleep(4)
        
        # Récupérer les propriétés après play
        try:
            props = await deezer_session.try_get_media_properties_async()
            timeline = deezer_session.get_timeline_properties()
            playback_info = deezer_session.get_playback_info()
            
            print(f"\n--- ÉTAT DE LA LECTURE ---")
            print(f"Titre : {props.title}")
            print(f"Artiste : {props.artist}")
            print(f"Status : {playback_info.playback_status.name}")
            if timeline:
                print(f"Position : {timeline.position.total_seconds()}s / {timeline.end_time.total_seconds()}s")
        except Exception as e:
            print(f"Erreur lors de la lecture des états : {e}")
    else:
        print("❌ Aucune session média active trouvée. Deezer n'est probablement pas enregistré auprès de Windows.")

if __name__ == "__main__":
    asyncio.run(test_winsdk_play())
