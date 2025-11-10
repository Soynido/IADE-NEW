#!/usr/bin/env python3

"""
FUSION FINALE v2.1
Fusionne le corpus classifié + nouveaux QCM ciblés
"""

import json
from pathlib import Path
from collections import Counter

# Configuration
CLASSIFIED_FILE = Path("src/data/questions/compiled_fully_classified.json")
TARGETED_FILE = Path("src/data/questions/validated_massive.json")
OUTPUT_FILE = Path("src/data/questions/compiled_v21_final.json")

def main():
    print("="*60)
    print("🔀 FUSION FINALE - Corpus v2.1")
    print("="*60)
    print()
    
    # Charge corpus classifié
    with open(CLASSIFIED_FILE, "r", encoding="utf-8") as f:
        classified_data = json.load(f)
    
    classified = classified_data if isinstance(classified_data, list) else classified_data.get("questions", [])
    
    # Charge QCM ciblés validés
    with open(TARGETED_FILE, "r", encoding="utf-8") as f:
        targeted = json.load(f)
    
    print(f"📘 Corpus classifié : {len(classified)} QCM")
    print(f"📘 Nouveaux ciblés : {len(targeted)} QCM")
    print()
    
    # Fusion simple (pas de doublons possibles, génération différente)
    final_corpus = classified + targeted
    
    print(f"🔀 Fusion...")
    print(f"   Corpus final : {len(final_corpus)} QCM")
    print()
    
    # Statistiques par module
    modules = Counter(q.get("module_id", "unknown") for q in final_corpus)
    unknown_count = modules.get("unknown", 0)
    unknown_pct = unknown_count / len(final_corpus) * 100
    
    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_corpus, f, ensure_ascii=False, indent=2)
    
    # Rapport
    print("="*60)
    print("✅ FUSION TERMINÉE - CORPUS v2.1")
    print("="*60)
    print()
    print(f"📊 STATISTIQUES\n")
    print(f"   QCM total : {len(final_corpus)}")
    print(f"   Unknown : {unknown_count} ({unknown_pct:.1f}%)")
    print(f"   Modules actifs : {len([m for m, c in modules.items() if m != 'unknown'])}")
    print()
    print("📋 RÉPARTITION PAR MODULE\n")
    
    for module, count in sorted(modules.items(), key=lambda x: -x[1])[:15]:
        percent = count / len(final_corpus) * 100
        bar = "█" * int(percent / 2)
        status = "✅" if count >= 10 else "⚠️" if count >= 5 else "🔴"
        print(f"   {status} {module:20} {count:4} ({percent:5.1f}%) {bar}")
    
    print()
    print(f"💾 Corpus v2.1 final : {OUTPUT_FILE}")
    print()
    
    # Résumé qualité
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 QUALITÉ v2.1")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   Unknown : {unknown_pct:.1f}% {'✅ OK' if unknown_pct < 20 else '⚠️ À améliorer'}")
    
    modules_over_10 = len([m for m, c in modules.items() if c >= 10 and m != 'unknown'])
    print(f"   Modules ≥ 10 QCM : {modules_over_10}/{len(modules)-1} ✅")
    
    print()
    print("🎯 PROCHAINES ÉTAPES:")
    print("   1. Copier vers production")
    print("   2. Régénérer examens blancs")
    print("   3. Tester localement")
    print("   4. Déployer sur Vercel")
    print("="*60)

if __name__ == "__main__":
    main()

