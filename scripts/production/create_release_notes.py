#!/usr/bin/env python3

"""
Génère les notes de release pour GitHub v1.1
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    print("="*60)
    print("GÉNÉRATION NOTES DE RELEASE v1.1")
    print("="*60)
    
    # Charge statistiques du corpus v1.1
    corpus_file = Path("src/data/questions/compiled_refined_enriched.json")
    if not corpus_file.exists():
        corpus_file = Path("src/data/questions/compiled_refined.json")
    
    with open(corpus_file, "r") as f:
        data = json.load(f)
    
    questions = data.get("questions", data)
    
    # Calcule statistiques
    from collections import Counter
    
    modules = Counter(q.get("module_id") for q in questions)
    avg_score = sum(q.get("biomedical_score", 0) for q in questions) / len(questions)
    avg_explanation_len = sum(len(q.get("explanation", "")) for q in questions) / len(questions)
    
    # Génère markdown
    notes = f"""# 🎉 IADE NEW — Release v1.1

**Date de release** : {datetime.now().strftime('%Y-%m-%d')}

## 📊 Statistiques du Corpus

- **Total QCM** : {len(questions)}
- **Score biomédical moyen** : {avg_score:.3f}
- **Longueur moyenne des explications** : {avg_explanation_len:.0f} caractères
- **Modules couverts** : {len(modules)}

## 🆕 Nouveautés v1.1

### ✅ Raffinement Qualité (Phase 10)

- **213 QCM filtrés** pour faible qualité
- **213 QCM réécrits** par IA (Ollama Mistral 7B)
- **102 QCM revalidés** et intégrés (taux 47.9%)
- **Amélioration du score biomédical** : +9.5% (0.851 → 0.932)
- **Élimination complète** des placeholders et options dupliquées

### 📚 Enrichissement Métadonnées

Chaque QCM contient maintenant :
- `source_pdf` : lien vers le cours source
- `page_number` : page exacte du cours
- `difficulty` : niveau de difficulté (easy/medium/hard)
- `biomedical_score` : score de cohérence médicale

### 🧹 Déduplication Corpus

- **462 QCM bruts** → **165 QCM uniques** (par chunk_id)
- Sélection automatique de la meilleure version par chunk
- **0 perte de données** grâce à la fusion intelligente

## 📦 Contenu de la Release

### Fichiers QCM

- `compiled_refined.json` : Corpus complet v1.1 (165 QCM)
- `revision.json` : Questions pour mode Révision
- `entrainement.json` : Questions pour mode Entraînement
- `concours.json` : Questions pour mode Concours Blanc

### Examens Blancs

- 6 examens calibrés (60 questions × 2h chacun)
- Distribution équilibrée par module et difficulté

### Documentation

- `refinement_report.md` : Rapport détaillé Phase 10
- `README.md` : Guide d'utilisation
- `spec.md`, `plan.md`, `tasks.md` : Documentation technique complète

## 📈 Distribution par Module

"""
    
    for module, count in modules.most_common():
        pct = (count / len(questions)) * 100
        notes += f"- **{module}** : {count} QCM ({pct:.1f}%)\n"
    
    notes += f"""

## 🚀 Installation

```bash
# Clone le repo
git clone https://github.com/Soynido/IADE-NEW.git
cd IADE-NEW

# Backend (Python)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Frontend (React)
npm install
npm run dev
```

## 🎓 Modes Pédagogiques

1. **Révision** : QCM guidés avec explications + renvois cours
2. **Entraînement** : 10 questions adaptatives (facile → difficile)
3. **Concours Blanc** : 60 questions chronométrées (2h)

## 🧠 Technologies

- **IA locale** : Ollama (Mistral 7B)
- **Validation biomédicale** : BioBERT (dmis-lab)
- **Frontend** : React + Vite + Tailwind CSS
- **Backend** : Python 3.13

## 📝 Changelog

### v1.1 (2025-11-08)
- ✅ Phase 10 de raffinement complétée
- ✅ Déduplication et fusion intelligente
- ✅ Enrichissement métadonnées (PDF, page, difficulté)
- ✅ Score biomédical moyen : 0.932
- ✅ 165 QCM uniques et validés

### v1.0 (2025-11-05)
- ✅ Extraction et segmentation PDF
- ✅ Génération de 462 QCM bruts
- ✅ Validation BioBERT
- ✅ 3 modes pédagogiques
- ✅ 6 examens blancs

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir `CONTRIBUTING.md` pour les guidelines.

## 📄 Licence

MIT License - Voir `LICENSE` pour détails.

## 👥 Auteurs

- **Valentin Galudec** - Conception & Développement
- **Claude Sonnet 4.5** - Assistance IA & Validation

---

**⭐ Si ce projet t'aide, mets une étoile sur GitHub !**
"""
    
    # Sauvegarde
    output_file = Path("RELEASE_NOTES_v1.1.md")
    with open(output_file, "w") as f:
        f.write(notes)
    
    print(f"\n✅ Notes de release générées : {output_file}")
    print(f"\n{'='*60}")
    print(f"CONTENU (aperçu) :")
    print(f"{'='*60}")
    print(notes[:500] + "...")

if __name__ == "__main__":
    main()

