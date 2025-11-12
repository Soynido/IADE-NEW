# 📋 Plan d'Action - Système Bug Report v2

**Date** : 12 novembre 2025  
**Status** : ⏳ EN ATTENTE DE VALIDATION

---

## 🎯 Vos Demandes

### 1. Multi-catégories ✅
**Besoin** : Une question peut avoir PLUSIEURS bugs simultanés
- Exemple : Faute de français + Réponse erronée
- Exemple : Question ambiguë + Explication incorrecte

### 2. Scoring 1-2-3 Obligatoire ✅
**Clarification** : 
- Le scoring 1/2/3 reste **TOUJOURS affiché**
- Le bouton "🐛 Signaler un bug" est **EN PLUS**
- Workflow : User répond → Score la question (1/2/3) → **PUIS** signale bug si besoin

### 3. Redis Organisé par Catégorie ✅
**Structure demandée** :
```
Redis:
  ├─ bug:reponse_incorrecte → [list de question_ids]
  ├─ bug:question_ambigue → [list de question_ids]
  ├─ bug:faute_orthographe → [list de question_ids]
  ├─ bug:explication_incorrecte → [list de question_ids]
  └─ ... (12 catégories)

Et pour chaque question:
  └─ bug_details:section_94_c01 → {full bug report JSON}
```

**Avantage** : Vous pouvez traiter **catégorie par catégorie** :
- Traiter toutes les fautes d'orthographe d'un coup
- Traiter toutes les réponses incorrectes ensemble
- Prioriser par type de bug

---

## 📐 Plan d'Action Proposé

### Phase 1 : Modifications UX (30 min)

#### 1.1 Modal Multi-sélection
**Actuellement** : L'utilisateur choisit 1 seule catégorie
**Changement** : Permettre de cocher **plusieurs catégories**

```
UI Proposée:
┌─────────────────────────────────────┐
│ Quels problèmes avez-vous trouvés? │
│ (Vous pouvez en sélectionner       │
│  plusieurs)                         │
│                                     │
│ ☑ ❌ Réponse incorrecte            │
│ ☐ 🔀 Plusieurs réponses possibles  │
│ ☐ ❓ Question ambiguë               │
│ ☑ ✏️ Faute d'orthographe           │
│ ☐ 📝 Explication incorrecte         │
│ ... (autres catégories)             │
└─────────────────────────────────────┘
```

#### 1.2 Clarification Workflow
Ajouter un texte dans le modal :

```
💡 Rappel : Vous avez déjà noté cette question (😊 Très utile).
   Ce formulaire est pour signaler des problèmes spécifiques.
```

---

### Phase 2 : Structure Redis Optimisée (30 min)

#### 2.1 Nouvelle Architecture Redis

**Clés Redis créées** :

```python
# 1. LISTES PAR CATÉGORIE (pour traiter par section)
bug:reponse_incorrecte       → [question_id1, question_id2, ...]
bug:question_ambigue         → [question_id3, question_id4, ...]
bug:faute_orthographe        → [question_id5, question_id6, ...]
bug:explication_incorrecte   → [question_id7, ...]
bug:reference_incorrecte     → [...]
... (12 catégories total)

# 2. DÉTAILS PAR QUESTION (rapport complet)
bug_details:section_94_c01   → {
  "questionId": "section_94_c01",
  "categories": ["reponse_incorrecte", "faute_orthographe"],
  "descriptions_by_category": {
    "reponse_incorrecte": ["La réponse B devrait être correcte car..."],
    "faute_orthographe": ["Il y a une faute: 'réspiratoire' au lieu de 'respiratoire'"]
  },
  "report_count": 3,
  "user_reports": [...],
  "first_reported": "2025-11-12T10:00:00Z",
  "last_reported": "2025-11-12T15:30:00Z"
}

# 3. COMPTEURS GLOBAUX (stats)
bug_stats:by_category        → hash {
  "reponse_incorrecte": 15,
  "faute_orthographe": 8,
  ...
}

bug_stats:by_question        → sorted set {
  "section_94_c01": 5,  // 5 rapports
  "section_18_c01": 3,
  ...
}
```

#### 2.2 Workflow Traitement par Catégorie

**Exemple : Vous voulez corriger toutes les fautes d'orthographe**

```bash
# 1. Récupérer toutes les questions avec faute
redis-cli LRANGE bug:faute_orthographe 0 -1

# Résultat: 
# ["section_94_c01", "section_18_c01", "section_27_c01"]

# 2. Voir détails de chaque question
redis-cli GET bug_details:section_94_c01
redis-cli GET bug_details:section_18_c01
redis-cli GET bug_details:section_27_c01

# 3. Script Python applique corrections
python scripts/bug_analysis/fix_category.py --category faute_orthographe
```

---

### Phase 3 : Scripts Python Améliorés (1h)

#### 3.1 Nouveau Script : `fix_by_category.py`

```bash
# Traiter UNE catégorie à la fois
python scripts/bug_analysis/fix_by_category.py \
  --category faute_orthographe \
  --dry-run

# Voir les stats par catégorie
python scripts/bug_analysis/category_stats.py

# Traiter plusieurs catégories d'un coup
python scripts/bug_analysis/fix_by_category.py \
  --categories faute_orthographe,reference_incorrecte \
  --auto-apply
```

#### 3.2 Script d'Analyse Enrichi

**Nouvelles fonctionnalités** :

1. **Groupement par catégorie**
```python
# Sortie:
Catégorie: faute_orthographe (8 questions)
  1. section_94_c01 (3 rapports) - "réspiratoire" → "respiratoire"
  2. section_18_c01 (2 rapports) - "hémmoragie" → "hémorragie"
  ...

Catégorie: reponse_incorrecte (15 questions)
  1. section_27_c01 (5 rapports) - Réponse B → C
  2. section_45_c01 (4 rapports) - Réponse A → D
  ...
```

2. **Détection patterns communs**
```python
# Exemple: 10 questions ont "réspiratoire" au lieu de "respiratoire"
# → Suggestion: Correction globale par regex
```

---

## 🎨 Modifications UI Détaillées

### Avant (v1.0)
```typescript
// Un seul bouton radio sélectionnable
<div className="grid grid-cols-2 gap-3">
  {BUG_CATEGORIES.map((cat) => (
    <button
      onClick={() => setCategory(cat.value)}  // ❌ Une seule catégorie
      className={category === cat.value ? 'selected' : ''}
    >
      {cat.label}
    </button>
  ))}
</div>
```

### Après (v2.0) - Proposition
```typescript
// Checkboxes multiples
<div className="grid grid-cols-2 gap-3">
  {BUG_CATEGORIES.map((cat) => (
    <label className="flex items-center gap-2 p-3 border rounded">
      <input
        type="checkbox"  // ✅ Multi-sélection
        checked={categories.includes(cat.value)}
        onChange={() => toggleCategory(cat.value)}
      />
      <div>
        <span>{cat.icon} {cat.label}</span>
        <p className="text-xs text-gray-500">{cat.description}</p>
      </div>
    </label>
  ))}
</div>

// Section description par catégorie
{categories.map(cat => (
  <div key={cat}>
    <label>Décrivez le problème: {cat}</label>
    <textarea
      value={descriptionsByCategory[cat]}
      onChange={(e) => setDescription(cat, e.target.value)}
      placeholder={`Précisez le problème de type "${cat}"...`}
    />
  </div>
))}
```

---

## 📊 Exemples Concrets

### Exemple 1 : Question avec 2 Bugs

**User signale** :
- ☑ Réponse incorrecte
- ☑ Faute d'orthographe

**Descriptions** :
- Réponse incorrecte : "La bonne réponse est C car le débit cardiaque..."
- Faute d'orthographe : "Il y a écrit 'réspiratoire' au lieu de 'respiratoire'"

**Redis créé** :
```
LPUSH bug:reponse_incorrecte "section_94_c01"
LPUSH bug:faute_orthographe "section_94_c01"
SET bug_details:section_94_c01 "{...full report...}"
HINCRBY bug_stats:by_category reponse_incorrecte 1
HINCRBY bug_stats:by_category faute_orthographe 1
ZINCRBY bug_stats:by_question 1 section_94_c01
```

**Vous pouvez traiter** :
- D'abord les fautes d'orthographe (simple) → Batch 1
- Puis les réponses incorrectes (complexe) → Batch 2

---

### Exemple 2 : Workflow Traitement

**Étape 1 : Voir les stats**
```bash
python scripts/bug_analysis/category_stats.py

# Sortie:
┌──────────────────────────┬───────┬──────────┐
│ Catégorie                │ Count │ Priority │
├──────────────────────────┼───────┼──────────┤
│ reponse_incorrecte       │  15   │  HIGH    │
│ faute_orthographe        │   8   │  LOW     │
│ question_ambigue         │   5   │  MEDIUM  │
│ explication_incorrecte   │   3   │  MEDIUM  │
└──────────────────────────┴───────┴──────────┘
```

**Étape 2 : Traiter fautes d'orthographe** (facile)
```bash
python scripts/bug_analysis/fix_by_category.py \
  --category faute_orthographe \
  --interactive

# Vous voyez:
# 1. section_94_c01: "réspiratoire" → "respiratoire"
#    Corriger? (o/N): o ✅
# 
# 2. section_18_c01: "hémmoragie" → "hémorragie"
#    Corriger? (o/N): o ✅
#
# ...
#
# ✅ 8/8 corrections appliquées
# Commit? (o/N): o
```

**Étape 3 : Traiter réponses incorrectes** (complexe)
```bash
python scripts/bug_analysis/fix_by_category.py \
  --category reponse_incorrecte \
  --interactive

# Vous voyez chaque question en détail
# Vous décidez une par une
```

---

## ✅ Checklist de Validation

### Je veux valider :

- [ ] **Multi-catégories** : Oui, permettre sélection multiple
- [ ] **Scoring 1-2-3** : Oui, reste obligatoire avant bug report
- [ ] **Redis par catégorie** : Oui, structure proposée OK
- [ ] **Descriptions par catégorie** : Oui, un champ texte par catégorie sélectionnée
- [ ] **Scripts traitement** : Oui, par catégorie avec mode interactif

### Modifications suggérées :

_(Ajoutez vos modifications ici si besoin)_

---

## 🚀 Implémentation

### Si Validé → 3 Étapes

#### Étape 1 : UI Multi-catégories (30 min)
- Modifier `BugReportModal.tsx`
- Checkbox au lieu de radio buttons
- Descriptions par catégorie

#### Étape 2 : Redis Structure (30 min)
- Modifier `bugReportApi.ts`
- Créer listes par catégorie
- Indexation double

#### Étape 3 : Scripts Python (1h)
- `category_stats.py` → Voir stats par catégorie
- `fix_by_category.py` → Traiter catégorie par catégorie
- Modifier `analyze_bug_reports.py` → Support multi-catégories

**Total estimé** : 2h de dev

---

## 🎯 Questions Restantes

### 1. Limite de catégories par rapport ?
- Maximum 3 catégories par rapport ?
- Ou illimité ?

### 2. Ordre de traitement ?
- Toujours commencer par les bugs "faciles" (orthographe) ?
- Ou vous décidez manuellement ?

### 3. Notification ?
- Email/notification quand ≥5 rapports sur même question ?
- Ou vous consultez manuellement Redis ?

---

## 📝 Validation

**Votre décision** :

- [ ] ✅ Plan validé tel quel → GO pour implémentation
- [ ] 🔄 Modifications demandées (préciser ci-dessous)
- [ ] ❌ Approche différente souhaitée

**Commentaires** :
```
(Ajoutez vos modifications/questions ici)
```

---

**En attente de votre validation pour démarrer l'implémentation ! 🚀**

