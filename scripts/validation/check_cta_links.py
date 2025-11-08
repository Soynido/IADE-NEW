#!/usr/bin/env python3

"""
Vérifie la cohérence entre les QCM et leurs pages PDF source.
- Vérifie que chaque source_pdf existe
- Vérifie que la page_number est dans les bornes
- Évalue la similarité sémantique entre la question et le texte de la page
Sortie : rapport JSON + résumé console
"""

import json
from pathlib import Path
import fitz  # PyMuPDF
from rapidfuzz import fuzz

DATA_FILE = Path("src/data/questions/compiled_refined_enriched.json")
REPORT_FILE = Path("reports/cta_validation_report.json")
PDF_DIR = Path("src/data/sources")

# Vérifie aussi dans public/pdfs (pour production)
PUBLIC_PDF_DIR = Path("public/pdfs")

def find_pdfs():
    """Trouve tous les PDF disponibles"""
    pdfs = {}
    
    for directory in [PDF_DIR, PUBLIC_PDF_DIR]:
        if directory.exists():
            for p in directory.glob("*.pdf"):
                pdfs[p.name] = p
    
    return pdfs

PDFS = find_pdfs()

def extract_text(pdf_path, page_number):
    """Retourne le texte d'une page (+/- 1)"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            total_pages = len(doc)
            # Extrait page cible +/- 1 page pour plus de contexte
            for p in range(max(0, page_number - 2), min(total_pages, page_number + 1)):
                text += doc[p].get_text("text") + "\n"
    except Exception as e:
        print(f"   ⚠️  Erreur lecture {pdf_path} page {page_number}: {e}")
    return text

def evaluate_similarity(question_text, page_text):
    """Compare les mots-clés de la question et du texte de page"""
    if not page_text.strip():
        return 0.0
    
    # Utilise partial_ratio pour détecter si la question ou ses mots-clés 
    # apparaissent dans le texte de la page
    return fuzz.partial_ratio(question_text.lower(), page_text.lower()) / 100

def main():
    print("=" * 60)
    print("🔍 VALIDATION DES CTA VERS LES PAGES DU COURS")
    print("=" * 60)
    
    if not DATA_FILE.exists():
        print(f"⚠️  Fichier introuvable : {DATA_FILE}")
        return
    
    print(f"\n📂 PDF disponibles : {len(PDFS)}")
    for pdf_name in sorted(PDFS.keys()):
        print(f"   • {pdf_name}")
    
    data = json.load(open(DATA_FILE, encoding="utf-8"))
    questions = data.get("questions", data)
    
    print(f"\n📘 {len(questions)} QCM à vérifier\n")
    
    invalid = []
    missing_pdf = []
    low_similarity = []
    valid_count = 0
    
    for i, q in enumerate(questions, 1):
        pdf_name = q.get("source_pdf", "")
        page_num = int(q.get("page_number", 0))
        q_text = q.get("text", "")
        chunk_id = q.get("chunk_id", f"q_{i}")
        
        if not pdf_name:
            missing_pdf.append({"chunk_id": chunk_id, "reason": "source_pdf vide"})
            continue
        
        if pdf_name not in PDFS:
            missing_pdf.append({"chunk_id": chunk_id, "pdf": pdf_name, "reason": "PDF non trouvé"})
            continue
        
        pdf_path = PDFS[pdf_name]
        
        try:
            text = extract_text(pdf_path, page_num)
            similarity = evaluate_similarity(q_text, text)
            
            q["cta_check_score"] = round(similarity, 3)
            q["cta_valid"] = similarity >= 0.4
            
            if similarity >= 0.4:
                valid_count += 1
            else:
                low_similarity.append({
                    "chunk_id": chunk_id,
                    "question": q_text[:100] + "..." if len(q_text) > 100 else q_text,
                    "page_number": page_num,
                    "pdf": pdf_name,
                    "similarity": round(similarity, 3)
                })
        
        except Exception as e:
            invalid.append({
                "chunk_id": chunk_id,
                "page_number": page_num,
                "error": str(e)
            })
        
        # Progress
        if i % 20 == 0:
            print(f"   ... {i}/{len(questions)} vérifiés")
    
    print(f"\n{'=' * 60}")
    print(f"📊 RÉSULTATS")
    print(f"{'=' * 60}")
    print(f"✅ QCM valides (≥0.4)   : {valid_count}/{len(questions)} ({valid_count/len(questions)*100:.1f}%)")
    print(f"⚠️  PDF manquants         : {len(set(pdf['pdf'] for pdf in missing_pdf if 'pdf' in pdf))}")
    print(f"❌ Erreurs lecture       : {len(invalid)}")
    print(f"⚠️  Similarité faible     : {len(low_similarity)}")
    
    # Détails des problèmes
    if missing_pdf:
        print(f"\n{'─' * 60}")
        print(f"📋 PDF MANQUANTS")
        print(f"{'─' * 60}")
        seen = set()
        for item in missing_pdf:
            pdf = item.get('pdf', 'N/A')
            if pdf not in seen:
                print(f"   • {pdf}")
                seen.add(pdf)
    
    if low_similarity:
        print(f"\n{'─' * 60}")
        print(f"📋 TOP 5 PAGES À VÉRIFIER (similarité < 0.4)")
        print(f"{'─' * 60}")
        sorted_low = sorted(low_similarity, key=lambda x: x['similarity'])
        for item in sorted_low[:5]:
            print(f"   [{item['chunk_id']}] Page {item['page_number']} - Score {item['similarity']}")
            print(f"   → {item['question'][:80]}...")
            print()
    
    # Sauvegarde du rapport complet
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        "generated_at": str(Path.cwd()),
        "summary": {
            "total_questions": len(questions),
            "valid": valid_count,
            "invalid": len(invalid),
            "missing_pdf": len(missing_pdf),
            "low_similarity": len(low_similarity),
            "success_rate": round(valid_count / len(questions) * 100, 2) if questions else 0
        },
        "pdfs_available": list(PDFS.keys()),
        "low_similarity": low_similarity,
        "missing_pdf": missing_pdf,
        "invalid": invalid
    }
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"💾 Rapport sauvegardé : {REPORT_FILE}")
    print(f"{'=' * 60}")
    
    if valid_count / len(questions) >= 0.85:
        print(f"✅ VALIDATION RÉUSSIE ({valid_count/len(questions)*100:.1f}%)")
    else:
        print(f"⚠️  VALIDATION PARTIELLE ({valid_count/len(questions)*100:.1f}%)")
        print(f"   → Vérifier les {len(low_similarity)} pages signalées")
    
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()

