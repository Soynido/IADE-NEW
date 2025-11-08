#!/usr/bin/env python3

"""
ALIGNEMENT SÉMANTIQUE GLOBAL — Phase 11
Recalcule automatiquement le meilleur PDF et la page la plus pertinente
pour chaque question du corpus IADE NEW.
"""

import json
from pathlib import Path
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

# Chemins
DATA_FILE = Path("src/data/questions/compiled_refined_enriched.json")
PDF_DIR = Path("src/data/sources")
PUBLIC_PDF_DIR = Path("public/pdfs")
OUTPUT_FILE = Path("src/data/questions/compiled_refined_aligned.json")
REPORT_FILE = Path("reports/cta_alignment_report.json")

# Initialisation du modèle sémantique
print("="*60)
print("🧠 ALIGNEMENT SÉMANTIQUE GLOBAL — Phase 11")
print("="*60)
print("\n🧠 Chargement modèle sémantique (MiniLM)...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("   ✓ Modèle chargé")

# Trouve tous les PDFs
def find_all_pdfs():
    pdfs = {}
    for directory in [PDF_DIR, PUBLIC_PDF_DIR]:
        if directory.exists():
            for pdf_path in directory.glob("*.pdf"):
                if pdf_path.name not in pdfs:
                    pdfs[pdf_path.name] = pdf_path
    return pdfs

# Chargement des PDFs
print("\n📚 Extraction du texte de tous les PDF...")
all_pdfs = find_all_pdfs()
pdf_texts = {}

for pdf_name, pdf_path in all_pdfs.items():
    try:
        with fitz.open(pdf_path) as doc:
            pages = []
            for page in doc:
                text = page.get_text("text")
                # Nettoie le texte
                text = " ".join(text.split())
                pages.append(text)
        
        pdf_texts[pdf_name] = pages
        print(f"   ✓ {pdf_name} → {len(pages)} pages")
    except Exception as e:
        print(f"   ⚠️  Erreur {pdf_name}: {e}")

if not pdf_texts:
    print("❌ Aucun PDF trouvé !")
    exit(1)

# Encodage des pages
print("\n⚙️  Encodage des pages PDF (peut prendre 2-3 min)...")
pdf_embeddings = {}

for pdf_name, pages in pdf_texts.items():
    print(f"   Encodage {pdf_name}...")
    embeddings = []
    
    # Encode par batch pour plus de rapidité
    for i in range(0, len(pages), 32):
        batch = pages[i:i+32]
        batch_embeds = model.encode(batch, convert_to_tensor=True, show_progress_bar=False)
        embeddings.extend(batch_embeds)
    
    pdf_embeddings[pdf_name] = embeddings
    print(f"   ✓ {len(embeddings)} pages encodées")

# Chargement du corpus
print(f"\n📂 Chargement corpus...")
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data.get("questions", data)
print(f"   ✓ {len(questions)} QCM à aligner\n")

# Alignement sémantique
aligned_results = []
changes = 0
improvements = 0

print("🔄 Alignement en cours...\n")

for q in tqdm(questions, desc="   Progression"):
    text = q.get("text", "")
    explanation = q.get("explanation", "")
    
    # Gère le cas où explanation est une liste
    if isinstance(explanation, list):
        explanation = " ".join(str(e) for e in explanation)
    
    q_text = text + " " + str(explanation)[:200]
    
    if not q_text.strip():
        aligned_results.append(q)
        continue
    
    # Encode la question
    q_embed = model.encode(q_text, convert_to_tensor=True, show_progress_bar=False)
    
    # Trouve la meilleure correspondance
    best_match = {"pdf": None, "page": None, "score": 0.0}
    
    for pdf_name, page_embeds in pdf_embeddings.items():
        for page_idx, page_embed in enumerate(page_embeds):
            similarity = float(util.cos_sim(q_embed, page_embed))
            
            if similarity > best_match["score"]:
                best_match.update({
                    "pdf": pdf_name,
                    "page": page_idx + 1,
                    "score": similarity
                })
    
    # Vérifie si c'est une amélioration
    old_pdf = q.get("source_pdf")
    old_page = q.get("page_number", 0)
    old_score = q.get("alignment_score", 0)
    
    if best_match["pdf"] != old_pdf or best_match["page"] != old_page:
        changes += 1
        
        if best_match["score"] > old_score:
            improvements += 1
    
    # Met à jour
    q["source_pdf"] = best_match["pdf"]
    q["page_number"] = best_match["page"]
    q["alignment_score"] = round(best_match["score"], 3)
    q["alignment_method"] = "semantic_v1.2"
    
    aligned_results.append(q)

# Statistiques
summary = {
    "total_questions": len(questions),
    "changes": changes,
    "improvements": improvements,
    "avg_score": round(sum(q["alignment_score"] for q in aligned_results) / len(aligned_results), 3) if aligned_results else 0,
    "high_confidence": sum(1 for q in aligned_results if q["alignment_score"] >= 0.5),
    "medium_confidence": sum(1 for q in aligned_results if 0.3 <= q["alignment_score"] < 0.5),
    "low_confidence": sum(1 for q in aligned_results if q["alignment_score"] < 0.3),
    "pdf_distribution": {}
}

# Distribution par PDF
from collections import Counter
pdf_counts = Counter(q["source_pdf"] for q in aligned_results)
summary["pdf_distribution"] = dict(pdf_counts)

# Sauvegarde du corpus corrigé
data["questions"] = aligned_results
data["alignment_version"] = "v1.2_semantic"
data["total_questions"] = len(aligned_results)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Sauvegarde du rapport
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

# Affichage
print("\n" + "="*60)
print("✅ ALIGNEMENT SÉMANTIQUE TERMINÉ")
print("="*60)
print(f"\n💾 Corpus corrigé : {OUTPUT_FILE}")
print(f"📊 Rapport : {REPORT_FILE}\n")
print(f"📈 RÉSULTATS\n")
print(f"   Score moyen d'alignement : {summary['avg_score']}")
print(f"   Changements effectués    : {changes}/{len(questions)} ({changes/len(questions)*100:.1f}%)")
print(f"   Améliorations détectées  : {improvements}/{changes if changes > 0 else 1}")
print(f"\n   Confiance haute (≥0.5)   : {summary['high_confidence']} QCM ({summary['high_confidence']/len(questions)*100:.1f}%)")
print(f"   Confiance moyenne (0.3-0.5): {summary['medium_confidence']} QCM ({summary['medium_confidence']/len(questions)*100:.1f}%)")
print(f"   Confiance faible (<0.3)  : {summary['low_confidence']} QCM ({summary['low_confidence']/len(questions)*100:.1f}%)")

print(f"\n📚 DISTRIBUTION PAR PDF\n")
for pdf_name, count in sorted(summary['pdf_distribution'].items(), key=lambda x: -x[1]):
    pct = count / len(questions) * 100
    print(f"   {pdf_name:45} : {count:3} QCM ({pct:5.1f}%)")

print("\n" + "="*60)

if summary['high_confidence'] >= len(questions) * 0.8:
    print("✅ ALIGNEMENT EXCELLENT (≥80% haute confiance)")
else:
    print("⚠️  ALIGNEMENT PARTIEL - Vérifier manuellement les scores faibles")

print("="*60)

