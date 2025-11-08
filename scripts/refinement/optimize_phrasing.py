#!/usr/bin/env python3

"""
Optimisation linguistique - Phase 10+
Reformule les questions maladroites ou rigides pour améliorer la fluidité
"""

import json
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"

def check_phrasing(question_text):
    """Évalue la fluidité d'une question (0-10)"""
    prompt = f"""Évalue la fluidité linguistique de cette question médicale IADE (0-10).

Question : "{question_text}"

Critères :
- Naturel et fluide : 8-10
- Correct mais rigide : 5-7
- Maladroit ou ambigu : 0-4

Réponds uniquement par un chiffre 0-10."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        score_text = result.get("response", "5").strip()
        
        # Extrait le chiffre
        import re
        match = re.search(r'\d+', score_text)
        if match:
            return int(match.group())
        return 5  # Score neutre par défaut
    except Exception as e:
        print(f"   ⚠️  Erreur évaluation : {e}")
        return 5

def optimize_question(question_text):
    """Reformule une question pour améliorer sa fluidité"""
    prompt = f"""Reformule cette question médicale IADE pour la rendre plus fluide et naturelle, sans changer le sens ni le contenu médical.

Question originale :
"{question_text}"

Réponds uniquement par la question reformulée, sans commentaire."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        return result.get("response", question_text).strip().strip('"')
    except Exception as e:
        print(f"   ⚠️  Erreur reformulation : {e}")
        return question_text

def main():
    print("="*60)
    print("OPTIMISATION LINGUISTIQUE — Phase 10+")
    print("="*60)
    
    # Charge corpus enrichi
    print("\n📂 Chargement corpus v1.1 enrichi...")
    input_file = Path("src/data/questions/compiled_refined_enriched.json")
    if not input_file.exists():
        print("   ⚠️  Fichier non trouvé, utilisation de compiled_refined.json")
        input_file = Path("src/data/questions/compiled_refined.json")
    
    with open(input_file, "r") as f:
        data = json.load(f)
    
    questions = data.get("questions", data)
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Évaluation + optimisation
    print("\n🔧 Analyse linguistique...")
    print("   (Seuil : score < 7 → reformulation)")
    
    to_optimize = []
    scores = []
    
    for i, q in enumerate(questions, 1):
        question_text = q.get("text", "")
        score = check_phrasing(question_text)
        scores.append(score)
        
        if score < 7:
            to_optimize.append(i-1)  # Index
        
        if i % 20 == 0:
            print(f"   ... {i}/{len(questions)} évalués")
    
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"\n📊 Score moyen de fluidité : {avg_score:.1f}/10")
    print(f"   → {len(to_optimize)} questions à optimiser ({len(to_optimize)/len(questions)*100:.1f}%)")
    
    if len(to_optimize) == 0:
        print(f"\n✅ Aucune optimisation nécessaire !")
        return
    
    # Reformulation
    print(f"\n🔄 Reformulation de {len(to_optimize)} questions...")
    optimized = 0
    
    for idx in to_optimize:
        q = questions[idx]
        original = q.get("text")
        
        print(f"   [{idx+1}] Reformulation...", end=" ")
        optimized_text = optimize_question(original)
        
        if optimized_text != original:
            q["text"] = optimized_text
            q["optimization_flag"] = "linguistically_improved"
            optimized += 1
            print("✓")
        else:
            print("⊘ (inchangé)")
    
    print(f"\n   ✓ {optimized} questions reformulées")
    
    # Sauvegarde
    data["questions"] = questions
    data["optimization_applied"] = True
    data["total_questions"] = len(questions)
    
    with open("src/data/questions/compiled_refined_optimized.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ OPTIMISATION LINGUISTIQUE TERMINÉE")
    print(f"{'='*60}")
    print(f"💾 Sauvegardé : compiled_refined_optimized.json")
    print(f"📈 {len(questions)} QCM linguistiquement optimisés")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
