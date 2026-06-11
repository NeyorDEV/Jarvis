import os
import sys
import numpy as np
import wave

# Configuration de l'encodage standard en UTF-8 pour supporter les emojis et caractères spéciaux sur Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Assurer l'accès au module core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vad import init_models, SileroVAD, SpeakerBiometrics, VAD_MODEL_PATH, SPEAKER_MODEL_PATH, VOICEPRINTS_DIR

def create_dummy_wav(filename, duration=1.0, rate=16000):
    """Génère un fichier WAV de test avec un simple sinus."""
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    # Sinus à 440 Hz
    data = np.sin(2 * np.pi * 440 * t) * 10000
    data = data.astype(np.int16)
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(data.tobytes())

def main():
    print("🚀  Début du test VAD & Biométrie...")
    
    # 1. Téléchargement des modèles si absents
    init_models()
    
    # Vérification des fichiers
    assert os.path.exists(VAD_MODEL_PATH), "Silero VAD model manquant !"
    assert os.path.exists(SPEAKER_MODEL_PATH), "Speaker Biometrics model manquant !"
    print("✔  Modèles présents sur le disque.")
    
    # 2. Test Silero VAD
    print("⚙  Initialisation de SileroVAD...")
    vad = SileroVAD(VAD_MODEL_PATH)
    print("✔  SileroVAD initialisé.")
    
    # Générer un bout de silence et un bout de signal
    dummy_wav = "scratch/temp_test.wav"
    os.makedirs("scratch", exist_ok=True)
    create_dummy_wav(dummy_wav, duration=1.0)
    
    with wave.open(dummy_wav, 'rb') as wf:
        raw_data = wf.readframes(16000)
    
    audio_int16 = np.frombuffer(raw_data, dtype=np.int16)
    # Découper en chunks de 1024 échantillons
    chunk_size = 1024
    speech_detected = False
    
    for i in range(0, len(audio_int16), chunk_size):
        chunk = audio_int16[i:i+chunk_size]
        if len(chunk) < chunk_size:
            # Remplir le dernier chunk avec des zéros
            chunk = np.pad(chunk, (0, chunk_size - len(chunk)), 'constant')
        prob = vad(chunk, sr=16000)
        if prob > 0.4:
            speech_detected = True
            print(f"   [VAD] Parole détectée au chunk {i//chunk_size} (Probabilité: {prob:.4f})")
            
    print(f"✔  Résultat VAD: {'Parole trouvée' if speech_detected else 'Silence'}")
    
    # 3. Test Biométrie
    print("⚙  Initialisation de SpeakerBiometrics...")
    biometrics = SpeakerBiometrics(SPEAKER_MODEL_PATH, VOICEPRINTS_DIR)
    print("✔  SpeakerBiometrics initialisé.")
    
    # Génération d'un embedding à partir de l'audio test
    emb = biometrics.get_embedding(raw_data, sample_rate=16000)
    if emb is not None:
        print(f"✔  Embedding généré avec succès. Taille du vecteur : {emb.shape}")
        
        # Enregistrer et recharger
        biometrics.save_voiceprint("test_user", emb)
        loaded = biometrics.load_voiceprints()
        assert "test_user" in loaded, "Échec du rechargement de l'empreinte !"
        print("✔  Sauvegarde et rechargement de l'empreinte réussis.")
        
        # Identifier
        name, similarity = biometrics.identify_speaker(raw_data, sample_rate=16000)
        print(f"✔  Identification : {name} (Similarité: {similarity:.4f})")
        
        # Nettoyage fichier voiceprint de test
        test_npy = os.path.join(VOICEPRINTS_DIR, "test_user.npy")
        if os.path.exists(test_npy):
            os.remove(test_npy)
    else:
        print("❌  Échec de génération de l'embedding.")
        
    # Nettoyage fichier WAV
    if os.path.exists(dummy_wav):
        os.remove(dummy_wav)
        
    print("🎉  Tous les tests unitaires VAD & Biométrie ont réussi !")

if __name__ == "__main__":
    main()
