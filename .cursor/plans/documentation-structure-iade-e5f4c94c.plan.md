<!-- e5f4c94c-a283-468e-8424-afc27666bf78 dfc6719f-aed7-4025-a38f-880549061886 -->
# Plan Optimisé Final : Documentation Structure IADE NEW

## Philosophie Fondamentale

**IADE NEW est un simulateur d'apprentissage intégral et une IA de calibration pédagogique.**

Principe directeur : "Aucune question ne sort du corpus, aucune explication n'est hors du texte."

Objectif : transformer un candidat en expert IADE via une réplication fidèle du cours et des annales, validée médicalement et sémantiquement. **L'app n'entraîne pas seulement le cerveau à raisonner selon le pattern des annales, elle devient elle-même calibrée sur ce pattern.**

## Métriques de Réussite v1 (affinées)

| Critère | Objectif |

|---------|----------|

| Couverture corpus | ≥ 90% |

| Nombre total QCM | ≥ 2000 |

| Examens blancs | 6 × 60 questions calibrées |

| Fidélité sémantique (context_score) | ≥ 0.75 |

| Overlap lexical (keywords_overlap) | ≥ 0.5 |

| Score BioBERT (adaptatif par module) | ≥ 0.05 (base), ≥ 0.08-0.10 (pharmaco) |

| Taux rejet global | < 20% |

| Accord expert (spot-check) | ≥ 90% |

| Distance stylistique vs annales | < 0.3 (Levenshtein normalisé) |

---

## 1. spec.md — Spécifications Techniques et Pédagogiques

### Ajouts Critiques Intégrés

**Section I. Vue d'ensemble** — inchangé, mais ajout explicite :

- "IADE NEW est une **IA de calibration pédagogique**, pas un générateur de QCM classique"

**Section II. Corpus et taxonomie** — ajout module-specifique :

- Configuration `biomedical_threshold` par module :
  ```json
  {
    "respiratoire": 0.05,
    "cardio": 0.06,
    "pharma_generaux": 0.10,
    "pharma_opioides": 0.10,
    "pharma_curares": 0.08,
    "transfusion": 0.09
  }
  ```


**Section III. Modèle de données** — ajout champs :

```json
{
  "biomedical_score": 0.83,
  "biomedical_threshold": 0.08,
  "context_score": 0.77,
  "keywords_overlap": 0.6,
  "stylistic_distance": 0.25,
  "explanation_length": 142
}
```

**Section IV. Pipeline IA** — nouvelles étapes :

**Étape 2ter : Feedback Itératif sur Analyse Annales**

- Après chaque génération batch, mesurer distance stylistique :
  - Levenshtein normalisé : `edit_distance(qcm_generated, annales_sample) / max_length`
  - Similarité phrastique (sentence-transformers)
- Auto-calibration des prompts si distance > 0.35
- Sortie : `src/data/style_calibration_log.json`

**Étape 4 (modifiée) : Validation BioBERT Adaptative**

- **Seuils adaptatifs par module** (voir Section II)
- Calcul moyenne par module après chaque batch
- Ajustement dynamique si écart > 0.02 vs cible

**Étape 7 (modifiée) : Classification Difficultés Automatique**

- Règle explicite :
  ```python
  if context_score > 0.9 and len(explanation.split()) > 40:
      difficulty = "hard"
  elif context_score < 0.65 or len(explanation.split()) < 20:
      difficulty = "easy"
  else:
      difficulty = "medium"
  ```


**Section VI. Interface utilisateur** — ajout :

**Mécanisme d'expiration localStorage**

- Purge automatique des logs > 90 jours
- Exécutée au démarrage de l'app
- Conserve uniquement : `examResults` (all), `feedbackLog` (90j), `byModule.lastSeen` (1 an)

**Section VII. Scripts** — ajouts :

13. `scripts/reports/stylistic_validator.py` **(NOUVEAU)**

    - Args : `--questions validated.json --annales-profile src/data/annales_profile.json --out docs/stylistic_report.md`
    - Out : `stylistic_report.md` (distance Levenshtein, similarité phrastique par module)

14. `scripts/reports/fidelity_report_visual.py` **(NOUVEAU)**

    - Args : `--questions validated.json --keywords src/data/keywords.json --out docs/fidelity_report.html`
    - Out : `fidelity_report.html` (table + heatmap par module, lisible humain)

15. `scripts/run_all.sh` — option `--subset N` **(MODIFIÉ)**

    - `--subset 10` : exécute pipeline sur 10 modules seulement (dry run)
    - Permet validation rapide avant full run

**Section VIII. Qualité** — ajout :

**Test pipeline global**

- `tests/test_pipeline.py` : exécute pipeline complet en mini sur 1 module (5 pages)
- Vérifie cohérence : `n_QCM_validés == n_QCM_générés - n_QCM_rejetés`
- Vérifie conservation `chunk_id` à travers toutes les étapes
- Coverage : pipeline complet

**Section IX. Pédagogie adaptative** — ajout :

**Mécanisme d'expiration mémoire**

```typescript
// Au démarrage de l'app
const purgeOldLogs = (stats: UserStats) => {
  const cutoff = Date.now() - 90 * 24 * 60 * 60 * 1000; // 90 jours
  stats.feedbackLog = stats.feedbackLog.filter(log => 
    new Date(log.ts).getTime() > cutoff
  );
};
```

**Section XI. Roadmap versions** — ajout v2 :

**v2 : Cas Cliniques & Simulation (future)**

- Mode "Cas cliniques" : 10 questions longues, chronométrées
- Format : énoncé de cas (200-400 mots) + QCM contextuel
- Extraction automatique des scénarios types depuis annales :
  - Choc septique
  - Intubation difficile
  - Complications transfusionnelles
  - Urgences anesthésiques
- Générateur de cas : combine chunks multiples d'un même module
- Validation renforcée : cohérence narrative + biomédicale

---

## 2. plan.md — Roadmap de Développement (9 phases, J1-J26)

### Modifications des Phases pour Intégrer les Raffinements

**Phase 2 (modifiée) : Indexation & Alignement (J6-J7)**

Ajout tâche :

- [024b] Créer script `stylistic_validator.py` — mesure distance Levenshtein + similarité phrastique
- [025b] Configurer seuils BioBERT adaptatifs par module dans `metadata.json`

**Phase 3 (modifiée) : Génération QCM (J8-J10)**

Ajout tâche :

- [023b] Exécuter feedback itératif stylistique : après génération, mesurer distance, ajuster prompts si nécessaire

**Phase 4 (modifiée) : Validation Double (J11-J13)**

Modification :

- [031] devient : calculer `biomedical_score` + appliquer seuil adaptatif du module

**Phase 5 (modifiée) : Compilation & Examens (J14-J16)**

Ajout tâches :

- [035b] Implémenter règle automatique de classification difficultés (context_score > 0.9 + explication > 40 mots = hard)
- [066b] Générer rapport visuel fidélité (`fidelity_report.html` avec heatmap)

**Phase 6 (modifiée) : Frontend Core (J17-J19)**

Ajout tâche :

- [040b] Implémenter mécanisme purge localStorage (> 90 jours)

**Phase 9 (modifiée) : QA & Polish (J25-J26)**

Ajout tâches :

- [069] Créer test pipeline global (`tests/test_pipeline.py`)
- [086b] Ajouter option `--subset N` dans `run_all.sh`

---

## 3. tasks.md — Liste des Tâches Actionnables (101 tâches)

### Nouvelles Tâches Critiques Ajoutées

**Phase 2 : Indexation & Alignement**

**[024b] TODO** Créer script stylistic_validator.py

- Description : mesurer distance Levenshtein + similarité phrastique QCM vs annales
- Dépendances : [025]
- Fichiers concernés : `scripts/reports/stylistic_validator.py`
- Critères de validation : script exécutable, sortie `stylistic_report.md`
- Estimation : 2h

**[025b] TODO** Configurer seuils BioBERT adaptatifs par module

- Description : ajouter `biomedical_thresholds` dans `metadata.json` (pharma: 0.08-0.10, autres: 0.05-0.06)
- Dépendances : [025]
- Fichiers concernés : `src/data/metadata.json`
- Critères de validation : configuration validée par schéma
- Estimation : 30 min

**Phase 3 : Génération QCM**

**[023b] TODO** Exécuter feedback itératif stylistique

- Description : après génération batch, mesurer distance stylistique, ajuster prompts si > 0.35
- Dépendances : [023], [024b]
- Fichiers concernés : `scripts/ai_generation/generate_batch.py`, `src/data/style_calibration_log.json`
- Critères de validation : distance stylistique < 0.3 après ajustements
- Estimation : 2h

**Phase 4 : Validation Double**

**[031b] TODO** Appliquer seuils BioBERT adaptatifs par module

- Description : charger seuils depuis `metadata.json`, appliquer par module dans validation
- Dépendances : [031], [025b]
- Fichiers concernés : `scripts/ai_generation/biobert_client.py`
- Critères de validation : log montre seuils différenciés appliqués
- Estimation : 1h

**Phase 5 : Compilation & Examens**

**[035b] TODO** Implémenter règle automatique classification difficultés

- Description : `difficulty = "hard"` si `context_score > 0.9` ET `len(explanation) > 40 mots`
- Dépendances : [035]
- Fichiers concernés : `scripts/ai_generation/validate_all.py`
- Critères de validation : distribution conforme (40/40/20 ou 30/50/20)
- Estimation : 1h

**[066b] TODO** Générer rapport visuel fidélité (HTML + heatmap)

- Description : créer `fidelity_report_visual.py`, générer HTML avec table + heatmap par module
- Dépendances : [066]
- Fichiers concernés : `scripts/reports/fidelity_report_visual.py`, `docs/fidelity_report.html`
- Critères de validation : rapport HTML affiché avec heatmap
- Estimation : 2h

**Phase 6 : Frontend Core**

**[040b] TODO** Implémenter mécanisme purge localStorage

- Description : fonction `purgeOldLogs()` : supprime logs > 90 jours, exécutée au démarrage
- Dépendances : [040]
- Fichiers concernés : `src/store/useUserStore.ts`
- Critères de validation : logs purgés après 90 jours (test manuel)
- Estimation : 1h

**Phase 9 : QA & Polish**

**[069] TODO** Créer test pipeline global

- Description : `tests/test_pipeline.py` : exécute pipeline complet sur 1 module (5 pages), vérifie cohérence compteurs
- Dépendances : [037]
- Fichiers concernés : `tests/test_pipeline.py`
- Critères de validation : `n_validés == n_générés - n_rejetés`, conservation `chunk_id`
- Estimation : 3h

**[086b] TODO** Ajouter option --subset N dans run_all.sh

- Description : `--subset 10` exécute pipeline sur 10 modules seulement (dry run rapide)
- Dépendances : [086]
- Fichiers concernés : `scripts/run_all.sh`
- Critères de validation : dry run sur 10 modules < 2h
- Estimation : 1h

---

## Métriques Finales de Validation v1 (enrichies)

| Critère | Objectif |

|---------|----------|

| Couverture corpus | ≥ 90% |

| Nombre total QCM | ≥ 2000 |

| Examens blancs | 6 × 60 questions |

| Fidélité sémantique (context_score) | ≥ 0.75 |

| Overlap lexical (keywords_overlap) | ≥ 0.5 |

| Score BioBERT adaptatif | ≥ seuil module (0.05-0.10) |

| Taux rejet global | < 20% |

| Accord expert | ≥ 90% |

| Distance stylistique vs annales | < 0.3 |

| Cohérence pipeline (test global) | 100% |

**Total tâches** : 101 tâches actionnables

---

## Fichiers à Créer

1. `/Users/valentingaludec/IADE NEW/spec.md` (contenu exhaustif sections I-XII + raffinements)
2. `/Users/valentingaludec/IADE NEW/plan.md` (contenu exhaustif phases 0-9 + modifications)
3. `/Users/valentingaludec/IADE NEW/tasks.md` (contenu exhaustif 101 tâches + 7 nouvelles)

## Philosophie Finale

**"IADE NEW ne prépare pas seulement à un examen. Elle entraîne le cerveau à penser, raisonner et répondre comme un candidat IADE le jour J."**

**"L'app ne reproduit pas les annales : elle entraîne le cerveau à raisonner selon le pattern des annales, tout en étant elle-même calibrée sur ce pattern."**

## Cohérence Inter-Documents

- **spec.md** définit QUOI (schémas, contraintes, métriques, seuils adaptatifs)
- **plan.md** définit QUAND et COMMENT (phases, dépendances, livrables, feedback itératif)
- **tasks.md** définit ACTIONS (tâches atomiques, 1 commit = 1 tâche, 101 tâches total)

## Points Critiques Intégrés (résumé)

1. ✅ Validation BioBERT adaptative (seuils 0.05-0.10 selon module)
2. ✅ Règle automatique difficulté (context_score > 0.9 + explication > 40 mots)
3. ✅ Option --subset pour dry runs (10 modules)
4. ✅ Feedback itératif stylistique (distance Levenshtein + auto-calibration prompts)
5. ✅ Mécanisme expiration localStorage (purge > 90 jours)
6. ✅ Test pipeline global (cohérence compteurs)
7. ✅ Rapport fidélité visuel (HTML + heatmap lisible humain)
8. ✅ Roadmap v2 Cas Cliniques (format long, scénarios types)

### To-dos

- [ ] Créer spec.md avec les 11 sections détaillées (vue d'ensemble, corpus, modèle de données, pipeline IA, modes pédagogiques, UI, scripts, qualité, sécurité, roadmap, points à challenger)
- [ ] Créer plan.md avec la roadmap complète en 8 phases (J1-J25) incluant vision, phases détaillées, dépendances, métriques de suivi
- [ ] Créer tasks.md avec les 84 tâches actionnables organisées par phase avec description, dépendances, fichiers, critères de validation, estimation
- [ ] Vérifier la cohérence entre les 3 fichiers (références croisées, alignement des numéros de tâches, cohérence des estimations)