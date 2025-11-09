# Intégration Redis Upstash - Système de Feedback

## Vue d'ensemble

Le système de feedback "Cette question vous a-t-elle été utile ?" envoie maintenant les données vers **Redis Upstash** en arrière-plan pour permettre une analyse globale.

### Architecture

```
Frontend (React)
    ↓
useUserStore.addFeedback()
    ↓
    ├─→ localStorage (toujours, immédiat)
    ↓
    └─→ Redis Upstash (async, non bloquant)
```

## Fonctionnement

### 1. Stockage Local (localStorage)

- **Toujours actif** : Les feedbacks sont stockés localement
- **Immédiat** : Pas de dépendance réseau
- **Privé** : Données utilisateur seulement

### 2. Envoi Redis Upstash (optionnel)

- **Non bloquant** : Exécuté en arrière-plan
- **Silencieux** : Les erreurs n'affectent pas l'utilisateur
- **Agrégation** : Permet l'analyse globale des feedbacks

## Configuration

### Variables d'environnement

Créer `.env.local` à la racine du projet :

```bash
# Redis Upstash - Feedback utilisateur
VITE_UPSTASH_REDIS_REST_URL=https://full-crab-26762.upstash.io
VITE_UPSTASH_REDIS_REST_TOKEN=AWiKAAIncDI0ZWFhNDNjYzA0N2I0NmI4YTQ0ZjU5OGJiNGY4OGY3YnAyMjY3NjI
```

### Récupération des credentials

1. Aller sur : https://console.upstash.com/redis/full-crab-26762
2. Section "REST API" → copier :
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

## Déploiement Vercel

### Configuration automatique

Le script `scripts/setup_vercel_env.sh` configure automatiquement les variables :

```bash
bash scripts/setup_vercel_env.sh
```

### Configuration manuelle

Si nécessaire, ajouter dans Vercel Dashboard :

1. Projet IADE NEW → Settings → Environment Variables
2. Ajouter :
   - `VITE_UPSTASH_REDIS_REST_URL`
   - `VITE_UPSTASH_REDIS_REST_TOKEN`
3. Scope : Production, Preview, Development

## Structure des données Redis

### Format des feedbacks

```json
{
  "questionId": "chunk_respiratoire_01_c03",
  "score": 3,
  "timestamp": "2025-11-09T14:30:00.000Z"
}
```

### Clés Redis

- **Liste des feedbacks** : `feedback:{questionId}`
- **Exemple** : `feedback:chunk_respiratoire_01_c03`
- **Expiration** : 90 jours (7776000 secondes)

### Commandes Redis CLI (debug)

```bash
# Lister toutes les clés feedback
redis-cli -u $UPSTASH_URL KEYS "feedback:*"

# Voir les feedbacks d'une question
redis-cli -u $UPSTASH_URL LRANGE "feedback:chunk_respiratoire_01_c03" 0 -1

# Compter les feedbacks
redis-cli -u $UPSTASH_URL LLEN "feedback:chunk_respiratoire_01_c03"

# Supprimer une clé (test)
redis-cli -u $UPSTASH_URL DEL "feedback:chunk_respiratoire_01_c03"
```

## API Service

### Fichier : `src/utils/feedbackApi.ts`

#### Fonctions disponibles

```typescript
// Envoyer un feedback (automatique)
sendFeedbackToRedis(questionId: string, score: 1 | 2 | 3): Promise<void>

// Récupérer les feedbacks d'une question (admin)
getFeedbackFromRedis(questionId: string): Promise<FeedbackPayload[]>

// Statistiques globales (admin)
getFeedbackStats(): Promise<Record<string, number>>
```

#### Exemple d'utilisation (admin)

```typescript
import { getFeedbackStats } from '@/utils/feedbackApi';

// Récupérer les stats globales
const stats = await getFeedbackStats();
console.log(stats);
// Output: { "chunk_respiratoire_01_c03": 42, "chunk_cardio_02_c05": 18, ... }
```

## Logs Console

### Développement

Activer les logs détaillés dans la console :

```javascript
// Console Browser DevTools
localStorage.setItem('debug', 'feedback:*');
```

### Messages types

- ✅ `[Feedback] ✅ Envoyé vers Redis: chunk_respiratoire_01_c03 score: 3`
- ℹ️ `[Feedback] Redis non configuré, stockage local uniquement`
- ⚠️ `[Feedback] Échec envoi Redis: 401`
- ⚠️ `[Feedback] Erreur Redis (ignorée): Network error`

## Tests

### Vérification locale

1. Démarrer l'application :
   ```bash
   npm run dev
   ```

2. Ouvrir la console navigateur (F12)

3. Tester un feedback :
   - Mode Révision → Répondre à une question
   - Cliquer sur "😊 Très utile"
   - Vérifier console : `[Feedback] ✅ Envoyé vers Redis`

### Vérification Redis

```bash
# Via Upstash Console
open https://console.upstash.com/redis/full-crab-26762

# Ou via CLI
redis-cli -u redis://full-crab-26762.upstash.io KEYS "feedback:*"
```

## Dépannage

### Problème : Aucun feedback ne remonte dans Redis

**Causes possibles :**

1. **Variables d'environnement non définies**
   - Vérifier `.env.local` existe
   - Vérifier les valeurs sont correctes
   - Redémarrer le serveur dev

2. **CORS ou erreur réseau**
   - Vérifier console navigateur (F12)
   - Vérifier token valide dans Upstash Console

3. **Token expiré**
   - Régénérer un nouveau token sur Upstash
   - Mettre à jour `.env.local`

### Problème : Erreur 401 Unauthorized

**Solution :**
- Vérifier le token dans Upstash Console
- Copier le token REST API (pas le token Redis standard)
- Format attendu : `Bearer AWiKAAInc...`

### Problème : Redis non configuré (logs)

**Explication :**
- C'est normal si `.env.local` n'existe pas
- Le système fonctionne en mode "localStorage uniquement"
- Pas d'erreur utilisateur

## Conformité spec.md

✅ **Section X - Redis optionnel (Upstash)**

- [x] Push feedback en arrière-plan (non bloquant)
- [x] Si Redis indisponible : stockage local uniquement
- [x] Pas critique pour fonctionnement app
- [x] Données stockées : `questionId`, `score`, `timestamp`

## Roadmap v2

### Analyse globale (admin)

- Dashboard admin : statistiques feedbacks
- Questions les plus appréciées (score ≥ 2.5)
- Questions à améliorer (score < 1.5)
- Tendances par module

### Export données

- Export CSV des feedbacks
- Analyse par période
- Heatmap qualité par module

---

**Version** : 1.0  
**Date** : 9 novembre 2025  
**Auteur** : Équipe IADE NEW  
**Statut** : Intégration complète ✅

