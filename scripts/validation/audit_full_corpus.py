#!/usr/bin/env python3

"""
AUDIT COMPLET DU CORPUS - Phase 11
Vérifie CHAQUE question et s'assure que la page source contient réellement
les informations de la question. Corrige automatiquement les erreurs.
"""

import json
import fitz
from pathlib import Path
from collections import defaultdict
import re

# Configuration
CORPUS_FILE = Path("src/data/questions/compiled_refined_aligned.json")
OUTPUT_FILE = Path("src/data/questions/compiled_verified.json")
REPORT_FILE = Path("reports/full_corpus_audit_report.json")
PDF_DIR = Path("public/pdfs")

def extract_keywords(text):
    """Extrait les mots-clés significatifs d'un texte"""
    # Supprime ponctuation et mots courts
    words = re.findall(r'\b\w+\b', text.lower())
    # Filtre mots significatifs (>= 4 caractères, pas des stopwords basiques)
    stopwords = {'dans', 'pour', 'avec', 'être', 'avoir', 'cette', 'sont', 'plus', 'quelle', 'quel', 'quels', 'quelles', 'une', 'des', 'les', 'sur', 'par'}
    keywords = [w for w in words if len(w) >= 4 and w not in stopwords]
    return keywords[:10]  # Top 10

def search_best_page(pdf_path, keywords, current_page=None):
    """Trouve la meilleure page pour un ensemble de mots-clés"""
    if not pdf_path.exists():
        return None, 0
    
    best_match = {'page': current_page or 1, 'score': 0}
    
    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text('text').lower()
                
                # Compte combien de keywords sont présents
                score = sum(1 for kw in keywords if kw in text)
                
                # Bonus si plusieurs occurrences
                score += sum(text.count(kw) - 1 for kw in keywords if kw in text)
                
                if score > best_match['score']:
                    best_match = {'page': page_num + 1, 'score': score}
    
    except Exception as e:
        print(f"   ⚠️  Erreur lecture {pdf_path.name}: {e}")
        return None, 0
    
    return best_match['page'], best_match['score']

def verify_page_content(pdf_path, page_num, keywords):
    """Vérifie si une page contient bien les mots-clés"""
    if not pdf_path.exists():
        return False, 0
    
    try:
        with fitz.open(pdf_path) as doc:
            if page_num < 1 or page_num > len(doc):
                return False, 0
            
            page = doc[page_num - 1]
            text = page.get_text('text').lower()
            
            # Compte les mots-clés présents
            found = sum(1 for kw in keywords if kw in text)
            score = found / len(keywords) if keywords else 0
            
            # Considère valide si >= 30% des keywords présents
            return score >= 0.3, score
    
    except Exception as e:
        return False, 0

def main():
    print("="*60)
    print("🔍 AUDIT COMPLET DU CORPUS - Vérification exhaustive")
    print("="*60)
    
    # Charge corpus
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data["questions"]
    print(f"\n📘 {len(questions)} QCM à vérifier")
    
    # Statistiques
    stats = {
        'total': len(questions),
        'valid': 0,
        'corrected': 0,
        'missing_pdf': 0,
        'no_match': 0
    }
    
    corrections = []
    no_match = []
    
    print("\n🔄 Vérification en cours...\n")
    
    for i, q in enumerate(questions, 1):
        text = q.get("text", "")
        explanation = q.get("explanation", "")
        full_text = text + " " + str(explanation)[:200]
        
        current_pdf = q.get("source_pdf", "")
        current_page = q.get("page_number", 0)
        chunk_id = q.get("chunk_id", f"q_{i}")
        
        # Extrait keywords
        keywords = extract_keywords(full_text)
        
        if not current_pdf:
            stats['missing_pdf'] += 1
            continue
        
        pdf_path = PDF_DIR / current_pdf
        
        if not pdf_path.exists():
            stats['missing_pdf'] += 1
            continue
        
        # Vérifie la page actuelle
        is_valid, current_score = verify_page_content(pdf_path, current_page, keywords)
        
        if is_valid:
            stats['valid'] += 1
            q['page_verified'] = True
            q['page_verification_score'] = round(current_score, 3)
        else:
            # Cherche la meilleure page
            best_page, best_score = search_best_page(pdf_path, keywords, current_page)
            
            if best_score > 0 and best_page != current_page:
                # Correction trouvée
                corrections.append({
                    'chunk_id': chunk_id,
                    'question': text[:100],
                    'old_page': current_page,
                    'new_page': best_page,
                    'old_score': round(current_score, 3),
                    'new_score': best_score,
                    'keywords': keywords[:3]
                })
                
                q['source_pdf'] = current_pdf
                q['page_number'] = best_page
                q['page_verified'] = True
                q['page_verification_score'] = round(best_score / len(keywords) if keywords else 0, 3)
                q['corrected_automatically'] = True
                
                stats['corrected'] += 1
            else:
                # Aucune correspondance trouvée
                no_match.append({
                    'chunk_id': chunk_id,
                    'question': text[:100],
                    'page': current_page,
                    'keywords': keywords[:3]
                })
                
                q['page_verified'] = False
                q['needs_manual_review'] = True
                stats['no_match'] += 1
        
        # Progress
        if i % 20 == 0:
            print(f"   ... {i}/{len(questions)} vérifiés")
    
    # Sauvegarde corpus corrigé
    data['questions'] = questions
    data['verification_version'] = 'v1.2.1_verified'
    data['total_questions'] = len(questions)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Rapport
    report = {
        'summary': stats,
        'success_rate': round(stats['valid'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0,
        'correction_rate': round(stats['corrected'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0,
        'corrections': corrections[:20],  # Top 20
        'no_match': no_match[:10]  # Top 10 problématiques
    }
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Affichage
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS DE L'AUDIT")
    print(f"{'='*60}")
    print(f"\n✅ QCM valides (sans correction)  : {stats['valid']}/{stats['total']} ({stats['valid']/stats['total']*100:.1f}%)")
    print(f"🔧 QCM corrigés automatiquement   : {stats['corrected']}/{stats['total']} ({stats['corrected']/stats['total']*100:.1f}%)")
    print(f"❌ QCM sans correspondance        : {stats['no_match']}/{stats['total']} ({stats['no_match']/stats['total']*100:.1f}%)")
    print(f"⚠️  PDF manquants                  : {stats['missing_pdf']}")
    
    if corrections:
        print(f"\n{'─'*60}")
        print(f"🔧 TOP 5 CORRECTIONS")
        print(f"{'─'*60}")
        for corr in corrections[:5]:
            print(f"\n• {corr['question']}...")
            print(f"  Page {corr['old_page']} → {corr['new_page']} (score {corr['old_score']} → {corr['new_score']})")
            print(f"  Keywords: {', '.join(corr['keywords'])}")
    
    if no_match:
        print(f"\n{'─'*60}")
        print(f"⚠️  TOP 3 QCM À RÉVISER MANUELLEMENT")
        print(f"{'─'*60}")
        for item in no_match[:3]:
            print(f"\n• {item['question']}...")
            print(f"  Page actuelle: {item['page']}")
            print(f"  Keywords: {', '.join(item['keywords'])}")
    
    print(f"\n{'='*60}")
    print(f"💾 Corpus corrigé : {OUTPUT_FILE}")
    print(f"📊 Rapport complet : {REPORT_FILE}")
    print(f"{'='*60}")
    
    success_rate = (stats['valid'] + stats['corrected']) / stats['total'] * 100
    
    if success_rate >= 95:
        print(f"✅ AUDIT EXCELLENT ({success_rate:.1f}% valide)")
    elif success_rate >= 85:
        print(f"✅ AUDIT BON ({success_rate:.1f}% valide)")
    else:
        print(f"⚠️  AUDIT PARTIEL ({success_rate:.1f}% valide)")
        print(f"   → {stats['no_match']} QCM nécessitent une révision manuelle")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

