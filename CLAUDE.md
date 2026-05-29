# JARVIS — Guide Claude Code

## Architecture générale

Système d'assistant IA Iron Man-style. Backend Python (WebSocket) + Frontend TypeScript/Three.js (Vite).

```
main2.py          — Orchestrateur principal (WebSocket, VAD, STT, plugins, LLM)
core/
  brain.py        — Client Gemini/Groq (génération LLM)
  speech.py       — TTS edge_tts + pygame, gestionnaire file de parole
  config.py       — Clés API, modèles
module/
  alarm_manager.py    — Alarmes/timers
  file_manager.py     — Gestion fichiers/dossiers
  memory_manager.py   — Mémoire clé-valeur persistante (memory.json)
  vector_memory.py    — Mémoire vectorielle ChromaDB (conversations passées)
  google_services.py  — Gmail, Drive, Calendar
  browser_service.py  — Agent navigateur autonome
  image_generator.py  — Génération d'images IA (Pollinations)
  ha_config.py        — Config domotique Home Assistant
  sports_web.py       — Résultats sportifs web
  vision_module.py    — Analyse image/écran
  homepod_audio.py    — Sortie audio HomePod (AirPlay)
  jarvis_agent.py     — Scaffold agent Gemini
controller/
  app_launcher.py       — Lancement/fermeture d'applications PC
  deezer_controller.py  — Contrôle Deezer Windows
  spotify_controller.py — Contrôle Spotify Windows
  homepod_controller.py — Commandes HomePod (play/pause/volume)
  tv_worker.py          — Worker TV Chromecast (sous-processus)
frontend/
  index.html      — Structure HUD, widgets inline, boot overlay
  src/
    main.ts       — WebSocket client, DOM automation queue, logique HUD
    orb.ts        — Orbe 3D Three.js (états: idle/listening/thinking/speaking)
    widgets.ts    — Calendrier, météo, musique (init + show/hide)
    widgets.css   — Styles widgets, .hud-revealed pour show/hide
    hand_tracking.ts — Mode AR MediaPipe, drag & resize gestuel
    globe.ts      — Globe 3D + carte Leaflet
    cards.ts      — Cartes contextuelles (notifications auto-dismiss)
    style.css     — Style global HUD Iron Man
plugins/
  dom_controller_resolver.py — Commandes vocales → actions DOM/HUD
  app_launcher_resolver.py   — Lancement d'applications
  globe_resolver.py          — Navigation géographique
  memory_resolver.py         — Gestion mémoire
  system_resolver.py         — Stats système
  time_resolver.py           — Heure/date
  tv_resolver.py             — Contrôle TV
  local_resolver.py          — Fichiers locaux
```

## Protocole WebSocket (ws://localhost:8765)

### Backend → Frontend (actions)
```json
{"state": "idle|listening|thinking|speaking"}
{"action": "jarvis_text", "text": "..."}
{"action": "weather_update", "weather": {...}, "weather_type": "local|monistrol"}
{"action": "weather_panel", "data": {...}}
{"action": "temp_panel", "data": {...}}
{"action": "music_update", "data": {"status": "Playing|Paused", "title": "...", "artist": "..."}}
{"action": "ctx_card", "title": "...", "text": "...", "type": "info|alert|system", "icon": "◈"}
{"action": "jarvis_globe", "globe_action": "show|hide|fly_to", ...}
{"action": "display_image", "url": "...", "prompt": "..."}
{"action": "timer_start", "duration": 60}
{"action": "timer_stop"}
{"action": "help"}
{"action": "system_stats", "cpu": 45, "ram": 60}
{"action": "set_volume", "volume": 0.8}
{"type": "dom_action", "action": "click|type|focus|select|add_class|remove_class", "selector": "#id", "text": "...", "class_name": "..."}
{"type": "show_recipe", "titre": "...", "ingredients": [...], "instructions": [...]}
```

### Frontend → Backend
```json
{"type": "stop_audio"}
{"type": "toggle_mic"}
{"type": "user_input", "text": "..."}
{"type": "music_control", "action": "prev|toggle|next"}
{"type": "set_location", "lat": 0.0, "lon": 0.0}
{"type": "get_settings"}
{"type": "update_settings", "settings": {...}}
{"type": "toggle_fullscreen"}
{"type": "screen_frame", "id": "...", "data": "base64..."}
```

## Pipeline voix

```
PyAudio (VAD) → transcribe_audio_groq() → Groq Whisper (fallback: Google STT)
→ if WAKE_WORD("jarvis") in texte OR jarvis_actif:
    → plugin resolvers (priorité ordre) → si None → traiter_reponse_ia()
        → Gemini streaming phrase-par-phrase → parler(phrase) en parallèle
```

**Important** : `from_voice=True` doit être passé à `traiter_reponse_ia()` depuis la boucle VAD uniquement. Les commandes clavier/mobile utilisent `from_voice=False` (défaut) pour ne pas ouvrir de session vocale.

SESSION_TIMEOUT = 20s. WAKE_WORD = "jarvis".

## Widgets HUD — visibilité

Les 3 widgets sont **cachés par défaut** et s'affichent sur commande vocale :

| Widget | Élément | Commande vocale |
|--------|---------|-----------------|
| Calendrier | `#calendar-hud` | "montre le calendrier" |
| Météo | `#weather-hud` | "montre moi la météo" |
| Musique | `#music-hud` | "montre la musique" |

Mécanisme : `dom_action add_class/remove_class` avec classe `hud-revealed`.
Drag souris activé sur les 3 widgets (makeDraggable dans main.ts).
Mode AR (hand_tracking.ts) supporte aussi le drag gestuel.

## Actions DOM depuis les plugins

```python
# Dans dom_controller_resolver.py ou tout plugin :
await builtins.send_web_action("click", selector="#element-id")
await builtins.send_web_action("type", selector="#input", text="valeur")
await builtins.send_web_action("add_class", selector="#element", class_name="ma-classe")
await builtins.send_web_action("remove_class", selector="#element", class_name="ma-classe")
```

`send_web_action` est défini dans main2.py (~ligne 548) et injecté via `builtins`.

## Mémoire

**Deux systèmes distincts :**

1. `memory_manager.py` — Faits clé-valeur (préférences, infos perso) → injectés en entier dans chaque prompt via `construire_contexte_memoire()`. Stocké dans `memory.json`.

2. `vector_memory.py` — Historique conversations vectorisé (ChromaDB, modèle all-MiniLM-L6-v2). `rechercher_souvenirs(query, n_results=4, seuil=0.72)` filtre par pertinence cosinus — si aucun souvenir n'est sous le seuil, rien n'est injecté (économie tokens).

## LLM

- **Principal** : Gemini (gemini-2.5-flash, gemini-flash-latest, gemini-2.0-flash, gemini-pro-latest) — failover automatique entre modèles
- **Fallback** : Groq (streaming OpenAI-compatible)
- **Streaming** : Gemini stream phrase-par-phrase, TTS déclenché dès qu'une phrase est complète (`. `, `! `, `? `, `\n`)
- **Flag** `_derniere_reponse_streamed` : évite de re-parler le texte déjà streamé

## Ajouter un plugin/resolver

1. Créer `plugins/mon_resolver.py` avec fonction `async def resoudre_X(cmd) -> str | None`
2. Normaliser le texte : `nettoyer_accent(cmd.lower().strip())`
3. Retourner `None` si la commande n'est pas reconnue (passage au resolver suivant)
4. Importer et brancher dans l'ordre de priorité dans main2.py (`executer_action_pc` ou `traiter_reponse_ia`)

## Conventions CSS widgets

- `.hud-widget` — base commune (position fixed, z-index 70, style Iron Man)
- `.hud-revealed` — rend le widget visible avec animation `widget-reveal`
- `.wp-visible` / `.tp-visible` — panneaux latéraux météo/température (slide-in)
- `ar-mode-active` sur `body` — mode AR actif
- `.widget-close-btn` — bouton ✕ commun aux widgets

## Fichiers de config

```
jarvis_config.json  — Préférences utilisateur (mic index, nom, âge, apps custom, HA entities)
memory.json         — Mémoire clé-valeur persistante
chroma_db/          — Base vectorielle ChromaDB
alarmes.json        — Alarmes/timers sauvegardés
.env                — Clés API (GEMINI_API_KEY, GROQ_API_KEY, etc.)
```

## Lancer le projet

```bash
# Backend
python main2.py

# Frontend (dans /frontend)
npm run dev
```
