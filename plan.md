# IADE NEW — Roadmap de Développement v1.0

**Document de référence** : planning complet phases 0-9 (J1-J26)

Date : 5 novembre 2025  
Version : 1.0  
Statut : Validé pour exécution

---

## Vision et Objectifs

### Vision

**IADE NEW est un simulateur d'apprentissage intégral qui prépare cognitivement et pédagogiquement un candidat au concours IADE, en répliquant fidèlement le cours officiel et les annales.**

L'application ne reproduit pas seulement les annales : elle entraîne le cerveau à raisonner selon le pattern des annales, tout en étant elle-même calibrée sur ce pattern via un feedback itératif stylistique.

### Objectifs mesurables v1

| Objectif | Cible | Outil de mesure |
|----------|-------|-----------------|
| QCM validés | ≥ 2000 | `compiled.json` |
| Examens blancs | 6 × 60 questions | `exams/*.json` |
| Couverture corpus | ≥ 90% | `coverage_report.py` |
| Accord expert | ≥ 90% | Spot-check manuel |
| Fidélité sémantique | ≥ 0.75 | `semantic_validator.py` |
| Overlap lexical | ≥ 0.5 | `fidelity_check.py` |
| Score BioBERT adaptatif | 0.05-0.10 selon module | `biobert_client.py` |
| Taux rejet global | < 20% | Logs pipeline |
| Distance stylistique | < 0.3 | `stylistic_validator.py` |

### Critères de succès

**Utilisateur** : "L'app me fait réviser exactement ce que j'ai lu dans mon PDF"

**Expert** : "Les questions sont indistinguables d'annales réelles"

**Technique** : tous les seuils métriques atteints (tableau ci-dessus)

---

## Vue d'ensemble des phases

```
Phase 0  : Setup & Infrastructure              (J1-J2)   [2 jours]
Phase 1  : Extraction PDF                      (J3-J5)   [3 jours]
Phase 2  : Indexation & Alignement             (J6-J7)   [2 jours]  ← NOUVEAU
Phase 3  : Génération QCM                      (J8-J10)  [3 jours]
Phase 4  : Validation Double                   (J11-J13) [3 jours]
Phase 5  : Compilation & Examens               (J14-J16) [3 jours]
Phase 6  : Frontend Core                       (J17-J19) [3 jours]
Phase 7  : Modes Avancés                       (J20-J22) [3 jours]
Phase 8  : Dashboard & Analytics               (J23-J24) [2 jours]
Phase 9  : QA & Polish                         (J25-J26) [2 jours]

TOTAL : 26 jours (sans week-ends)
```

---

## Phase 0 : Setup & Infrastructure

**Durée** : J1-J2 (2 jours)

**Objectif** : environnement complet IA locale opérationnel

### Livrables

✅ Structure de dossiers complète  
✅ Vite + React + Tailwind configuré  
✅ Python 3.13 + venv + dépendances installées  
✅ Ollama + Mistral 7B testé (génération QCM test)  
✅ BioBERT installé et testé (calcul score test)

### Tâches

**[001]** Initialiser structure de dossiers du projet  
**[002]** Configurer Vite + React + Tailwind  
**[003]** Configurer Python 3.13 + venv + requirements.txt  
**[004]** Installer Ollama + Mistral 7B + script test génération  
**[005]** Installer BioBERT + script test calcul score

### Validation

- `npm run dev` démarre sans erreur
- `python scripts/test_ollama.py` génère un QCM test valide
- `python scripts/test_biobert.py` calcule un score biomédical sur texte test

### Temps estimé

**Total** : 2h30 (setup) + tests

**Répartition** :
- J1 matin : setup frontend (001-002)
- J1 après-midi : setup Python + Ollama (003-004)
- J2 matin : setup BioBERT + tests (005)
- J2 après-midi : validation environnement complet

### Dépendances

Aucune (phase d'initialisation)

### Risques

⚠️ **Ollama installation** : peut échouer si macOS < 13 → installer via Docker si nécessaire  
⚠️ **BioBERT téléchargement** : ~400 Mo, connexion lente → prévoir temps supplémentaire

---

## Phase 1 : Extraction PDF

**Durée** : J3-J5 (3 jours)

**Objectif** : segmentation modules + chunks propres à partir des 3 PDF sources

### Livrables

✅ `src/data/modules/*.json` (≥ 12 modules générés)  
✅ `src/data/metadata.json` (mapping pages → modules)  
✅ Taxonomie validée manuellement (overrides appliqués)

### Tâches

**[010]** Développer `extract_pdfs.py` — détection titres (regex, heuristiques)  
**[011]** Développer `extract_pdfs.py` — découpage chunks (< 1200 tokens)  
**[012]** Exécuter extraction sur les 3 PDF  
**[013]** Générer `metadata.json` initial  
**[014]** Validation manuelle taxonomie + ajustements overrides

### Validation

- ≥ 12 modules générés avec sections + chunks valides
- Chaque chunk a `chunk_id`, `text`, `token_count < 1200`
- `metadata.json` conforme au schéma (cf. spec.md Section III)
- Couverture attendue ≥ 70% des chapitres identifiables

### Temps estimé

**Total** : 8-10h (dont 2-3h temps machine)

**Répartition** :
- J3 : développement extraction (010-011) — 4h
- J4 matin : exécution extraction (012) — 3h (dont 2h machine)
- J4 après-midi : génération metadata (013) — 1h
- J5 : validation manuelle + ajustements (014) — 2h

### Dépendances

**Dépend de** : Phase 0 (Python configuré)

**Bloque** : Phase 2 (indexation nécessite modules extraits)

### Risques

⚠️ **PDF mal structurés** : si titres non détectables → augmenter temps validation manuelle (J5)  
⚠️ **Tableaux complexes** : conversion texte peut être bruitée → prévoir nettoyage manuel

---

## Phase 2 : Indexation & Alignement

**Durée** : J6-J7 (2 jours) **[PHASE NOUVELLE]**

**Objectif** : indexation fine des chunks (TF-IDF) + analyse style annales

### Livrables

✅ `src/data/keywords.json` (mots-clés dominants par module, TF-IDF)  
✅ `src/data/annales_profile.json` (profil calibrage style annales)  
✅ Configuration seuils BioBERT adaptatifs par module dans `metadata.json`

### Tâches

**[018]** Créer script `index_chunks.py` — extraction TF-IDF keywords  
**[019]** Exécuter indexation complète sur tous modules  
**[024]** Créer script `analyze_annales.py` — analyse des annales (longueur, structure, pondération)  
**[025]** Exécuter analyse des 2 volumes d'annales  
**[024b]** Créer script `stylistic_validator.py` — mesure distance Levenshtein + similarité phrastique  
**[025b]** Configurer seuils BioBERT adaptatifs par module dans `metadata.json`

### Validation

- ≥ 80% de chunks avec ≥ 3 mots-clés pertinents
- `annales_profile.json` contient :
  - Longueur moyenne énoncés
  - Structure syntaxique (débuts phrases)
  - Pondération modules (fréquence dans annales)
- `metadata.json` enrichi avec `biomedical_thresholds` par module

### Temps estimé

**Total** : 5-6h

**Répartition** :
- J6 matin : développement index_chunks.py (018) — 2h
- J6 après-midi : exécution indexation (019) + développement analyze_annales.py (024) — 3h
- J7 matin : exécution analyse annales (025) — 1h
- J7 après-midi : stylistic_validator.py + config seuils (024b, 025b) — 2h30

### Dépendances

**Dépend de** : Phase 1 (modules extraits)

**Bloque** : Phase 3 (génération nécessite keywords + profil annales)

### Risques

⚠️ **TF-IDF trop générique** : si mots-clés pas assez spécifiques → ajuster `max_features` ou filtrer stopwords médicaux  
⚠️ **Annales hétérogènes** : si styles variés → calculer profil par année, moyenner

---

## Phase 3 : Génération QCM

**Durée** : J8-J10 (3 jours)

**Objectif** : génération de 2500+ QCM bruts ancrés dans le texte via Ollama Mistral 7B

### Livrables

✅ `src/data/questions/generated_raw.json` (≥ 2500 QCM avant filtrage)  
✅ Logs génération : taux succès > 85% par module  
✅ Style calibré : distance stylistique < 0.35 après feedback itératif

### Tâches

**[020]** Développer `generate_batch.py` — prompt engineering (système + user)  
**[021]** Développer `generate_batch.py` — parsing JSON + gestion erreurs  
**[022]** Développer `generate_batch.py` — batch processing (boucle modules/chunks)  
**[023]** Exécuter génération batch complète sur tous modules  
**[023b]** Exécuter feedback itératif stylistique : mesurer distance, ajuster prompts si > 0.35

### Validation

- ≥ 2500 questions générées
- Chaque question a : `text`, `options[4]`, `correctAnswer`, `explanation`, `source_context`
- Taux succès parsing JSON > 85%
- Distance stylistique moyenne < 0.35 (après ajustements prompts si nécessaire)

### Temps estimé

**Total** : 6-8h (dont 4-6h temps machine)

**Répartition** :
- J8 : développement generate_batch.py (020-022) — 4h30
- J9 : exécution génération batch (023) — 6h (dont 5h machine)
- J10 : feedback itératif stylistique (023b) — 2h

### Dépendances

**Dépend de** : Phase 2 (keywords + profil annales nécessaires)

**Bloque** : Phase 4 (validation nécessite QCM générés)

### Risques

⚠️ **Taux génération < 80%** : si Mistral échoue parsing JSON → itérer sur prompts, ajouter retry logic  
⚠️ **Distance stylistique > 0.35** : si style trop différent annales → ajuster prompts (longueur, structure), re-générer échantillon

---

## Phase 4 : Validation Double

**Durée** : J11-J13 (3 jours)

**Objectif** : validation BioBERT + similarité contextuelle + fidélité lexicale (triple scoring)

### Livrables

✅ `src/data/questions/generated_scored.json` (avec 3 scores : biomedical, context, keywords_overlap)  
✅ Taux de rejet < 20%  
✅ ≥ 2000 questions passent les seuils

### Tâches

**[030]** Développer `biobert_client.py` — embeddings + centroïdes  
**[031]** Développer `biobert_client.py` — calcul `biomedical_score`  
**[031b]** Appliquer seuils BioBERT adaptatifs par module (chargés depuis `metadata.json`)  
**[032]** Exécuter scoring BioBERT complet  
**[026]** Ajouter calcul `context_score` dans `semantic_validator.py`  
**[027]** Ajouter calcul `keywords_overlap` dans `semantic_validator.py`  
**[038]** Développer validation combinée (rejette si score < seuil)  
**[039]** Exécuter validation sémantique complète

### Validation

- 100% des questions ont 3 scores calculés
- ≥ 2000 questions passent les seuils :
  - `biomedical_score > biomedical_threshold` (adaptatif : 0.05-0.10 selon module)
  - `context_score > 0.75`
  - `keywords_overlap > 0.5`
- Taux de rejet global < 20%
- Logs détaillés : motif rejet par question

### Temps estimé

**Total** : 8-10h (dont 4-5h temps machine)

**Répartition** :
- J11 : développement biobert_client.py (030-031, 031b) — 3h
- J11 après-midi : exécution scoring BioBERT (032) — 3h (dont 2h machine)
- J12 : développement semantic_validator.py (026-027, 038) — 3h30
- J13 : exécution validation sémantique (039) — 2h (dont 1h30 machine)

### Dépendances

**Dépend de** : Phase 3 (QCM générés)

**Bloque** : Phase 5 (compilation nécessite QCM validés)

### Risques

⚠️ **Taux rejet > 30%** : si seuils trop élevés → revoir seuils (abaisser context_score à 0.70) ou prompts génération  
⚠️ **Seuils adaptatifs trop stricts** : si pharmacologie > 40% rejet → abaisser seuil BioBERT pharmaco à 0.08

---

## Phase 5 : Compilation & Examens

**Durée** : J14-J16 (3 jours)

**Objectif** : fichiers finaux (révision/entraînement/concours) + 6 examens blancs calibrés

### Livrables

✅ `validated.json`, `revision.json`, `entrainement.json`, `concours.json`, `compiled.json`  
✅ `exams/exam_01.json` ... `exam_06.json` (6 examens × 60 Q)  
✅ `docs/coverage_report.md` + `docs/fidelity_report.html` (rapport visuel)

### Tâches

**[033]** Développer `validate_all.py` — déduplication  
**[034]** Développer `validate_all.py` — validation format  
**[035]** Développer `validate_all.py` — distribution difficultés  
**[035b]** Implémenter règle automatique classification difficultés (context_score > 0.9 + explication > 40 mots = hard)  
**[036]** Développer `classify_modes.py` — répartition révision/entraînement/concours  
**[037]** Exécuter consolidation finale  
**[056]** Développer `exam_builder.py` — création 6 examens calibrés (pondération modules + difficultés)  
**[057]** Vérifier équilibre examens (tous modules représentés dans ≥ 4 examens)  
**[065]** Développer `coverage_report.py` — rapport couverture & fidélité  
**[066]** Exécuter génération rapport de couverture  
**[066b]** Générer rapport visuel fidélité (HTML + heatmap)

### Validation

- ≥ 2000 QCM dans `compiled.json`
- Couverture corpus ≥ 90%
- 6 examens × 60 questions
- Distribution difficultés conforme :
  - Révision : 40% easy / 40% medium / 20% hard
  - Examens : 30% easy / 50% medium / 20% hard
- `coverage_report.md` généré avec métriques complètes
- `fidelity_report.html` généré avec heatmap par module

### Temps estimé

**Total** : 8-10h

**Répartition** :
- J14 : développement validate_all.py (033-035, 035b) — 3h30
- J14 après-midi : développement classify_modes.py (036) + exécution consolidation (037) — 2h
- J15 : développement exam_builder.py (056) + vérification équilibre (057) — 3h
- J16 : développement coverage_report.py (065) + exécution rapports (066, 066b) — 2h30

### Dépendances

**Dépend de** : Phase 4 (QCM validés)

**Bloque** : Phase 6 (frontend nécessite fichiers compilés)

### Risques

⚠️ **Couverture < 85%** : si chunks orphelins nombreux → re-générer sur chunks non couverts (itération Phase 3-4)  
⚠️ **Examens déséquilibrés** : si module absent → ajuster pondération `exam_builder.py`

---

## Phase 6 : Frontend Core

**Durée** : J17-J19 (3 jours)

**Objectif** : UI révision + entraînement fonctionnels avec store Zustand

### Livrables

✅ Store Zustand opérationnel (`useUserStore.ts`)  
✅ Composants `QuestionCard`, `RevisionMode`, `TrainingMode`  
✅ Navigation et routing (React Router)  
✅ Mécanisme purge localStorage (> 90 jours)

### Tâches

**[040]** Créer Zustand store `useUserStore.ts` (interface UserStats, actions, persistance)  
**[040b]** Implémenter mécanisme purge localStorage (> 90 jours)  
**[041]** Créer composant `QuestionCard.tsx` (affichage question + 4 options + correction)  
**[042]** Créer composant `RevisionMode.tsx` (liste filtrable + QuestionCard + lien cours)  
**[043]** Créer composant `TrainingMode.tsx` (sélection module + 10Q + score temps réel)  
**[044]** Setup routing et navigation (React Router, routes, menu)

### Validation

- Mode Révision : liste filtrable par module, explication immédiate, navigation fluide
- Mode Entraînement : parcours complet 10Q, score affiché, feedback enregistré
- Navigation entre modes fonctionnelle
- localStorage persistant (données conservées après refresh)
- Purge logs > 90 jours au démarrage

### Temps estimé

**Total** : 8-10h

**Répartition** :
- J17 : store Zustand (040, 040b) + QuestionCard (041) — 3h30
- J18 : RevisionMode (042) — 3h
- J19 : TrainingMode (043) + routing (044) — 4h

### Dépendances

**Dépend de** : Phase 5 (fichiers `revision.json`, `entrainement.json` nécessaires)

**Bloque** : Phase 7 (modes avancés nécessitent composants de base)

### Risques

⚠️ **localStorage plein** : si > 10 Mo → alerte utilisateur, proposer export JSON

---

## Phase 7 : Modes Avancés

**Durée** : J20-J22 (3 jours)

**Objectif** : concours blancs + logique adaptative + feedback utilisateur

### Livrables

✅ Composant `ExamMode.tsx` (chronomètre 120 min, 60Q, navigation libre)  
✅ Logique adaptative calibrée (algorithme progression niveau)  
✅ Système feedback (Bad/Good/Very Good) fonctionnel

### Tâches

**[050]** Créer composant `ExamMode.tsx` (chronomètre, navigation, blocage explications)  
**[051]** Implémenter logique adaptative `TrainingMode` (algorithme progression : p(bonne) > 0.7 → +niveau)  
**[052]** Implémenter système feedback utilisateur (UI boutons 1/2/3 + stockage)  
**[053]** Implémenter persistance localStorage complète (sauvegarde auto)

### Validation

- Concours blanc : 60Q affichées, chronomètre 120 min, correction à la fin uniquement
- Adaptatif : ajustement niveau selon performance (test sur 3 sessions)
- Feedback enregistré dans `useUserStore`, récupérable
- Persistance complète : toutes données sauvegardées après chaque action

### Temps estimé

**Total** : 8-10h

**Répartition** :
- J20 : ExamMode (050) — 4h
- J21 : logique adaptative (051) — 2h30
- J22 : système feedback (052) + persistance (053) — 2h30

### Dépendances

**Dépend de** : Phase 6 (composants de base) + Phase 5 (fichiers `exams/*.json`)

**Bloque** : Phase 8 (dashboard nécessite données complètes)

### Risques

⚠️ **Algorithme adaptatif sur-ajuste** : si variance élevée sur 10Q → augmenter à 15Q ou ajuster règle progression

---

## Phase 8 : Dashboard & Analytics

**Durée** : J23-J24 (2 jours)

**Objectif** : mesure fidélité & progression utilisateur (métriques complètes)

### Livrables

✅ Dashboard complet : score global, jours actifs, modules faibles, progression EMA 7j  
✅ Historique examens blancs (tableau scores + dates)

### Tâches

**[060]** Créer composant `Dashboard.tsx` (score global, jours actifs)  
**[061]** Ajouter identification modules faibles (tri byModule, top 5)  
**[062]** Ajouter graphique progression (EMA 7 jours, recharts)  
**[063]** Ajouter historique examens blancs (tableau)

### Validation

- Métriques calculées correctement (score = correct/attempts)
- Modules faibles identifiés (top 5, barre progression)
- Graphique progression affiché (courbe EMA 7j)
- Historique examens persistant (tableau avec scores, dates, durées)

### Temps estimé

**Total** : 5-6h

**Répartition** :
- J23 matin : Dashboard base (060) + modules faibles (061) — 3h30
- J23 après-midi : graphique progression (062) — 2h
- J24 matin : historique examens (063) — 1h

### Dépendances

**Dépend de** : Phase 7 (données utilisateur complètes)

**Bloque** : Phase 9 (tests nécessitent UI complète)

### Risques

Aucun risque majeur identifié.

---

## Phase 9 : QA & Polish

**Durée** : J25-J26 (2 jours)

**Objectif** : contrôle expert + UX finale + documentation

### Livrables

✅ Tests unitaires (Python + React) avec coverage ≥ 80% / 70%  
✅ Tests e2e (Playwright) : scénarios principaux  
✅ Spot-check expert ≥ 90%  
✅ Documentation complète (README.md, DEVELOPER.md)  
✅ Rapport final qualité (`final_report.md`)  
✅ Script pipeline complet (`run_all.sh` avec option `--subset`)

### Tâches

**[069]** Créer test pipeline global (`tests/test_pipeline.py`)  
**[070]** Tests unitaires Python — extraction  
**[071]** Tests unitaires Python — validation  
**[072]** Tests unitaires React — composants  
**[073]** Tests d'intégration e2e (Playwright)  
**[074]** Spot-check expert sur 50 questions  
**[075]** Ajustements prompts si taux < 90%  
**[074b]** Vérification fidélité lexicale automatique (`fidelity_check.py`)  
**[080]** UX/UI refinement (responsive, animations, cohérence visuelle)  
**[081]** Rédiger README.md utilisateur  
**[082]** Rédiger guide développeur (DEVELOPER.md)  
**[083]** Nettoyage code et linting (ESLint + Prettier + Black + Flake8)  
**[084]** Audit final qualité données  
**[085]** Générer rapport final qualité (`final_report.md`)  
**[086]** Créer script `run_all.sh` (pipeline complet)  
**[086b]** Ajouter option `--subset N` dans `run_all.sh`

### Validation

- Coverage tests : ≥ 80% Python, ≥ 70% React
- Test pipeline global : `n_validés == n_générés - n_rejetés`, conservation `chunk_id`
- Taux spot-check expert ≥ 90%
- Fidélité lexicale ≥ 50% (automatique)
- Aucune erreur linter
- `final_report.md` généré avec toutes métriques
- Pipeline complet exécutable via `bash scripts/run_all.sh`
- Dry run sur 10 modules < 2h via `bash scripts/run_all.sh --subset 10`

### Temps estimé

**Total** : 10-12h

**Répartition** :
- J25 matin : tests unitaires Python (069-071) — 4h
- J25 après-midi : tests unitaires React (072) + e2e (073) — 4h
- J26 matin : spot-check expert (074) + ajustements si nécessaire (075) + fidelity check (074b) — 3h
- J26 après-midi : UX/UI refinement (080) + documentation (081-082) + linting (083) + audits finaux (084-085) + pipeline script (086, 086b) — 4h

### Dépendances

**Dépend de** : toutes les phases précédentes (tests sur application complète)

**Bloque** : rien (phase finale)

### Risques

⚠️ **Spot-check < 90%** : si taux insuffisant → itération prompts (Phase 3), re-génération partielle, re-validation → peut ajouter 1-2 jours  
⚠️ **Tests e2e échouent** : si bugs UI critiques → correction + re-tests

---

## Dépendances Critiques (graphe)

```
Phase 0 (Setup)
    ↓
Phase 1 (Extraction)
    ↓
Phase 2 (Indexation & Alignement)  ← NOUVELLE
    ↓
Phase 3 (Génération QCM)
    ↓
Phase 4 (Validation Double)
    ↓
Phase 5 (Compilation & Examens)
    ↓
Phase 6 (Frontend Core)
    ↓
Phase 7 (Modes Avancés)
    ↓
Phase 8 (Dashboard)
    ↓
Phase 9 (QA & Polish)
```

**Chemin critique** : toutes les phases sont séquentielles (aucun parallélisme possible entre phases).

**Points de blocage potentiels** :

| Phase | Risque de blocage | Mitigation |
|-------|-------------------|------------|
| 3 | Taux génération < 80% | Itérer prompts, retry logic |
| 4 | Taux rejet > 30% | Revoir seuils ou re-générer |
| 5 | Couverture < 85% | Re-générer chunks orphelins |
| 9 | Spot-check < 90% | Itération prompts + re-génération partielle |

---

## Métriques de Suivi par Phase

| Phase | KPI Principal | Seuil de validation | Outil de mesure |
|-------|---------------|---------------------|-----------------|
| 0 | Tests IA passants | 100% | Scripts test manuels |
| 1 | Modules générés | ≥ 12 | Count `modules/*.json` |
| 2 | Chunks indexés | ≥ 80% avec ≥ 3 mots-clés | `keywords.json` stats |
| 3 | QCM générés | ≥ 2500 | Count `generated_raw.json` |
| 4 | Taux validation | ≥ 80% (≥ 2000 QCM) | Logs pipeline |
| 5 | Couverture corpus | ≥ 90% | `coverage_report.md` |
| 6 | UI fonctionnelle | 100% modes révision + entraînement | Tests manuels |
| 7 | Examens calibrés | 6 × 60 Q | Count `exams/*.json` |
| 8 | Dashboard complet | 100% métriques affichées | Tests manuels |
| 9 | Spot-check expert | ≥ 90% | Revue manuelle 50 Q |

---

## Planning Détaillé (calendrier)

### Semaine 1 (J1-J5)

| Jour | Phase | Activités principales | Livrables |
|------|-------|----------------------|-----------|
| J1 | 0 | Setup frontend + Python + Ollama | Environnement complet |
| J2 | 0 | Setup BioBERT + tests environnement | Tests IA passants |
| J3 | 1 | Développement extraction PDF (regex, chunks) | `extract_pdfs.py` |
| J4 | 1 | Exécution extraction + génération metadata | `modules/*.json` |
| J5 | 1 | Validation manuelle taxonomie | Taxonomie validée |

### Semaine 2 (J6-J10)

| Jour | Phase | Activités principales | Livrables |
|------|-------|----------------------|-----------|
| J6 | 2 | Indexation TF-IDF + développement analyse annales | `keywords.json` en cours |
| J7 | 2 | Analyse annales + config seuils adaptatifs | `annales_profile.json` + seuils |
| J8 | 3 | Développement génération batch | `generate_batch.py` |
| J9 | 3 | Exécution génération batch (5h machine) | `generated_raw.json` |
| J10 | 3 | Feedback itératif stylistique | Style calibré |

### Semaine 3 (J11-J15)

| Jour | Phase | Activités principales | Livrables |
|------|-------|----------------------|-----------|
| J11 | 4 | Développement BioBERT + scoring | BioBERT opérationnel |
| J12 | 4 | Développement semantic_validator | `semantic_validator.py` |
| J13 | 4 | Exécution validation sémantique | `generated_scored.json` |
| J14 | 5 | Développement validate_all.py | Déduplication + validation |
| J15 | 5 | Développement exam_builder.py | `exam_builder.py` |

### Semaine 4 (J16-J20)

| Jour | Phase | Activités principales | Livrables |
|------|-------|----------------------|-----------|
| J16 | 5 | Génération rapports (coverage + fidelity) | Rapports qualité |
| J17 | 6 | Store Zustand + QuestionCard | Store + composant de base |
| J18 | 6 | RevisionMode | Mode Révision fonctionnel |
| J19 | 6 | TrainingMode + routing | Mode Entraînement fonctionnel |
| J20 | 7 | ExamMode | Mode Concours fonctionnel |

### Semaine 5 (J21-J26)

| Jour | Phase | Activités principales | Livrables |
|------|-------|----------------------|-----------|
| J21 | 7 | Logique adaptative | Adaptatif calibré |
| J22 | 7 | Système feedback + persistance | Feedback fonctionnel |
| J23 | 8 | Dashboard (score, modules faibles, progression) | Dashboard complet |
| J24 | 8 | Historique examens | Dashboard finalisé |
| J25 | 9 | Tests unitaires + e2e | Tests complets |
| J26 | 9 | Spot-check expert + documentation + polish | Application v1 prête |

---

## Estimations Temps Total

| Phase | Temps estimé | % du total |
|-------|--------------|-----------|
| 0 | 2h30 | 2% |
| 1 | 8-10h | 8% |
| 2 | 5-6h | 5% |
| 3 | 6-8h (+ 5h machine) | 11% |
| 4 | 8-10h (+ 3h machine) | 11% |
| 5 | 8-10h | 8% |
| 6 | 8-10h | 8% |
| 7 | 8-10h | 8% |
| 8 | 5-6h | 5% |
| 9 | 10-12h | 10% |

**Total travail effectif** : ~70-85h (hors temps machine ~8h)

**Total calendaire** : 26 jours (sans week-ends)

**Avec week-ends** : ~5-6 semaines calendaires

---

## Modifications Intégrées (vs plan initial)

### Phase 2 (nouvelle) : Indexation & Alignement

**Ajouts** :
- `index_chunks.py` : extraction TF-IDF keywords
- `analyze_annales.py` : analyse style annales (longueur, structure, pondération)
- `stylistic_validator.py` : mesure distance Levenshtein + similarité phrastique
- Configuration seuils BioBERT adaptatifs par module (0.05-0.10)

**Justification** : garantir fidélité lexicale (TF-IDF) et stylistique (annales) dès le départ.

### Phase 3 : Génération QCM

**Ajout** :
- [023b] Feedback itératif stylistique : auto-calibration prompts si distance > 0.35

**Justification** : L'IA se calibre elle-même sur le style des annales (IA de calibration pédagogique).

### Phase 4 : Validation Double

**Modification** :
- [031b] Application seuils BioBERT adaptatifs par module (chargés depuis `metadata.json`)

**Justification** : pharmacologie nécessite précision biomédicale supérieure (0.08-0.10 vs 0.05-0.06).

### Phase 5 : Compilation & Examens

**Ajouts** :
- [035b] Règle automatique classification difficultés (context_score > 0.9 + explication > 40 mots = hard)
- [066b] Rapport visuel fidélité (HTML + heatmap)

**Justification** : automatiser classification difficultés, rendre rapports lisibles humain.

### Phase 6 : Frontend Core

**Ajout** :
- [040b] Mécanisme purge localStorage (> 90 jours)

**Justification** : éviter croissance indéfinie localStorage (limite navigateur ~10 Mo).

### Phase 9 : QA & Polish

**Ajouts** :
- [069] Test pipeline global (cohérence compteurs : n_validés == n_générés - n_rejetés)
- [086b] Option `--subset N` dans `run_all.sh` (dry run sur N modules)

**Justification** : valider cohérence pipeline end-to-end, permettre dry runs rapides avant full run.

---

## Checklist Avant Lancement

✅ **Environnement** :
- [ ] Node.js 20.x installé
- [ ] Python 3.13 installé
- [ ] Ollama installé + Mistral 7B téléchargé
- [ ] GPU disponible (optionnel, accélère BioBERT)

✅ **Corpus** :
- [ ] 3 PDF sources présents dans `/Concours IADE/`
- [ ] PDF lisibles (pas de protection DRM)

✅ **Outils** :
- [ ] Git configuré (pour versionner fichiers JSON)
- [ ] VSCode + extensions (ESLint, Prettier, Python)

✅ **Documentation** :
- [ ] `spec.md` lu et compris
- [ ] `plan.md` lu et compris (ce document)
- [ ] `tasks.md` généré (101 tâches détaillées)

---

## Ajustements Possibles en Cours de Route

### Si taux rejet Phase 4 > 30%

**Option 1** : abaisser seuils (context_score à 0.70, keywords_overlap à 0.45)  
**Option 2** : re-générer avec prompts améliorés (Phase 3)  
**Option 3** : accepter taux rejet plus élevé, viser 1800 QCM au lieu de 2000

**Décision** : à prendre en J13 après exécution validation complète.

### Si couverture Phase 5 < 85%

**Option 1** : re-générer sur chunks orphelins uniquement (mini-itération Phase 3-4)  
**Option 2** : accepter couverture réduite, documenter sections non couvertes  
**Option 3** : extraire manuellement sections manquantes, ajouter dans modules

**Décision** : à prendre en J16 après génération rapports.

### Si spot-check Phase 9 < 90%

**Option 1** : itérer sur prompts (identifier patterns d'erreurs), re-générer 500 Q, re-valider  
**Option 2** : correction manuelle des 50 Q échouées, documenter améliations v2  
**Option 3** : accepter seuil 85%, release v1 avec avertissement

**Décision** : à prendre en J26 après spot-check expert.

---

## Livrables Finaux v1

### Fichiers de données

- `src/data/modules/*.json` (≥ 12 modules)
- `src/data/keywords.json`
- `src/data/annales_profile.json`
- `src/data/metadata.json`
- `src/data/questions/revision.json` (≥ 800 Q)
- `src/data/questions/entrainement.json` (≥ 800 Q)
- `src/data/questions/concours.json` (≥ 800 Q)
- `src/data/questions/compiled.json` (≥ 2000 Q)
- `src/data/exams/exam_*.json` (6 examens)

### Scripts Python

- `scripts/extract_pdfs.py`
- `scripts/index_chunks.py`
- `scripts/analyze_annales.py`
- `scripts/ai_generation/generate_batch.py`
- `scripts/ai_generation/biobert_client.py`
- `scripts/ai_generation/semantic_validator.py`
- `scripts/ai_generation/validate_all.py`
- `scripts/ai_generation/classify_modes.py`
- `scripts/ai_generation/exam_builder.py`
- `scripts/reports/coverage_report.py`
- `scripts/reports/fidelity_check.py`
- `scripts/reports/stylistic_validator.py`
- `scripts/reports/fidelity_report_visual.py`
- `scripts/run_all.sh` (avec option `--subset`)

### Application React

- Composants : `QuestionCard`, `RevisionMode`, `TrainingMode`, `ExamMode`, `Dashboard`, `PDFViewer`
- Store : `useUserStore.ts`
- Routes : `/`, `/revision`, `/entrainement`, `/concours`, `/dashboard`

### Rapports qualité

- `docs/coverage_report.md`
- `docs/fidelity_report.md`
- `docs/fidelity_report.html` (avec heatmap)
- `docs/stylistic_report.md`
- `docs/spot_check_report.md`
- `docs/final_report.md`

### Documentation

- `README.md` (installation, démarrage rapide, utilisation modes)
- `docs/DEVELOPER.md` (architecture, contribution, scripts)
- `spec.md` (spécifications techniques complètes)
- `plan.md` (ce document, roadmap)
- `tasks.md` (101 tâches détaillées)

### Tests

- `tests/test_extraction.py`
- `tests/test_validation.py`
- `tests/test_semantic.py`
- `tests/test_pipeline.py`
- `src/components/__tests__/*.test.tsx`
- `e2e/*.spec.ts`

---

## Conclusion

Ce plan de développement couvre **26 jours de travail effectif** (5-6 semaines calendaires) pour livrer IADE NEW v1, une application complète et validée scientifiquement.

**Tous les raffinements critiques sont intégrés** :
- Seuils BioBERT adaptatifs
- Règle automatique difficultés
- Feedback itératif stylistique
- Mécanisme expiration localStorage
- Test pipeline global
- Option `--subset` pour dry runs
- Rapports visuels (HTML + heatmap)

**Le plan est prêt pour exécution.**

---

**Version** : 1.0  
**Date** : 5 novembre 2025  
**Statut** : Validé pour exécution

