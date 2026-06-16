import os
import urllib.request
import numpy as np

# Ajout manuel des répertoires DLL pour Windows (CUDA + cuDNN)
if os.name == 'nt':
    cuda_bin = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9\bin"
    cudnn_bin = r"C:\Program Files\NVIDIA\CUDNN\v9.23\bin\12.9\x64"
    if os.path.exists(cuda_bin):
        try: os.add_dll_directory(cuda_bin)
        except: pass
        os.environ["PATH"] = cuda_bin + os.pathsep + os.environ["PATH"]
    if os.path.exists(cudnn_bin):
        try: os.add_dll_directory(cudnn_bin)
        except: pass
        os.environ["PATH"] = cudnn_bin + os.pathsep + os.environ["PATH"]

import onnxruntime as ort
import sherpa_onnx

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CORE_DIR = os.path.join(_BASE_DIR, "core")

VAD_MODEL_PATH = os.path.join(_CORE_DIR, "silero_vad.onnx")
SPEAKER_MODEL_PATH = os.path.join(_CORE_DIR, "3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx")
VOICEPRINTS_DIR = os.path.join(_CORE_DIR, "voiceprints")

def init_models():
    """Télécharge automatiquement les modèles de VAD et de biométrie vocale s'ils sont absents."""
    os.makedirs(_CORE_DIR, exist_ok=True)
    
    # 1. Silero VAD (2 Mo)
    if not os.path.exists(VAD_MODEL_PATH):
        url_vad = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
        print("🎙  [VAD] Téléchargement du modèle Silero VAD (2 Mo)...")
        try:
            urllib.request.urlretrieve(url_vad, VAD_MODEL_PATH)
            print("✔  [VAD] Silero VAD téléchargé avec succès.")
        except Exception as e:
            print(f"❌  [VAD] Échec du téléchargement Silero VAD : {e}")
            
    # 2. CAM++ Speaker Recognition (23 Mo)
    if not os.path.exists(SPEAKER_MODEL_PATH):
        url_speaker = "https://huggingface.co/csukuangfj/speaker-embedding-models/resolve/main/3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx"
        print("🎙  [BIOMETRICS] Téléchargement du modèle de reconnaissance vocale (23 Mo)...")
        try:
            urllib.request.urlretrieve(url_speaker, SPEAKER_MODEL_PATH)
            print("✔  [BIOMETRICS] Modèle de reconnaissance vocale téléchargé avec succès.")
        except Exception as e:
            print(f"❌  [BIOMETRICS] Échec du téléchargement du modèle de reconnaissance vocale : {e}")


class SileroVAD:
    def __init__(self, model_path):
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        so = ort.SessionOptions()
        so.log_severity_level = 3
        
        self.session = ort.InferenceSession(model_path, providers=providers, sess_options=so)
        self.input_names = [i.name for i in self.session.get_inputs()]
        self.reset_states()
        
    def reset_states(self):
        if "state" in self.input_names:
            state_shape = [2, 1, 64]  # valeur par défaut
            for i in self.session.get_inputs():
                if i.name == "state":
                    state_shape = [s if isinstance(s, int) and s > 0 else 1 for s in i.shape]
                    break
            self._state = np.zeros(state_shape, dtype=np.float32)
        else:
            self._h = np.zeros((2, 1, 64), dtype=np.float32)
            self._c = np.zeros((2, 1, 64), dtype=np.float32)
        
    def __call__(self, audio_chunk_int16, sr=16000):
        # Normalisation float32 [-1.0, 1.0]
        audio_chunk = audio_chunk_int16.astype(np.float32) / 32768.0
        
        # Le modèle attend des sous-chunks de 512 échantillons.
        # Si la taille est différente, on la traite par blocs de 512.
        sub_chunk_size = 512
        probs = []
        
        for offset in range(0, len(audio_chunk), sub_chunk_size):
            sub_chunk = audio_chunk[offset:offset+sub_chunk_size]
            if len(sub_chunk) < sub_chunk_size:
                sub_chunk = np.pad(sub_chunk, (0, sub_chunk_size - len(sub_chunk)), 'constant')
                
            x = np.expand_dims(sub_chunk, axis=0)
            ort_inputs = {
                "input": x,
                "sr": np.array([sr], dtype=np.int64)
            }
            
            if "state" in self.input_names:
                ort_inputs["state"] = self._state
                out, state = self.session.run(None, ort_inputs)
                self._state = state
                probs.append(out[0][0])
            else:
                ort_inputs["h"] = self._h
                ort_inputs["c"] = self._c
                out, hn, cn = self.session.run(None, ort_inputs)
                self._h = hn
                self._c = cn
                probs.append(out[0][0])
                
        return max(probs) if probs else 0.0




class SpeakerBiometrics:
    def __init__(self, model_path, voiceprints_dir):
        self.model_path = model_path
        self.voiceprints_dir = voiceprints_dir
        os.makedirs(self.voiceprints_dir, exist_ok=True)
        
        config = sherpa_onnx.SpeakerEmbeddingExtractorConfig(
            model=self.model_path,
            num_threads=1,
            debug=False,
        )
        self.extractor = sherpa_onnx.SpeakerEmbeddingExtractor(config)
        
    def get_embedding(self, raw_audio_bytes, sample_rate=16000):
        samples = np.frombuffer(raw_audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        stream = self.extractor.create_stream()
        stream.accept_waveform(sample_rate=sample_rate, waveform=samples)
        stream.input_finished()
        
        if self.extractor.is_ready(stream):
            emb = self.extractor.compute(stream)
            return np.array(emb)
        return None
        
    def save_voiceprint(self, username, embedding):
        username_clean = username.lower().strip()
        user_dir = os.path.join(self.voiceprints_dir, username_clean)
        os.makedirs(user_dir, exist_ok=True)

        max_samples = 5
        chosen_file = None
        
        # Trouver un emplacement d'échantillon libre de 1 à 5
        for i in range(1, max_samples + 1):
            filepath = os.path.join(user_dir, f"sample_{i}.npy")
            if not os.path.exists(filepath):
                chosen_file = filepath
                break
                
        # S'ils sont tous pris, on écrase le plus ancien (basé sur le temps de modification)
        if not chosen_file:
            oldest_time = float('inf')
            oldest_file = None
            for i in range(1, max_samples + 1):
                filepath = os.path.join(user_dir, f"sample_{i}.npy")
                if os.path.exists(filepath):
                    mtime = os.path.getmtime(filepath)
                    if mtime < oldest_time:
                        oldest_time = mtime
                        oldest_file = filepath
            chosen_file = oldest_file or os.path.join(user_dir, "sample_1.npy")
            
        np.save(chosen_file, embedding)
        print(f"[BIOMETRICS] Empreinte sauvegardée dans : {chosen_file}")
        
    def load_voiceprints(self):
        import re
        import shutil
        voiceprints = {}
        if not os.path.exists(self.voiceprints_dir):
            return voiceprints

        # 1. Migration automatique des anciens fichiers en vrac de la racine vers leurs sous-dossiers respectifs
        for f in os.listdir(self.voiceprints_dir):
            fpath = os.path.join(self.voiceprints_dir, f)
            if os.path.isfile(fpath) and f.endswith(".npy"):
                raw_name = f[:-4]
                # Identifier le nom de profil en retirant le suffixe de numéro (ex: mylane ou mylane_1)
                name = re.sub(r'_\d+$', '', raw_name).lower()
                
                # Détecter l'index
                match = re.search(r'_(\d+)$', raw_name)
                index = match.group(1) if match else "1"
                
                # Créer le sous-dossier et déplacer le fichier
                user_dir = os.path.join(self.voiceprints_dir, name)
                os.makedirs(user_dir, exist_ok=True)
                new_fpath = os.path.join(user_dir, f"sample_{index}.npy")
                
                try:
                    shutil.move(fpath, new_fpath)
                    print(f"[BIOMETRICS] Migration : {f} déplacé vers {name}/sample_{index}.npy")
                except Exception as me:
                    print(f"[BIOMETRICS] Échec de la migration de {f} : {me}")
        
        # 2. Chargement depuis les sous-dossiers par profil
        for entry in os.listdir(self.voiceprints_dir):
            dir_path = os.path.join(self.voiceprints_dir, entry)
            if os.path.isdir(dir_path):
                username = entry.lower()
                for f in os.listdir(dir_path):
                    if f.endswith(".npy"):
                        try:
                            emb = np.load(os.path.join(dir_path, f))
                            if username not in voiceprints:
                                voiceprints[username] = []
                            voiceprints[username].append(emb)
                        except Exception:
                            pass
        return voiceprints
        
    def identify_speaker(self, raw_audio_bytes, sample_rate=16000, threshold=0.60):
        emb = self.get_embedding(raw_audio_bytes, sample_rate)
        if emb is None:
            return "guest", 0.0
            
        voiceprints = self.load_voiceprints()
        if not voiceprints:
            return "guest", 0.0
            
        best_name = "guest"
        best_score = 0.0
        
        # Normalisation du vecteur d'entrée
        emb_norm = emb / (np.linalg.norm(emb) + 1e-8)
        
        for name, emb_list in voiceprints.items():
            for ref_emb in emb_list:
                ref_norm = ref_emb / (np.linalg.norm(ref_emb) + 1e-8)
                score = float(np.dot(emb_norm, ref_norm))
                if score > best_score:
                    best_score = score
                    best_name = name
                
        if best_score >= threshold:
            return best_name, best_score
        return "guest", best_score
