#!/usr/bin/env python3

"""
Correction manuelle des alignements problématiques
Identifie et corrige les QCM avec score d'alignement < 0.5
"""

import json
import fitz
from pathlib import Path

def search_in_pdf(pdf_path, search_terms, context_words=20):
    """Cherche les termes dans le PDF et retourne les pages pertinentes"""
    matches = []
    
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text('text').lower()
            
            # Vérifie si tous les termes sont présents
            if all(term.lower() in text for term in search_terms):
                # Calcule un score basique (nombre d'occurrences)
                score = sum(text.count(term.lower()) for term in search_terms)
                matches.append({
                    'page': page_num + 1,
                    'score': score
                })
    
    # Trie par score décroissant
    matches.sort(key=lambda x: -x['score'])
    return matches

def main():
    print("="*60)
    print("🔧 CORRECTION ALIGNEMENTS PROBLÉMATIQUES")
    print("="*60)
    
    # Charge corpus
    corpus_file = Path("src/data/questions/compiled_refined_aligned.json")
    with open(corpus_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data["questions"]
    
    # Identifie les QCM avec alignement faible
    low_alignment = [q for q in questions if q.get("alignment_score", 1.0) < 0.5]
    
    print(f"\n📊 {len(low_alignment)} QCM avec score < 0.5 détectés\n")
    
    corrections = []
    pdf_dir = Path("public/pdfs")
    
    for i, q in enumerate(low_alignment[:10], 1):  # Limite à 10 pour test
        text = q.get("text", "")
        current_pdf = q.get("source_pdf", "")
        current_page = q.get("page_number", 0)
        
        # Extrait mots-clés importants (> 4 caractères)
        words = [w for w in text.split() if len(w) > 4 and w.isalpha()]
        keywords = words[:5]  # Top 5 mots
        
        if not keywords:
            continue
        
        # Cherche dans le cours principal
        pdf_path = pdf_dir / "Prepaconcoursiade-Complet.pdf"
        if pdf_path.exists():
            matches = search_in_pdf(pdf_path, keywords)
            
            if matches and matches[0]['page'] != current_page:
                suggested_page = matches[0]['page']
                corrections.append({
                    'chunk_id': q.get('chunk_id'),
                    'question': text[:80],
                    'current_page': current_page,
                    'suggested_page': suggested_page,
                    'keywords': keywords,
                    'confidence': matches[0]['score']
                })
                
                print(f"{i}. {text[:60]}...")
                print(f"   Actuel: page {current_page} (score {q.get('alignment_score', 0):.3f})")
                print(f"   Suggéré: page {suggested_page} (conf {matches[0]['score']})")
                print()
    
    # Sauvegarde rapport
    report_file = Path("reports/alignment_corrections.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            'total_low_alignment': len(low_alignment),
            'corrections_suggested': corrections
        }, f, ensure_ascii=False, indent=2)
    
    print(f"{'='*60}")
    print(f"💾 Rapport sauvegardé : {report_file}")
    print(f"📊 {len(corrections)} corrections suggérées")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

