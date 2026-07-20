# Entraînement du wake word « Jarvis » (français)

Notebook Colab pour entraîner un modèle openWakeWord custom qui détecte
**« jarvis » prononcé à la française**, en remplacement du modèle communautaire
`hey_jarvis_v0.1` (entraîné sur « hey jarvis » en anglais).

## Quand l'utiliser

Seulement si le modèle actuel te rate trop souvent : regarde les scores
`[WAKEWORD]` dans la console de JARVIS quand tu dis « Jarvis ».

- Scores ≥ 0.3 la plupart du temps → pas besoin d'entraîner, baisse juste
  `"wakeword_threshold"` dans `jarvis_config.json` (ex : `0.2`).
- Scores < 0.2 ou très irréguliers → entraîne le modèle custom.

## Mode d'emploi

1. Ouvre [Google Colab](https://colab.research.google.com) → `Importer` →
   `jarvis_fr_colab.ipynb`
2. `Exécution` → `Modifier le type d'exécution` → **GPU (T4)**
3. `Exécution` → `Tout exécuter` (~1 h au total)
4. À la fin, le fichier `jarvis_fr.onnx` se télécharge automatiquement
5. Copie-le dans `N:\JARVIS\core\jarvis_fr.onnx`
6. Relance JARVIS : `core/wakeword.py` le détecte automatiquement
   (message `[WAKEWORD] Modèle custom français détecté`)
7. Ajuste `"wakeword_threshold"` (commence à `0.5` — le modèle custom score
   beaucoup plus haut que hey_jarvis sur la prononciation française)

Pour revenir à hey_jarvis : supprime ou renomme `core/jarvis_fr.onnx`.

## Ce que le notebook fait

- Génère ~7 000 « jarvis » synthétiques avec 5 voix françaises Piper
  (siwis, tom, upmc ×2 locuteurs, gilles, mls ×~125 locuteurs), en variant
  débit et intonation, avec les orthographes `jarvis`/`jarviss`/`jarvisse`
  pour forcer la prononciation du S final
- Génère ~3 500 mots pièges phonétiquement proches (« parvis », « gervais »,
  « service », « jarret », « tandis »…) que le modèle apprend à rejeter
- Augmente le tout avec bruits de fond (musique FMA) et réverbérations de
  pièces réelles (MIT RIR)
- Entraîne contre 2 000 h de features audio négatives pré-calculées
  (pipeline officiel openWakeWord)

Rappel : même avec un faux positif du détecteur, JARVIS ne se réveille pas —
la vérification `"jarvis" in texte` après transcription reste l'autorité
finale. Un faux positif ne coûte qu'un appel STT.
