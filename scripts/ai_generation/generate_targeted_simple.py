#!/usr/bin/env python3

"""
GÉNÉRATION CIBLÉE SIMPLIFIÉE
Version simplifiée avec feedback immédiat et gestion robuste
"""

import json
import requests
from pathlib import Path
import time
import sys

# Configuration
OUTPUT_FILE = Path("src/data/questions/generated_targeted.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"
TIMEOUT = 90

# Modules prioritaires (réduits selon recommandation utilisateur)
MODULES = {
    "ventilation": {
        "count": 10,
        "keywords": "intubation, PEEP, ventilation mécanique, modes ventilatoires, courbes",
        "context": "gestion des voies aériennes et ventilation artificielle"
    },
    "pediatrie": {
        "count": 10,
        "keywords": "enfant, nouveau-né, score Apgar, dosage pédiatrique",
        "context": "anesthésie pédiatrique et réanimation néonatale"
    },
    "monitorage": {
        "count": 8,
        "keywords": "capnographie, ECG, SpO2, monitoring, cathéter artériel",
        "context": "surveillance anesthésique et monitorage"
    },
    "pharma_opioides": {
        "count": 6,
        "keywords": "morphine, fentanyl, naloxone, opioïdes",
        "context": "pharmacologie des opioïdes en anesthésie"
    },
    "legislation": {
        "count": 6,
        "keywords": "loi, consentement, rôle IDE, rôle IADE, déontologie",
        "context": "cadre légal de l'anesthésie et rôle de l'IADE"
    }
}

PROMPT = """Tu es un expert IADE. Génère 2 QCM sur : {module_name}

Mots-clés à utiliser : {keywords}
Contexte : {context}

Retourne UNIQUEMENT un JSON array strict (rien d'autre):
[
  {{
    "text": "Question précise ?",
    "options": ["A", "B", "C", "D"],
    "correctAnswer": 2,
    "explanation": "Explication claire et détaillée."
  }}
]"""

def generate_qcm(module_id, config):
    """Génère des QCM pour un module."""
    print(f"\n🔄 {module_id.upper()} (+{config['count']} QCM)")
    
    qcms = []
    batches = (config["count"] + 1) // 2
    
    for batch in range(batches):
        print(f"   Batch {batch+1}/{batches}...", end=" ", flush=True)
        
        try:
            prompt = PROMPT.format(
                module_name=module_id.replace("_", " ").title(),
                keywords=config["keywords"],
                context=config["context"]
            )
            
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": prompt, "stream": False},
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                print(f"❌ Ollama error {response.status_code}")
                continue
            
            result = response.json()
            text = result.get("response", "").strip()
            
            # Parse JSON robuste
            try:
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(text)
                batch_qcms = parsed if isinstance(parsed, list) else parsed.get("questions", parsed.get("QCM", []))
                
                # Enrichit
                for i, qcm in enumerate(batch_qcms):
                    qcm["id"] = f"{module_id}_targeted_{batch}_{i}"
                    qcm["module_id"] = module_id
                    qcm["difficulty"] = "medium"
                    qcm["mode"] = "revision"
                    qcm["generation_method"] = "targeted_simple"
                    qcm["source_pdf"] = "Prepaconcoursiade-Complet.pdf"
                    qcm["page"] = 1
                    qcms.append(qcm)
                
                print(f"✅ {len(batch_qcms)} QCM")
                
            except Exception as e:
                print(f"❌ Parse error: {e}")
                continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ {e}")
            continue
    
    return qcms

def main():
    print("="*60)
    print("🎯 GÉNÉRATION CIBLÉE SIMPLIFIÉE")
    print("="*60)
    print()
    
    total = sum(m["count"] for m in MODULES.values())
    print(f"📊 {len(MODULES)} modules prioritaires")
    print(f"🎯 Objectif : +{total} QCM")
    
    all_qcms = []
    
    for module_id, config in MODULES.items():
        qcms = generate_qcm(module_id, config)
        all_qcms.extend(qcms)
    
    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_qcms, f, ensure_ascii=False, indent=2)
    
    print()
    print("="*60)
    print("✅ GÉNÉRATION TERMINÉE")
    print("="*60)
    print(f"\n📊 QCM générés : {len(all_qcms)}/{total}")
    print(f"💾 Fichier : {OUTPUT_FILE}")
    print("="*60)

if __name__ == "__main__":
    main()

