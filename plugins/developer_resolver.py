import os
import sys
import subprocess
import importlib
import builtins
import json
import re
import asyncio
import google.genai as genai
from google.genai import types
from core.config import GEMINI_API_KEY, CHOSEN_MODEL

# Initialisation du client de vision/génération Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def nettoyer_accent(texte):
    """Supprime les accents pour faciliter la comparaison."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

SYSTEM_INSTRUCTION = """
Tu es l'intelligence artificielle de JARVIS. Ton but est de modifier ou d'ajouter de nouvelles fonctionnalités à ta propre codebase à la demande de l'utilisateur.
Tu as un accès complet de lecture/écriture sur ton code source.

Voici la structure de ton projet pour t'orienter :
- main2.py : Orchestrateur principal Python (gestion des resolvers de commandes et exécution)
- core/
  - brain.py : Client de génération Gemini/Groq
  - speech.py : Moteur de synthèse vocale (TTS)
- plugins/
  - dom_controller_resolver.py : Commandes vocales -> actions DOM/HUD
  - app_launcher_resolver.py : Lancement d'applications PC
  - system_resolver.py : Commandes volume, screenshot, processeur, batterie
  - time_resolver.py : Commandes heure et date
- frontend/
  - index.html : Structure HTML du HUD, widgets, orbe 3D
  - src/
    - main.ts : Orchestration du HUD, WebSocket, queue d'actions DOM
    - widgets.ts : Logique des widgets (Musique, Météo, Calendrier)
    - widgets.css : Style CSS des widgets (.hud-widget, .hud-revealed)
    - style.css : Styles néon Iron Man globaux du HUD

Tu dois renvoyer obligatoirement un TABLEAU JSON d'objets décrivant chaque modification. Chaque objet doit suivre ce schéma précis :
{
  "file_path": "chemin/relatif/depuis/racine.ts",
  "target_code": "code exact à remplacer, y compris l'indentation et les espaces",
  "replacement_code": "nouveau code complet à insérer"
}

Pour CRÉER un nouveau fichier (ex: plugins/nouveau_resolver.py), mets "target_code" à "" (chaîne vide) et fournis le code complet dans "replacement_code".
Pour MODIFIER un fichier existant, fournis une portion de code existant extrêmement précise dans "target_code" afin qu'elle puisse être localisée de façon infaillible par un simple string.replace(). Évite de remplacer de trop grands blocs de code d'un coup.

Ne renvoie aucun texte explicatif en dehors du JSON. Sois extrêmement rigoureux sur la syntaxe TypeScript, CSS et Python.

---------------------------------------------------------
CONSIGNES D'ÉDITIONS CRITIQUES POUR MAIN2.PY :
Si tu dois importer et enregistrer un nouveau resolver (ex : plugins.recipe_resolver) dans main2.py, voici les blocs EXACTS du fichier sur lesquels faire tes remplacements :

1. Bloc d'importation des resolvers dans main2.py :
---------------------------------------------
import plugins.dom_controller_resolver
import plugins.developer_resolver
---------------------------------------------
Remplacement type pour ajouter ton import :
target_code: "import plugins.dom_controller_resolver\nimport plugins.developer_resolver"
replacement_code: "import plugins.dom_controller_resolver\nimport plugins.developer_resolver\nimport plugins.recipe_resolver"

2. Bloc de la chaîne de résolution locale dans traiter_reponse_ia (main2.py) :
---------------------------------------------
        # TENTATIVE DE RÉSOLUTION LOCALE (Commandes, Math, Français, etc.)
        print(f"[DEBUG] Tentative de résolution locale pour : {texte_utilisateur}")
        reponse = await builtins.resoudre_developpement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_dom_hud(texte_utilisateur)
---------------------------------------------
Remplacement type pour ajouter l'appel à ton nouveau resolver :
target_code: "        reponse = await builtins.resoudre_developpement(texte_utilisateur)\n        if not reponse: reponse = await builtins.resoudre_dom_hud(texte_utilisateur)"
replacement_code: "        reponse = await builtins.resoudre_developpement(texte_utilisateur)\n        if not reponse: reponse = await builtins.resoudre_recipe(texte_utilisateur)\n        if not reponse: reponse = await builtins.resoudre_dom_hud(texte_utilisateur)"

---------------------------------------------------------
EXEMPLE DE STRUCTURE POUR UN NOUVEAU RESOLVER (plugins/mon_resolver.py) :
---------------------------------------------
import builtins
import json

def nettoyer_accent(texte):
    import unicodedata
    return "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

async def resoudre_mon_resolver(cmd):
    t = nettoyer_accent(cmd.lower().strip())
    # Logique de commande ...
    return None

builtins.resoudre_mon_resolver = resoudre_mon_resolver
---------------------------------------------
"""

def appliquer_edits(edits):
    """Applique les modifications de code de façon sécurisée."""
    for edit in edits:
        file_path = edit.get("file_path", "")
        target = edit.get("target_code", "")
        replacement = edit.get("replacement_code", "")
        
        path = os.path.join("n:\\JARVIS", file_path)
        
        # 1. Création de fichier
        if target == "":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(replacement)
            print(f"[MUTATOR] Nouveau fichier créé : {path}")
        # 2. Modification de fichier existant
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Fichier introuvable pour modification : {file_path}")
                
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if target not in content:
                # Essayer en retirant les espaces superflus en fin de ligne si le matching échoue
                target_clean = "\n".join(l.rstrip() for l in target.splitlines())
                content_clean = "\n".join(l.rstrip() for l in content.splitlines())
                if target_clean in content_clean:
                    content = content_clean
                    target = target_clean
                else:
                    raise ValueError(f"Le code cible n'a pas été trouvé dans {file_path}. Modification avortée.")
            
            new_content = content.replace(target, replacement, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[MUTATOR] Fichier modifié : {path}")

def compiler_et_valider():
    """Valide les modifications par compilation statique TypeScript et vérification Python."""
    # 1. Validation Frontend (TypeScript)
    print("[MUTATOR] Lancement de la validation statique TypeScript...")
    res_ts = subprocess.run("npx tsc --noEmit", shell=True, cwd="n:\\JARVIS\\frontend", capture_output=True, text=True)
    if res_ts.returncode != 0:
        return False, f"TypeScript compilation error:\n{res_ts.stderr or res_ts.stdout}"
        
    # 2. Validation Backend (Python)
    print("[MUTATOR] Lancement de la validation des modules Python...")
    for file in os.listdir("n:\\JARVIS\\plugins"):
        if file.endswith(".py"):
            res_py = subprocess.run([sys.executable, "-m", "py_compile", os.path.join("n:\\JARVIS\\plugins", file)], capture_output=True, text=True)
            if res_py.returncode != 0:
                return False, f"Erreur de syntaxe Python dans {file} :\n{res_py.stderr}"
                
    return True, "Validation réussie !"

def recharger_plugins_python():
    """Recharge dynamiquement à chaud tous les modules du package plugins."""
    for name in list(sys.modules.keys()):
        if name.startswith("plugins."):
            try:
                importlib.reload(sys.modules[name])
                print(f"[MUTATOR] Module Python rechargé avec succès : {name}")
            except Exception as e:
                print(f"[MUTATOR] Échec du rechargement de {name} : {e}")

async def resoudre_developpement(cmd):
    """Résout les commandes d'auto-évolution et de restauration Git."""
    t = nettoyer_accent(cmd.lower().strip())
    
    # Nettoyage des variantes du mot-clé de réveil (VAD phonétique)
    t = re.sub(r'^(jarvis|jervis|jarvys|jervys|gervis)(,)?\s*', '', t)
    
    # 1. COMMANDES DE RESTAURATION / ROLLBACK GIT
    mots_cles_rollback = [
        "annule la derniere modification", "annule le dernier changement",
        "annule la modification", "annule le changement", "fais un rollback",
        "restaure le systeme", "restaure jarvis", "retour en arriere"
    ]
    if any(kw in t for kw in mots_cles_rollback):
        print("[MUTATOR] Déclenchement du protocole de rollback Git...")
        # Lancer le reset Git
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd="n:\\JARVIS", capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd="n:\\JARVIS", capture_output=True)
        
        # Envoyer une carte visuelle au HUD
        if hasattr(builtins, "envoyer_carte_contextuelle"):
            await builtins.envoyer_carte_contextuelle(
                "Restauration",
                "Le protocole de rollback a été exécuté. La codebase a été restaurée dans son état stable précédent.",
                type_carte="system",
                icon="◈"
            )
            
        # Recharger les plugins au cas où
        recharger_plugins_python()
        
        return "Très bien, mylane. J'ai annulé les dernières modifications et j'ai restauré la codebase à son dernier état stable."

    # 2. COMMANDES DE MUTATION / DÉVELOPPEMENT
    mots_cles_mutation = [
        "modifie ton code", "modifie le code", "ajoute le widget", "ajoute un widget",
        "modifie le style", "ajoute un bouton", "cree un bouton", "cree le bouton",
        "ajoute une commande", "cree un resolver", "cree un nouveau resolver",
        "developpe une fonctionnalite", "developpe un nouveau widget",
        "ajoute un commentaire de test", "modifie l'orbe", "ajoute un effet",
        "ajoute-moi", "cree-moi", "crée-moi", "developpe-moi"
    ]
    is_mutation_req = any(kw in t for kw in mots_cles_mutation) or t.startswith("modifie ") or t.startswith("ajoute ") or t.startswith("cree ") or t.startswith("developpe ") or t.startswith("ajoute-moi ") or t.startswith("cree-moi ")
    
    if is_mutation_req:
        description = cmd
        print(f"[MUTATOR] Requête d'auto-évolution reçue : {description}")
        
        # A. Créer un point de sauvegarde Git de sécurité (sur les fichiers modifiés uniquement)
        print("[MUTATOR] Création du point de sauvegarde Git...")
        # On ne fait pas de commit pour éviter de polluer l'historique et risquer de reculer HEAD.
        # On fait juste un reset HEAD pour annuler les modifs en cours si nécessaire.
        # Le reset HEAD remettra le dépôt dans l'état exact du dernier commit stable.
        
        # B. Informer l'utilisateur
        builtins.parler("J'initialise les protocoles d'auto-évolution, mylane. J'analyse le projet et je prépare les modifications de code...")
        
        # C. Boucle d'essais pour la génération et l'auto-correction
        prompt = f"L'utilisateur (mylane) demande la modification suivante :\n\"{description}\"\n\nGénère le tableau JSON des modifications de code nécessaires."
        
        err_prev = ""
        edits = []
        success = False
        
        for attempt in range(3):
            try:
                # Si tentative ultérieure, inclure l'erreur de compilation pour correction
                if attempt > 0:
                    builtins.parler(f"La validation a échoué. Tentative d'auto-correction numéro {attempt}...")
                    prompt_actuel = (
                        f"Tu as précédemment généré ces modifications de code :\n"
                        f"{json.dumps(edits, indent=2)}\n\n"
                        f"Cependant, la compilation a échoué avec l'erreur suivante :\n"
                        f"\"{err_prev}\"\n\n"
                        f"Corrige ces erreurs et renvoie le nouveau tableau JSON complet corrigé."
                    )
                else:
                    prompt_actuel = prompt
                
                response = client.models.generate_content(
                    model=CHOSEN_MODEL,
                    contents=prompt_actuel,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json"
                    )
                )
                
                edits = json.loads(response.text)
                print(f"[MUTATOR] Application des modifications (tentative {attempt+1})...")
                appliquer_edits(edits)
                
                # Validation par compilation
                valid, msg = compiler_et_valider()
                if valid:
                    success = True
                    break
                else:
                    err_prev = msg
                    # Annuler les modifications incorrectes avant la prochaine tentative
                    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd="n:\\JARVIS", capture_output=True)
                    subprocess.run(["git", "clean", "-fd"], cwd="n:\\JARVIS", capture_output=True)
                    
            except Exception as ex:
                err_prev = str(ex)
                subprocess.run(["git", "reset", "--hard", "HEAD"], cwd="n:\\JARVIS", capture_output=True)
                subprocess.run(["git", "clean", "-fd"], cwd="n:\\JARVIS", capture_output=True)
                
        # D. Résultat final
        if success:
            # Recharger dynamiquement les resolvers Python
            recharger_plugins_python()
            
            # Envoyer une carte de succès au HUD
            if hasattr(builtins, "envoyer_carte_contextuelle"):
                mod_files = [e.get("file_path") for e in edits]
                await builtins.envoyer_carte_contextuelle(
                    "Évolution Réussie",
                    f"Code modifié avec succès :\n" + "\n".join(f"- {f}" for f in mod_files),
                    type_carte="info",
                    icon="◈"
                )
            
            return "Les modifications ont été écrites, compilées avec succès, et injectées à chaud dans mes processeurs, mylane. La nouvelle fonctionnalité est active."
        else:
            # Restauration finale propre en cas d'échec de toutes les tentatives (remise au dernier commit stable)
            subprocess.run(["git", "reset", "--hard", "HEAD"], cwd="n:\\JARVIS", capture_output=True)
            subprocess.run(["git", "clean", "-fd"], cwd="n:\\JARVIS", capture_output=True)
            
            if hasattr(builtins, "envoyer_carte_contextuelle"):
                await builtins.envoyer_carte_contextuelle(
                    "Évolution Échouée",
                    f"La compilation a échoué. Le système a été restauré.\nErreur : {err_prev[:120]}...",
                    type_carte="alert",
                    icon="⚠"
                )
                
            return f"Je n'ai pas réussi à stabiliser le nouveau code après plusieurs tentatives d'auto-correction, mylane. J'ai préféré annuler toutes les modifications et restaurer le système. L'erreur de compilation était : {err_prev}"

    return None

# Injection globale dans builtins
builtins.resoudre_developpement = resoudre_developpement
