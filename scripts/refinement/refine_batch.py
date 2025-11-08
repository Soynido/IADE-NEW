#!/usr/bin/env python3

"""
IADE NEW — Réécriture IA ciblée (via Ollama)
Améliore les QCM identifiés comme faibles, sans changer la réponse correcte.
"""

import json, subprocess, os, tempfile

IN_FILE = "src/data/questions/to_refine.json"
OUT_FILE = "src/data/questions/to_refine_refined.json"
MODEL = "mistral:latest"

PROMPT_TEMPLATE = """Tu es un formateur IADE.

Améliore ce QCM sans changer la notion médicale ni la bonne réponse.
- Reformule la question en français clair, fidèle au cours.
- Rends les 4 options plausibles (évite les évidences).
- Reformule l'explication en 2 phrases précises et formatives.
- Supprime tout placeholder ("Citation.", "..." ou vide).

Retourne uniquement du JSON valide : 
{"text": "...", "options": ["...", "...", "...", "..."], "correctAnswer": X, "explanation": "...", "source_context": "..."}
"""

if not os.path.exists(IN_FILE):
    raise FileNotFoundError("❌ Fichier à raffiner introuvable")

with open(IN_FILE) as f:
    questions = json.load(f)

refined = []
for i, q in enumerate(questions, 1):
    content = PROMPT_TEMPLATE + "\n\nQCM actuel :\n" + json.dumps(q, ensure_ascii=False)
    cmd = ["ollama", "run", MODEL, content]
    try:
        result = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        # Parse JSON de la réponse
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            j = json.loads(result[start:end])
            # Garde métadonnées originales
            refined_q = q.copy()
            refined_q.update(j)
            refined_q['refined'] = True
            refined.append(refined_q)
            print(f"[{i}/{len(questions)}] ✅ {q.get('id', 'unknown')}")
        else:
            print(f"[{i}/{len(questions)}] ⚠️ JSON invalide")
            refined.append(q)
    except Exception as e:
        print(f"[{i}/{len(questions)}] ⚠️ Erreur : {str(e)[:50]}")
        refined.append(q)

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, "w") as f:
    json.dump(refined, f, indent=2, ensure_ascii=False)

print(f"\n✅ {len(refined)} QCM raffinés enregistrés dans {OUT_FILE}")

