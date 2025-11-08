# 🚀 Déploiement IADE NEW v1.1 sur Vercel

**Date** : 8 novembre 2025  
**Version** : 1.1.0  
**Statut** : ✅ Déployé avec succès

---

## 🎯 URLs de production

### Production principale
```
https://iade-6rtw18xmu-valentin-galudec-s-projects.vercel.app
```

### Dashboard Vercel
```
https://vercel.com/valentin-galudec-s-projects/iade-new
```

---

## ⚠️ Configuration requise

### Désactiver la protection d'accès

Le site est actuellement en mode **privé** (Vercel Authentication activée).

**Étapes pour rendre l'application publique** :

1. **Se connecter à Vercel**
   - Aller sur https://vercel.com/dashboard
   - Se connecter avec le compte GitHub (@Soynido)

2. **Sélectionner le projet**
   - Cliquer sur "iade-new"
   - Ou aller directement sur : https://vercel.com/valentin-galudec-s-projects/iade-new

3. **Désactiver la protection**
   - Aller dans **Settings** (onglet en haut)
   - Section **Deployment Protection**
   - Désactiver "Vercel Authentication"
   - Sauvegarder

4. **Vérifier l'accès**
   - Ouvrir l'URL en navigation privée
   - L'application doit être accessible sans authentification

---

## 📊 Informations techniques

### Build

| Propriété | Valeur |
|-----------|--------|
| **Framework** | Vite |
| **Node version** | Automatique (Vercel default) |
| **Build command** | `npm run build` |
| **Output directory** | `dist/` |
| **Build time** | ~6 secondes |
| **Bundle size** | 23.2 MB |

### Assets produits

```
dist/
├── index.html (0.48 KB)
├── assets/
│   ├── index-Bw416_-t.css (20 KB)
│   └── index-6tKhP-l6.js (205 KB)
└── data/
    └── questions/
        ├── compiled.json (154 KB)
        ├── revision.json (146 KB)
        ├── entrainement.json (146 KB)
        └── concours.json (146 KB)
```

### Configuration Vercel (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/data/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, must-revalidate"
        }
      ]
    }
  ]
}
```

---

## 🔄 Redéploiement

### Automatique (GitHub)

Chaque push sur la branche `master` déclenche un redéploiement automatique.

```bash
git add -A
git commit -m "Update application"
git push origin master
```

### Manuel (Vercel CLI)

```bash
cd "/Users/valentingaludec/IADE NEW"
vercel --prod --yes
```

### Via Dashboard

1. Aller sur https://vercel.com/valentin-galudec-s-projects/iade-new
2. Onglet "Deployments"
3. Cliquer sur "Redeploy" pour le dernier déploiement

---

## 🌐 Domaine personnalisé (optionnel)

Pour ajouter un domaine custom (ex: `iade-prep.com`) :

1. **Acheter un domaine** (Namecheap, GoDaddy, OVH, etc.)

2. **Ajouter sur Vercel**
   - Settings → Domains
   - Ajouter le domaine
   - Suivre les instructions DNS

3. **Configurer les DNS**
   - Type A : `76.76.21.21`
   - Type CNAME : `cname.vercel-dns.com`

4. **Attendre la propagation** (~24h max)

---

## 📝 Logs et monitoring

### Voir les logs de build

```bash
vercel logs https://iade-6rtw18xmu-valentin-galudec-s-projects.vercel.app
```

### Inspect un déploiement

```bash
vercel inspect https://iade-6rtw18xmu-valentin-galudec-s-projects.vercel.app
```

### Analytics

- Aller sur https://vercel.com/valentin-galudec-s-projects/iade-new/analytics
- Voir les visiteurs, performances, erreurs

---

## 🐛 Troubleshooting

### Build échoue

```bash
# Tester le build en local
npm run build

# Vérifier les logs Vercel
vercel inspect --logs
```

### 404 sur les routes

Vérifier que `vercel.json` contient bien :

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Données QCM non chargées

Vérifier que :
1. Les fichiers sont dans `public/data/questions/`
2. Les chemins dans le code sont `/data/questions/...`
3. Les headers CORS sont configurés

---

## ✅ Checklist post-déploiement

- [x] Build réussi
- [x] Application déployée sur Vercel
- [x] GitHub connecté (auto-deploy)
- [ ] Protection d'accès désactivée (à faire manuellement)
- [ ] Domaine custom configuré (optionnel)
- [ ] Analytics activé (optionnel)

---

## 🎓 Application prête

**IADE NEW v1.1** est maintenant déployé et prêt pour la préparation au concours IADE !

**Prochaines étapes** :
1. Désactiver la protection Vercel
2. Partager l'URL avec les utilisateurs
3. Collecter les feedbacks
4. Itérer selon les retours

---

**Documentation** : Voir `PROJECT_COMPLETE.md` pour plus d'infos  
**Release GitHub** : https://github.com/Soynido/IADE-NEW/releases/tag/v1.1  
**Code source** : https://github.com/Soynido/IADE-NEW

