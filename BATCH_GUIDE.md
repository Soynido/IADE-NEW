# 📊 GUIDE GÉNÉRATION PAR BATCH - Phase 12

## ✅ **BATCH 1 EN COURS** 🚀

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🔄 BATCH 1 - Pages 0-30 (DÉMARRÉ)                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

### **État actuel**
- ✅ Processus long arrêté (12-14h)
- ✅ Mode batch activé
- 🔄 **Batch 1 en cours** (pages 0-30)
- ⏱️ Temps estimé : **~2 heures**

---

## 📋 **PLANNING DES 4 BATCHS**

| Batch | Pages | QCM estimés | Durée | Status |
|-------|-------|-------------|-------|--------|
| **1** | 0-30 | +60 QCM | 2h | 🔄 **EN COURS** |
| **2** | 30-60 | +60 QCM | 2h | ⏳ Pending |
| **3** | 60-90 | +60 QCM | 2h | ⏳ Pending |
| **4** | 90-124 | +68 QCM | 2h | ⏳ Pending |

**TOTAL** : 8h étalé sur 4 sessions

---

## 🔍 **MONITORING EN TEMPS RÉEL**

### **Option 1 : Script de monitoring** (recommandé)

```bash
# Monitoring automatique du batch 1
cd "/Users/valentingaludec/IADE NEW"
bash scripts/expansion/monitor_batch.sh 1
```

→ Refresh automatique toutes les 10 secondes

### **Option 2 : Logs en temps réel**

```bash
# Suivre les logs du batch 1
tail -f "/Users/valentingaludec/IADE NEW/logs/batch_1.log"
```

### **Option 3 : Vérification ponctuelle**

```bash
# Voir la progression
tail -n 20 "/Users/valentingaludec/IADE NEW/logs/batch_1.log"

# Compter les QCM générés
cat "/Users/valentingaludec/IADE NEW/src/data/questions/generated_massive.json" | python3 -c "import sys, json; print(f'QCM: {len(json.load(sys.stdin))}')"
```

---

## 🎯 **APRÈS BATCH 1 (~2h)**

### **Résultat attendu**
```
Corpus actuel : 165 QCM (v1.2.2)
+ Batch 1      : ~60 QCM (nouveaux)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL         : ~225 QCM (×1.4)
```

### **Actions automatiques**
Le script `run_batch.sh` exécute automatiquement :
1. ✅ Génération (30 pages)
2. ✅ Validation BioBERT
3. ✅ Fusion avec corpus existant
4. ✅ Génération du résumé

### **Lancer Batch 2**

```bash
cd "/Users/valentingaludec/IADE NEW"
bash scripts/expansion/run_batch.sh 2 2>&1 | tee logs/batch_2.log &

# Puis monitoring
bash scripts/expansion/monitor_batch.sh 2
```

---

## 📊 **PROGRESSION ESTIMÉE**

### **Après chaque batch**

```
Batch 1 terminé → ~225 QCM (×1.4)
   ↓ 2h
Batch 2 terminé → ~285 QCM (×1.7)
   ↓ 2h
Batch 3 terminé → ~345 QCM (×2.1)
   ↓ 2h
Batch 4 terminé → ~405 QCM (×2.5)
```

**Tu peux arrêter après n'importe quel batch si le corpus est suffisant !**

---

## ⚡ **COMMANDES RAPIDES**

### **Lancer un batch**
```bash
cd "/Users/valentingaludec/IADE NEW"

# Batch 1
bash scripts/expansion/run_batch.sh 1 2>&1 | tee logs/batch_1.log &

# Batch 2
bash scripts/expansion/run_batch.sh 2 2>&1 | tee logs/batch_2.log &

# Batch 3
bash scripts/expansion/run_batch.sh 3 2>&1 | tee logs/batch_3.log &

# Batch 4
bash scripts/expansion/run_batch.sh 4 2>&1 | tee logs/batch_4.log &
```

### **Monitoring**
```bash
# Monitoring batch 1
bash scripts/expansion/monitor_batch.sh 1

# Monitoring batch 2
bash scripts/expansion/monitor_batch.sh 2

# etc.
```

### **Vérifier état**
```bash
# Voir résumé final
cat src/data/questions/expansion_summary.txt

# Compter QCM total
cat src/data/questions/compiled_expanded.json | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'Total: {len(data.get(\"questions\", data))}')"
```

---

## 🔧 **DÉPANNAGE**

### **Batch bloqué ?**
```bash
# Trouver le PID
ps aux | grep run_batch.sh | grep -v grep

# Arrêter proprement
kill <PID>

# Relancer
bash scripts/expansion/run_batch.sh <batch_num> 2>&1 | tee logs/batch_<batch_num>.log &
```

### **Voir les erreurs**
```bash
# Dernières erreurs du batch
grep -i "erreur\|error" logs/batch_1.log | tail -n 10
```

### **État Ollama**
```bash
# Vérifier qu'Ollama tourne
ollama ps

# Si vide, démarrer Ollama
# (il démarre automatiquement au premier appel)
```

---

## 📈 **APRÈS LES 4 BATCHS**

### **Corpus final estimé**
```
165 QCM (v1.2.2)
+ ~240 QCM (nouveaux validés)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
≈ 405 QCM (×2.5)

Couverture : 90-95% du corpus
Score BioBERT moyen : ~0.7-0.8
```

### **Prochaines étapes**
1. ✅ Audit corpus élargi
2. ✅ Régénération 6 examens blancs
3. ✅ Tests complets modes pédagogiques
4. ✅ Déploiement v2.0 sur Vercel
5. ✅ Release GitHub

---

## 🎯 **RÉSUMÉ**

```
MODE BATCH ACTIVÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Avantages :
   • Résultats progressifs (toutes les 2h)
   • Contrôle total
   • Possibilité d'arrêter quand suffisant
   • Moins de risque de crash

⏱️ Timeline :
   • Batch 1 : EN COURS (~2h)
   • Batch 2 : À lancer après
   • Batch 3 : À lancer après
   • Batch 4 : À lancer après

📊 Monitoring :
   bash scripts/expansion/monitor_batch.sh 1

🎯 Corpus après batch 1 :
   165 → ~225 QCM (déjà utilisable !)
```

---

**🚀 Batch 1 en cours... Résultat dans ~2h !**

