#!/usr/bin/env python3
"""
Phase 10 - Refinement QCM
Réécrit les questions sous-optimales via Ollama
"""

import json
import time
from pathlib import Path
from ollama import Client
from tqdm import tqdm

def refine_qcm(client, question):
    """Réécrit un QCM pour améliorer clarté et plausibilité"""
    
    prompt_system = """Tu es un expert IADE et rédacteur pédagogique.
Améliore ce QCM en rendant :
1. La question plus claire et précise
2. Les 4 options plausibles mais distinctes
3. L'explication plus structurée et pédagogique

GARDE la même réponse correcte et le même sens médical.
Retourne UNIQUEMENT un JSON : {"text": "...", "options": [...], "explanation": "..."}"""
    
    prompt_user = f"""QCM actuel :
Question : {question['text']}
Options : {json.dumps(question['options'], ensure_ascii=False)}
Réponse correcte : {question['options'][question['correctAnswer']]}
Explication : {question['explanation']}

Raisons de révision : {', '.join(question.get('refinement_reasons', ['qualité']))}

Améliore ce QCM."""
    
    try:
        response = client.chat(
            model='mistral:latest',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': prompt_user}
            ],
            format='json',
            options={'temperature': 0.7, 'num_predict': 600}
        )
        
        content = response['message']['content'].strip()
        refined = json.loads(content)
        
        # Validation format
        if ('text' in refined and 'options' in refined and 
            len(refined['options']) == 4 and 'explanation' in refined):
            
            # Garde metadata original
            result = question.copy()
            result['text'] = refined['text']
            result['options'] = refined['options']
            result['explanation'] = refined['explanation']
            result['refined'] = True
            result['refinement_date'] = time.strftime('%Y-%m-%d')
            
            return result
        
        return None
        
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)[:50]}")
        return None

def main():
    print("="*60)
    print("REFINEMENT QCM - RÉÉCRITURE INTELLIGENTE")
    print("="*60)
    
    # Charge questions à réviser
    input_path = Path("src/data/questions/to_refine.json")
    
    if not input_path.exists():
        print("\n❌ Fichier to_refine.json introuvable")
        print("   Lancez d'abord : python scripts/reports/filter_low_quality.py")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        to_refine = json.load(f)
    
    print(f"\n📊 {len(to_refine)} questions à raffiner")
    
    if len(to_refine) == 0:
        print("\n✅ Aucune question à raffiner ! Qualité déjà optimale.")
        return
    
    # Client Ollama
    client = Client()
    
    # Refinement
    refined = []
    failed = 0
    
    print(f"\n🚀 Démarrage refinement...\n")
    
    for q in tqdm(to_refine, desc="Refinement", unit="QCM"):
        result = refine_qcm(client, q)
        
        if result:
            refined.append(result)
        else:
            failed += 1
            # Garde l'original si échec
            refined.append(q)
    
    # Stats
    success_rate = (len(refined) - failed) / len(to_refine) * 100 if to_refine else 0
    
    print(f"\n📊 RÉSULTATS REFINEMENT")
    print(f"  Questions traitées  : {len(to_refine)}")
    print(f"  Succès              : {len(refined) - failed}")
    print(f"  Échecs              : {failed}")
    print(f"  Taux succès         : {success_rate:.1f}%")
    
    # Sauvegarde
    output_path = Path("src/data/questions/refined.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(refined, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Questions raffinées sauvegardées : {output_path}")
    
    print(f"\n🚀 PROCHAINES ÉTAPES")
    print(f"  1. Re-valider avec BioBERT")
    print(f"  2. Comparer scores avant/après")
    print(f"  3. Merger si amélioration confirmée")
    
    print(f"\n{'='*60}")
    print(f"✅ REFINEMENT TERMINÉ")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

