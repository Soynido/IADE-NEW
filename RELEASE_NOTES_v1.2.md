# 🎉 IADE NEW — Release v1.2

**Date de release** : 8 novembre 2025  
**Version** : 1.2.0

---

## 🆕 Nouveautés v1.2

### 🧠 Alignement Sémantique Automatique

La v1.2 introduit un **alignement sémantique intelligent** de chaque question vers sa page source optimale dans les PDF de cours.

#### Fonctionnement

- **Analyse de 141 pages** des 3 PDF sources (Cours + Annales V1 & V2)
- **Encodage sémantique** via SentenceTransformers (all-MiniLM-L6-v2)
- **Calcul de similarité** entre chaque question et chaque page
- **Relocalisation automatique** vers la page la plus pertinente

#### Résultats

✅ **146/165 QCM relocalisés** (88.5%) avec amélioration du score  
✅ **Score moyen d'alignement** : 0.546  
✅ **Haute confiance (≥0.5)** : 105 QCM (63.6%)  
✅ **Moyenne confiance (0.3-0.5)** : 60 QCM (36.4%)  
✅ **Faible confiance (<0.3)** : 0 QCM (0.0%) ✨  

#### Distribution optimisée

- **Prepaconcoursiade-Complet.pdf** : 104 QCM (63%)
- **Annales Volume 2** : 32 QCM (19%)
- **Annales Volume 1** : 29 QCM (18%)

---

## 📊 Comparaison v1.1 → v1.2

| Métrique | v1.1 | v1.2 | Amélioration |
|----------|------|------|--------------|
| **QCM total** | 165 | 165 | = |
| **Score biomédical** | 0.932 | 0.932 | = |
| **Score alignement** | Manuel | 0.546 | ✅ Automatisé |
| **Liens CTA validés** | 100% | 100% | = |
| **Pages relocalisées** | - | 146 (88.5%) | ✅ Nouveau |
| **Confiance ≥ 0.3** | - | 100% | ✅ Nouveau |

---

## 🎯 Avantages de v1.2

### Pour les Étudiants

✅ **Précision maximale** : Le bouton "Voir le cours" pointe vers la page exacte du contenu  
✅ **Contexte optimal** : Chaque question renvoie vers sa source sémantiquement la plus proche  
✅ **Zéro erreur** : 100% des liens validés et fonctionnels  

### Pour le Système

✅ **Automatisation complète** : Plus besoin de mapping manuel  
✅ **Évolutivité** : Peut traiter de nouveaux PDF automatiquement  
✅ **Qualité mesurable** : Score d'alignement pour chaque question  

---

## 🛠️ Technique

### Modèle utilisé

- **sentence-transformers/all-MiniLM-L6-v2**
- Embeddings de 384 dimensions
- Optimisé pour la similarité sémantique
- Temps d'alignement : 77 secondes pour 165 QCM

### Pipeline

1. Extraction texte des 3 PDF (141 pages)
2. Encodage des pages par batch (32 pages/batch)
3. Encodage des questions (texte + début explication)
4. Calcul cosine similarity question ↔ pages
5. Sélection de la meilleure correspondance
6. Mise à jour automatique du corpus

---

## 📦 Contenu de la Release

### Fichiers QCM

- `compiled.json` : Corpus complet v1.2 (165 QCM alignés)
- `revision.json` : Questions pour mode Révision
- `entrainement.json` : Questions pour mode Entraînement
- `concours.json` : Questions pour mode Concours Blanc

### Examens Blancs

- 6 examens calibrés (60 questions × 2h chacun)
- Distribution équilibrée par module et difficulté

### Rapports

- `cta_alignment_report.json` : Détails de l'alignement sémantique
- `refinement_report.md` : Rapport Phase 10 (raffinement qualité)

---

## 🚀 Installation & Mise à Jour

### Nouvelle installation

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

### Mise à jour depuis v1.1

```bash
git pull origin master
npm install
npm run dev
```

Les données QCM seront automatiquement mises à jour (chargement depuis `/data/questions/`).

---

## 🎓 Modes Pédagogiques

Les 3 modes restent inchangés :

1. **Révision** : QCM guidés avec explications + renvois cours optimisés
2. **Entraînement** : 10 questions adaptatives (facile → difficile)
3. **Concours Blanc** : 60 questions chronométrées (2h)

---

## 🔗 Liens

- **Application Vercel** : https://iade-onaukog0x-valentin-galudec-s-projects.vercel.app
- **GitHub Repository** : https://github.com/Soynido/IADE-NEW
- **Release v1.1** : https://github.com/Soynido/IADE-NEW/releases/tag/v1.1

---

## 📝 Changelog

### v1.2 (2025-11-08)

- ✅ Alignement sémantique automatique (SentenceTransformers)
- ✅ 146 QCM relocalisés vers pages optimales
- ✅ Score d'alignement moyen : 0.546
- ✅ 100% confiance ≥ 0.3 (0 lien faible)
- ✅ Distribution PDF optimisée (63% Cours / 37% Annales)
- ✅ Validation CTA 100% maintenue

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

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir `CONTRIBUTING.md` pour les guidelines.

---

## 📄 Licence

MIT License - Voir `LICENSE` pour détails.

---

## 👥 Auteurs

- **Valentin Galudec** - Conception & Développement
- **Claude Sonnet 4.5** - Assistance IA & Validation

---

**⭐ Si ce projet t'aide, mets une étoile sur GitHub !**

---

**🎓 Bon courage pour le concours IADE !**

