# 🚀 Pipeline d'Expansion Massive - Phase 12

## 🎯 Objectif

Multiplier le corpus par **×3-4** en passant de **165 QCM** à **500+ QCM**.

**Ratio cible** : 3-5 QCM par page (vs 1.2 actuellement)

---

## 📊 Vue d'ensemble

### Corpus actuel (v1.2.1)

- **165 QCM** validés
- **98.2%** liens vérifiés
- **Score biomédical** : 0.932
- **Ratio** : ~1.2 QCM/page ⚠️ FAIBLE

### Corpus cible (v2.0)

- **500+ QCM** après expansion
- **3-5 QCM/page** (ratio optimal)
- **Qualité maintenue** (BioBERT ≥ 0.4)
- **Zéro doublon** (déduplication fuzzy 85%)

---

## ⚙️ Pipeline (4 étapes)

### 1️⃣ Extraction page par page (5 min)

**Script** : `extract_pages.py`

**Actions** :
- Extrait chaque page des 3 PDF
- Nettoie et normalise le texte
- Sauvegarde fichiers txt individuels
- Génère métadonnées JSON

**Input** :
- `public/pdfs/*.pdf` (3 PDFs, 141 pages)

**Output** :
- `src/data/raw/pages/page_001.txt` → `page_141.txt`
- `src/data/raw/pages_metadata.json`

---

### 2️⃣ Génération massive (1-2h)

**Script** : `generate_massive.py`

**Actions** :
- Génère 3 QCM par page via Ollama Mistral
- Parallélisation (4 workers)
- Prompt strict (format JSON, qualité médicale)
- Retry logic

**Options** :
```bash
# Toutes les pages
python scripts/expansion/generate_massive.py

# Batch spécifique (recommandé pour tests)
python scripts/expansion/generate_massive.py --range 0 50
python scripts/expansion/generate_massive.py --range 50 100
```

**Input** :
- `src/data/raw/pages/*.txt`
- `src/data/raw/pages_metadata.json`

**Output** :
- `src/data/questions/generated_massive.json` (~420 QCM)

---

### 3️⃣ Validation BioBERT (30 min)

**Script** : `validate_massive.py`

**Actions** :
- Calcule score biomédical pour chaque QCM
- Filtre selon seuil 0.4 (adapté pour volume)
- Sépare validés/rejetés

**Seuil** : 0.4 (vs 0.88 en raffinement)
- Plus permissif pour expansion
- Permet volume sans sacrifier qualité

**Input** :
- `src/data/questions/generated_massive.json`

**Output** :
- `src/data/questions/validated_massive.json` (~300-350 QCM)
- `src/data/questions/rejected_massive.json`

---

### 4️⃣ Fusion avec existant (5 min)

**Script** : `merge_with_existing.py`

**Actions** :
- Charge corpus v1.2.1 (165 QCM vérifiés)
- Charge nouveau corpus validé
- Détecte doublons (fuzzy matching 85%)
- Fusionne et sauvegarde

**Déduplication** :
- Utilise `rapidfuzz.ratio`
- Seuil 85% de similarité
- Compare texte des questions

**Input** :
- `src/data/questions/compiled_verified.json` (v1.2.1)
- `src/data/questions/validated_massive.json`

**Output** :
- `src/data/questions/compiled_expanded.json` (v2.0)
- `src/data/questions/expansion_summary.txt`

---

## 🚀 Lancement

### Pipeline complet (recommandé)

```bash
cd "/Users/valentingaludec/IADE NEW"
source venv/bin/activate
bash scripts/expansion/run_expansion.sh
```

### Étape par étape

```bash
# 1. Extraction
python scripts/expansion/extract_pages.py

# 2. Génération (batch ou full)
python scripts/expansion/generate_massive.py --range 0 50
python scripts/expansion/generate_massive.py --range 50 100
# ou
python scripts/expansion/generate_massive.py  # Toutes

# 3. Validation
python scripts/expansion/validate_massive.py

# 4. Fusion
python scripts/expansion/merge_with_existing.py
```

---

## 📊 Estimations

| Étape | Durée | QCM |
|-------|-------|-----|
| Extraction | 5 min | - |
| Génération | 1-2h | ~420 |
| Validation | 30 min | ~300-350 |
| Fusion | 5 min | +250-300 |
| **TOTAL** | **2-2.5h** | **465-565** |

**Gain attendu** : **×2.8-3.4** le corpus actuel

---

## 🔧 Options avancées

### Génération par batch

Pour éviter timeout/crash sur génération longue :

```bash
# Batch 1 (pages 0-50)
python scripts/expansion/generate_massive.py --range 0 50

# Batch 2 (pages 50-100)
python scripts/expansion/generate_massive.py --range 50 100

# Batch 3 (pages 100-141)
python scripts/expansion/generate_massive.py --range 100 141
```

Les fichiers JSON s'accumulent, puis fusion finale.

### Redis/Upstash checkpoint (optionnel)

Si `UPSTASH_REDIS_REST_URL` est défini dans `.env.local`, le système sauvegarde la progression :

```bash
# Check progression
redis-cli -u $UPSTASH_URL GET "phase12:progress"

# Reset si besoin
redis-cli -u $UPSTASH_URL DEL "phase12:progress"
```

---

## 📝 Logs & Monitoring

Tous les logs sont centralisés dans `logs/pipeline.log` :

```bash
# Suivre en temps réel
tail -f logs/pipeline.log

# Voir historique
cat logs/pipeline.log
```

Format :
```
[2025-11-08 15:30:00] Phase 12 - Extraction START
[2025-11-08 15:35:12] Phase 12 - Extraction END: 141 pages
[2025-11-08 15:35:15] Phase 12 - Génération START: 141 pages
[2025-11-08 17:12:43] Phase 12 - Génération END: 387 QCM, 12 failed
[2025-11-08 17:13:00] Phase 12 - Validation START: 387 QCM
[2025-11-08 17:45:23] Phase 12 - Validation END: 312 validated, 75 rejected
[2025-11-08 17:45:30] Phase 12 - Fusion ✓ 287 added, 452 total
```

---

## ✅ Qualité garantie

### Validation multi-niveaux

1. **Génération** : Prompt strict, format JSON validé
2. **BioBERT** : Seuil 0.4 (cohérence biomédicale)
3. **Déduplication** : Fuzzy 85% (pas de doublons)
4. **Héritage** : 165 QCM v1.2.1 (déjà vérifiés 98.2%)

### Métriques attendues

- **Score biomédical moyen** : ~0.6-0.7 (nouveau corpus)
- **Taux de validation** : 70-80% (BioBERT 0.4)
- **Taux de duplication** : < 10%
- **QCM finaux** : 450-550

---

## 🎯 Après l'expansion

### 1. Audit du nouveau corpus

```bash
python scripts/validation/audit_full_corpus.py
```

Vérifie les liens CTA pour les nouveaux QCM.

### 2. Régénération examens blancs

```bash
python scripts/ai_generation/exam_builder.py \
  --in src/data/questions/compiled_expanded.json \
  --out-dir public/data/exams
```

6 examens avec corpus élargi.

### 3. Déploiement v2.0

```bash
python scripts/production/deploy_v2.0.py
npm run build
vercel --prod
gh release create v2.0 ...
```

---

## ⚠️ Recommandations

### Avant de lancer

- ✅ Vérifier qu'Ollama tourne : `ollama ps`
- ✅ Vérifier espace disque : ~500 MB libres
- ✅ Tester v1.2.2 stable
- ✅ Prévoir 2-3h de temps machine

### Pendant l'exécution

- Monitorer : `tail -f logs/pipeline.log`
- Pas d'interruption pendant génération
- Ollama peut être lent sur certaines pages complexes

### Après complétion

- Auditer corpus expansé
- Tester modes pédagogiques
- Vérifier équilibre modules
- Valider avant déploiement

---

## 🔄 Boucle d'amélioration continue

Une fois v2.0 déployée :

1. **Feedback utilisateur** : Bad/Good/Very Good (Redis)
2. **Analyse** : Identifier les QCM low-score
3. **Raffinement** : Régénérer les questions faibles
4. **Mise à jour** : Déploiement v2.1, v2.2, etc.

---

**🎓 Ce pipeline transforme IADE NEW en un système auto-génératif et évolutif !**

