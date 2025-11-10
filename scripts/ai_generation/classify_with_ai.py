#!/usr/bin/env python3

"""
CLASSIFICATION IA DES MODULES
Utilise Ollama/Mistral pour classifier les questions "unknown" restantes
"""

import json
import requests
from pathlib import Path
from collections import Counter
import time

# Configuration
INPUT = Path("src/data/questions/compiled_reclassified.json")
OUTPUT = Path("src/data/questions/compiled_fully_classified.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"
TIMEOUT = 30

# Modules valides
MODULES = [
    "cardio", "respiratoire", "neuro", "bases_physio",
    "pharma_opioides", "douleur", "reanimation", "infectio",
    "transfusion", "ventilation", "monitorage", "pediatrie",
    "legislation"
]

CLASSIFICATION_PROMPT = """Tu es un expert en médecine d'anesthésie-réanimation IADE.

Analyse cette question de QCM et détermine à quel module thématique elle appartient.

QUESTION: {question}

EXPLICATION: {explanation}

MODULES POSSIBLES:
- cardio: Cardiologie, hémodynamique, ECG, choc cardiogénique
- respiratoire: Physiologie respiratoire, PaO2, SpO2, poumons
- neuro: Neurologie, Glasgow, PIC, sédation, conscience
- bases_physio: Homéostasie, équilibre acide-base, ions, pH
- pharma_opioides: Morphine, fentanyl, sufentanil, analgésie opioïde
- douleur: Analgésie générale, EVA, paliers OMS, blocs
- reanimation: Choc, catécholamines, remplissage, SDRA
- infectio: Infections, antibiotiques, sepsis, asepsie
- transfusion: Sang, plaquettes, hémoglobine, coagulation
- ventilation: Intubation, ventilation mécanique, PEEP, modes
- monitorage: Capnographie, SpO2, monitoring, cathéters
- pediatrie: Enfants, nouveau-nés, dosages pédiatriques
- legislation: Lois, consentement, déontologie, éthique

Réponds UNIQUEMENT par le nom du module (un seul mot parmi la liste).
Si vraiment impossible à classifier, réponds "unknown".

MODULE:"""

def classify_with_mistral(question_text: str, explanation: str) -> str:
    """Classifie une question avec Mistral."""
    try:
        prompt = CLASSIFICATION_PROMPT.format(
            question=question_text,
            explanation=explanation
        )
        
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            return "unknown"
        
        result = response.json()
        module = result.get("response", "").strip().lower()
        
        # Nettoie la réponse
        module = module.replace("module:", "").strip()
        module = module.replace("**", "").strip()
        module = module.split()[0] if module.split() else "unknown"
        
        # Valide le module
        if module in MODULES:
            return module
        
        return "unknown"
        
    except Exception as e:
        print(f"      ⚠️  Erreur classification: {e}")
        return "unknown"

def main():
    print("="*60)
    print("🤖 CLASSIFICATION IA DES MODULES (Mistral)")
    print("="*60)
    print()
    
    # Charge le corpus
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, list):
        questions = data
    else:
        questions = data.get("questions", data)
    
    # Filtre uniquement les "unknown"
    unknown_questions = [q for q in questions if q.get("module_id") == "unknown"]
    
    print(f"📘 {len(questions)} questions au total")
    print(f"⚠️  {len(unknown_questions)} questions 'unknown' à classifier")
    print()
    
    if len(unknown_questions) == 0:
        print("✅ Aucune question 'unknown', rien à faire !")
        return
    
    print("🤖 Classification IA en cours (Mistral)...")
    print()
    
    classified = 0
    failed = 0
    
    for i, q in enumerate(unknown_questions, 1):
        question_text = q.get("text", "")
        explanation = q.get("explanation", "")
        
        # Affiche progression
        if i % 10 == 0 or i == 1:
            print(f"   ... {i}/{len(unknown_questions)} ({i/len(unknown_questions)*100:.0f}%)")
        
        # Classification
        new_module = classify_with_mistral(question_text, explanation)
        
        if new_module != "unknown":
            # Trouve la question dans le corpus principal
            for original_q in questions:
                if original_q.get("id") == q.get("id"):
                    original_q["module_id"] = new_module
                    classified += 1
                    break
        else:
            failed += 1
        
        # Petite pause pour ne pas surcharger Ollama
        time.sleep(0.5)
    
    # Statistiques finales
    modules_final = Counter(q.get("module_id", "unknown") for q in questions)
    unknown_final = modules_final.get("unknown", 0)
    
    # Sauvegarde
    if isinstance(data, list):
        output_data = questions
    else:
        data["questions"] = questions
        output_data = data
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Rapport
    print()
    print("="*60)
    print("✅ CLASSIFICATION IA TERMINÉE")
    print("="*60)
    print()
    print(f"📊 RÉSULTATS\n")
    print(f"   Questions traitées : {len(unknown_questions)}")
    print(f"   Classifiées avec succès : {classified} ({classified/len(unknown_questions)*100:.1f}%)")
    print(f"   Échecs : {failed} ({failed/len(unknown_questions)*100:.1f}%)")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   Unknown final : {unknown_final} ({unknown_final/len(questions)*100:.1f}%)")
    print()
    print("📋 RÉPARTITION FINALE\n")
    
    for module, count in sorted(modules_final.items(), key=lambda x: -x[1]):
        percent = count / len(questions) * 100
        bar = "█" * int(percent / 2)
        print(f"   {module:20} {count:4} ({percent:5.1f}%) {bar}")
    
    print()
    print(f"💾 Corpus final : {OUTPUT}")
    print("="*60)

if __name__ == "__main__":
    main()

