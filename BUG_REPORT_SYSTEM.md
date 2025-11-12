# 🐛 Système de Rapport de Bugs Structuré

**Date** : 12 novembre 2025  
**Version** : v1.3.0  
**Status** : ✅ IMPLÉMENTÉ

---

## 🎯 Objectif

Permettre aux utilisateurs de **remonter des bugs de manière structurée** avec des catégories précises, pour que l'IA puisse :
1. **Comprendre** le type de problème
2. **Analyser** automatiquement les patterns
3. **Proposer** des corrections
4. **Appliquer** les fixes automatiquement quand c'est possible

---

## 📋 Types de Bugs Supportés

### 🔴 Haute Sévérité
- **Réponse incorrecte** → La bonne réponse est fausse
- **Terme médical incorrect** → Erreur biomédicale grave

### 🟡 Sévérité Moyenne
- **Question ambiguë** → Formulation pas claire
- **Plusieurs réponses possibles** → Ambiguïté dans les options
- **Explication incorrecte** → Erreur dans l'explication

### 🟢 Sévérité Basse
- **Explication incomplète** → Manque de détails
- **Référence incorrecte** → Lien vers mauvaise page
- **Faute d'orthographe** → Erreur française
- **Options similaires** → Options trop proches
- **Difficulté mal calibrée** → Easy/Medium/Hard inadapté
- **Hors programme** → Question non pertinente

---

## 🎨 Interface Utilisateur

### Bouton de Signalement

Après avoir répondu à une question, un **bouton "🐛 Signaler un bug"** apparaît à côté des boutons de feedback (Pas utile/Utile/Très utile).

### Modal de Rapport

Le modal contient :

1. **Sélection catégorie** (12 types de bugs)
   - Affichage en grille avec icônes
   - Description courte pour chaque type

2. **Réponse attendue** (si applicable)
   - Pour "Réponse incorrecte" ou "Plusieurs réponses"
   - L'utilisateur sélectionne la bonne réponse

3. **Description détaillée** (obligatoire)
   - Champ texte libre
   - Placeholder adapté à la catégorie

4. **Suggestion de correction** (optionnel)
   - Comment l'utilisateur corrigerait le problème

---

## 🗄️ Stockage des Données

### Structure du Rapport

```typescript
{
  bugId: "bug_1731408959039_a7c3f",
  questionId: "section_94_c01",
  userId: undefined,  // Anonyme par défaut
  
  category: "reponse_incorrecte",
  severity: "high",
  
  description: "La réponse C devrait être correcte car...",
  suggestedFix: "Changer la réponse correcte de B à C",
  
  userAnswer: 2,
  expectedAnswer: 2,
  
  context: {
    mode: "revision",
    moduleId: "pharma_opioides",
    timestamp: "2025-11-12T10:15:59.039Z",
    deviceInfo: "desktop"
  },
  
  status: "pending",
  createdAt: "2025-11-12T10:15:59.039Z"
}
```

### Double Stockage

1. **localStorage** (backup local)
   - Clé : `iade_bug_reports_v1`
   - Limite : 100 rapports max
   - Toujours disponible même sans Redis

2. **Redis Upstash** (agrégation globale)
   - Liste globale : `bug_reports:all`
   - Par question : `bug_reports:question:{questionId}`
   - Stats : `bug_stats:categories` (hash)

---

## 🤖 Analyse Automatique par IA

### Script d'Analyse

**Fichier** : `scripts/bug_analysis/analyze_bug_reports.py`

**Fonctions** :

1. **Extraction Redis**
   - Récupère tous les rapports
   - Récupère les stats par catégorie

2. **Analyse Pattern**
   ```python
   # Questions les plus signalées
   most_reported_questions = [
     {
       'question_id': 'section_94_c01',
       'report_count': 5,
       'categories': ['reponse_incorrecte', 'explication_incorrecte'],
       'severity_max': 'high'
     }
   ]
   
   # Issues critiques (≥2 rapports + haute sévérité)
   critical_issues = [...]
   ```

3. **Propositions de Correction**
   ```python
   {
     'question_id': 'section_94_c01',
     'issue_category': 'reponse_incorrecte',
     'report_count': 5,
     'auto_fixable': False,  # Nécessite validation expert
     'confidence': 0.85,
     'priority': 95,         # 1-100
     'proposed_action': 'Vérifier et corriger la réponse correcte'
   }
   ```

### Seuils de Décision

- **Confiance minimale** : 0.7
- **Rapports minimum** : 2 (pour issues critiques)
- **Priorité haute** : ≥70/100

---

## ⚙️ Corrections Automatiques

### Bugs Auto-Corrigeables

✅ **Peut être corrigé automatiquement** :
- Faute d'orthographe (avec correcteur)
- Difficulté mal calibrée (recalcul statistique)
- Référence incorrecte (si suggestion fournie)

❌ **Nécessite validation humaine** :
- Réponse incorrecte (impact critique)
- Terme médical incorrect (validation biomédicale)
- Question ambiguë (reformulation complexe)
- Explication incorrecte (vérification biomédicale)

### Workflow de Correction

```
1. Extraction rapports (analyze_bug_reports.py)
   ↓
2. Analyse + Priorisation
   ↓
3. Génération propositions (corrections_proposed.json)
   ↓
4. Application automatique (apply_corrections.py)
   - Corrections simples → Auto
   - Corrections complexes → Validation humaine
   ↓
5. Mise à jour corpus + Redéploiement
```

---

## 📊 Rapports Générés

### 1. Analyse des Bugs

**Fichier** : `reports/bug_reports_analysis.json`

```json
{
  "total_reports": 42,
  "by_category": {
    "reponse_incorrecte": 15,
    "question_ambigue": 12,
    "faute_orthographe": 8,
    "explication_incorrecte": 7
  },
  "by_severity": {
    "high": 22,
    "medium": 15,
    "low": 5
  },
  "by_module": {
    "pharma_opioides": 12,
    "cardio": 10,
    "respiratoire": 8
  },
  "most_reported_questions": [...],
  "critical_issues": [...]
}
```

### 2. Corrections Proposées

**Fichier** : `reports/bug_corrections_proposed.json`

```json
{
  "corrections": [
    {
      "question_id": "section_94_c01",
      "current_question": {...},
      "issue_category": "reponse_incorrecte",
      "report_count": 5,
      "user_descriptions": ["...", "...", "..."],
      "proposed_action": "Vérifier et corriger la réponse correcte",
      "auto_fixable": false,
      "confidence": 0.85,
      "priority": 95
    }
  ],
  "summary": {
    "total_corrections": 18,
    "auto_fixable": 5,
    "high_priority": 12,
    "high_confidence": 14
  }
}
```

---

## 🚀 Utilisation

### Pour les Utilisateurs

1. **Répondre** à une question
2. **Cliquer** sur "🐛 Signaler un bug"
3. **Sélectionner** le type de problème
4. **Décrire** le bug en détail
5. **Soumettre** → Enregistré + analysé par l'IA

### Pour les Développeurs

#### 1. Analyser les Rapports

```bash
# Analyse complète depuis Redis
python scripts/bug_analysis/analyze_bug_reports.py

# Sortie:
# ✅ reports/bug_reports_analysis.json
# ✅ reports/bug_corrections_proposed.json
```

#### 2. Consulter les Rapports

```bash
# Voir les statistiques
cat reports/bug_reports_analysis.json | jq '.by_category'

# Voir les corrections prioritaires
cat reports/bug_corrections_proposed.json | jq '.corrections[:5]'
```

#### 3. Appliquer Corrections (TODO)

```bash
# Appliquer corrections automatiques uniquement
python scripts/bug_analysis/apply_corrections.py --auto-only

# Appliquer toutes les corrections (avec confirmation)
python scripts/bug_analysis/apply_corrections.py --interactive
```

---

## 🔐 Confidentialité & RGPD

### Données Collectées

- ✅ **ID question** (anonyme)
- ✅ **Catégorie bug**
- ✅ **Description**
- ✅ **Contexte** (module, mode, device)
- ✅ **Timestamp**

### Données NON Collectées

- ❌ **Aucun identifiant personnel**
- ❌ **Pas d'email**
- ❌ **Pas d'IP**
- ❌ **Pas de cookies de tracking**

### Conformité

- ✅ **100% anonyme**
- ✅ **Opt-in** (utilisateur décide de signaler ou non)
- ✅ **Expiration 90 jours** (purge automatique Redis)
- ✅ **Export JSON** possible (localStorage)

---

## 📈 Métriques & Monitoring

### Dashboard Admin (TODO)

```typescript
// Composant BugReportsDashboard.tsx
- Total rapports
- Distribution par catégorie (graphique)
- Top questions signalées
- Taux de correction appliquée
- Evolution temporelle
```

### Alertes Automatiques

- ⚠️ **Alerte sévérité haute** : >5 rapports identiques
- 🚨 **Alerte critique** : Réponse incorrecte confirmée
- 📊 **Rapport hebdomadaire** : Nouveaux bugs vs corrigés

---

## 🛠️ Maintenance & Évolution

### Phase 1 : MVP (Actuel)

- ✅ Modal de rapport structuré
- ✅ Stockage localStorage + Redis
- ✅ Script d'analyse Python
- ✅ Propositions de correction

### Phase 2 : Automatisation

- 🔄 Script `apply_corrections.py`
- 🔄 Correction automatique orthographe
- 🔄 Recalibrage difficulté automatique
- 🔄 Dashboard admin React

### Phase 3 : IA Avancée

- 🔮 Détection automatique bugs (sans user input)
- 🔮 Génération corrections via LLM
- 🔮 A/B testing corrections
- 🔮 Feedback loop (mesure qualité post-correction)

---

## 🧪 Tests

### Test Manuel

1. Aller sur `/revision`
2. Répondre à une question
3. Cliquer "🐛 Signaler un bug"
4. Remplir le formulaire
5. Vérifier console : `[BugReport] ✅ Rapport enregistré`
6. Vérifier localStorage : `iade_bug_reports_v1`
7. Vérifier Redis : https://console.upstash.com/...

### Test Script Analyse

```bash
# 1. Simuler quelques rapports de bugs
# 2. Lancer analyse
python scripts/bug_analysis/analyze_bug_reports.py

# 3. Vérifier outputs
ls -lh reports/bug_*.json
```

---

## 📚 Références

### Fichiers Clés

- `src/types/bugReport.ts` → Types TypeScript
- `src/components/BugReportModal.tsx` → UI Modal
- `src/components/QuestionCard.tsx` → Intégration bouton
- `src/utils/bugReportApi.ts` → API service
- `scripts/bug_analysis/analyze_bug_reports.py` → Analyse IA

### Documentation Technique

- **Spec.md Section X** : Redis optionnel
- **tasks.md** : Roadmap phases

---

## ✅ Avantages du Système

### Pour les Utilisateurs

1. ✅ **Simple** : 1 clic + formulaire guidé
2. ✅ **Rapide** : < 1 minute pour signaler
3. ✅ **Impact** : Leur feedback améliore réellement l'app
4. ✅ **Anonyme** : Pas de données personnelles

### Pour les Développeurs

1. ✅ **Structuré** : Données exploitables par l'IA
2. ✅ **Priorisé** : Focus sur bugs critiques d'abord
3. ✅ **Automatisable** : Corrections sans intervention manuelle
4. ✅ **Traceable** : Historique des corrections

### Pour la Qualité

1. ✅ **Amélioration continue** : Corpus s'améliore avec le temps
2. ✅ **Détection précoce** : Bugs identifiés par les users avant qu'ils deviennent critiques
3. ✅ **Feedback loop** : Mesure de la qualité des corrections
4. ✅ **Scalable** : Système supporte des milliers de rapports

---

## 🎉 Résultat

**Le système transforme les utilisateurs en contributeurs actifs** de la qualité du contenu, tout en permettant à l'IA de corriger automatiquement les problèmes simples et de proposer des corrections pour les problèmes complexes.

**Code drift résolu** : Les bugs sont maintenant **structurés, analysables et corrigeables automatiquement** ! 🚀

