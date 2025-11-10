#!/bin/bash

# Script complet pour finaliser le corpus v2.1
# - Classification IA des 100 "unknown"
# - Génération ciblée modules sous-représentés
# - Validation BioBERT
# - Fusion finale

set -e

cd "$(dirname "$0")/../.."

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     🚀 CORPUS v2.1 - FINALISATION COMPLÈTE             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

source venv/bin/activate

# ÉTAPE 1: Classification IA des "unknown"
echo "════════════════════════════════════════════════════════════"
echo "🤖 ÉTAPE 1/5 : Classification IA (Mistral)"
echo "════════════════════════════════════════════════════════════"
python scripts/ai_generation/classify_with_ai.py
echo "✅ Classification IA terminée"
echo ""

# ÉTAPE 2: Génération ciblée modules critiques
echo "════════════════════════════════════════════════════════════"
echo "🎯 ÉTAPE 2/5 : Génération ciblée modules sous-représentés"
echo "════════════════════════════════════════════════════════════"
python scripts/ai_generation/generate_targeted.py --batch critical
echo "✅ Génération ciblée terminée"
echo ""

# ÉTAPE 3: Validation BioBERT des nouveaux QCM
echo "════════════════════════════════════════════════════════════"
echo "🔬 ÉTAPE 3/5 : Validation BioBERT"
echo "════════════════════════════════════════════════════════════"

# Copie les QCM ciblés pour validation
cp src/data/questions/generated_targeted.json src/data/questions/generated_massive.json

python scripts/expansion/validate_massive.py
echo "✅ Validation BioBERT terminée"
echo ""

# ÉTAPE 4: Fusion avec corpus classifié
echo "════════════════════════════════════════════════════════════"
echo "🔀 ÉTAPE 4/5 : Fusion finale"
echo "════════════════════════════════════════════════════════════"

# Script de fusion spécifique pour v2.1
python - <<'FUSION_SCRIPT'
import json
from pathlib import Path
from collections import Counter

# Charge corpus classifié
with open("src/data/questions/compiled_fully_classified.json", "r") as f:
    data = json.load(f)
    classified = data if isinstance(data, list) else data.get("questions", [])

# Charge nouveaux QCM validés
with open("src/data/questions/validated_massive.json", "r") as f:
    new_qcms = json.load(f)

print(f"📘 Corpus classifié : {len(classified)} QCM")
print(f"📘 Nouveaux QCM : {len(new_qcms)} QCM")

# Fusion
final_corpus = classified + new_qcms

# Déduplication par ID
seen_ids = set()
unique_corpus = []
for q in final_corpus:
    qid = q.get("id")
    if qid not in seen_ids:
        seen_ids.add(qid)
        unique_corpus.append(q)

print(f"📊 Corpus final : {len(unique_corpus)} QCM")

# Statistiques finales
modules = Counter(q.get("module_id", "unknown") for q in unique_corpus)
print("\n📋 RÉPARTITION FINALE:\n")
for mod, count in sorted(modules.items(), key=lambda x: -x[1]):
    pct = count / len(unique_corpus) * 100
    print(f"   {mod:20} {count:4} ({pct:5.1f}%)")

# Sauvegarde
with open("src/data/questions/compiled_v21_final.json", "w") as f:
    json.dump(unique_corpus, f, ensure_ascii=False, indent=2)

print(f"\n💾 Corpus v2.1 : src/data/questions/compiled_v21_final.json")
FUSION_SCRIPT

echo "✅ Fusion terminée"
echo ""

# ÉTAPE 5: Copie vers production
echo "════════════════════════════════════════════════════════════"
echo "📦 ÉTAPE 5/5 : Copie vers production"
echo "════════════════════════════════════════════════════════════"

cp src/data/questions/compiled_v21_final.json public/data/questions/revision.json
cp src/data/questions/compiled_v21_final.json public/data/questions/entrainement.json
cp src/data/questions/compiled_v21_final.json public/data/questions/concours.json

echo "✅ Fichiers production mis à jour"
echo ""

# Résumé final
python - <<'SUMMARY'
import json
from collections import Counter

with open("src/data/questions/compiled_v21_final.json") as f:
    corpus = json.load(f)

modules = Counter(q.get("module_id", "unknown") for q in corpus)
unknown = modules.get("unknown", 0)

print("╔═══════════════════════════════════════════════════════════╗")
print("║                                                           ║")
print("║     ✅ CORPUS v2.1 FINALISÉ                             ║")
print("║                                                           ║")
print("╚═══════════════════════════════════════════════════════════╝")
print()
print(f"📊 QCM total : {len(corpus)}")
print(f"📊 Unknown : {unknown} ({unknown/len(corpus)*100:.1f}%)")
print(f"📊 Modules : {len(modules)}")
print()
print("🎯 PROCHAINES ÉTAPES:")
print("   1. Régénérer examens blancs")
print("   2. Tester localement (npm run dev)")
print("   3. Déployer sur Vercel")
print()
SUMMARY

echo "════════════════════════════════════════════════════════════"

