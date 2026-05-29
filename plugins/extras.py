import random
import builtins
import time

_BLAGUES = [
    "Pourquoi les plongeurs plongent-ils toujours en arrière ? Parce que sinon ils tomberaient dans le bateau !",
    "Un homme entre dans une bibliothèque et demande : 'Avez-vous des livres sur la paranoïa ?' La bibliothécaire chuchote : 'Ils sont juste derrière vous.'",
    "Qu'est-ce qu'un canif ? Un petit fien.",
    "Pourquoi l'épouvantail a-t-il reçu un prix ? Parce qu'il était exceptionnel dans son domaine.",
    "Qu'est-ce qu'un crocodile qui surveille la cour d'école ? Un sac à dents.",
    "Pourquoi les mathématiciens confondent-ils Halloween et Noël ? Parce que Oct 31 = Dec 25.",
    "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-peint de Noël.",
    "Qu'est-ce qu'un yaourt dans la forêt ? Un yaourt nature.",
    "Pourquoi les girafes ont-elles un long cou ? Parce que leurs pieds sentent mauvais.",
    "Qu'est-ce qu'un os dans un bain de boue ? Sherlock Bones.",
    "Comment appelle-t-on un chat qui est tombé dans un pot de confiture ? Un chat confit."
]

_CITATIONS = [
    "Le succès, c'est tomber sept fois et se relever huit. — Proverbe japonais",
    "La vie, c'est comme une bicyclette, il faut avancer pour ne pas perdre l'équilibre. — Albert Einstein",
    "Le seul moyen de faire du bon travail est d'aimer ce que vous faites. — Steve Jobs",
    "Celui qui déplace les montagnes commence par enlever les petites pierres. — Confucius",
    "La créativité, c'est l'intelligence qui s'amuse. — Albert Einstein",
    "Le pessimiste voit la difficulté dans chaque opportunité. L'optimiste voit l'opportunité dans chaque difficulté. — Winston Churchill"
]

_CAPITALES = {
    "france": "Paris", "espagne": "Madrid", "italie": "Rome", "allemagne": "Berlin",
    "royaume-uni": "Londres", "portugal": "Lisbonne", "belgique": "Bruxelles",
    "suisse": "Berne", "etats-unis": "Washington", "canada": "Ottawa",
    "japon": "Tokyo", "chine": "Pekin", "russie": "Moscou", "bresil": "Brasilia",
    "maroc": "Rabat", "algerie": "Alger", "tunisie": "Tunis", "egypte": "Le Caire"
}

_MONNAIES = {
    "france": "Euro", "etats-unis": "Dollar americain", "royaume-uni": "Livre sterling",
    "japon": "Yen", "suisse": "Franc suisse", "canada": "Dollar canadien"
}

async def resoudre_extras_locaux(texte):
    """Gère la culture générale, l'humour et l'identité."""
    t = texte.lower().strip()
    
    # 1. SALUTATIONS / ÉTAT
    if any(m in t for m in ["bonjour", "salut", "hello", "hey jarvis", "bonsoir"]) and len(t) < 50:
        h = int(time.strftime("%H"))
        moment = "Bonsoir" if h >= 18 else ("Bon après-midi" if h >= 12 else "Bonjour")
        return f"{moment} mylane ! Je suis opérationnel et prêt à vous aider."
    if any(m in t for m in ["comment tu vas", "ça va", "tu vas bien"]):
        return "Je vais très bien merci, mylane ! Tous mes processeurs tournent à plein régime."

    # 2. HUMOUR / INSPIRATION
    if any(m in t for m in ["blague", "humour"]): return random.choice(_BLAGUES)
    if any(m in t for m in ["citation", "inspire-moi"]): return random.choice(_CITATIONS)

    # 3. CULTURE GÉNÉRALE (Capitales / Monnaies)
    if "capitale de" in t or "capitale du" in t:
        for pays, cap in _CAPITALES.items():
            if pays in t: return f"La capitale de {pays.capitalize()} est {cap}, Monsieur."
    if "monnaie de" in t or "monnaie du" in t:
        for pays, mon in _MONNAIES.items():
            if pays in t: return f"La monnaie officielle en {pays.capitalize()} est le {mon}, Monsieur."

    # 4. IDENTITÉ
    if any(m in t for m in ["qui es-tu", "ton nom", "c'est quoi jarvis"]):
        return "Je suis JARVIS — Just A Rather Very Intelligent System. Votre assistant personnel."
    if any(m in t for m in ["ton createur", "qui t'a fait"]):
        return "Mon créateur est Mylane. Un développeur passionné qui m'a conçu de A à Z."

    return None

# Injection builtins
builtins.resoudre_extras_locaux = resoudre_extras_locaux
