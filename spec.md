# IADE NEW — Spécifications Techniques v1.0

**Document de référence absolu** : toute décision technique doit être justifiée par ce document.

Date : 5 novembre 2025  
Version : 1.0  
Statut : Validé pour implémentation

---

## I. Vue d'ensemble du projet

### Objectif pédagogique

IADE NEW est un **simulateur d'apprentissage intégral**, pas une simple application de QCM.

**Principe fondateur** : "Aucune question ne sort du corpus, aucune explication n'est hors du texte."

L'application transforme un candidat IADE en expert via une réplication fidèle du cours officiel et des annales, validée médicalement (BioBERT), sémantiquement (embeddings) et lexicalement (TF-IDF).

**IADE NEW est une IA de calibration pédagogique** : elle n'entraîne pas seulement le cerveau à raisonner selon le pattern des annales, elle devient elle-même calibrée sur ce pattern via un feedback itératif stylistique.

### Stack technique complète

| Domaine | Technologies | Justification |
|---------|--------------|---------------|
| Frontend | React 18 + Vite + Tailwind CSS + Zustand | Moderne, performant, composants réutilisables |
| Backend/Scripts | Python 3.13 (scripts autonomes) | Écosystème IA riche, pas de serveur nécessaire |
| IA Génération | Ollama (Mistral 7B) | IA locale, gratuite, qualité suffisante |
| IA Validation | BioBERT (dmis-lab/biobert-base-cased-v1.1) | Spécialisé biomédical, embeddings de qualité |
| Données | JSON plats dans `/src/data/` | Simple, versionnable, pas de SGBD nécessaire |
| Persistance | localStorage (navigateur) | 100% local, pas de backend requis |
| Cache optionnel | Redis (Upstash) | Pour feedback utilisateur (Bad/Good/Very Good) |

### Architecture générale

```
IADE NEW/
├── src/                          # Application React
│   ├── components/               # Composants UI
│   ├── data/                     # Données compilées (JSON)
│   ├── store/                    # État global (Zustand)
│   └── utils/                    # Utilitaires frontend
├── scripts/                      # Pipeline IA Python
│   ├── extract_pdfs.py          # Extraction corpus
│   ├── index_chunks.py          # Indexation TF-IDF
│   ├── analyze_annales.py       # Analyse style annales
│   ├── ai_generation/           # Génération et validation
│   ├── reports/                 # Génération rapports
│   └── run_all.sh               # Pipeline complet
├── tests/                        # Tests unitaires et e2e
└── docs/                         # Rapports qualité
```

### Contraintes fondamentales

1. **Cohérence biomédicale validée** : score BioBERT avec seuils adaptatifs par module (0.05-0.10)
2. **Fidélité sémantique mesurée** : cosine similarity embeddings ≥ 0.75
3. **Fidélité lexicale contrôlée** : overlap mots-clés TF-IDF ≥ 0.5
4. **Exhaustivité du corpus garantie** : couverture ≥ 90%, chaque chunk → ≥ 1 QCM
5. **Calibration stylistique** : distance Levenshtein vs annales < 0.3, auto-ajustement prompts

---

## II. Corpus source et taxonomie

### Description des 3 PDF sources

| Fichier | Type | Rôle | Pages estimées |
|---------|------|------|----------------|
| `Prepaconcoursiade-Complet.pdf` | Cours officiels IADE | Source primaire pour génération QCM révision | ~800-1000 |
| `annalescorrigées-Volume-1.pdf` | Annales corrigées | Calibrage style + génération QCM concours | ~300-400 |
| `annalescorrigées-Volume-2.pdf` | Annales corrigées | Calibrage style + génération QCM concours | ~300-400 |

### Liste des 17 modules thématiques

Chaque module est identifié automatiquement puis validé manuellement.

| ID Module | Titre | Mots-clés seed | Seuil BioBERT |
|-----------|-------|----------------|---------------|
| `bases_physio` | Bases physiologie & homéostasie | cellule, compartiments, pH, osmolarité | 0.05 |
| `respiratoire` | Respiratoire | PEEP, Vt, PaO2/FiO2, capnographie, compliance | 0.05 |
| `cardio` | Cardio & Hémodynamique | PVC, PAM, DC, précharge, amines, remplissage | 0.06 |
| `neuro` | Neurologie & Anesthésie | PIC, PPC, GCS, sédation, neuroprotection | 0.06 |
| `pharma_generaux` | Pharmacologie – Anesthésiques généraux | propofol, étomidate, kétamine, thiopental | 0.10 |
| `pharma_locaux` | Pharmacologie – Anesthésiques locaux | lidocaïne, bupivacaïne, ropivacaïne, ALR | 0.08 |
| `pharma_opioides` | Pharmacologie – Opioïdes/Analgésie | morphine, sufentanil, fentanyl, palier OMS | 0.10 |
| `pharma_curares` | Pharmacologie – Curares | rocuronium, atracurium, sugammadex, décurarisation | 0.08 |
| `alr` | Anesthésie locorégionale | rachianesthésie, péridurale, blocs périphériques | 0.07 |
| `ventilation` | Ventilation & Voies aériennes | intubation, LMA, VNI, VMI, EtCO2, PEEP | 0.06 |
| `transfusion` | Transfusion & Hémostase | CGR, PFC, plaquettes, ROTEM, TEG, hémostase | 0.09 |
| `reanimation` | Réanimation & Urgences | sepsis, SDRA, choc, polytrauma, brûlés | 0.06 |
| `douleur` | Douleur aiguë & chronique | échelles, PCA, co-antalgiques, douleur chronique | 0.07 |
| `infectio` | Infectio, Asepsie, SSI | ATB périop, préparation cutanée, ISO | 0.07 |
| `monitorage` | Monitorage | SpO2, EtCO2, NIBP, IBP, BIS, PVC | 0.05 |
| `pediatrie` | Pédiatrie & Populations particulières | gériatrie, grossesse, obésité, pédiatrie | 0.06 |
| `legislation` | Législation, Éthique, Gestion des risques | consentement, traçabilité, vigilances | 0.05 |

**Objectif** : ≥ 200 QCM validés par module (total ≥ 2000 QCM pour 17 modules).

### Configuration seuils BioBERT adaptatifs par module

**Justification** : les modules de pharmacologie exigent une précision biomédicale supérieure (noms de molécules, posologies, contre-indications). Les modules physiologiques/procéduraux tolèrent un seuil plus bas.

**Implémentation** : stocké dans `src/data/metadata.json` :

```json
{
  "biomedical_thresholds": {
    "bases_physio": 0.05,
    "respiratoire": 0.05,
    "cardio": 0.06,
    "neuro": 0.06,
    "pharma_generaux": 0.10,
    "pharma_locaux": 0.08,
    "pharma_opioides": 0.10,
    "pharma_curares": 0.08,
    "alr": 0.07,
    "ventilation": 0.06,
    "transfusion": 0.09,
    "reanimation": 0.06,
    "douleur": 0.07,
    "infectio": 0.07,
    "monitorage": 0.05,
    "pediatrie": 0.06,
    "legislation": 0.05
  }
}
```

### Matrice de couverture

Générée automatiquement par `scripts/extract_pdfs.py`, puis complétée par `scripts/reports/coverage_report.py`.

Format `src/data/metadata.json` :

```json
{
  "coverage_map": {
    "respiratoire": {
      "pages_covered": [112, 113, 114, "...", 126],
      "total_pages": 80,
      "coverage_percent": 92.5,
      "chunks_count": 45,
      "chunks_with_qcm": 43
    }
  }
}
```

### Alignement Annales (nouvelle section)

**Objectif** : calibrer automatiquement les prompts de génération pour reproduire le style des annales IADE.

**Script** : `scripts/analyze_annales.py`

**Extraction** :
- **Typologie questions** : QCM simple (70%), QCM calculs (20%), QROC (10%)
- **Formulation typique** :
  - Longueur moyenne énoncé : 80-120 caractères
  - Structure syntaxique : "Quelle est...", "Parmi les propositions...", "Concernant..."
  - Pièges courants : options proches, valeurs numériques décalées
- **Pondération réelle** : modules les plus fréquents dans concours (cardio 25%, pharmaco 30%, respiratoire 20%)

**Sortie** : `src/data/annales_profile.json`

```json
{
  "avg_question_length": 95,
  "avg_explanation_length": 140,
  "common_starters": ["Quelle est", "Parmi les", "Concernant"],
  "module_weights": {
    "cardio": 0.25,
    "pharma_generaux": 0.15,
    "pharma_opioides": 0.10,
    "respiratoire": 0.20
  },
  "difficulty_distribution": {
    "easy": 0.30,
    "medium": 0.50,
    "hard": 0.20
  }
}
```

---

## III. Modèle de données (schémas JSON complets)

### Schéma `Question` (enrichi avec fidélité)

```json
{
  "id": "module_05_q12",
  "module_id": "pharma_opioides",
  "text": "Quelle est la classe thérapeutique de la morphine selon l'OMS ?",
  "options": [
    "Antalgique palier 1",
    "Antalgique palier 2",
    "Antalgique palier 3",
    "Aucune classification"
  ],
  "correctAnswer": 2,
  "explanation": "La morphine est un opioïde fort de palier 3 selon l'OMS. Elle est indiquée dans les douleurs intenses après échec des paliers 1 et 2. Posologie initiale : 10 mg PO ou 5 mg IV.",
  "difficulty": "medium",
  "mode": "revision",
  "source_pdf": "Prepaconcoursiade-Complet.pdf",
  "page": 142,
  "chunk_id": "pharma_opioides_05_c03",
  "source_context": "La morphine appartient à la classe des opioïdes forts (palier 3 OMS). Indications : douleurs sévères, post-opératoire...",
  "biomedical_score": 0.83,
  "biomedical_threshold": 0.10,
  "context_score": 0.77,
  "keywords_overlap": 0.6,
  "stylistic_distance": 0.25,
  "explanation_length": 142,
  "flags": {
    "ambiguous": false,
    "calc_needed": false,
    "validated_by_expert": false
  }
}
```

**Contraintes de validation strictes** :
- `options` : exactement 4, toutes distinctes (no duplicates)
- `correctAnswer` : ∈ [0, 1, 2, 3]
- `biomedical_score` > `biomedical_threshold` (adaptatif par module)
- `context_score` > 0.75
- `keywords_overlap` > 0.5
- `source_context` : non vide (preuve d'ancrage au texte)
- `stylistic_distance` < 0.3 (similitude aux annales)

### Schéma `Module`

```json
{
  "module_id": "respiratoire",
  "title": "Physiologie respiratoire & ventilation mécanique",
  "keywords": ["PEEP", "Vt", "PaO2/FiO2", "capnographie", "compliance", "résistances"],
  "sections": [
    {
      "section_id": "resp_01",
      "title": "Mécanique ventilatoire",
      "pages": [112, 126],
      "chunks": [
        {
          "chunk_id": "resp_01_c01",
          "text": "La mécanique ventilatoire repose sur...",
          "source_pdf": "Prepaconcoursiade-Complet.pdf",
          "page_start": 112,
          "page_end": 114,
          "token_count": 1150
        }
      ]
    }
  ],
  "coverage_percent": 92.5,
  "question_count": 245,
  "biomedical_threshold": 0.05
}
```

### Schéma `metadata.json`

```json
{
  "generated_at": "2025-11-05T10:00:00Z",
  "sources": [
    {
      "file": "Prepaconcoursiade-Complet.pdf",
      "type": "cours",
      "pages": 950,
      "extracted_pages": 920
    },
    {
      "file": "annalescorrigées-Volume-1.pdf",
      "type": "annales",
      "pages": 350,
      "extracted_pages": 340
    },
    {
      "file": "annalescorrigées-Volume-2.pdf",
      "type": "annales",
      "pages": 380,
      "extracted_pages": 370
    }
  ],
  "modules": {
    "respiratoire": {
      "title": "Physiologie respiratoire & ventilation",
      "chunks_count": 45,
      "coverage_percent": 92.5
    }
  },
  "extraction_date": "2025-11-05T10:00:00Z",
  "total_pages": 1680,
  "total_chunks": 780,
  "coverage_map": {},
  "biomedical_thresholds": {},
  "module_map_overrides": {
    "Transfusion sanguine": "transfusion",
    "Douleur post-opératoire": "douleur"
  }
}
```

### Schéma `UserStats` (localStorage)

```typescript
interface UserStats {
  attempts: number;
  correct: number;
  byModule: Record<string, {
    attempts: number;
    correct: number;
    lastSeen: string; // ISO date
    weakKeywords: string[]; // mots-clés des questions ratées
  }>;
  streakDays: number;
  lastActivityDate: string;
  feedbackLog: Array<{
    questionId: string;
    score: 1 | 2 | 3; // Bad / Good / Very Good
    ts: string; // ISO timestamp
  }>;
  examResults: Array<{
    examId: string;
    score: number;
    totalQuestions: number;
    date: string;
    duration: number; // minutes
  }>;
  nextReview: Record<string, string>; // questionId → ISO date (SM-2 algorithm)
}
```

**Mécanisme d'expiration** : logs > 90 jours purgés au démarrage (sauf `examResults` conservés indéfiniment).

### Schéma `Exam` (examens blancs)

```json
{
  "exam_id": "exam_01_physio_pharma",
  "title": "Examen Blanc 1 : Physiologie & Pharmacologie",
  "description": "Examen thématique couvrant respiratoire, cardio, pharmaco générale",
  "duration_minutes": 120,
  "question_count": 60,
  "question_ids": [
    "respiratoire_03_q12",
    "cardio_05_q08",
    "..."
  ],
  "module_weights": {
    "respiratoire": 0.25,
    "cardio": 0.20,
    "pharma_generaux": 0.30,
    "pharma_opioides": 0.15,
    "monitorage": 0.10
  },
  "difficulty_distribution": {
    "easy": 0.30,
    "medium": 0.50,
    "hard": 0.20
  }
}
```

### Schéma `compiled.json` (consolidation finale)

```json
{
  "generated_at": "2025-11-05T10:00:00Z",
  "total_questions": 2145,
  "modules": {
    "respiratoire": 245,
    "cardio": 210,
    "pharma_generaux": 180
  },
  "coverage_percent": 91.3,
  "avg_biomedical_score": 0.79,
  "avg_context_score": 0.81,
  "avg_keywords_overlap": 0.67,
  "avg_stylistic_distance": 0.27,
  "rejection_rate": 0.17,
  "questions": []
}
```

---

## IV. Pipeline IA complet (avec double validation)

### Vue d'ensemble du pipeline

```
PDF Sources
    ↓
[Étape 1] Extraction & Segmentation (extract_pdfs.py)
    ↓
Modules/*.json (chunks)
    ↓
[Étape 2] Indexation TF-IDF (index_chunks.py)
    ↓
keywords.json
    ↓
[Étape 2bis] Analyse Annales (analyze_annales.py)
    ↓
annales_profile.json
    ↓
[Étape 2ter] Feedback Itératif Stylistique (stylistic_validator.py)
    ↓
style_calibration_log.json
    ↓
[Étape 3] Génération Q/A (generate_batch.py + Ollama Mistral)
    ↓
generated_raw.json (2500+ QCM bruts)
    ↓
[Étape 4] Validation BioBERT Adaptative (biobert_client.py)
    ↓
generated_biobert.json (+ biomedical_score)
    ↓
[Étape 5] Validation Sémantique (semantic_validator.py)
    ↓
generated_scored.json (+ context_score + keywords_overlap)
    ↓
[Étape 6] Réécriture Explicative (optionnelle, Mistral)
    ↓
generated_rewritten.json
    ↓
[Étape 7] Déduplication & Rigueur (validate_all.py)
    ↓
validated.json (2000+ QCM validés)
    ↓
[Étape 8] Classification par mode (classify_modes.py)
    ↓
revision.json + entrainement.json + concours.json
    ↓
[Étape 9] Génération Examens Blancs (exam_builder.py)
    ↓
exams/exam_*.json (6 examens × 60 Q)
    ↓
[Étape 10] Rapports Qualité (coverage_report.py + fidelity_report_visual.py)
    ↓
docs/*.md + docs/*.html
```

### Étape 1 : Extraction PDF (`extract_pdfs.py`)

**Objectif** : segmenter les 3 PDF en modules thématiques + chunks < 1200 tokens.

**Heuristiques de détection de titres** :
- Regex niveaux : `^\d+\.`, `^CHAPITRE`, `^PARTIE`, `^\p{Lu}{3,}`
- Sauts de pages + densité mots-clés
- Lignes majuscules suivies de paragraphe explicatif

**Découpage en chunks** :
- Fenêtres sémantiques : < 1200 tokens (pour Mistral 7B)
- Contexte stable : chaque chunk conserve le titre de section parent
- `chunk_id` unique : `{module_id}_{section_id}_c{num}`

**Normalisation** :
- Suppression en-têtes/pieds de page
- Conversion tableaux → texte structuré
- Nettoyage caractères spéciaux

**Sortie** : `src/data/modules/*.json`

**Signature** :
```bash
python scripts/extract_pdfs.py \
  --input "src/data/sources/*.pdf" \
  --out src/data/modules/ \
  --metadata src/data/metadata.json
```

### Étape 2 : Indexation & Alignement (`index_chunks.py`)

**Objectif** : extraire mots-clés dominants par chunk (TF-IDF) pour contrôle lexical ultérieur.

**Algorithme TF-IDF** :
- Vectorisation : `TfidfVectorizer(max_features=50, ngram_range=(1,2))`
- Top N mots-clés par chunk : N = 10
- Agrégation par module : union des mots-clés de tous les chunks

**Sortie** : `src/data/keywords.json`

```json
{
  "respiratoire": {
    "chunk_keywords": {
      "resp_01_c01": ["PEEP", "compliance", "résistances", "Vt", "pression"],
      "resp_01_c02": ["capnographie", "EtCO2", "CO2", "courbe"]
    },
    "module_keywords": ["PEEP", "Vt", "compliance", "EtCO2", "capnographie"]
  }
}
```

**Signature** :
```bash
python scripts/index_chunks.py \
  --modules src/data/modules/ \
  --out src/data/keywords.json
```

### Étape 2bis : Analyse des Annales (`analyze_annales.py`)

**Objectif** : extraire le profil stylistique des annales pour calibrer les prompts de génération.

**Extraction** :
- Longueur moyenne énoncés (caractères, mots)
- Structure syntaxique récurrente (débuts de phrases, connecteurs)
- Types de questions (QCM simple, calculs, QROC)
- Pondération modules (fréquence dans annales)

**Sortie** : `src/data/annales_profile.json` (cf. Section II)

**Signature** :
```bash
python scripts/analyze_annales.py \
  --annales "src/data/sources/annalescorrigées-*.pdf" \
  --out src/data/annales_profile.json
```

### Étape 2ter : Feedback Itératif sur Analyse Annales

**Objectif** : mesurer distance stylistique entre QCM générés et annales, auto-calibrer les prompts.

**Métriques** :
- **Levenshtein normalisé** : `edit_distance(qcm_text, annales_sample) / max(len(qcm_text), len(annales_sample))`
- **Similarité phrastique** : sentence-transformers (`all-MiniLM-L6-v2`)

**Auto-calibration** :
- Si `stylistic_distance > 0.35` → ajuster prompts (longueur, structure)
- Itération : re-générer échantillon, re-mesurer
- Objectif : `stylistic_distance < 0.3`

**Sortie** : `src/data/style_calibration_log.json`

```json
{
  "iterations": [
    {
      "iter": 1,
      "avg_distance": 0.42,
      "prompt_adjustments": ["Raccourcir énoncés", "Ajouter 'Quelle est...'"]
    },
    {
      "iter": 2,
      "avg_distance": 0.28,
      "status": "converged"
    }
  ]
}
```

**Signature** :
```bash
python scripts/reports/stylistic_validator.py \
  --questions generated_raw.json \
  --annales-profile src/data/annales_profile.json \
  --out src/data/style_calibration_log.json
```

### Étape 3 : Génération Q/A (`generate_batch.py`)

**Objectif** : générer 2500+ QCM bruts via Ollama Mistral 7B, strictement ancrés dans les chunks.

**Prompts Mistral** :

**Système prompt** :
```
Tu es un expert IADE. Génère des QCM *factuels* UNIQUEMENT à partir du CONTEXTE fourni.

Règles impératives :
- 4 options, 1 correcte
- Reprends les termes exacts du cours (fidélité lexicale)
- Pas d'ambiguïté, pas d'improvisation
- Style conforme aux annales IADE (voir profil)
- Cite toujours le contexte source (1-2 phrases)

Retourne un JSON array strict du schéma :
[
  {
    "text": "...",
    "options": ["...", "...", "...", "..."],
    "correctAnswer": 0-3,
    "explanation": "...",
    "source_context": "..."
  }
]
```

**User prompt** :
```
[MODULE]: respiratoire
[SECTION]: Mécanique ventilatoire
[CONTEXTE SOURCE]:
{chunk_text}

[MOTS-CLÉS ATTENDUS]: {keywords_list}
[PROFIL ANNALES]: Longueur moyenne 95 caractères, débute par "Quelle est...", "Parmi les..."
```

**Génération** : 2-4 QCM par chunk, retry 3× si parsing échoue.

**Sortie** : `src/data/questions/generated_raw.json`

**Signature** :
```bash
python scripts/ai_generation/generate_batch.py \
  --modules src/data/modules/ \
  --keywords src/data/keywords.json \
  --profile src/data/annales_profile.json \
  --out src/data/questions/generated_raw.json \
  --model mistral:latest \
  --per-chunk 3
```

### Étape 4 : Validation BioBERT Adaptative (`biobert_client.py`)

**Objectif** : valider cohérence biomédicale avec seuils adaptatifs par module.

**Pipeline HuggingFace** : `dmis-lab/biobert-base-cased-v1.1`

**Embeddings** :
- Input : `question_text + " " + explanation`
- Output : vecteur 768 dimensions

**Calcul score** :
- Centroïdes par module : embeddings moyens de seed-sentences biomédicales
- Cosine similarity : `cosine(question_embedding, module_centroid)`
- Score `biomedical_score ∈ [0, 1]`

**Seuils adaptatifs** :
- Chargés depuis `metadata.json` → `biomedical_thresholds`
- Appliqués par module : rejette si `biomedical_score < threshold`

**Heuristiques additionnelles** :
- Blacklist énoncés : "toujours", "jamais" (hors lois universelles)
- Détection items non mesurables (opinions, jugements)
- Cohérence numérique : unités, plages physiologiques (ex: PaO2 70-100 mmHg)

**Ajustement dynamique** :
- Calcul moyenne `biomedical_score` par module après chaque batch
- Si écart > 0.02 vs cible → ajuster seuil ±0.01

**Sortie** : `src/data/questions/generated_biobert.json` (ajout champs `biomedical_score`, `biomedical_threshold`)

**Signature** :
```bash
python scripts/ai_generation/biobert_client.py \
  --in generated_raw.json \
  --out generated_biobert.json \
  --metadata src/data/metadata.json
```

### Étape 5 : Validation Sémantique (`semantic_validator.py`)

**Objectif** : valider fidélité sémantique (embeddings) et lexicale (TF-IDF overlap).

**Calcul `context_score`** :
- Embeddings : question vs chunk source (BioBERT ou sentence-transformers)
- Cosine similarity : `cosine(question_embedding, source_chunk_embedding)`
- Seuil : `context_score > 0.75`

**Calcul `keywords_overlap`** :
- Extraction mots-clés question : intersection avec `keywords.json[module_id]`
- Overlap : `len(intersection) / len(module_keywords)`
- Seuil : `keywords_overlap > 0.5`

**Validation combinée** :
- Rejette question si **l'un des 3 scores** (biomedical, context, keywords) sous le seuil
- Logs détaillés : motif rejet par question

**Sortie** : `src/data/questions/generated_scored.json` (ajout champs `context_score`, `keywords_overlap`)

**Signature** :
```bash
python scripts/ai_generation/semantic_validator.py \
  --in generated_biobert.json \
  --modules src/data/modules/ \
  --keywords src/data/keywords.json \
  --out generated_scored.json
```

### Étape 6 : Réécriture Explicative (optionnelle)

**Objectif** : reformuler explications dans zone grise (biomedical_score ∈ [0.05, 0.15]).

**Prompt Mistral** :
```
Reformule l'explication pour un étudiant IADE : clair, structuré, garder chiffres et recommandations. 3-5 lignes maximum.
```

**Sortie** : `src/data/questions/generated_rewritten.json`

### Étape 7 : Déduplication & Rigueur (`validate_all.py`)

**Objectif** : nettoyer, dédupliquer, lisser distribution difficultés.

**Déduplication** :
- Hash unique : `sha256(text + "|" + options_sorted + "|" + module_id)`
- Suppression doublons exacts

**Validation format** :
- Exactement 4 options
- `correctAnswer ∈ [0, 1, 2, 3]`
- Options distinctes (no duplicates)

**Lissage distribution difficultés** :
- Cible par module : 40% easy / 40% medium / 20% hard
- Rééquilibrage si écart > 10%

**Classification automatique difficultés** :
```python
if context_score > 0.9 and len(explanation.split()) > 40:
    difficulty = "hard"
elif context_score < 0.65 or len(explanation.split()) < 20:
    difficulty = "easy"
else:
    difficulty = "medium"
```

**Vérification exhaustivité** :
- Chaque `chunk_id` doit avoir ≥ 1 QCM validé
- Alerte si chunks orphelins (sans QCM)

**Rattachement métadonnées** :
- Ajoute `source_pdf`, `page`, `chunk_id` si manquants

**Sortie** : `src/data/questions/validated.json`

**Signature** :
```bash
python scripts/ai_generation/validate_all.py \
  --in generated_scored.json \
  --out validated.json
```

### Étape 8 : Classification par mode (`classify_modes.py`)

**Objectif** : répartir questions entre révision / entraînement / concours.

**Critères** :
- **Révision** : toutes difficultés, explications détaillées (≥ 100 caractères)
- **Entraînement** : distribution équilibrée difficultés, explications + feedback immédiat
- **Concours** : répartition selon pondération annales, difficultés calibrées (30/50/20)

**Sortie** :
- `src/data/questions/revision.json`
- `src/data/questions/entrainement.json`
- `src/data/questions/concours.json`

**Signature** :
```bash
python scripts/ai_generation/classify_modes.py \
  --in validated.json \
  --out-dir src/data/questions/
```

### Étape 9 : Génération Examens Blancs (`exam_builder.py`)

**Objectif** : créer 6 examens thématiques calibrés (60 Q × 120 min).

**Examens** :
1. Exam 1 : Physiologie + Pharmacologie générale
2. Exam 2 : Cardio + Hémodynamique + Réanimation
3. Exam 3 : Respiratoire + Ventilation + Monitorage
4. Exam 4 : Pharmaco (opioïdes + curares + locaux)
5. Exam 5 : Anesthésie locorégionale + Douleur + Transfusion
6. Exam 6 : Mixte complet (tous modules, pondération annales)

**Équilibrage** :
- Difficultés : 30% easy / 50% medium / 20% hard
- Tous modules représentés dans ≥ 4 examens

**Sortie** : `src/data/exams/exam_01.json` ... `exam_06.json`

**Signature** :
```bash
python scripts/ai_generation/exam_builder.py \
  --in concours.json \
  --annales-profile src/data/annales_profile.json \
  --out-dir src/data/exams/ \
  --count 6
```

### Étape 10 : Rapports de Qualité

**`coverage_report.py`** :
- Nb QCM par module
- Couverture pages (%)
- Taux de rejet (%)
- Moyennes scores (BioBERT, context, keywords, stylistic)
- Liste chunks orphelins

**Sortie** : `docs/coverage_report.md`

**Signature** :
```bash
python scripts/reports/coverage_report.py \
  --modules src/data/modules/ \
  --questions validated.json \
  --out docs/coverage_report.md
```

**`fidelity_report_visual.py`** (nouveau) :
- Table fidélité par module (HTML)
- Heatmap keywords_overlap (couleurs : rouge < 0.5, vert > 0.7)
- Lisible humain, export PDF

**Sortie** : `docs/fidelity_report.html`

**Signature** :
```bash
python scripts/reports/fidelity_report_visual.py \
  --questions validated.json \
  --keywords src/data/keywords.json \
  --out docs/fidelity_report.html
```

---

## V. Modes pédagogiques (flux détaillés)

### Mode Révision

**Objectif** : apprentissage guidé par module avec explications immédiates.

**Flux UX** :
1. Sélection module (dropdown)
2. Liste QCM (pagination 10 par page)
3. Affichage question + 4 options
4. Sélection réponse → feedback immédiat (vert/rouge)
5. Explication détaillée affichée
6. Bouton "Voir le cours" → ouvre `PDFViewer` à la page source OU panneau latéral avec `source_context`
7. Bouton "Marquer à revoir" → enregistre dans `localStorage`

**Format données** : `revision.json` (toutes difficultés)

**Pas de chrono**, score local affiché en temps réel.

### Mode Entraînement (adaptatif 10Q)

**Objectif** : renforcement mémoire active avec adaptation niveau.

**Flux UX** :
1. Sélection module
2. Génération session 10 questions adaptatives
3. Question 1 : démarre `easy`
4. Feedback immédiat + explication
5. Système notation : Bad (1) / Good (2) / Very Good (3)
6. Questions 2-10 : ajuste niveau selon performance

**Algorithme adaptatif** :
```python
if user_correct_rate > 0.7:
    next_difficulty = min(current + 1, "hard")
elif user_correct_rate < 0.4:
    next_difficulty = max(current - 1, "easy")
```

**Format données** : `entrainement.json` (distribution équilibrée)

**Mémorisation** : feedback → `user_stats.feedbackLog`

### Mode Concours Blanc

**Objectif** : simulation conditions réelles concours IADE (60 Q / 120 min).

**Flux UX** :
1. Sélection examen (6 examens disponibles)
2. Lancement chronomètre 120 min
3. Navigation libre entre 60 questions (retour arrière autorisé)
4. **Pas d'explication pendant l'épreuve** (blocage UI)
5. Soumission finale (ou timeout)
6. Correction complète :
   - Score global (%)
   - Temps moyen par question
   - Sections faibles (modules < 60% réussite)
   - Détail question par question

**Format données** : `exams/exam_*.json` (60 Q calibrées)

**Stockage résultat** : `user_stats.examResults[]`

---

## VI. Interface utilisateur (composants React)

### Composants principaux

| Composant | Rôle | Props clés |
|-----------|------|-----------|
| `QuestionCard.tsx` | Affichage question + 4 options + correction conditionnelle | `question`, `showExplanation`, `onAnswer` |
| `RevisionMode.tsx` | Liste filtrable + intégration QuestionCard + lien cours | `questions`, `moduleId` |
| `TrainingMode.tsx` | Sélection module + logique adaptative + feedback | `questions`, `onComplete` |
| `ExamMode.tsx` | Chronomètre + navigation + blocage explications | `exam`, `onSubmit` |
| `Dashboard.tsx` | Métriques + modules faibles + progression | `userStats` |
| `PDFViewer.tsx` | Viewer PDF natif (react-pdf) | `pdfUrl`, `pageNumber` |

### Store Zustand (`useUserStore.ts`)

```typescript
interface UserStore {
  stats: UserStats;
  
  // Actions principales
  incrementAttempt: (moduleId: string, correct: boolean) => void;
  addFeedback: (questionId: string, score: 1|2|3) => void;
  addExamResult: (examId: string, score: number, totalQuestions: number, duration: number) => void;
  
  // Getters
  getWeakModules: () => Array<{moduleId: string; score: number}>;
  getStreakDays: () => number;
  
  // Maintenance
  purgeOldLogs: () => void; // Supprime logs > 90 jours
}
```

**Persistance localStorage** :
- Clé : `iade_user_stats_v1`
- Sauvegarde automatique après chaque action
- Récupération au démarrage de l'app

### Mécanisme d'expiration localStorage

**Implémentation** :

```typescript
// Au démarrage de l'app (dans useUserStore.ts)
const purgeOldLogs = (stats: UserStats): UserStats => {
  const cutoff = Date.now() - 90 * 24 * 60 * 60 * 1000; // 90 jours
  
  return {
    ...stats,
    feedbackLog: stats.feedbackLog.filter(log => 
      new Date(log.ts).getTime() > cutoff
    ),
    // Conserve examResults indéfiniment
    // Conserve byModule.lastSeen si < 1 an
    byModule: Object.fromEntries(
      Object.entries(stats.byModule).filter(([_, data]) => 
        new Date(data.lastSeen).getTime() > Date.now() - 365 * 24 * 60 * 60 * 1000
      )
    )
  };
};

// Exécuté au montage du store
useEffect(() => {
  const storedStats = localStorage.getItem('iade_user_stats_v1');
  if (storedStats) {
    const parsed = JSON.parse(storedStats);
    const purged = purgeOldLogs(parsed);
    set({ stats: purged });
  }
}, []);
```

### Navigation et routing

**Routes** :
- `/` : Accueil (sélection mode)
- `/revision` : Mode Révision
- `/entrainement` : Mode Entraînement
- `/concours` : Mode Concours Blanc (liste examens)
- `/concours/:examId` : Examen en cours
- `/dashboard` : Dashboard utilisateur

**Menu de navigation fixe** : toujours accessible, sauf pendant examen (confirmation avant sortie).

### Liaison "Voir le cours"

**Implémentation** :

Chaque `Question` porte :
- `source_pdf` : nom fichier
- `page` : numéro page
- `source_context` : extrait 1-2 phrases

**Clic "Voir le cours"** :
- **Option 1** : ouvre `PDFViewer` en modal, scroll automatique à `page`
- **Option 2** : affiche panneau latéral avec `source_context` (plus rapide)

**Composant** :

```typescript
<button onClick={() => openPDFViewer(question.source_pdf, question.page)}>
  📖 Voir le cours (p. {question.page})
</button>
```

### Dashboard (métriques affichées)

| Métrique | Calcul | Affichage |
|----------|--------|-----------|
| Score global | `correct / attempts × 100` | Pourcentage + jauge circulaire |
| Jours actifs | Nombre jours avec ≥ 1 session | Badge + calendrier heatmap |
| Modules faibles | `byModule` trié par score croissant | Top 5 modules, barre progression |
| Progression EMA 7j | Moyenne mobile exponentielle | Graphique ligne (recharts) |
| Historique examens | `examResults[]` | Tableau scores + dates |

---

## VII. Scripts et outils (signatures I/O complètes)

### Scripts d'extraction

**1. `scripts/extract_pdfs.py`**

```bash
python scripts/extract_pdfs.py \
  --input "src/data/sources/*.pdf" \
  --out src/data/modules/ \
  --metadata src/data/metadata.json
```

- **Entrée** : PDF sources (3 fichiers)
- **Sortie** : `modules/*.json`, mise à jour `metadata.json`

### Scripts d'indexation

**2. `scripts/index_chunks.py`**

```bash
python scripts/index_chunks.py \
  --modules src/data/modules/ \
  --out src/data/keywords.json
```

- **Entrée** : modules/*.json
- **Sortie** : `keywords.json` (TF-IDF par module)

**3. `scripts/analyze_annales.py`**

```bash
python scripts/analyze_annales.py \
  --annales "src/data/sources/annalescorrigées-*.pdf" \
  --out src/data/annales_profile.json
```

- **Entrée** : annales PDF (2 fichiers)
- **Sortie** : `annales_profile.json` (profil calibrage)

### Scripts de génération

**4. `scripts/ai_generation/generate_batch.py`**

```bash
python scripts/ai_generation/generate_batch.py \
  --modules src/data/modules/ \
  --keywords src/data/keywords.json \
  --profile src/data/annales_profile.json \
  --out src/data/questions/generated_raw.json \
  --model mistral:latest \
  --per-chunk 3
```

- **Entrée** : modules + keywords + annales_profile
- **Sortie** : `generated_raw.json` (2500+ QCM bruts)

### Scripts de validation

**5. `scripts/ai_generation/biobert_client.py`**

```bash
python scripts/ai_generation/biobert_client.py \
  --in generated_raw.json \
  --out generated_biobert.json \
  --metadata src/data/metadata.json
```

- **Entrée** : generated_raw.json + metadata (seuils adaptatifs)
- **Sortie** : `generated_biobert.json` (+ biomedical_score)

**6. `scripts/ai_generation/semantic_validator.py`**

```bash
python scripts/ai_generation/semantic_validator.py \
  --in generated_biobert.json \
  --modules src/data/modules/ \
  --keywords src/data/keywords.json \
  --out generated_scored.json
```

- **Entrée** : generated_biobert.json + modules + keywords
- **Sortie** : `generated_scored.json` (+ context_score + keywords_overlap)

**7. `scripts/ai_generation/validate_all.py`**

```bash
python scripts/ai_generation/validate_all.py \
  --in generated_scored.json \
  --out validated.json
```

- **Entrée** : generated_scored.json
- **Sortie** : `validated.json` (dédupliqué, distribution lissée)

### Scripts de classification

**8. `scripts/ai_generation/classify_modes.py`**

```bash
python scripts/ai_generation/classify_modes.py \
  --in validated.json \
  --out-dir src/data/questions/
```

- **Entrée** : validated.json
- **Sortie** : `revision.json`, `entrainement.json`, `concours.json`

**9. `scripts/ai_generation/exam_builder.py`**

```bash
python scripts/ai_generation/exam_builder.py \
  --in concours.json \
  --annales-profile src/data/annales_profile.json \
  --out-dir src/data/exams/ \
  --count 6
```

- **Entrée** : concours.json + annales_profile
- **Sortie** : `exam_01.json` ... `exam_06.json`

### Scripts de rapports

**10. `scripts/reports/coverage_report.py`**

```bash
python scripts/reports/coverage_report.py \
  --modules src/data/modules/ \
  --questions validated.json \
  --out docs/coverage_report.md
```

- **Entrée** : modules + validated.json
- **Sortie** : `coverage_report.md`

**11. `scripts/reports/fidelity_check.py`**

```bash
python scripts/reports/fidelity_check.py \
  --questions validated.json \
  --keywords src/data/keywords.json \
  --out docs/fidelity_report.md
```

- **Entrée** : validated.json + keywords
- **Sortie** : `fidelity_report.md` (contrôle lexical auto)

**12. `scripts/reports/stylistic_validator.py`** (nouveau)

```bash
python scripts/reports/stylistic_validator.py \
  --questions validated.json \
  --annales-profile src/data/annales_profile.json \
  --out docs/stylistic_report.md
```

- **Entrée** : validated.json + annales_profile
- **Sortie** : `stylistic_report.md` (distance Levenshtein, similarité phrastique)

**13. `scripts/reports/fidelity_report_visual.py`** (nouveau)

```bash
python scripts/reports/fidelity_report_visual.py \
  --questions validated.json \
  --keywords src/data/keywords.json \
  --out docs/fidelity_report.html
```

- **Entrée** : validated.json + keywords
- **Sortie** : `fidelity_report.html` (table + heatmap, lisible humain)

### Script pipeline complet

**14. `scripts/run_all.sh`** (modifié avec option `--subset`)

```bash
# Full run (tous modules)
bash scripts/run_all.sh

# Dry run (10 modules seulement)
bash scripts/run_all.sh --subset 10
```

- **Entrée** : PDF sources
- **Sortie** : tous fichiers compilés + rapports
- **Option --subset N** : exécute pipeline sur N modules seulement (validation rapide avant full run)

---

## VIII. Qualité et métriques de validation

### Tests unitaires Python

**`tests/test_extraction.py`** :
- Tests sur `extract_pdfs.py`
- Mocks de PDF (fixtures)
- Validation : détection titres, découpage chunks, token count < 1200

**`tests/test_validation.py`** :
- Tests sur `validate_all.py`
- Validation : déduplication, format (4 options, correctAnswer valide), distribution difficultés

**`tests/test_semantic.py`** :
- Tests sur `semantic_validator.py`
- Validation : calcul context_score, keywords_overlap, seuils appliqués

**`tests/test_pipeline.py`** (nouveau test global) :
- Exécute pipeline complet sur 1 module (5 pages)
- Vérifie cohérence : `n_QCM_validés == n_QCM_générés - n_QCM_rejetés`
- Vérifie conservation `chunk_id` à travers toutes les étapes
- Coverage : pipeline complet end-to-end

**Coverage cible** : ≥ 80%

### Tests unitaires React

**`src/components/__tests__/*.test.tsx`** :
- Tests : `QuestionCard`, `RevisionMode`, `TrainingMode`, `ExamMode`, `Dashboard`
- Library : Testing Library + Vitest
- Validation : render correct, interactions utilisateur, états locaux

**Coverage cible** : ≥ 70%

### Tests d'intégration end-to-end

**Outil** : Playwright ou Cypress

**Scénarios** :
1. Parcours Révision : sélection module → réponse 10 Q → "Voir le cours"
2. Parcours Entraînement : session 10Q adaptatives → feedback Bad/Good/Very Good
3. Parcours Concours : examen complet 60Q → chronomètre → correction finale
4. Dashboard : vérification métriques (score, modules faibles, progression)

**Coverage** : scénarios principaux utilisateur

### Statistiques de qualité

**Distributions** :
- Difficultés par module (histogramme)
- Modules dans examens blancs (équilibre)
- Taux de rejet par étape du pipeline (funnel)

**Couverture corpus** :
- % pages avec ≥ 1 QCM
- Chunks orphelins (liste détaillée)

**Scores moyens** :
- `avg_biomedical_score` par module
- `avg_context_score` par module
- `avg_keywords_overlap` par module
- `avg_stylistic_distance` global

### Spot-check expert

**Procédure** :
1. Sélection aléatoire 50 questions (après validation complète)
2. Revue manuelle par expert IADE :
   - Cohérence biomédicale (exact, approximatif, faux)
   - Pertinence pédagogique (utile, neutre, hors-sujet)
   - Exactitude factuelle (vrai, discutable, faux)
3. Calcul taux d'accord : `nb_validés / 50`

**Seuil** : ≥ 90%

**Si < 90%** :
- Analyse causes (prompt trop vague, BioBERT insuffisant, chunks bruités)
- Itération prompts + re-génération partielle
- Re-validation jusqu'à atteinte du seuil

### Métriques continues

**Détection dérives** :
- Hash SHA-256 sur `compiled.json` + `metadata.json`
- Alerte si modification non documentée

**Logs génération** :
- Taux succès/échec par module
- Temps moyen génération par chunk
- Taux retry Mistral (parsing errors)

**Alertes** :
- Chunks orphelins (sans QCM validé)
- Modules sous-représentés (< 60 Q)
- Examens déséquilibrés (module absent)

---

## IX. Pédagogie adaptative (algorithme)

### Score d'ancrage utilisateur

**Objectif** : identifier faiblesses spécifiques par module (mots-clés ratés).

**Calcul `weakKeywords`** :
```typescript
// Après chaque réponse incorrecte
const updateWeakKeywords = (questionId: string, moduleId: string) => {
  const question = getQuestionById(questionId);
  const keywords = extractKeywords(question.text); // top 3 mots-clés
  
  userStats.byModule[moduleId].weakKeywords.push(...keywords);
  
  // Déduplication + top 10 mots-clés les plus ratés
  userStats.byModule[moduleId].weakKeywords = 
    [...new Set(userStats.byModule[moduleId].weakKeywords)].slice(0, 10);
};
```

**Proposition sessions ciblées** :
```typescript
const suggestTargetedSession = (moduleId: string) => {
  const weakKeywords = userStats.byModule[moduleId].weakKeywords;
  
  // Filtre questions contenant ≥ 2 weak keywords
  const targetedQuestions = questions.filter(q => 
    q.module_id === moduleId &&
    weakKeywords.filter(kw => q.text.includes(kw)).length >= 2
  );
  
  return targetedQuestions.slice(0, 10); // Session 10Q ciblée
};
```

### Répétition espacée dynamique (SM-2 simplifié)

**Algorithme** :
```typescript
const updateNextReview = (questionId: string, correct: boolean) => {
  const currentInterval = getInterval(questionId) || 1; // jours
  
  let nextInterval: number;
  
  if (correct) {
    nextInterval = currentInterval * 2.5;
  } else {
    nextInterval = Math.max(currentInterval / 2, 1);
  }
  
  const nextReviewDate = new Date();
  nextReviewDate.setDate(nextReviewDate.getDate() + nextInterval);
  
  userStats.nextReview[questionId] = nextReviewDate.toISOString();
};
```

**Intégration Mode Révision** :
- Filtre questions : `nextReview <= today` (questions dues)
- Affichage prioritaire dans liste

### Feedback loop

**Système notation Bad/Good/Very Good** :
- Bad (1) : question confuse, ambiguë, ou erreur détectée
- Good (2) : question correcte, utile
- Very Good (3) : question excellente, très formative

**Pondération questions** :
```typescript
const getQuestionWeight = (questionId: string) => {
  const feedbacks = userStats.feedbackLog.filter(f => f.questionId === questionId);
  
  if (feedbacks.length === 0) return 1.0; // neutre
  
  const avgScore = feedbacks.reduce((sum, f) => sum + f.score, 0) / feedbacks.length;
  
  // Pondération : Bad (0.5) → Good (1.0) → Very Good (1.5)
  return 0.5 + (avgScore - 1) * 0.5;
};
```

**Marquage re-génération (v2)** :
- Questions avec `avgScore < 1.5` (majorité Bad) → marquées pour amélioration
- Pas implémenté v1 (roadmap v2)

---

## X. Sécurité et contraintes

### Mode 100% local (offline-first)

**Composants locaux** :
- **Ollama (Mistral 7B)** : installé localement, aucun appel API externe
- **BioBERT** : téléchargé une fois (cache HuggingFace `~/.cache/huggingface/`)
- **Fichiers JSON** : tous dans `/src/data/`, versionnable Git
- **localStorage** : données utilisateur 100% navigateur

**Avantages** :
- Pas de coûts API
- Pas de limite de génération
- Confidentialité totale (pas de données envoyées en cloud)

### Pas de données nominatives

**localStorage anonyme** :
- Aucun champ : nom, email, identifiant
- Uniquement : scores, dates, historique sessions
- Pas de tracking analytics

**Conformité RGPD** :
- Pas de collecte données personnelles
- Pas de cookies tiers
- Utilisateur = appareil (pas de compte)

### Redis optionnel (Upstash)

**Rôle** : agrégation feedback utilisateur (Bad/Good/Very Good) pour analyse globale.

**Implémentation** :
- Si Redis disponible : push feedback en arrière-plan (non bloquant)
- Si Redis indisponible : stockage local uniquement
- Pas critique pour fonctionnement app

**Données stockées** :
```json
{
  "questionId": "module_05_q12",
  "score": 2,
  "timestamp": "2025-11-05T10:00:00Z"
}
```

---

## XI. Roadmap versions

### v0 : MVP (J1-J16)

**Objectif** : prototype fonctionnel avec extraction complète et UI révision/entraînement.

**Livrables** :
- Extraction complète 3 PDF
- ≥ 1500 QCM validés (double validation BioBERT + sémantique)
- Fichiers : `revision.json`, `entrainement.json`, `concours.json`
- UI : Mode Révision + Mode Entraînement
- Dashboard simple : score global, modules faibles

**Critères d'acceptation v0** :
- ≥ 12 modules avec ≥ 60 Q révision/module
- Taux rejet < 25%
- Couverture ≥ 70%
- UI fonctionnelle (révision + entraînement)

**Non inclus v0** :
- Examens blancs calibrés
- PDF viewer intégré
- Rapports qualité visuels

---

### v1 : Production (J1-J26)

**Objectif** : application complète prête pour utilisation intensive par candidats IADE.

**Livrables** :
- ≥ 2000 QCM validés
- 6 examens blancs calibrés (60 Q × 120 min)
- UI : tous les modes (Révision + Entraînement + Concours Blanc)
- Dashboard complet : progression EMA, historique examens, modules faibles
- PDF viewer intégré
- Rapports qualité : coverage, fidélité (HTML + heatmap), stylistique

**Critères d'acceptation v1** :
- ≥ 2000 QCM
- 6 examens × 60 Q
- Couverture ≥ 90%
- Accord expert ≥ 90%
- Fidélité sémantique ≥ 0.75
- Overlap lexical ≥ 0.5
- Distance stylistique < 0.3
- Tests : coverage ≥ 80% Python, ≥ 70% React
- Pipeline complet exécutable via `run_all.sh`

**Amélirations v1 vs v0** :
- Seuils BioBERT adaptatifs par module
- Règle automatique classification difficultés
- Feedback itératif stylistique
- Mécanisme expiration localStorage
- Test pipeline global
- Option `--subset` pour dry runs
- Rapports visuels (HTML + heatmap)

---

### v2 : Cas Cliniques & Simulation (future)

**Objectif** : ajouter mode "Cas cliniques" pour simulation réaliste concours.

**Nouvelles fonctionnalités** :

**1. Mode "Cas cliniques"** :
- Format : énoncé de cas (200-400 mots) + QCM contextuel
- 10 questions longues, chronométrées (15 min/cas)
- Scénarios types :
  - Choc septique (reconnaissance, prise en charge initiale)
  - Intubation difficile (arbre décisionnel)
  - Complications transfusionnelles (diagnostic différentiel)
  - Urgences anesthésiques (hyperthermie maligne, bronchospasme)

**2. Extraction automatique scénarios** :
- Parse annales → identification cas cliniques (regex + heuristiques)
- Extraction : contexte patient, examens, évolution, question
- Stockage : `src/data/cas_cliniques/*.json`

**3. Générateur de cas** :
- Combine chunks multiples d'un même module (narrative cohérente)
- Validation renforcée : cohérence narrative + biomédicale
- Prompt spécifique : "Génère un cas clinique réaliste basé sur les contextes suivants..."

**4. Validation narrative** :
- Vérification cohérence temporelle (chronologie événements)
- Vérification cohérence clinique (signes → diagnostic)
- Score `narrative_coherence` (BioBERT embeddings de segments)

**Critères d'acceptation v2** :
- ≥ 100 cas cliniques validés (10 par module clé)
- UI Mode Cas Cliniques
- Validation narrative ≥ 0.8

---

### Roadmap long terme (v3+)

**v3 : Synchronisation multi-devices** (optionnel cloud)
- Compte utilisateur (optionnel)
- Sync localStorage via API simple (Supabase ou équivalent)
- Pas de serveur backend complexe

**v4 : Génération dynamique de questions** (boucle fermée)
- Utilisateur identifie lacune → demande nouvelles questions
- Génération à la demande via Ollama local
- Validation immédiate BioBERT + feedback

**v5 : Communauté et partage** (peer-review)
- Plateforme partage questions (validation communautaire)
- Spot-check distribué (experts IADE valident questions)
- Gamification (badges, leaderboard anonyme)

---

## XII. Points à challenger (validation continue)

Ces décisions techniques doivent être validées empiriquement pendant l'implémentation et ajustées si nécessaire.

### 1. Seuil context_score 0.75

**Justification** : élevé pour garantir fidélité sémantique stricte au corpus.

**Risque** : taux de rejet élevé (> 30%).

**Monitoring** :
- Mesurer taux rejet par module après Phase 4
- Si > 30% → abaisser à 0.70, re-valider

**Décision finale** : à prendre après génération batch complète (Phase 3-4).

---

### 2. Overlap lexical 0.5

**Justification** : équilibre entre fidélité (> 0.5) et reformulation pédagogique (< 0.7).

**Risque** : trop restrictif, empêche paraphrases utiles.

**Monitoring** :
- Spot-check expert : si questions "trop littérales" > 20% → abaisser à 0.4
- Si questions "hors-sujet" > 10% → augmenter à 0.6

**Décision finale** : à prendre après spot-check expert (Phase 9).

---

### 3. 6 examens blancs

**Justification** : couvre diversité thématique + mixte complet.

**Risque** : insuffisant pour entraînement intensif (certains candidats veulent 10-15 examens).

**Monitoring** :
- Feedback utilisateurs pilotes : demande d'examens supplémentaires ?
- Analyser taux de répétition examens (si > 3× par examen → ajouter examens v2)

**Décision finale** : à valider après tests utilisateurs (Phase 9).

---

### 4. Algorithme adaptatif 10Q

**Justification** : 10 questions suffisent pour ajuster niveau.

**Risque** : sur-ajustement au hasard court terme (variance élevée sur petit échantillon).

**Monitoring** :
- Mesurer corrélation score 10Q vs score révision complète module
- Si corrélation < 0.6 → augmenter à 15Q ou ajuster règle progression

**Décision finale** : à calibrer sur sessions longues (Phase 7-8).

---

### 5. JSON plats

**Justification** : simple, versionnable, suffisant jusqu'à ~2500 QCM (< 30 Mo).

**Risque** : performances dégradées si > 3000 QCM.

**Seuil critique** : ~3000 QCM ou 50 Mo de JSON.

**Migration si nécessaire** :
- **Option 1** : sharding par module (`questions_respiratoire.json`, etc.)
- **Option 2** : SQLite local (requêtes SQL, indexation)

**Décision finale** : réévaluer si génération > 2500 QCM (Phase 5).

---

### 6. Seuils BioBERT adaptatifs (0.05-0.10)

**Justification** : pharmacologie exige précision supérieure.

**Risque** : seuils trop élevés pour pharmaco → taux rejet > 40%.

**Monitoring** :
- Mesurer taux rejet par module (Phase 4)
- Si `pharma_*` > 40% rejet → abaisser à 0.08 (au lieu 0.10)
- Si `bases_physio` < 10% rejet → augmenter à 0.06 (rehausser qualité)

**Décision finale** : ajustement itératif après Phase 4.

---

### 7. Distance stylistique < 0.3

**Justification** : similitude forte aux annales pour mimétisme cognitif.

**Risque** : Levenshtein normalisé peut être trop strict (pénalise synonymes utiles).

**Monitoring** :
- Spot-check expert : questions "style annales" jugées par expert
- Si désaccord expert vs métrique > 30% → remplacer par similarité phrastique seule

**Décision finale** : à valider après Phase 2ter (feedback itératif stylistique).

---

### 8. Mécanisme expiration localStorage (90 jours)

**Justification** : évite croissance indéfinie localStorage (limite navigateur ~10 Mo).

**Risque** : perte données utilisateur si absence prolongée.

**Alternative** :
- Proposer export JSON manuel (bouton "Exporter mes stats")
- Proposer import JSON au retour

**Décision finale** : implémenter export/import v1 si feedback utilisateurs (Phase 6).

---

## XIII. Métriques finales de validation v1 (récapitulatif)

| Critère | Objectif | Outil de mesure |
|---------|----------|-----------------|
| Couverture corpus | ≥ 90% | `coverage_report.py` |
| Nombre total QCM | ≥ 2000 | `compiled.json` |
| Examens blancs | 6 × 60 questions | `exams/*.json` |
| Fidélité sémantique | ≥ 0.75 | `semantic_validator.py` |
| Overlap lexical | ≥ 0.5 | `fidelity_check.py` |
| Score BioBERT adaptatif | ≥ seuil module (0.05-0.10) | `biobert_client.py` |
| Taux rejet global | < 20% | Logs pipeline |
| Accord expert | ≥ 90% | Spot-check manuel |
| Distance stylistique | < 0.3 | `stylistic_validator.py` |
| Cohérence pipeline | 100% | `test_pipeline.py` |

**Validation globale** : tous les seuils doivent être atteints avant release v1.

---

## XIV. Conclusion

Ce document **spec.md** définit la vérité absolue du projet IADE NEW.

**Toute décision technique doit être justifiée par ce document.**

**Toute modification de ce document doit être documentée (changelog) et validée par revue.**

---

**Version** : 1.0  
**Date** : 5 novembre 2025  
**Auteur** : Équipe IADE NEW  
**Statut** : Validé pour implémentation

