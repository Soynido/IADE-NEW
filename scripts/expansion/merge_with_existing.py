#!/usr/bin/env python3

"""
FUSION CORPUS - Phase 12
Fusionne le nouveau corpus massif avec l'existant (v1.2.1)
Évite les doublons et maintient la qualité
"""

import json
from pathlib import Path
from rapidfuzz import fuzz

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
    print(f"\n🎯 GAIN : +{len(added)} QCM (×{len(final_corpus)/len(existing_qcms):.1f})")
    print("="*60)

if __name__ == "__main__":
    main()

