import pyaudio
import re

p = pyaudio.PyAudio()
print("--- LISTE BRUTE ---")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info.get("maxInputChannels", 0) > 0:
        print(f"[{i}] {repr(info.get('name'))}")

print("\n--- TEST DEDUPLICATION AMELIOREE ---")
raw_devices = []
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info.get("maxInputChannels", 0) > 0:
        nom = info.get("name", f"Périphérique {i}")
        nom_normalise = nom.lower().strip()
        exclus = ["mappeur de sons", "capture audio principal", "mixage", "stereo mix", "ivcam", "entrée ligne", "line input", "realtek hd audio mic input"]
        if any(x in nom_normalise for x in exclus):
            continue
            
        # Nettoyage cosmétique du nom pour fusionner les doublons physiques
        nom_propre = re.sub(r'\d+-\s*', '', nom) # Retirer les préfixes comme "3- " ou "6- "
        nom_propre = re.sub(r'sur casque', '', nom_propre, flags=re.IGNORECASE)
        nom_propre = nom_propre.replace("Headset Microphone", "Microphone")
        
        # Supprimer les parenthèses vides ou ne contenant que des espaces
        nom_propre = re.sub(r'\(\s*\)', '', nom_propre)
        nom_propre = re.sub(r'\s+', ' ', nom_propre).strip()
        
        # Ignorer si le nom est trop générique ou vide
        if nom_propre.lower() in ["microphone", ""]:
            continue
            
        raw_devices.append({"index": i, "clean_name": nom_propre})

# Déduplication intelligente par longueur décroissante (priorité aux noms complets non tronqués)
raw_devices.sort(key=lambda d: len(d["clean_name"]), reverse=True)
seen_clean_names = set()
filtered_devices = []

for dev in raw_devices:
    name_lower = dev["clean_name"].lower()
    # Ignorer si c'est un préfixe ou une sous-chaîne d'un nom plus complet déjà enregistré
    is_truncated_duplicate = any(name_lower in seen or seen.startswith(name_lower) for seen in seen_clean_names)
    if not is_truncated_duplicate:
        seen_clean_names.add(name_lower)
        filtered_devices.append(dev)

# Réordonner par index croissant pour l'affichage console final
filtered_devices.sort(key=lambda d: d["index"])

print("[MIC] Périphériques audio détectés (filtrés et nettoyés) :")
for dev in filtered_devices:
    print(f"      [{dev['index']}] {dev['clean_name']}")
