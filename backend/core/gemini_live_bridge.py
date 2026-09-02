import os
import sys
import json
import builtins
import asyncio
import base64
import google.genai as genai
from google.genai import types
from core.config import GEMINI_API_KEY
class GeminiLiveBridge:
    """
    Pont bi-directionnel full-duplex entre le navigateur (WebAudio/WebSocket)
    et l'API Gemini 2.0 Multimodal Live.
    """
    def __init__(self):
        # Construction paresseuse : genai.Client(api_key="") lève immédiatement
        # si la clé est vide/absente. Comme cette classe est instanciée au niveau
        # module (ligne finale du fichier), une clé manquante aurait fait planter
        # l'IMPORT — donc potentiellement tout le démarrage de JARVIS — avant même
        # qu'on essaie d'utiliser la fonctionnalité Gemini Live.
        self.client = None
        self.active_session = None
        self.is_connected = False
        self.current_ws_client = None

    def _client_pret(self):
        if self.client is not None:
            return True
        if not GEMINI_API_KEY:
            print("[GEMINI LIVE] Clé Gemini absente : fonctionnalité indisponible.")
            return False
        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            return True
        except Exception as e:
            print(f"[GEMINI LIVE] Impossible d'initialiser le client Gemini : {e}")
            return False

    async def demarrer_session(self, ws_client):
        """Initialise la connexion WebSocket bi-directionnelle avec Gemini Live."""
        if not self._client_pret():
            return
        self.current_ws_client = ws_client
        self.is_connected = True
        print("[GEMINI LIVE] Démarrage de la session Live bi-directionnelle...")
        # Configuration de la session Live avec voix native et réponses audio PCM
        config = types.LiveConnectConfig(
            # Le SDK installé (google-genai 1.75.0) n'expose pas
            # `LiveResponseModality` — ce nom n'a probablement jamais existé dans
            # une version publiée, ou provient d'une doc/version différente.
            # Le bon type est `types.Modality`.
            response_modalities=[types.Modality.AUDIO],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            )
        )
        try:
            # « gemini-2.0-flash-exp » n'existe plus au catalogue (vérifié via
            # client.models.list() — même sort que le modèle Groq retiré ce jour).
            # « -latest » suit automatiquement la dernière version stable côté
            # Google, évitant que ce nom précis ne se périme à nouveau.
            async with self.client.aio.live.connect(model="gemini-2.5-flash-native-audio-latest", config=config) as session:
                self.active_session = session
                print("[GEMINI LIVE] Connecté avec succès à Gemini 2.0 Flash Live API !")
                                # Écoute continue des réponses entrantes de Gemini
                async for response in session.receive():
                    if not self.is_connected:
                        break
                    server_content = getattr(response, "server_content", None)
                    if server_content and server_content.model_turn:
                        for part in server_content.model_turn.parts:
                            if hasattr(part, "inline_data") and part.inline_data:
                                pcm_bytes = part.inline_data.data
                                b64_audio = base64.b64encode(pcm_bytes).decode("utf-8")
                                
                                # Relayer le flux audio PCM 24kHz au navigateur pour lecture instantanée
                                if self.current_ws_client:
                                    msg = json.dumps({
                                        "action": "live_audio_output",
                                        "pcm_base64": b64_audio,
                                        "sample_rate": 24000
                                    })
                                    await self.current_ws_client.send(msg)
                    # Gestion des Function Calls (Outils émis par Gemini)
                    tool_call = getattr(response, "tool_call", None)
                    if tool_call:
                        await self.traiter_tool_call(tool_call, session)
        except Exception as e:
            print(f"[GEMINI LIVE ERROR] Erreur session Live : {e}")
        finally:
            self.is_connected = False
            self.active_session = None
            print("[GEMINI LIVE] Session Live terminée.")
    async def envoyer_audio_chunk(self, pcm_base64: str):
        """Reçoit un morceau d'audio PCM 16kHz du navigateur et l'envoie à Gemini Live."""
        if not self.active_session or not self.is_connected:
            return
        try:
            raw_pcm = base64.b64decode(pcm_base64)
            await self.active_session.send(
                input={"data": raw_pcm, "mime_type": "audio/pcm;rate=16000"},
                end_of_turn=False
            )
        except Exception as e:
            print(f"[GEMINI LIVE CHUNK ERROR] {e}")
    async def traiter_tool_call(self, tool_call, session):
        """Exécute les actions système/plugins demandées par Gemini Live."""
        for function_call in tool_call.function_calls:
            name = function_call.name
            args = function_call.args
            print(f"[GEMINI LIVE TOOL CALL] Fonction demandée : {name} avec args : {args}")
            # Routage vers les résolveurs rattachés dans builtins
            res_str = "Commande exécutée."
            resolver_func = getattr(builtins, f"resoudre_{name}", None)
            if resolver_func:
                try:
                    if asyncio.iscoroutinefunction(resolver_func):
                        res_str = await resolver_func(str(args))
                    else:
                        res_str = resolver_func(str(args))
                except Exception as ex:
                    res_str = f"Erreur d'exécution : {ex}"
            # Répondre à Gemini avec le résultat de l'outil
            try:
                await session.send(
                    input=types.LiveClientToolResponse(
                        function_responses=[
                            types.FunctionResponse(
                                name=name,
                                id=function_call.id,
                                response={"result": res_str}
                            )
                        ]
                    )
                )
            except Exception as e:
                print(f"[GEMINI LIVE TOOL RESPONSE ERROR] {e}")
    def arreter_session(self):
        """Arrête proprement la session en cours."""
        self.is_connected = False
        self.active_session = None
# Instance globale exportée
gemini_live_bridge = GeminiLiveBridge()
builtins.gemini_live_bridge = gemini_live_bridge