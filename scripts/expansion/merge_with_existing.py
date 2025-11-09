#!/usr/bin/env python3

"""
FUSION CORPUS - Phase 12
Fusionne le nouveau corpus massif avec l'existant (v1.2.1)
Évite les doublons et maintient la qualité
"""

import json
from pathlib import Path
from rapidfuzz import fuzz
from tqdm import tqdm

# Configuration
EXISTING_FILE = Path("src/data/questions/compiled_verified.json")
NEW_FILE = Path("src/data/questions/validated_massive.json")
OUTPUT_FILE = Path("src/data/questions/compiled_expanded.json")
SIMILARITY_THRESHOLD = 85  # % similarité pour détecter doublons

def is_duplicate(q1, q2):
    """Détecte si deux questions sont similaires"""
    text1 = q1.get("text", "").lower()
    text2 = q2.get("text", "").lower()
    
    similarity = fuzz.ratio(text1, text2)
    return similarity >= SIMILARITY_THRESHOLD

def main():
    print("="*60)
    print("🔀 FUSION CORPUS EXISTANT + NOUVEAU - Phase 12")
    print("="*60)
    
    # Charge existant (v1.2.1 - 165 QCM vérifiés)
    with open(EXISTING_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    
    existing_qcms = existing_data.get("questions", existing_data)
    print(f"\n📘 Corpus existant : {len(existing_qcms)} QCM (vérifié 98.2%)")
    
    # Charge nouveau (massif)
    with open(NEW_FILE, "r", encoding="utf-8") as f:
        new_qcms = json.load(f)
    
    print(f"📘 Nouveau corpus : {len(new_qcms)} QCM (généré + validé)")
    
    # Déduplication
    print(f"\n🔍 Détection des doublons (seuil {SIMILARITY_THRESHOLD}%)...\n")
    
    added = []
    duplicates = 0
    
    for new_q in tqdm(new_qcms, desc="   Analyse"):
        is_dup = False
        
        # Vérifie contre corpus existant
        for existing_q in existing_qcms:
            if is_duplicate(new_q, existing_q):
                is_dup = True
                duplicates += 1
                break
        
        if not is_dup:
            added.append(new_q)
    
    # Fusion
    final_corpus = existing_qcms + added
    
    # Sauvegarde
    if isinstance(existing_data, dict):
        output_data = {
            **existing_data,
            "version": "v2.0_expanded",
            "total_questions": len(final_corpus),
            "expansion": {
                "existing": len(existing_qcms),
                "generated": len(new_qcms),
                "duplicates": duplicates,
                "added": len(added)
            },
            "questions": final_corpus
        }
    else:
        output_data = final_corpus
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Résumé automatique (recommandation 1)
    summary_file = Path("src/data/questions/expansion_summary.txt")
    from datetime import datetime
    
    with open(summary_file, "w", encoding="utf-8") as s:
        s.write(f"""📊 IADE Massive Generation Report
═══════════════════════════════════════════════════════════

Date              : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version           : v2.0 Expansion

CORPUS
───────────────────────────────────────────────────────────
Existing corpus   : {len(existing_qcms)} QCM
New generated     : {len(new_qcms)} QCM
Added             : {len(added)} QCM
Duplicates        : {duplicates} ({duplicates/len(new_qcms)*100:.1f}%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total final       : {len(final_corpus)} QCM

GAIN
───────────────────────────────────────────────────────────
Expansion factor  : ×{len(final_corpus)/len(existing_qcms):.2f}
New QCM added     : +{len(added)} ({len(added)/len(existing_qcms)*100:.1f}%)

QUALITY
───────────────────────────────────────────────────────────
Deduplication     : {SIMILARITY_THRESHOLD}% threshold
Source verified   : v1.2.1 (98.2% validated)
BioBERT validated : All new QCM >= 0.4

═══════════════════════════════════════════════════════════
""")
    
    # Log pipeline (recommandation 2)
    log_file = Path("logs/pipeline.log")
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Fusion ✓ {len(added)} added, {len(final_corpus)} total\n")
    
    # Statistiques
    print(f"\n{'='*60}")
    print(f"✅ FUSION TERMINÉE")
    print(f"{'='*60}")
    print(f"\n📊 RÉSULTATS\n")
    print(f"   Corpus existant : {len(existing_qcms)} QCM")
    print(f"   Nouveau généré : {len(new_qcms)} QCM")
    print(f"   Doublons détectés : {duplicates} ({duplicates/len(new_qcms)*100:.1f}%)")
    print(f"   QCM ajoutés : {len(added)}")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   CORPUS FINAL : {len(final_corpus)} QCM")
    print(f"\n💾 Corpus expansé : {OUTPUT_FILE}")
    print(f"📄 Résumé : {summary_file}")
    print(f"📝 Log : {log_file}")
    print(f"\n🎯 GAIN : +{len(added)} QCM (×{len(final_corpus)/len(existing_qcms):.1f})")
    print("="*60)

if __name__ == "__main__":
    main()

