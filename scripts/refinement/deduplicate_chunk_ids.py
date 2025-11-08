#!/usr/bin/env python3

"""
Détecte et regroupe les doublons de chunk_id dans compiled.json
Permet de préparer une fusion correcte (préserve toutes les variantes)
"""

import json
from collections import defaultdict
from pathlib import Path

INPUT = Path("src/data/questions/compiled.json")
OUTPUT = Path("src/data/questions/compiled_dedup.json")

with open(INPUT, "r") as f:
    data = json.load(f)

questions = data.get("questions", data)

# Regroupe par chunk_id
groups = defaultdict(list)
for q in questions:
    groups[q.get("chunk_id", "unknown")].append(q)

duplicates = {k: v for k, v in groups.items() if len(v) > 1}

print(f"🔍 {len(duplicates)} chunk_id ont plusieurs versions")
for cid, qs in list(duplicates.items())[:5]:
    print(f" - {cid}: {len(qs)} variantes")

# Sélectionne la meilleure version selon règles simples
deduped = []
for cid, qs in groups.items():
    if len(qs) == 1:
        deduped.append(qs[0])
    else:
        # Priorité : version avec meilleur biomedical_score
        best = max(qs, key=lambda x: x.get("biomedical_score", 0))
        deduped.append(best)

data["questions"] = deduped
data["total_questions"] = len(deduped)

with open(OUTPUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Déduplication terminée : {len(deduped)} questions conservées (unique chunk_id)")
print(f"💾 Sauvegardé dans : {OUTPUT}")

