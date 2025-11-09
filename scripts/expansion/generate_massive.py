#!/usr/bin/env python3

"""
GÉNÉRATION MASSIVE - Phase 12
Génère 3 QCM par page avec Ollama Mistral
"""

import json
import requests
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PAGES_DIR = Path("src/data/raw/pages")
METADATA_FILE = Path("src/data/raw/pages_metadata.json")
OUTPUT_FILE = Path("src/data/questions/generated_massive.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"
QCM_PER_PAGE = 3
MAX_WORKERS = 4  # Parallélisation

PROMPT_TEMPLATE = """Tu es un expert IADE. À partir de ce texte de cours, génère EXACTEMENT 3 QCM.

CONSIGNES STRICTES:
• 3 questions différentes sur des concepts distincts
• 4 options par question (A, B, C, D)
• 1 seule réponse correcte par question
• Explication médicale précise (80-150 mots)
• Vocabulaire rigoureux (IADE/anesthésie/réanimation)
• Questions factuelles (pas d'opinions)

TEXTE SOURCE:
{text}

FORMAT DE SORTIE (JSON strict):
[
  {{
    "text": "Question 1 ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 2,
    "explanation": "Explication détaillée..."
  }},
  {{
    "text": "Question 2 ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 0,
    "explanation": "Explication détaillée..."
  }},
  {{
    "text": "Question 3 ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 1,
    "explanation": "Explication détaillée..."
  }}
]

Réponds UNIQUEMENT avec le JSON (pas de texte avant/après).
"""

def generate_qcm_for_page(page_data):
    """Génère 3 QCM pour une page"""
    page_id = page_data["page_id"]
    page_file = PAGES_DIR / page_data["file"]
    
    # Charge le texte
    with open(page_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Limite à 2000 caractères pour ne pas saturer Ollama
    text = text[:2000]
    
    # Génère avec Ollama
    prompt = PROMPT_TEMPLATE.format(text=text)
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 1500
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        raw_text = result.get("response", "[]")
        
        # Parse JSON
        import re
        json_match = re.search(r'\[[\s\S]*\]', raw_text)
        if json_match:
            qcms = json.loads(json_match.group())
            
            # Enrichit avec métadonnées
            for qcm in qcms:
                qcm["page_id"] = page_id
                qcm["source_pdf"] = page_data["pdf"]
                qcm["page_number"] = page_data["page_number"]
                qcm["generation_method"] = "massive_v1"
            
            return qcms
        else:
            return []
    
    except Exception as e:
        print(f"   ⚠️  Erreur {page_id}: {e}")
        return []

def main():
    print("="*60)
    print("⚡ GÉNÉRATION MASSIVE - Phase 12")
    print("="*60)
    
    # Charge métadonnées pages
    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)
    
    pages = metadata["pages"]
    print(f"\n📘 {len(pages)} pages à traiter")
    print(f"🎯 Objectif : {len(pages) * QCM_PER_PAGE} QCM\n")
    
    all_qcms = []
    failed = 0
    
    print("🔄 Génération en cours (parallèle)...\n")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(generate_qcm_for_page, page): page for page in pages}
        
        for future in tqdm(as_completed(futures), total=len(pages), desc="   Progression"):
            try:
                qcms = future.result()
                if qcms:
                    all_qcms.extend(qcms)
                else:
                    failed += 1
            except Exception as e:
                failed += 1
    
    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_qcms, f, ensure_ascii=False, indent=2)
    
    # Statistiques
    print(f"\n{'='*60}")
    print(f"✅ GÉNÉRATION TERMINÉE")
    print(f"{'='*60}")
    print(f"\n📊 RÉSULTATS\n")
    print(f"   QCM générés : {len(all_qcms)}")
    print(f"   Pages traitées : {len(pages) - failed}/{len(pages)} ({(len(pages)-failed)/len(pages)*100:.1f}%)")
    print(f"   Pages échouées : {failed}")
    print(f"   Moyenne QCM/page : {len(all_qcms)/len(pages):.2f}")
    print(f"\n💾 Corpus brut : {OUTPUT_FILE}")
    print(f"\n🎯 PROCHAINE ÉTAPE : Validation BioBERT")
    print(f"   python scripts/expansion/validate_massive.py")
    print("="*60)

if __name__ == "__main__":
    main()

