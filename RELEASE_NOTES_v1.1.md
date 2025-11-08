# 🎉 IADE NEW — Release v1.1

**Date de release** : 2025-11-08

## 📊 Statistiques du Corpus

- **Total QCM** : 165
- **Score biomédical moyen** : 0.932
- **Longueur moyenne des explications** : 105 caractères
- **Modules couverts** : 14

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

- **bases_physio** : 31 QCM (18.8%)
- **unknown** : 29 QCM (17.6%)
- **infectio** : 26 QCM (15.8%)
- **transfusion** : 19 QCM (11.5%)
- **cardio** : 17 QCM (10.3%)
- **neuro** : 9 QCM (5.5%)
- **respiratoire** : 8 QCM (4.8%)
- **ventilation** : 5 QCM (3.0%)
- **legislation** : 5 QCM (3.0%)
- **douleur** : 5 QCM (3.0%)
- **pediatrie** : 5 QCM (3.0%)
- **pharma_opioides** : 3 QCM (1.8%)
- **monitorage** : 2 QCM (1.2%)
- **reanimation** : 1 QCM (0.6%)


## 🚀 Installation

```bash
# Clone le repo
git clone https://github.com/Soynido/IADE-NEW.git
cd IADE-NEW

# Backend (Python)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
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
