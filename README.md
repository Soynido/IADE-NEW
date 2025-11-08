# IADE NEW - Simulateur d'Apprentissage Intégral

**Version** : 1.0.0  
**Date** : 5 novembre 2025  
**Statut** : En développement (Backend complet, Frontend opérationnel)

---

## 🎯 Vue d'Ensemble

IADE NEW est un **simulateur d'apprentissage intégral** pour la préparation au concours IADE (Infirmier Anesthésiste Diplômé d'État).

**Philosophie** : "Aucune question ne sort du corpus, aucune explication n'est hors du texte."

L'application transforme les supports officiels (cours + annales) en une expérience d'apprentissage complète avec :
- ✅ **≥ 2000 QCM validés** (biomédicalement + sémantiquement)
- ✅ **6 examens blancs calibrés** (60 Q × 120 min)
- ✅ **3 modes pédagogiques** (Révision, Entraînement adaptatif, Concours blanc)
- ✅ **Dashboard complet** (progression, modules faibles, historique)

---

## 🚀 Installation

### Prérequis

- **Node.js** : 20.x (LTS)
- **Python** : 3.13+
- **Ollama** : dernière version + Mistral 7B
- **Espace disque** : ~10 Go (modèles IA + données)

### Installation Étape par Étape

```bash
# 1. Cloner le projet
cd "/Users/valentingaludec/IADE NEW"

# 2. Backend Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend Node.js
npm install

# 4. Installer Ollama (si pas déjà fait)
# macOS:
brew install ollama
ollama serve &
ollama pull mistral:latest

# 5. Vérifier l'installation
python scripts/test_ollama.py
python scripts/test_biobert.py
```

---

## 📚 Utilisation

### Démarrage Rapide

```bash
# Terminal 1 : Frontend
npm run dev
# Ouvre http://localhost:5173

# Terminal 2 : Génération des QCM (si pas déjà fait)
source venv/bin/activate
bash scripts/run_all.sh
```

### Modes Disponibles

#### 📖 Mode Révision
- Apprentissage guidé par module
- Explications immédiates après réponse
- Lien "Voir le cours" (page source PDF)
- Marquage questions à revoir
- **Aucun chrono**, apprenez à votre rythme

**Accès** : Menu > Révision

#### 💪 Mode Entraînement (10 questions adaptatives)
- Sélection d'un module thématique
- Session de 10 questions
- **Adaptation automatique du niveau** (easy → medium → hard)
- Feedback immédiat + système de notation (Bad/Good/Very Good)
- Score en temps réel

**Accès** : Menu > Entraînement

#### 🎯 Mode Concours Blanc (60 questions, 120 min)
- 6 examens thématiques calibrés
- Conditions réelles : chronomètre 120 min, navigation libre
- **Pas d'explication pendant l'épreuve**
- Correction complète à la fin avec :
  - Score global
  - Temps moyen par question
  - Détail question par question
  - Sections faibles

**Accès** : Menu > Concours Blanc

#### 📊 Dashboard
- Score global (%)
- Jours actifs (série)
- Top 5 modules faibles
- Historique examens blancs
- Statistiques détaillées par module

**Accès** : Menu > Dashboard

---

## 🔧 Pipeline de Génération QCM

### Extraction du Corpus (Phase 1)

```bash
python scripts/extract_pdfs.py \
    --input "src/data/sources/*.pdf" \
    --out src/data/modules/ \
    --metadata src/data/metadata.json
```

**Sortie** : 14 modules thématiques, 422 chunks

### Indexation TF-IDF (Phase 2)

```bash
python scripts/index_chunks.py \
    --modules src/data/modules/ \
    --out src/data/keywords.json
```

**Sortie** : Mots-clés dominants par module (fidélité lexicale)

### Génération QCM (Phase 3)

```bash
python scripts/ai_generation/generate_batch.py \
    --modules src/data/modules/ \
    --keywords src/data/keywords.json \
    --profile src/data/annales_profile.json \
    --out src/data/questions/generated_raw.json \
    --model mistral:latest \
    --per-chunk 3
```

**Durée** : ~4-6h (422 chunks × 3-4 min/chunk)  
**Sortie** : ≥ 2500 QCM bruts

### Validation Double (Phase 4)

**BioBERT (cohérence biomédicale)** :
```bash
python scripts/ai_generation/biobert_client.py \
    --in generated_raw.json \
    --out generated_biobert.json \
    --metadata src/data/metadata.json
```

**Sémantique + Lexicale** :
```bash
python scripts/ai_generation/semantic_validator.py \
    --in generated_biobert.json \
    --modules src/data/modules/ \
    --keywords src/data/keywords.json \
    --out generated_scored.json
```

**Validation combinée** :
- `biomedical_score` > seuil adaptatif (0.05-0.10 selon module)
- `context_score` > 0.75 (fidélité sémantique)
- `keywords_overlap` > 0.5 (fidélité lexicale)

### Consolidation (Phase 5)

```bash
python scripts/ai_generation/validate_all.py \
    --in generated_scored.json \
    --out validated.json

python scripts/ai_generation/classify_modes.py \
    --in validated.json \
    --out-dir src/data/questions/

python scripts/ai_generation/exam_builder.py \
    --in concours.json \
    --annales-profile src/data/annales_profile.json \
    --out-dir src/data/exams/ \
    --count 6
```

**Sortie finale** :
- `revision.json` (toutes questions)
- `entrainement.json` (avec explications détaillées)
- `concours.json` (pool examens)
- `exams/exam_*.json` (6 examens calibrés)
- `compiled.json` (consolidation)

### Pipeline Complet Automatisé

```bash
bash scripts/run_all.sh              # Full run (tous modules)
bash scripts/run_all.sh --subset 10  # Dry run (10 modules test)
```

---

## 📊 Métriques de Qualité

Toutes les questions générées sont validées selon des critères stricts :

| Critère | Objectif | Outil |
|---------|----------|-------|
| Couverture corpus | ≥ 90% | coverage_report.py |
| Nombre QCM | ≥ 2000 | compiled.json |
| Examens blancs | 6 × 60 Q | exam_builder.py |
| Fidélité sémantique | ≥ 0.75 | semantic_validator.py |
| Overlap lexical | ≥ 0.5 | TF-IDF |
| Score BioBERT | 0.05-0.10 (adaptatif) | biobert_client.py |
| Taux rejet | < 20% | Logs pipeline |

---

## 🏗️ Architecture

```
IADE NEW/
├── src/                          # Frontend React
│   ├── components/               # UI composants
│   │   ├── QuestionCard.tsx     # Affichage question
│   │   ├── RevisionMode.tsx     # Mode révision
│   │   ├── TrainingMode.tsx     # Mode entraînement
│   │   ├── ExamMode.tsx         # Mode concours blanc
│   │   ├── Dashboard.tsx        # Statistiques
│   │   └── Navigation.tsx       # Menu
│   ├── store/                    # État global (Zustand)
│   │   └── useUserStore.ts      # Store utilisateur
│   ├── types/                    # TypeScript types
│   └── data/                     # Données JSON
│       ├── modules/              # Corpus segmenté
│       ├── questions/            # QCM validés
│       └── exams/                # Examens blancs
├── scripts/                      # Pipeline Python
│   ├── extract_pdfs.py          # Extraction corpus
│   ├── index_chunks.py          # Indexation TF-IDF
│   ├── analyze_annales.py       # Analyse style
│   ├── ai_generation/           # Génération + validation
│   ├── reports/                 # Rapports qualité
│   └── run_all.sh               # Pipeline complet
├── docs/                         # Documentation
├── spec.md                       # Spécifications
├── plan.md                       # Roadmap
└── tasks.md                      # Liste tâches
```

---

## 📖 Documentation Technique

- **spec.md** : Spécifications techniques complètes (14 sections)
- **plan.md** : Roadmap développement (9 phases, J1-J26)
- **tasks.md** : Liste des 101 tâches détaillées
- **PROGRESS.md** : Suivi progression en temps réel

---

## 🔒 Sécurité et Confidentialité

- ✅ **100% local** (aucun appel API externe)
- ✅ **Aucune donnée nominative** (localStorage anonyme)
- ✅ **Ollama + BioBERT locaux** (pas de cloud)
- ✅ **Pas de tracking** (aucun analytics)

---

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifiez les dépendances
npm install
source venv/bin/activate
pip install -r requirements.txt
```

### Ollama ne répond pas

```bash
# Démarrez le serveur Ollama
ollama serve &

# Vérifiez que Mistral est installé
ollama list
ollama pull mistral:latest
```

### Aucune question n'apparaît

- Vérifiez que le pipeline de génération a bien tourné : `bash scripts/run_all.sh`
- Vérifiez que les fichiers JSON existent : `ls -lh src/data/questions/`

---

## 🤝 Contribution

Ce projet suit une méthodologie stricte :

1. **Toute modification** doit être justifiée dans `spec.md`, `plan.md` ou `tasks.md`
2. **1 commit = 1 tâche** (référence tasks.md)
3. **Tests obligatoires** avant commit
4. **Pas de génération hors corpus** (fidélité absolue au texte)

---

## 📜 Licence

Usage personnel uniquement - Formation médicale IADE

---

## 👨‍⚕️ Auteur

Projet IADE NEW - Préparation Concours 2025

---

## 📞 Support

Pour toute question technique :
- Consultez `docs/DEVELOPER.md`
- Vérifiez `PROGRESS.md` pour l'état actuel
- Consultez les logs : `logs/generation_batch.log`

---

**Dernière mise à jour** : 5 novembre 2025

