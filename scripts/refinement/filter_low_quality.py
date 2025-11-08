#!/usr/bin/env python3

"""
IADE NEW — Filtrage des QCM à retravailler
Filtre automatiquement les questions faibles selon critères quantitatifs et qualitatifs.
"""

import json, os

IN_FILE = "src/data/questions/compiled.json"
OUT_FILE = "src/data/questions/to_refine.json"

if not os.path.exists(IN_FILE):
    raise FileNotFoundError(f"❌ Fichier introuvable : {IN_FILE}")

with open(IN_FILE) as f:
    data = json.load(f)

# Gestion du format (array direct ou objet avec clé)
if isinstance(data, dict):
    questions = data.get('questions', [])
else:
    questions = data

subset = []
for q in questions:
    conds = [
        q.get("biomedical_score", 1) < 0.88,
        len(q.get("explanation", "")) < 60,
        q.get("source_context", "") in ["Citation.", "", None],
        len(set(q.get("options", []))) < 4,
    ]
    if any(conds):
        subset.append(q)

print(f"✅ {len(subset)} questions retenues pour refinement sur {len(questions)} totales ({len(subset)/len(questions)*100:.1f} %).")
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, "w") as f:
    json.dump(subset, f, indent=2, ensure_ascii=False)

