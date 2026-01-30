# Déploiement sur Vercel (serverless) - Guide pédagogique

Ce document décrit les étapes nécessaires pour déployer ce projet Django sur Vercel en gardant la logique métier intacte.

Important : ne pas exécuter de migrations automatiquement sur Vercel. Les migrations doivent être appliquées depuis une machine de confiance (CI/CD ou local) vers la base PostgreSQL distante.

---

## Fichiers ajoutés / modifiés
- Créés :
  - `api/index.py` (point d'entrée serverless pour Vercel)
  - `vercel.json` (routage et build)
  - `DEPLOYMENT.md` (ce document)
- Modifiés :
  - `config/settings.py` (lecture de SECRET_KEY, DEBUG, ALLOWED_HOSTS, support DATABASE_URL, WhiteNoise)
  - `requirements.txt` (ajout de `dj-database-url`, `psycopg2-binary`, `vercel-wsgi`, `whitenoise`)
  - `.gitignore` (exclusions supplémentaires)

---

## Variables d'environnement à configurer dans Vercel
- `SECRET_KEY` : clé secrète Django (important pour la sécurité)
- `DATABASE_URL` : chaîne de connexion PostgreSQL (ex: `postgres://user:pass@host:5432/dbname`)
- `ALLOWED_HOSTS` : (optionnel) hôtes autorisés, ex: `.vercel.app,mydomain.com`
- `DEBUG` : `False` (laisser vide par défaut)

Ne pas mettre `DEBUG=True` en production.

---

## Étapes manuelles recommandées
1. Préparer les migrations localement / sur CI (machine de confiance):
   - `python manage.py makemigrations` (si nécessaire)
   - Exporter la variable d'environnement `DATABASE_URL` pointant vers votre PostgreSQL de production
   - `./scripts/run_migrations.sh`  # script d'aide fourni (exécute `python manage.py migrate --noinput`)

2. Créer un superuser (optionnel) depuis la machine de confiance :
   - `python manage.py createsuperuser`

3. Gestion des fichiers statiques (recommandé dans CI):
   - `python manage.py collectstatic --noinput` (le workflow CI le fait automatiquement et publie l'artefact `staticfiles/`)
   - Dans Vercel, configurez **Build Command** = `python manage.py collectstatic --noinput` pour générer les assets si vous préférez que Vercel les produise lors du build.

> Note : Vercel serverless **n'est pas** conçu pour exécuter des tâches d'administration (migrations longues, jobs lourds). Exécutez toujours les migrations depuis une machine/CI de confiance avec accès à la base PostgreSQL.

---

## Protections recommandées (sécurité)
- **GitHub branch protection** : protégez `main` (exiger checks pass: CI) pour éviter un déploiement non testé.
- **GitHub Environments** : activez l'environnement `production` et **exigez des réviseurs** avant d'autoriser l'exécution du workflow `Apply migrations (MANUAL)`.
- **Secrets** : stockez `DATABASE_URL` comme secret (GitHub & Vercel) et limitez l'accès.

---

## Trigger manuel des migrations via GitHub Actions
- Aller dans l'onglet `Actions` > `Apply migrations (MANUAL)` > `Run workflow`.
- Fournir l'input (`env=production`) et exécuter ; la job utilisera le secret `DATABASE_URL` pour se connecter et exécuter `python manage.py migrate`.

---

## Checklist final avant premier déploiement
- [ ] `SECRET_KEY` ajouté dans Vercel
- [ ] `DATABASE_URL` ajouté dans Vercel
- [ ] `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` ajoutés comme GitHub Secrets
- [ ] Branch protection activée sur `main` (obliger CI à réussir)
- [ ] Optionnel : configurer `Build Command` sur Vercel → `python manage.py collectstatic --noinput`

---

## Déploiement (synthèse)
1. Commit & push sur GitHub :
   - `git add .` / `git commit -m "Prepare project for Vercel"` / `git push`.
2. Dans Vercel :
   - Créer un nouveau projet en liant votre repo GitHub.
   - Dans **Settings > Environment Variables**, ajouter `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`.
   - Déployer.

---

## Remarques pédagogiques
- Nous avons choisi `vercel-wsgi` pour adapter l'application WSGI Django au runtime `@vercel/python`.
- WhiteNoise permet de servir des assets statiques simples en production. Pour des sites à forte charge, priorisez un CDN ou un stockage d'objets (S3, DigitalOcean Spaces...).
- On conserve SQLite pour le développement local ; utilisez PostgreSQL en production via `DATABASE_URL`.
