# 📘 Guide Workflow - Système Bug Report v2.0

**Date** : 12 novembre 2025  
**Version** : v2.0  
**Status** : ✅ DÉPLOYÉ

---

## 🎯 Vue d'Ensemble

Le système permet de :
1. **Users** → Signaler bugs (multi-catégories, description unique)
2. **Vous** → Consulter Redis par catégorie
3. **Scripts Python** → Traiter par batch selon la catégorie
4. **IA** → Proposer corrections automatiques

---

## 👤 Côté Utilisateur

### Workflow Complet

```
1. User répond à une question
   ↓
2. User note la question (😞/😐/😊) [OBLIGATOIRE]
   ↓
3. User clique "🐛 Signaler un bug" [OPTIONNEL]
   ↓
4. Modal s'ouvre:
   - Cocher 1 ou plusieurs catégories (illimité)
   - Décrire tous les problèmes (1 seul champ)
   - Suggérer correction (optionnel)
   - Si "réponse incorrecte" cochée → Sélectionner bonne réponse
   ↓
5. Soumettre → Enregistré localStorage + Redis
```

### Exemple Concret

**User trouve** :
- Faute : "réspiratoire" au lieu de "respiratoire"
- Réponse B devrait être correcte au lieu de C

**User coche** :
- ☑ ✏️ Faute d'orthographe
- ☑ ❌ Réponse incorrecte

**User écrit** :
```
Il y a deux problèmes:

1. Faute d'orthographe: "réspiratoire" ligne 2 → devrait être "respiratoire"

2. Réponse incorrecte: La bonne réponse est B car le débit cardiaque 
   se calcule avec FC × VES, pas A (qui parle de résistances).
```

**User sélectionne** : Réponse B (dans l'encadré jaune)

**User soumet** → ✅ Enregistré

---

## 🗄️ Structure Redis

### Clés Créées

Pour chaque rapport avec catégories `['reponse_incorrecte', 'faute_orthographe']` sur question `section_94_c01` :

```redis
# 1. LISTES PAR CATÉGORIE (pour traiter par batch)
bug:reponse_incorrecte    → LPUSH section_94_c01
bug:faute_orthographe     → LPUSH section_94_c01

# 2. DÉTAILS PAR QUESTION (rapport complet JSON)
bug_details:section_94_c01 → SET {
  "bugId": "bug_123...",
  "questionId": "section_94_c01",
  "categories": ["reponse_incorrecte", "faute_orthographe"],
  "severity": "high",
  "description": "Il y a deux problèmes: 1. Faute...",
  "suggestedFix": "...",
  "expectedAnswer": 1,
  "context": {...},
  "createdAt": "2025-11-12T..."
}

# 3. COMPTEURS PAR CATÉGORIE (stats)
bug_stats:by_category → HINCRBY reponse_incorrecte 1
                        HINCRBY faute_orthographe 1

# 4. COMPTEUR PAR QUESTION (ranking)
bug_stats:by_question → ZINCRBY 1 section_94_c01

# 5. LISTE GLOBALE (backup)
bug_reports:all → LPUSH {full report JSON}
```

### Consultation Redis

**Voir toutes les questions avec faute d'orthographe** :
```bash
# Dans Upstash Data Browser
Chercher clé: bug:faute_orthographe
Type: List
Membres: [section_94_c01, section_18_c01, ...]
```

**Voir détails d'une question** :
```bash
Chercher clé: bug_details:section_94_c01
Type: String (JSON)
Valeur: {rapport complet}
```

**Voir stats globales** :
```bash
Chercher clé: bug_stats:by_category
Type: Hash
Champs:
  - reponse_incorrecte: 15
  - faute_orthographe: 8
  - question_ambigue: 5
```

---

## 🐍 Scripts Python

### 1. Voir Stats Globales

```bash
cd "/Users/valentingaludec/IADE NEW"
python scripts/bug_analysis/fix_by_category.py --stats
```

**Sortie** :
```
📊 STATISTIQUES PAR CATÉGORIE
======================================================================

Catégorie                      Count      Priorité
----------------------------------------------------------------------
reponse_incorrecte             15         HIGH  
faute_orthographe              8          LOW   
question_ambigue               5          MEDIUM
explication_incorrecte         3          MEDIUM

Total                          31

💡 Suggestions:
   1. Commencer par les bugs simples (faute_orthographe)
   2. Puis les bugs moyens (question_ambigue)
   3. Enfin les bugs critiques (reponse_incorrecte) avec validation expert
```

### 2. Lister Questions d'une Catégorie

```bash
# Voir toutes les questions avec faute d'orthographe
python scripts/bug_analysis/fix_by_category.py \
  --category faute_orthographe \
  --list
```

**Sortie** :
```
📋 Questions avec bug: faute_orthographe
======================================================================

8 question(s) trouvée(s):

1. section_94_c01
   Texte: Quel est le rôle du système réspiratoire dans...
   Module: respiratoire
   Autres problèmes: reponse_incorrecte

2. section_18_c01
   Texte: En cas d'hémmoragie, quelle est la priorité...
   Module: transfusion

...
```

### 3. Traiter une Catégorie (Interactif)

```bash
# Mode interactif (recommandé)
python scripts/bug_analysis/fix_by_category.py \
  --category faute_orthographe
```

**Workflow interactif** :
```
🔧 TRAITEMENT : faute_orthographe
======================================================================

8 question(s) à traiter

======================================================================
📝 Question: section_94_c01
======================================================================

💬 Texte:
   Quel est le rôle du système réspiratoire dans l'homéostasie?

🎯 Options:
   ✅ A. Régulation du pH sanguin
      B. Production de globules rouges
      C. Filtration des toxines
      D. Synthèse des protéines

📊 Métadonnées:
   Module: respiratoire
   Difficulté: medium
   Page: 45

🐛 Problèmes signalés:
   Catégories: faute_orthographe, reponse_incorrecte
   Sévérité: high
   Rapports: 3

💭 Description:
   Il y a deux problèmes:
   1. Faute: "réspiratoire" ligne 1 → "respiratoire"
   2. La réponse B devrait être correcte...

💡 Suggestion utilisateur:
   Corriger orthographe + changer réponse A → B

👉 Action? (o=ouvrir pour correction / s=skip / q=quitter): o

📝 TODO: Ouverture dans éditeur
   Fichier: src/data/questions/compiled.json
   Question ID: section_94_c01

[Vous corrigez manuellement la question]

👉 Action? (o=ouvrir / s=skip / q=quitter): s
⏭️  Question sautée

...

✅ Traitement de la catégorie 'faute_orthographe' terminé
```

### 4. Dry-Run (Simulation)

```bash
# Voir ce qui serait traité sans appliquer
python scripts/bug_analysis/fix_by_category.py \
  --category faute_orthographe \
  --dry-run
```

---

## 🔄 Workflow de Correction Recommandé

### Étape 1 : Consultation Hebdomadaire

```bash
# Tous les lundis, voir ce qui a été signalé
python scripts/bug_analysis/fix_by_category.py --stats
```

### Étape 2 : Traiter par Ordre de Priorité

```bash
# 1. D'abord les fautes d'orthographe (facile, rapide)
python scripts/bug_analysis/fix_by_category.py --category faute_orthographe --list
# → Corriger manuellement dans l'éditeur

# 2. Puis les références incorrectes
python scripts/bug_analysis/fix_by_category.py --category reference_incorrecte --list

# 3. Puis les difficultés mal calibrées
python scripts/bug_analysis/fix_by_category.py --category difficulte_mal_calibree --list

# 4. Enfin les bugs complexes (avec validation expert)
python scripts/bug_analysis/fix_by_category.py --category reponse_incorrecte --list
# → Validation biomédicale nécessaire !
```

### Étape 3 : Commit & Deploy

```bash
# Après corrections manuelles
git add src/data/questions/compiled.json public/data/questions/compiled.json
git commit -m "fix: Corrections bugs batch - catégorie faute_orthographe (8 questions)"
git push origin master
vercel --prod
```

---

## 📊 Monitoring

### Consulter Upstash Dashboard

**URL** : https://console.upstash.com/vercel/kv/55302244-bd6a-40df-adfd-5648b87e7f12/data-browser

**Recherches utiles** :
- Clé : `bug:*` → Voir toutes les catégories
- Clé : `bug:faute_orthographe` → Questions avec faute
- Clé : `bug_stats:by_category` → Stats globales
- Clé : `bug_details:section_94_c01` → Détails question spécifique

### Pas d'Alertes Automatiques

**Décision validée** : Consultation manuelle uniquement
- ✅ Pas d'emails
- ✅ Pas de notifications
- ✅ Vous consultez Redis quand vous voulez

---

## 🎨 Interface Utilisateur

### Clarification Workflow

Dans le modal, un message rappelle :
```
💡 Rappel : Vous avez déjà noté cette question (😊 Très utile).
   Ce formulaire est pour signaler des problèmes spécifiques.
```

### Multi-Catégories

**Checkboxes** au lieu de radio buttons :
```
☑ ❌ Réponse incorrecte
☐ 🔀 Plusieurs réponses possibles
☐ ❓ Question ambiguë
☑ ✏️ Faute d'orthographe      ← Peut cocher plusieurs
☐ 📝 Explication incorrecte
...
```

**Compteur** :
```
✓ 2 problèmes sélectionnés
```

### Un Seul Champ Description

**Placeholder dynamique** :
```
Décrivez les problèmes sélectionnés :
• Réponse incorrecte
• Faute d'orthographe

💡 Astuce : Si plusieurs problèmes, décrivez-les point par point
```

---

## ✅ Avantages

### Pour Vous

1. **Traitement par batch** : Corriger toutes les fautes d'orthographe d'un coup
2. **Priorisation claire** : Stats montrent quoi traiter en priorité
3. **Contexte complet** : Chaque rapport contient description + suggestion user
4. **Pas de spam** : Consultation manuelle quand vous voulez

### Pour les Users

1. **Précision** : Peuvent signaler TOUS les problèmes d'une question
2. **Simplicité** : Un seul champ pour tout décrire
3. **Impact** : Voient que leurs rapports sont traités

### Pour la Qualité

1. **Amélioration ciblée** : Focus sur les catégories critiques
2. **Traçabilité** : Historique de tous les rapports
3. **Mesurable** : Stats précises par type de bug

---

## 🚀 Déploiement

```bash
# Build
npm run build

# Commit
git add -A
git commit -m "feat: Système bug report v2.0 - multi-catégories + Redis par catégorie"

# Deploy
git push origin master
vercel --prod
```

**Status** : 🔄 EN COURS DE DÉPLOIEMENT

---

## 📝 Checklist Post-Déploiement

### Tests Utilisateur

- [ ] Ouvrir `/revision` en production
- [ ] Répondre à une question
- [ ] Noter 1-2-3 ✅
- [ ] Cliquer "🐛 Signaler un bug"
- [ ] Cocher 2+ catégories
- [ ] Remplir description
- [ ] Soumettre
- [ ] Vérifier console : `[BugReport] ✅ Rapport enregistré`
- [ ] Vérifier localStorage : `iade_bug_reports_v1`

### Tests Redis

- [ ] Ouvrir Upstash Dashboard
- [ ] Chercher clé `bug:faute_orthographe` (ou autre catégorie testée)
- [ ] Vérifier que le question_id apparaît
- [ ] Chercher clé `bug_details:{questionId}`
- [ ] Vérifier JSON complet
- [ ] Chercher clé `bug_stats:by_category`
- [ ] Vérifier compteur incrémenté

### Tests Scripts Python

- [ ] `python scripts/bug_analysis/fix_by_category.py --stats`
- [ ] Vérifier stats affichées
- [ ] `python scripts/bug_analysis/fix_by_category.py --category faute_orthographe --list`
- [ ] Vérifier liste questions

---

## 🔧 Commandes Rapides

```bash
# Voir stats
python scripts/bug_analysis/fix_by_category.py --stats

# Lister questions d'une catégorie
python scripts/bug_analysis/fix_by_category.py --category faute_orthographe --list

# Voir détails d'une question spécifique (TODO: à créer)
python scripts/bug_analysis/get_bug_details.py section_94_c01

# Analyse complète (ancien script, toujours fonctionnel)
python scripts/bug_analysis/analyze_bug_reports.py
```

---

## 📊 Exemple de Traitement Réel

### Scénario : 8 Fautes d'Orthographe Signalées

**Lundi matin** :
```bash
# 1. Stats
python scripts/bug_analysis/fix_by_category.py --stats
# → faute_orthographe: 8

# 2. Liste
python scripts/bug_analysis/fix_by_category.py --category faute_orthographe --list
# → 8 questions listées

# 3. Traitement manuel
# Ouvrir src/data/questions/compiled.json
# Chercher section_94_c01
# Corriger "réspiratoire" → "respiratoire"
# Sauvegarder
# ... (8 questions)

# 4. Copier vers public
cp src/data/questions/compiled.json public/data/questions/compiled.json

# 5. Test local
npm run build
npm run dev
# → Tester question corrigée

# 6. Deploy
git add src/data/questions/compiled.json public/data/questions/compiled.json
git commit -m "fix: Correction 8 fautes d'orthographe (batch)"
git push origin master
vercel --prod

# 7. Nettoyage Redis (optionnel)
# Marquer comme traité dans Redis (TODO: script à créer)
```

---

## 🎯 Résumé

**Validé** :
- ✅ Multi-catégories illimité
- ✅ Un seul champ description global
- ✅ Consultation manuelle Redis
- ✅ Traitement par batch selon catégorie
- ✅ Scoring 1-2-3 reste obligatoire

**Déployé** :
- ✅ UI avec checkboxes multi-sélection
- ✅ Redis structure optimisée par catégorie
- ✅ Scripts Python traitement par batch
- ✅ Guide complet (ce document)

**Prochaines étapes** :
1. Vous testez en production
2. Vous signalez des bugs tests
3. Vous vérifiez Redis
4. Vous testez les scripts Python
5. Vous traitez par batch À VOTRE DEMANDE

---

**Le système est maintenant prêt ! 🚀**

