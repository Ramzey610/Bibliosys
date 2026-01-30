Check-list de déploiement vers Vercel

Avant de déployer :
- [ ] Commit & push vers `main`
- [ ] CI (tests) passe (vérifier les checks GitHub)
- [ ] Secrets GitHub configurés: VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID, DATABASE_URL
- [ ] Variables Vercel configurées: SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS
- [ ] Branch protection activée sur `main` (requérir checks verts)
- [ ] Exécuter le workflow `Apply migrations (MANUAL)` si vous avez des migrations non appliquées
- [ ] Vérifier la page de déploiement Vercel et les logs

Après déploiement :
- [ ] Vérifier l'URL publique et les pages principales (dashboard admin, page livres)
- [ ] Vérifier que les fichiers statiques sont servis correctement
- [ ] Tester la connexion d'un utilisateur (login)
- [ ] Vérifier les logs d'erreur dans Vercel
