#!/usr/bin/env python3

"""
CLASSIFICATION AUTOMATIQUE DES MODULES
Analyse le texte des QCM pour assigner un module cohérent.
"""

import json
import re
from pathlib import Path
from collections import Counter

# Configuration
INPUT = Path("src/data/questions/compiled_expanded.json")
OUTPUT = Path("src/data/questions/compiled_reclassified.json")

# Dictionnaire de mots-clés thématiques (ordre de priorité décroissant)
KEYWORDS = {
    # Modules spécifiques en premier (plus précis)
    "pharma_opioides": [
        "morphine", "fentanyl", "sufentanil", "rémifentanil", "alfentanil",
        "opioïde", "opiacé", "naloxone", "antagoniste morphinique",
        "palier 3", "OMS analgésie"
    ],
    "monitorage": [
        "capnographie", "oxymétrie", "SpO2", "EtCO2", "BIS", "entropie",
        "monitor", "scope", "cathéter artériel", "PVC", "Swan-Ganz",
        "pression invasive", "thermodilution"
    ],
    "ventilation": [
        "intubation", "extubation", "ventilation mécanique", "PEEP", "PEP",
        "volume courant", "Vt", "FR", "fréquence respiratoire",
        "mode ventilatoire", "VAC", "VSAI", "VACI", "pression plateau",
        "compliance", "résistance respiratoire", "auto-PEEP"
    ],
    "neuro": [
        "cerveau", "coma", "crâne", "épilepsie", "encéphal", "Glasgow", "GCS",
        "PIC", "pression intracrânienne", "PPC", "perfusion cérébrale",
        "AVC", "hémorragie méningée", "trauma crânien", "sédation",
        "midazolam", "propofol", "thiopental", "convulsion"
    ],
    "cardio": [
        "coeur", "cardiaque", "tachy", "brady", "coronar", "ECG", "valve",
        "choc cardiogénique", "infarctus", "IDM", "angor", "ischémie",
        "insuffisance cardiaque", "IC", "débit cardiaque", "précharge",
        "postcharge", "contractilité", "arythmie", "fibrillation",
        "flutter", "bloc auriculo-ventriculaire", "BAV"
    ],
    "reanimation": [
        "choc", "état de choc", "catécholamine", "adrénaline", "noradrénaline",
        "dobutamine", "dopamine", "remplissage vasculaire", "cristalloïde",
        "colloïde", "lactat", "lactate", "acidose", "défaillance",
        "SDRA", "syndrome de détresse", "ARDS"
    ],
    "respiratoire": [
        "O2", "PaO2", "PaCO2", "SpO2", "saturation", "poumon", "asthme",
        "BPCO", "bronchospasme", "hypoxie", "hypercapnie", "pneumonie",
        "atélectasie", "oedème pulmonaire", "embolie pulmonaire",
        "shunt", "rapport ventilation perfusion", "alvéole"
    ],
    "infectio": [
        "infection", "bactérie", "antibiotique", "ATB", "sepsis", "septique",
        "choc septique", "endotoxine", "pyrogène", "fièvre", "hypothermie",
        "leucocyte", "GB", "CRP", "procalcitonine", "asepsie",
        "antisepsie", "stérilisation", "désinfection", "ISO", "SSI"
    ],
    "transfusion": [
        "sang", "plaquettes", "hémoglobine", "Hb", "hématocrite", "Ht",
        "transfusion", "CGR", "PFC", "plasma", "culot", "groupe sanguin",
        "ABO", "Rhésus", "compatibilité", "RAI", "hémolyse",
        "thrombopénie", "coagulation", "hémostase", "CIVD"
    ],
    "douleur": [
        "analgésie", "analgésique", "douleur", "EVA", "EN", "échelle",
        "palier OMS", "paracétamol", "AINS", "kétamine",
        "anesthésie locorégionale", "ALR", "bloc", "péridurale",
        "rachianesthésie", "PCA", "analgésie contrôlée"
    ],
    "pediatrie": [
        "enfant", "nouveau-né", "nourrisson", "pédiatrique", "néonatal",
        "prématuré", "score Apgar", "réanimation néonatale",
        "dosage pédiatrique", "poids enfant"
    ],
    "legislation": [
        "loi", "décret", "consentement", "déontologie", "éthique",
        "droit", "responsabilité", "faute", "article", "code santé",
        "secret professionnel", "directives anticipées", "personne de confiance"
    ],
    "bases_physio": [
        "homéostasie", "ion", "acide-base", "pH", "osmolarité", "osmolalité",
        "natrémie", "kaliémie", "calcémie", "magnésémie", "phosphorémie",
        "bicarbonate", "tampon", "gazométrie", "équilibre hydrique",
        "compartiment", "LEC", "LIC", "secteur", "diffusion", "osmose"
    ],
}

def detect_module(text: str) -> str:
    """
    Détecte le module le plus probable basé sur les mots-clés.
    Priorité aux modules spécifiques (ordre du dictionnaire).
    """
    text_lower = text.lower()
    
    # Score pour chaque module
    scores = {}
    
    for module, keywords in KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Recherche par mot entier (avec \b pour les bordures de mot)
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            score += matches
        
        if score > 0:
            scores[module] = score
    
    # Retourne le module avec le score le plus élevé
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    
    return "unknown"

def main():
    print("="*60)
    print("🔄 CLASSIFICATION AUTOMATIQUE DES MODULES")
    print("="*60)
    print()
    
    # Charge le corpus
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extrait les questions (gère format array ou dict avec 'questions')
    if isinstance(data, list):
        questions = data
    else:
        questions = data.get("questions", data)
    
    print(f"📘 {len(questions)} questions à analyser")
    print()
    
    # Statistiques avant
    modules_before = Counter(q.get("module_id", "unknown") for q in questions)
    unknown_before = modules_before.get("unknown", 0)
    
    print(f"⚠️  Avant : {unknown_before} questions 'unknown' ({unknown_before/len(questions)*100:.1f}%)")
    print()
    
    # Classification
    print("🔄 Classification en cours...")
    reassigned = 0
    
    for q in questions:
        current_module = q.get("module_id", "unknown")
        
        # Ne reclassifie que les "unknown"
        if current_module in [None, "unknown", ""]:
            # Combine texte + explication pour analyse
            text_blob = f"{q.get('text', '')} {q.get('explanation', '')}"
            
            new_module = detect_module(text_blob)
            
            if new_module != "unknown":
                q["module_id"] = new_module
                reassigned += 1
    
    # Statistiques après
    modules_after = Counter(q.get("module_id", "unknown") for q in questions)
    unknown_after = modules_after.get("unknown", 0)
    
    # Sauvegarde
    if isinstance(data, list):
        output_data = questions
    else:
        data["questions"] = questions
        output_data = data
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Rapport
    print()
    print("="*60)
    print("✅ CLASSIFICATION TERMINÉE")
    print("="*60)
    print()
    print(f"📊 RÉSULTATS\n")
    print(f"   Questions reclassées : {reassigned}")
    print(f"   Unknown avant : {unknown_before} ({unknown_before/len(questions)*100:.1f}%)")
    print(f"   Unknown après : {unknown_after} ({unknown_after/len(questions)*100:.1f}%)")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   Réduction : -{unknown_before - unknown_after} ({(unknown_before - unknown_after)/unknown_before*100:.1f}%)")
    print()
    print("📋 RÉPARTITION PAR MODULE\n")
    
    for module, count in sorted(modules_after.items(), key=lambda x: -x[1]):
        percent = count / len(questions) * 100
        bar = "█" * int(percent / 2)
        print(f"   {module:20} {count:4} ({percent:5.1f}%) {bar}")
    
    print()
    print(f"💾 Corpus reclassifié : {OUTPUT}")
    print("="*60)

if __name__ == "__main__":
    main()

