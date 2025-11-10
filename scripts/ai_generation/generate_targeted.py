#!/usr/bin/env python3

"""
GÉNÉRATION CIBLÉE PAR MODULE
Génère des QCM spécifiques pour les modules sous-représentés
"""

import json
import requests
from pathlib import Path
import time
import sys

# Configuration
SOURCE_PDF_DIR = Path("public/pdfs")
OUTPUT_FILE = Path("src/data/questions/generated_targeted.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"
TIMEOUT = 120

# Modules critiques à renforcer
CRITICAL_MODULES = {
    "monitorage": {
        "count": 18,
        "keywords": "capnographie, SpO2, EtCO2, monitoring hémodynamique, cathéter artériel, PVC, Swan-Ganz, BIS, entropie",
        "context": "surveillance anesthésique, paramètres vitaux, monitorage invasif et non-invasif"
    },
    "pharma_opioides": {
        "count": 16,
        "keywords": "morphine, fentanyl, sufentanil, rémifentanil, alfentanil, naloxone, analgésie opioïde",
        "context": "pharmacologie des opioïdes, analgésie peropératoire, antagonistes"
    },
    "ventilation": {
        "count": 14,
        "keywords": "intubation, ventilation mécanique, PEEP, volume courant, modes ventilatoires, compliance",
        "context": "gestion des voies aériennes, ventilation artificielle, réglages du respirateur"
    },
    "legislation": {
        "count": 13,
        "keywords": "loi, consentement éclairé, déontologie, responsabilité, secret professionnel",
        "context": "cadre légal de l'anesthésie, droits du patient, obligations de l'IADE"
    },
    "reanimation": {
        "count": 10,
        "keywords": "choc, catécholamines, remplissage vasculaire, SDRA, défaillance d'organe",
        "context": "réanimation polyvalente, états de choc, support hémodynamique"
    },
    "pediatrie": {
        "count": 10,
        "keywords": "enfant, nouveau-né, dosage pédiatrique, score Apgar, particularités pédiatriques",
        "context": "anesthésie pédiatrique, réanimation néonatale"
    }
}

TARGETED_PROMPT = """Tu es un expert IADE spécialisé en {module_name}.

Génère 2 QCM de qualité sur le thème : {theme}

CONTEXTE THÉMATIQUE: {context}

MOTS-CLÉS À INCLURE: {keywords}

CONSIGNES:
• 2 questions différentes et précises
• 4 options par question (A, B, C, D)
• 1 seule bonne réponse
• Explication détaillée (3-4 lignes minimum)
• Utilise au moins 2 mots-clés dans chaque question
• Niveau IADE (précis et technique)
• Format JSON strict

EXEMPLE DE FORMAT:
[
  {{
    "text": "Question précise avec contexte ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 2,
    "explanation": "Explication détaillée avec justification médicale et références aux recommandations."
  }}
]

Retourne UNIQUEMENT le JSON (rien d'autre):"""

def generate_for_module(module_id: str, module_config: dict) -> list:
    """Génère des QCM pour un module spécifique."""
    qcms = []
    target_count = module_config["count"]
    keywords = module_config["keywords"]
    context = module_config["context"]
    
    print(f"\n   🔄 {module_id.upper()} (objectif: +{target_count} QCM)")
    
    # Génère par batch de 2
    batches = (target_count + 1) // 2
    
    for batch in range(batches):
        try:
            prompt = TARGETED_PROMPT.format(
                module_name=module_id.replace("_", " ").title(),
                theme=module_id,
                context=context,
                keywords=keywords
            )
            
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": prompt, "stream": False},
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                print(f"      ⚠️  Erreur Ollama: {response.status_code}")
                continue
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            # Parse JSON
            try:
                parsed = json.loads(generated_text)
                if isinstance(parsed, dict):
                    batch_qcms = parsed.get("questions", parsed.get("QCM", []))
                else:
                    batch_qcms = parsed
            except json.JSONDecodeError:
                # Essaye d'extraire JSON entre ```
                if "```json" in generated_text:
                    json_str = generated_text.split("```json")[1].split("```")[0].strip()
                    batch_qcms = json.loads(json_str)
                elif "```" in generated_text:
                    json_str = generated_text.split("```")[1].split("```")[0].strip()
                    batch_qcms = json.loads(json_str)
                else:
                    print(f"      ⚠️  Parse JSON échoué")
                    continue
            
            # Enrichit les QCM
            for i, qcm in enumerate(batch_qcms):
                qcm["id"] = f"{module_id}_targeted_{batch}_{i+1}"
                qcm["module_id"] = module_id
                qcm["difficulty"] = "medium"
                qcm["mode"] = "revision"
                qcm["generation_method"] = "targeted"
                qcm["source_pdf"] = "Prepaconcoursiade-Complet.pdf"
                qcm["page"] = 1  # À classifier plus tard
                
                qcms.append(qcm)
            
            print(f"      ✅ Batch {batch+1}/{batches} : {len(batch_qcms)} QCM")
            
            # Pause pour ne pas surcharger
            time.sleep(1)
            
        except Exception as e:
            print(f"      ⚠️  Erreur batch {batch+1}: {e}")
            continue
    
    return qcms

def main():
    print("="*60)
    print("🎯 GÉNÉRATION CIBLÉE - Modules sous-représentés")
    print("="*60)
    print()
    
    # Détermine quels modules générer
    if "--batch" in sys.argv and sys.argv[sys.argv.index("--batch") + 1] == "critical":
        # Génère tous les modules critiques
        modules_to_generate = CRITICAL_MODULES
    elif "--module" in sys.argv:
        # Génère un seul module
        idx = sys.argv.index("--module")
        module_name = sys.argv[idx + 1]
        if module_name in CRITICAL_MODULES:
            modules_to_generate = {module_name: CRITICAL_MODULES[module_name]}
        else:
            print(f"❌ Module '{module_name}' non trouvé")
            return
    else:
        # Par défaut, génère tous
        modules_to_generate = CRITICAL_MODULES
    
    total_target = sum(m["count"] for m in modules_to_generate.values())
    print(f"📊 Modules à renforcer : {len(modules_to_generate)}")
    print(f"🎯 Objectif total : +{total_target} QCM")
    print()
    
    all_qcms = []
    
    # Génère pour chaque module
    for module_id, config in modules_to_generate.items():
        module_qcms = generate_for_module(module_id, config)
        all_qcms.extend(module_qcms)
    
    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_qcms, f, ensure_ascii=False, indent=2)
    
    # Rapport
    print()
    print("="*60)
    print("✅ GÉNÉRATION CIBLÉE TERMINÉE")
    print("="*60)
    print()
    print(f"📊 RÉSULTATS\n")
    print(f"   QCM générés : {len(all_qcms)}/{total_target}")
    print(f"   Taux de réussite : {len(all_qcms)/total_target*100:.1f}%")
    print()
    print("📋 DÉTAIL PAR MODULE\n")
    
    from collections import Counter
    modules_count = Counter(q["module_id"] for q in all_qcms)
    for module, count in sorted(modules_count.items()):
        target = modules_to_generate.get(module, {}).get("count", 0)
        print(f"   {module:20} {count:3}/{target:3} ({count/target*100:.0f}%)")
    
    print()
    print(f"💾 QCM ciblés : {OUTPUT_FILE}")
    print()
    print("🎯 PROCHAINE ÉTAPE : Validation BioBERT")
    print("   python scripts/expansion/validate_massive.py")
    print("="*60)

if __name__ == "__main__":
    main()

