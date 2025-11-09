#!/usr/bin/env python3

"""
GÉNÉRATION MASSIVE OPTIMISÉE - Phase 12
Version optimisée avec:
- Timeout 180s (au lieu de 60s)
- 2 workers (au lieu de 4) pour moins saturer Ollama
- 2 QCM par page (au lieu de 3) pour pages complexes
- Retry logic améliorée
"""

import json
import requests
import sys
import os
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

# Configuration OPTIMISÉE
PAGES_DIR = Path("src/data/raw/pages")
METADATA_FILE = Path("src/data/raw/pages_metadata.json")
OUTPUT_FILE = Path("src/data/questions/generated_massive.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"
QCM_PER_PAGE = 2  # ✅ Réduit de 3 à 2
MAX_WORKERS = 2  # ✅ Réduit de 4 à 2
TIMEOUT = 180  # ✅ Augmenté de 60 à 180 secondes
MAX_RETRIES = 2  # ✅ Nombre de tentatives

PROMPT_TEMPLATE = """Tu es un expert IADE. À partir de ce texte de cours, génère EXACTEMENT 2 QCM.

CONSIGNES STRICTES:
• 2 questions différentes sur des concepts distincts
• 4 options par question (A, B, C, D)
• 1 seule bonne réponse
• Explication claire et concise (2-3 lignes)
• Format JSON strict

CONTEXTE:
{context}

Retourne UNIQUEMENT ce format JSON (rien d'autre):
[
  {{
    "text": "Quelle est la question ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 2,
    "explanation": "Explication claire de la bonne réponse."
  }},
  {{
    "text": "Seconde question ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 1,
    "explanation": "Explication de la seconde réponse."
  }}
]"""

def generate_for_page(page_data: dict, retry=0) -> list:
    """Génère QCM pour une page avec retry logic."""
    page_id = page_data["page_id"]
    page_file = PAGES_DIR / page_data["file"]
    
    try:
        # Lecture du contenu
        with open(page_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        if len(content) < 50:
            return []
        
        # Prompt
        prompt = PROMPT_TEMPLATE.format(context=content)
        
        # Appel Ollama avec timeout augmenté
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=TIMEOUT  # ✅ 180s au lieu de 60s
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.status_code}")
        
        # Parse réponse
        result = response.json()
        generated_text = result.get("response", "").strip()
        
        # Parse JSON
        # Gère {"QCM": [...]} ou directement [...]
        try:
            parsed = json.loads(generated_text)
            if isinstance(parsed, dict):
                qcms = parsed.get("QCM", parsed.get("questions", []))
            else:
                qcms = parsed
        except json.JSONDecodeError:
            # Essaye d'extraire JSON entre ```
            if "```json" in generated_text:
                json_str = generated_text.split("```json")[1].split("```")[0].strip()
                parsed = json.loads(json_str)
                qcms = parsed if isinstance(parsed, list) else parsed.get("QCM", [])
            elif "```" in generated_text:
                json_str = generated_text.split("```")[1].split("```")[0].strip()
                qcms = json.loads(json_str)
            else:
                raise
        
        # Enrichit les QCM
        for i, qcm in enumerate(qcms):
            qcm["id"] = f"{page_id}_q{i+1}"
            qcm["source_pdf"] = page_data["pdf_name"]
            qcm["page"] = page_data["page_num"]
            qcm["page_id"] = page_id
            qcm["module_id"] = "unknown"  # À classifier plus tard
            qcm["difficulty"] = "medium"
            qcm["mode"] = "revision"
            qcm["generation_method"] = "massive_optimized"
        
        return qcms[:QCM_PER_PAGE]  # Limite à 2 QCM
    
    except requests.exceptions.Timeout:
        if retry < MAX_RETRIES:
            print(f"   ⏱️  Timeout {page_id}, tentative {retry+1}/{MAX_RETRIES}")
            time.sleep(5)  # Pause avant retry
            return generate_for_page(page_data, retry + 1)
        else:
            print(f"   ⚠️  Timeout définitif {page_id}")
            return []
    
    except Exception as e:
        if retry < MAX_RETRIES:
            print(f"   ⚠️  Erreur {page_id}, retry {retry+1}/{MAX_RETRIES}")
            time.sleep(5)
            return generate_for_page(page_data, retry + 1)
        else:
            print(f"   ⚠️  Erreur définitive {page_id}: {e}")
            return []

def main():
    print("="*60)
    print("⚡ GÉNÉRATION MASSIVE OPTIMISÉE - Phase 12")
    print("="*60)
    print("\n✅ OPTIMISATIONS:")
    print(f"   • Timeout: {TIMEOUT}s (au lieu de 60s)")
    print(f"   • Workers: {MAX_WORKERS} (au lieu de 4)")
    print(f"   • QCM/page: {QCM_PER_PAGE} (au lieu de 3)")
    print(f"   • Retries: {MAX_RETRIES}\n")
    
    # Charge métadonnées pages
    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)
    
    pages = metadata["pages"]
    
    # Charge QCM existants si on relance
    existing_qcms = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r") as f:
            existing_qcms = json.load(f)
        existing_page_ids = {q["page_id"] for q in existing_qcms}
        pages = [p for p in pages if p["page_id"] not in existing_page_ids]
        print(f"📘 {len(existing_qcms)} QCM existants, {len(pages)} pages restantes\n")
    
    # Support --range pour génération par batch
    if "--range" in sys.argv:
        idx = sys.argv.index("--range")
        start = int(sys.argv[idx + 1])
        end = int(sys.argv[idx + 2])
        pages = pages[start:end]
        print(f"📘 Batch [{start}:{end}] = {len(pages)} pages")
    else:
        print(f"📘 {len(pages)} pages à traiter")
    
    print(f"🎯 Objectif : {len(pages) * QCM_PER_PAGE} QCM\n")
    
    # Log
    log_file = Path("logs/pipeline.log")
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Génération OPTIMISÉE START: {len(pages)} pages\n")
    
    all_qcms = existing_qcms.copy()
    failed = 0
    
    print("🔄 Génération en cours (optimisée)...\n")
    
    # Parallélisation réduite (2 workers)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(generate_for_page, page): page for page in pages}
        
        with tqdm(total=len(pages), desc="   Progression") as pbar:
            for future in as_completed(futures):
                try:
                    qcms = future.result()
                    if qcms:
                        all_qcms.extend(qcms)
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                pbar.update(1)
    
    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_qcms, f, ensure_ascii=False, indent=2)
    
    # Log
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Phase 12 - Génération OPTIMISÉE END: {len(all_qcms)} QCM, {failed} failed\n")
    
    # Statistiques
    success_rate = (len(pages) - failed) / len(pages) * 100 if pages else 0
    print(f"\n{'='*60}")
    print(f"✅ GÉNÉRATION OPTIMISÉE TERMINÉE")
    print(f"{'='*60}")
    print(f"\n📊 RÉSULTATS\n")
    print(f"   QCM générés : {len(all_qcms)}")
    print(f"   Pages traitées : {len(pages) - failed}/{len(pages)} ({success_rate:.1f}%)")
    print(f"   Pages échouées : {failed}")
    if pages:
        print(f"   Moyenne QCM/page : {len(all_qcms)/len(pages):.2f}")
    print(f"\n💾 Corpus brut : {OUTPUT_FILE}")
    print(f"📝 Log : {log_file}")
    print(f"\n🎯 PROCHAINE ÉTAPE : Validation BioBERT")
    print(f"   python scripts/expansion/validate_massive.py")
    print("="*60)

if __name__ == "__main__":
    main()

