# 📦 EXPORT IADE - Données QCM

**Date export** : 8 novembre 2025  
**Version** : v1.0  
**Total QCM** : 462

---

## 📁 FICHIERS INCLUS

### Questions par Mode
1. **compiled.json** (462 QCM) - Base complète avec tous métadonnées
2. **revision.json** (462 QCM) - Mode révision
3. **entrainement.json** (200 QCM) - Mode entraînement
4. **concours.json** (462 QCM) - Mode concours

### Examens Blancs
5. **exam_1.json** (60 Q, 120 min)
6. **exam_2.json** (60 Q, 120 min)
7. **exam_3.json** (60 Q, 120 min)
8. **exam_4.json** (60 Q, 120 min)
9. **exam_5.json** (60 Q, 120 min)
10. **exam_6.json** (60 Q, 120 min)

---

## 📊 MÉTRIQUES QUALITÉ

### Validation BioBERT
- **Score moyen** : 0.93/1.0 (excellent)
- **Taux validation** : 100%
- **Seuils adaptatifs** : 0.05-0.10 par module

### Distribution Modules
```
BASES PHYSIO    : 96 QCM  (20.8%)
INFECTIO        : 80 QCM  (17.3%)
CARDIO          : 43 QCM  (9.3%)
TRANSFUSION     : 39 QCM  (8.4%)
RESPIRATOIRE    : 23 QCM  (5.0%)
NEURO           : 22 QCM  (4.8%)
DOULEUR         : 13 QCM  (2.8%)
LEGISLATION     : 12 QCM  (2.6%)
PEDIATRIE       : 10 QCM  (2.2%)
VENTILATION     : 10 QCM  (2.2%)
MONITORAGE      : 8 QCM   (1.7%)
PHARMA_OPIOIDES : 6 QCM   (1.3%)
REANIMATION     : 2 QCM   (0.4%)
UNKNOWN         : 98 QCM  (21.2%)
```

---

## 🔍 SCHÉMA QUESTION

```json
{
  "id": "unique_id",
  "module_id": "cardio",
  "chunk_id": "section_78_c01",
  "text": "Question complète ici ?",
  "options": [
    "Option A",
    "Option B",
    "Option C",
    "Option D"
  ],
  "correctAnswer": 2,
  "explanation": "Explication détaillée...",
  "difficulty": "medium",
  "source_pdf": "Prepaconcoursiade-Complet.pdf",
  "page": 142,
  "biomedical_score": 0.935
}
```

---

## 🎯 UTILISATION POUR REFINEMENT

### Analyse des patterns
```python
import json

with open('compiled.json', 'r') as f:
    qcms = json.load(f)

# Questions courtes (potentiellement trop vagues)
short_questions = [q for q in qcms if len(q['text']) < 50]

# Explications courtes (potentiellement insuffisantes)
short_explanations = [q for q in qcms if len(q['explanation']) < 100]

# Score BioBERT < 0.10 (à améliorer)
low_biomedical = [q for q in qcms if q.get('biomedical_score', 1) < 0.10]
```

### Réécriture ciblée
Utiliser Ollama pour améliorer :
- Questions trop vagues
- Distracteurs trop évidents
- Explications incomplètes

### Re-validation
- BioBERT scoring
- Semantic validation
- Merge dans corpus

---

## 📈 OBJECTIFS REFINEMENT

| Métrique | Actuel | Cible |
|----------|--------|-------|
| Score BioBERT moy | 0.93 | 0.95+ |
| Questions claires | ~90% | 95%+ |
| Explications complètes | ~85% | 95%+ |
| Distracteurs plausibles | ~80% | 90%+ |

---

## 💾 BACKUP

Ces fichiers sont la **version originale v1.0**

Toute modification devrait :
1. Créer une copie backup
2. Travailler sur copie
3. Valider qualité
4. Merger si amélioration confirmée

---

## 📊 STATISTIQUES GÉNÉRATION

- **Générateur** : Ollama Mistral 7B
- **Validation** : BioBERT (dmis-lab/biobert-base-cased-v1.1)
- **Durée génération** : ~6h (297 chunks)
- **Taux succès** : 79%
- **Corpus source** : 141 pages, 3 PDFs

---

**Ces fichiers sont prêts pour analyse et refinement par une autre IA.**

