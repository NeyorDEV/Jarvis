import builtins
import json
import unicodedata
import re
import asyncio
from google.genai import types

def nettoyer_accent(texte):
    return "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

async def resoudre_recipe(cmd):
    t = nettoyer_accent(cmd.lower().strip())

    # Patterns de détection des demandes de recette
    recipe_patterns = [
        r"donne moi la recette de (.*)",
        r"quelle est la recette de (.*)",
        r"je voudrais la recette de (.*)",
        r"trouve moi une recette de (.*)",
        r"montre moi la recette de (.*)",
        r"recette (.*)"
    ]

    recipe_name = None
    for pattern in recipe_patterns:
        match = re.search(pattern, t)
        if match:
            recipe_name = match.group(1).strip()
            break

    if recipe_name:
        print(f"[Recipe Resolver] Demande de recette détectée pour : {recipe_name}")
        prompt = (
            f"Génère une recette de cuisine pour \"{recipe_name}\". "
            "Le résultat doit être un objet JSON STRICTEMENT du format suivant :\n"
            "```json\n{{\n  \"recipe_title\": \"Nom de la recette\",\n  \"ingredients\": [\"Ingrédient 1\", \"Ingrédient 2\"],\n  \"instructions\": [\"Étape 1\", \"Étape 2\"]\n}}\n```\n"
            "Assure-toi que les valeurs des tableaux `ingredients` et `instructions` sont des chaînes de caractères simples. "
            "Ne rajoute aucun texte avant ou après le JSON. Si tu ne trouves pas la recette, réponds avec un JSON vide comme ceci : {}."
        )

        try:
            print("[Recipe Resolver] Appel à Gemini pour générer la recette...")
            # Appel à Gemini via le client global synchrone dans un thread asynchrone non bloquant
            def call_gemini():
                return builtins.client.models.generate_content(
                    model=builtins.CHOSEN_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
            
            response = await asyncio.to_thread(call_gemini)
            recipe_data = json.loads(response.text)

            if recipe_data and isinstance(recipe_data, dict) and recipe_data.get("recipe_title"):
                print(f"[Recipe Resolver] Recette générée : {recipe_data.get('recipe_title')}")
                await builtins.send_action_to_frontend({
                    "type": "show_recipe",
                    "recipe_title": recipe_data.get("recipe_title", ""),
                    "ingredients": recipe_data.get("ingredients", []),
                    "instructions": recipe_data.get("instructions", []),
                })
                return True
            else:
                print("[Recipe Resolver] Aucune recette valide n'a pu être générée ou la réponse est vide.")
                await builtins.send_action_to_frontend({"type": "speak", "text": "Désolé, je n'ai pas pu trouver de recette pour cela."})
                return True # On gère l'action même si c'est un échec pour ne pas passer au LLM global

        except json.JSONDecodeError as e:
            print(f"[Recipe Resolver] Erreur de décodage JSON : {e}")
            await builtins.send_action_to_frontend({"type": "speak", "text": "Désolé, il y a eu un problème pour générer la recette."})
            return True
        except Exception as e:
            print(f"[Recipe Resolver] Une erreur inattendue est survenue : {e}")
            await builtins.send_action_to_frontend({"type": "speak", "text": "Désolé, une erreur interne est survenue lors de la recherche de la recette."})
            return True

    return None

builtins.resoudre_recipe = resoudre_recipe
