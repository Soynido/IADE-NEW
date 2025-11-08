#!/usr/bin/env python3

"""
IADE NEW — Revalidation BioBERT + fusion finale
Recalcule les scores biomédicaux, sémantiques et fusionne avec le corpus complet.
"""

import json, os, subprocess

REFINED = "src/data/questions/to_refine_refined.json"
COMPILED = "src/data/questions/compiled.json"
FINAL = "src/data/questions/compiled_refined.json"

if not all(os.path.exists(f) for f in [REFINED, COMPILED]):
    raise FileNotFoundError("❌ Fichiers manquants pour fusion")

print("="*60)
print("REVALIDATION & FUSION CORPUS RAFFINÉ")
print("="*60)

# Étape 1 : rescoring biomédical
print("\n🔬 Étape 1: Re-scoring BioBERT...")
subprocess.run([
    "python", "scripts/ai_generation/biobert_client.py",
    "--in", REFINED,
    "--out", "src/data/questions/to_refine_rescored.json",
    "--metadata", "src/data/metadata.json"
], check=True)

print("\n✅ Re-scoring terminé")

# Étape 2 : fusion
print("\n🔀 Étape 2: Fusion avec corpus principal...")
with open(COMPILED) as f1:
    base_data = json.load(f1)

with open("src/data/questions/to_refine_rescored.json") as f2:
    refined_data = json.load(f2)

# Extraire les questions du compiled.json (structure avec métadonnées)
if isinstance(base_data, dict) and 'questions' in base_data:
    base = base_data['questions']
    metadata = {k: v for k, v in base_data.items() if k != 'questions'}
else:
    base = base_data if isinstance(base_data, list) else []
    metadata = {}

# Extraire les questions du refined (même structure potentielle)
if isinstance(refined_data, dict) and 'questions' in refined_data:
    refined = refined_data['questions']
elif isinstance(refined_data, list):
    refined = refined_data
else:
    refined = []

# Crée un dict par ID pour faciliter merge
base_dict = {q.get("id", q.get("chunk_id", i)): q for i, q in enumerate(base)}
refined_dict = {q.get("id", q.get("chunk_id", i)): q for i, q in enumerate(refined)}

# Remplace les versions raffinées
for qid, refined_q in refined_dict.items():
    if qid in base_dict:
        base_dict[qid] = refined_q
        print(f"  ✓ Remplacé: {qid}")

# Sauvegarde corpus final
final_corpus = list(base_dict.values())

# Reconstruit structure avec métadonnées si nécessaire
if metadata:
    final_output = {**metadata, 'questions': final_corpus, 'total_questions': len(final_corpus)}
else:
    final_output = final_corpus

with open(FINAL, "w") as f:
    json.dump(final_output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Corpus fusionné et revalidé → {FINAL}")
print(f"   Total questions : {len(final_corpus)}")
print(f"   Questions raffinées : {len(refined_dict)}")

# Stats comparaison
base_scores = [q.get("biomedical_score", 0) for q in base]
refined_scores = [q.get("biomedical_score", 0) for q in final_corpus]

avg_base = sum(base_scores) / len(base_scores) if base_scores else 0
avg_refined = sum(refined_scores) / len(refined_scores) if refined_scores else 0

print(f"\n📊 COMPARAISON QUALITÉ")
print(f"   Score BioBERT avant : {avg_base:.3f}")
print(f"   Score BioBERT après : {avg_refined:.3f}")
print(f"   Amélioration        : {(avg_refined - avg_base)*100:+.2f}%")

print(f"\n{'='*60}")
print(f"✅ REFINEMENT COMPLET TERMINÉ")
print(f"{'='*60}")

