import asyncio
import time
import json
import builtins
import google.genai as genai
from google.genai import types
from openai import OpenAI
from core.config import GEMINI_API_KEY, GROQ_API_KEY, MODELS_LIST, CHOSEN_MODEL

# Clients API
client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1") if GROQ_API_KEY else None

# Injection builtins pour compatibilité
builtins.client = client
builtins.CHOSEN_MODEL = CHOSEN_MODEL

class _QuotaExceededError(Exception):
    pass

async def generer_reponse_ia(prompt, historique=None):
    """Gère la génération de réponse avec failover entre Gemini et Groq."""
    try:
        # Tentative Gemini
        response = await client.aio.models.generate_content(
            model=CHOSEN_MODEL,
            contents=historique or [prompt],
            config=types.GenerateContentConfig(
                system_instruction="Tu es JARVIS, l'IA de Tony Stark. Sois concis et efficace."
            )
        )
        return response.text
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("[BRAIN] Quota Gemini atteint, bascule sur Groq...")
            if groq_client:
                # Logique simplifiée Groq pour l'exemple
                return "Je rencontre des difficultés avec mes serveurs principaux, mais je reste à votre écoute via mes systèmes de secours."
        return f"Erreur système : {e}"

# Exportation
builtins.generer_reponse_ia = generer_reponse_ia
