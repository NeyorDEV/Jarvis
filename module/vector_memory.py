import os
import time
import chromadb
from chromadb.utils import embedding_functions

# Chemin vers la DB vectorielle
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

# Variable globale pour le client et la collection afin d'éviter de les recharger à chaque fois
_client = None
_collection = None
on_souvenir_added = []

def _get_collection():
    """Initialise le client ChromaDB et retourne la collection d'historique."""
    global _client, _collection
    if _collection is None:
        try:
            if not os.path.exists(CHROMA_PATH):
                os.makedirs(CHROMA_PATH)
            
            _client = chromadb.PersistentClient(path=CHROMA_PATH)
            
            # Utilisation de la fonction d'embedding par défaut de Chroma
            # Elle télécharge automatiquement un modèle léger (all-MiniLM-L6-v2) au premier appel
            emb_fn = embedding_functions.DefaultEmbeddingFunction()
            
            _collection = _client.get_or_create_collection(
                name="jarvis_deep_memory",
                embedding_function=emb_fn,
                metadata={"hnsw:space": "cosine"} # Utilisation de la similarité cosinus
            )
            print(f"[VECTOR DB] Mémoire vectorielle chargée : {_collection.count()} souvenirs.")
        except Exception as e:
            print(f"[VECTOR DB] Erreur initialisation ChromaDB : {e}")
            return None
    return _collection

def ajouter_souvenir(user_text, model_text):
    """Ajoute un échange à la base de données vectorielle pour un rappel futur."""
    # Exclure les échanges qui sont des commandes système, des actions ou du contenu dynamique transitoire
    u_lower = user_text.lower()
    m_lower = model_text.lower()
    
    # Détecter le JSON / Actions
    if "{" in model_text or "action" in m_lower:
        return
        
    # Liste de mots-clés dynamiques transitoires
    mots_exclus = [
        "alarme", "alarm", "minuteur", "réveil", "reveil",
        "spotify", "deezer", "chanson", "musique", "volume", "playlist", "pause", "play", "stop",
        "ordinateur", "application", "éteindre", "redémarrer", "fermer", "ouvrir", "luminosité", "luminosite",
        "navigateur", "web", "recherche", "google", "site", "browser",
        "liste", "mémoire locale", "memo",
        "heure", "date", "météo", "meteo", "température", "temperature",
        "agenda", "calendrier", "calendar",
        "oublie", "oublier", "supprime", "supprimer", "efface", "effacer", "vide", "vider", "annule", "annuler", "retire", "retirer",
        "retiens", "retienne", "enregistre", "enregistrer", "mémorise", "memorise", "mémoriser", "memoriser", "note", "noter", "rappelle", "rappeler"
    ]
    
    if any(w in u_lower for w in mots_exclus) or any(w in m_lower for w in mots_exclus):
        return

    coll = _get_collection()
    if coll is None: return

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_content = f"Date: {timestamp}\nUser: {user_text}\nAssistant: {model_text}"
    
    # ID unique basé sur l'heure actuelle
    entry_id = f"msg_{int(time.time())}"
    
    try:
        coll.add(
            documents=[full_content],
            metadatas=[{"timestamp": timestamp, "type": "conversation"}],
            ids=[entry_id]
        )
        # Déclencher les callbacks enregistrés
        for cb in on_souvenir_added:
            try:
                cb(user_text, model_text)
            except Exception as cb_err:
                print(f"[VECTOR DB] Erreur callback souvenir_added: {cb_err}")
    except Exception as e:
        print(f"[VECTOR DB] Erreur ajout souvenir : {e}")

def rechercher_souvenirs(query_text, n_results=4, seuil=0.55):
    """Recherche des souvenirs pertinents basés sur la requête.

    seuil: distance cosinus max acceptable (0=identique, 1=sans rapport).
    Les souvenirs trop éloignés sont écartés plutôt que forcés dans le prompt.
    """
    coll = _get_collection()
    if coll is None or coll.count() == 0:
        return ""

    try:
        actual_n = min(n_results, coll.count())
        results = coll.query(
            query_texts=[query_text],
            n_results=actual_n,
            include=["documents", "distances"]
        )

        if not results or not results['documents'] or not results['documents'][0]:
            return ""

        docs      = results['documents'][0]
        distances = results.get('distances', [[]])[0]

        # Ne garder que les souvenirs réellement proches de la requête
        pertinents = [
            doc for doc, dist in zip(docs, distances)
            if dist <= seuil
        ]

        if not pertinents:
            print(f"[VECTOR DB] Aucun souvenir pertinent (meilleure distance: {distances[0]:.3f} > seuil {seuil})")
            return ""

        print(f"[VECTOR DB] {len(pertinents)}/{len(docs)} souvenir(s) pertinent(s) injecté(s) (distances: {[round(d,3) for d in distances[:len(pertinents)]]})")
        formatted = "\n---\n".join(pertinents)
        return f"\n[SOUVENIRS DU PASSÉ RETROUVÉS]\n{formatted}\n"

    except Exception as e:
        print(f"[VECTOR DB] Erreur recherche souvenirs : {e}")
        return ""

def rechercher_souvenir_semantique(query_text, threshold=0.4):
    """Recherche un souvenir extrêmement proche sémantiquement.
    Retourne la réponse de l'assistant si le score de distance est inférieur ou égal au threshold."""
    # Éviter les requêtes dynamiques ou d'apprentissage qui ne doivent pas utiliser de cache statique
    q_lower = query_text.lower().strip()
    mots_exclus = [
        "alarme", "alarm", "minuteur", "réveil", "reveil",
        "spotify", "deezer", "chanson", "musique", "volume", "playlist", "pause", "play", "stop",
        "ordinateur", "application", "éteindre", "redémarrer", "fermer", "ouvrir", "luminosité", "luminosite",
        "navigateur", "web", "recherche", "google", "site", "browser",
        "liste", "mémoire locale", "memo",
        "heure", "date", "météo", "meteo", "température", "temperature",
        "agenda", "calendrier", "calendar",
        "oublie", "oublier", "supprime", "supprimer", "efface", "effacer", "vide", "vider", "annule", "annuler", "retire", "retirer",
        "retiens", "retienne", "enregistre", "enregistrer", "mémorise", "memorise", "mémoriser", "memoriser", "note", "noter", "rappelle", "rappeler"
    ]
    if any(w in q_lower for w in mots_exclus):
        return None

    coll = _get_collection()
    if coll is None or coll.count() == 0:
        return None

    try:
        results = coll.query(
            query_texts=[query_text],
            n_results=1
        )
        
        if not results or not results['documents'] or not results['documents'][0]:
            return None
            
        # Vérifier la distance
        if 'distances' in results and results['distances'] and results['distances'][0]:
            dist = results['distances'][0][0]
            if dist <= threshold:
                doc = results['documents'][0][0]
                # Le document est sous la forme:
                # "Date: YYYY-MM-DD HH:MM:SS\nUser: ...\nAssistant: ..."
                # On extrait la partie Assistant
                if "Assistant:" in doc:
                    parts = doc.split("Assistant:")
                    assistant_reply = parts[-1].strip()
                    
                    # S'assurer qu'on ne renvoie pas une action JSON
                    if "{" in assistant_reply or "action" in assistant_reply.lower():
                        print(f"[VECTOR DB] Hit sémantique local ignoré car il contient une action ou du JSON.")
                        return None
                        
                    print(f"[VECTOR DB] Hit sémantique local (dist={dist:.3f}) : {assistant_reply}")
                    return assistant_reply
    except Exception as e:
        print(f"[VECTOR DB] Erreur recherche sémantique : {e}")
    return None

def supprimer_souvenir_semantique(query_text, seuil=0.5):
    """Recherche et supprime les souvenirs dans ChromaDB qui sont sémantiquement trop proches de la requête."""
    coll = _get_collection()
    if coll is None or coll.count() == 0:
        return False
    try:
        # Recherche des documents les plus proches
        results = coll.query(
            query_texts=[query_text],
            n_results=5,
            include=["distances"]
        )
        if not results or not results['ids'] or not results['ids'][0]:
            return False
        
        ids_to_delete = []
        if 'distances' in results and results['distances'] and results['distances'][0]:
            for entry_id, dist in zip(results['ids'][0], results['distances'][0]):
                # Si le souvenir est à moins de `seuil` (ex. 0.5 similarité élevée)
                if dist <= seuil:
                    ids_to_delete.append(entry_id)
        
        if ids_to_delete:
            coll.delete(ids=ids_to_delete)
            print(f"[VECTOR DB] Supprimé {len(ids_to_delete)} souvenir(s) sémantique(s) de la DB vectorielle.")
            return True
    except Exception as e:
        print(f"[VECTOR DB] Erreur lors de la suppression sémantique : {e}")
    return False

def lister_souvenirs():
    """Retourne la liste de tous les souvenirs enregistrés (pour consultation)."""
    coll = _get_collection()
    if coll is None: return []
    try:
        results = coll.get()
        return results['documents']
    except Exception as e:
        print(f"[VECTOR DB] Erreur lors du listage : {e}")
        return []

def lister_souvenirs_complets():
    """Retourne la liste de tous les souvenirs complets avec ids et documents."""
    coll = _get_collection()
    if coll is None: return []
    try:
        results = coll.get()
        souvenirs = []
        ids = results.get('ids', [])
        docs = results.get('documents', [])
        metas = results.get('metadatas', [])
        for i in range(len(ids)):
            souvenirs.append({
                "id": ids[i],
                "document": docs[i],
                "metadata": metas[i] if i < len(metas) else {}
            })
        return souvenirs
    except Exception as e:
        print(f"[VECTOR DB] Erreur lister_souvenirs_complets: {e}")
        return []

if __name__ == "__main__":
    # Petit test si lancé seul
    ajouter_souvenir("J'adore le café Blue Mountain de Jamaïque.", "C'est noté, mylane. C'est un excellent choix très raffiné.")
    print("Test de recherche : 'café'")
    print(rechercher_souvenirs("Quel type de café j'aime ?"))
