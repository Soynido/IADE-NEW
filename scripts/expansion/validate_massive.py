#!/usr/bin/env python3

"""
VALIDATION MASSIVE - Phase 12
Valide les QCM générés avec BioBERT (seuil 0.4)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Ajoute le chemin pour importer biobert_client
sys.path.append(str(Path(__file__).parent.parent))

from ai_generation.biobert_client import BioBERTClient

# Configuration
INPUT_FILE = Path("src/data/questions/generated_massive.json")
OUTPUT_FILE = Path("src/data/questions/validated_massive.json")
REJECTED_FILE = Path("src/data/questions/rejected_massive.json")
THRESHOLD = 0.4  # Seuil abaissé pour génération massive
LOG_FILE = Path("logs/pipeline.log")

def main():
    print("="*60)
    print("🔬 VALIDATION MASSIVE BioBERT - Phase 12")
    print("="*60)
    
    # Charge QCM générés
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        qcms = json.load(f)
    
    print(f"\n📘 {len(qcms)} QCM à valider")
    print(f"🎯 Seuil BioBERT : {THRESHOLD}\n")
    
    # Log (recommandation 2)
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Validation START: {len(qcms)} QCM\n")
    
    # Init BioBERT
    print("🧠 Chargement BioBERT...")
    client = BioBERTClient()
    print("   ✓ Modèle chargé\n")
    
    validated = []
    rejected = []
    
    print("🔄 Validation en cours...\n")
    
    for i, qcm in enumerate(qcms, 1):
        text = qcm.get("text", "")
        explanation = qcm.get("explanation", "")
        
        # Calcule score
        full_text = f"{text} {explanation}"
        score = client.score_question(full_text, qcm.get("source_pdf", ""))
        
        qcm["biomedical_score"] = round(score, 3)
        
        if score >= THRESHOLD:
            validated.append(qcm)
        else:
            rejected.append(qcm)
        
        if i % 50 == 0:
            print(f"   ... {i}/{len(qcms)} validés ({len(validated)} OK / {len(rejected)} KO)")
    
    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)
    
    with open(REJECTED_FILE, "w", encoding="utf-8") as f:
        json.dump(rejected, f, ensure_ascii=False, indent=2)
    
    # Log (recommandation 2)
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Validation END: {len(validated)} validated, {len(rejected)} rejected\n")
    
    # Statistiques
    success_rate = len(validated) / len(qcms) * 100 if qcms else 0
    avg_score = sum(q["biomedical_score"] for q in validated) / len(validated) if validated else 0
    
    print(f"\n{'='*60}")
    print(f"✅ VALIDATION TERMINÉE")
    print(f"{'='*60}")
    print(f"\n📊 RÉSULTATS\n")
    print(f"   QCM validés : {len(validated)}/{len(qcms)} ({success_rate:.1f}%)")
    print(f"   QCM rejetés : {len(rejected)} ({len(rejected)/len(qcms)*100:.1f}%)")
    print(f"   Score moyen (validés) : {avg_score:.3f}")
    print(f"\n💾 Corpus validé : {OUTPUT_FILE}")
    print(f"❌ Rejetés : {REJECTED_FILE}")
    print(f"\n🎯 PROCHAINE ÉTAPE : Fusion avec corpus existant")
    print(f"   python scripts/expansion/merge_with_existing.py")
    print("="*60)

if __name__ == "__main__":
    main()

