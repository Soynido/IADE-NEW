#!/usr/bin/env python3

"""
EXTRACTION PAGE PAR PAGE - Phase 12
Découpe les PDF en pages individuelles pour génération massive
"""

import fitz
import json
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# Configuration
PDF_DIR = Path("public/pdfs")
OUTPUT_DIR = Path("src/data/raw/pages")
METADATA_FILE = Path("src/data/raw/pages_metadata.json")
LOG_FILE = Path("logs/pipeline.log")

def extract_page_by_page(pdf_path, pdf_name):
    """Extrait chaque page comme fichier texte séparé"""
    pages_data = []
    
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            # Nettoie le texte
            text = " ".join(text.split())  # Normalise espaces
            
            if len(text.strip()) < 100:  # Skip pages vides
                continue
            
            # Sauvegarde page individuelle
            page_id = f"{pdf_name.replace('.pdf', '')}__page_{page_num + 1:03d}"
            page_file = OUTPUT_DIR / f"{page_id}.txt"
            
            with open(page_file, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Métadonnées
            pages_data.append({
                "page_id": page_id,
                "pdf": pdf_name,
                "page_number": page_num + 1,
                "char_count": len(text),
                "word_count": len(text.split()),
                "file": str(page_file.name)
            })
    
    return pages_data

def main():
    print("="*60)
    print("📚 EXTRACTION PAGE PAR PAGE - Phase 12")
    print("="*60)
    
    # Crée répertoire output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Log (recommandation 2)
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Extraction START\n")
    
    # Liste des PDFs
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    print(f"\n📂 {len(pdf_files)} PDF à traiter\n")
    
    all_pages = []
    
    for pdf_path in pdf_files:
        print(f"📄 {pdf_path.name}...")
        pages = extract_page_by_page(pdf_path, pdf_path.name)
        all_pages.extend(pages)
        print(f"   ✓ {len(pages)} pages extraites\n")
    
    # Sauvegarde métadonnées
    metadata = {
        "total_pages": len(all_pages),
        "pdf_count": len(pdf_files),
        "pages": all_pages
    }
    
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Log (recommandation 2)
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Extraction END: {len(all_pages)} pages\n")
    
    # Statistiques
    total_chars = sum(p["char_count"] for p in all_pages)
    total_words = sum(p["word_count"] for p in all_pages)
    
    print("="*60)
    print("✅ EXTRACTION TERMINÉE")
    print("="*60)
    print(f"\n📊 STATISTIQUES\n")
    print(f"   Pages extraites : {len(all_pages)}")
    print(f"   Caractères total : {total_chars:,}")
    print(f"   Mots total : {total_words:,}")
    print(f"   Moyenne mots/page : {total_words // len(all_pages)}")
    print(f"\n💾 Fichiers : {OUTPUT_DIR}")
    print(f"📊 Métadonnées : {METADATA_FILE}")
    print(f"\n🎯 PROCHAINE ÉTAPE : Génération 3 QCM/page")
    print(f"   → Estimation : {len(all_pages)} × 3 = {len(all_pages) * 3} QCM potentiels")
    print("="*60)

if __name__ == "__main__":
    main()

