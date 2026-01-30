# GUIDE DE DÉMARRAGE RAPIDE

## ⚡ Installation en 5 minutes

### Linux/Mac
```bash
cd /home/ramadane/bibliosys
chmod +x init_project.sh
./init_project.sh
python manage.py runserver
```

### Windows
```cmd
cd C:\path\to\bibliosys
init_project.bat
python manage.py runserver
```

## 🎯 Points Clés du Projet

### 1. Configuration Django (config/settings.py)
```python
INSTALLED_APPS = [
    'accounts',      # Gestion des utilisateurs
    'library',       # Livres et catégories
    'members',       # Abonnés
    'loans',         # Emprunts
]

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = 'accounts:login'
```

### 2. Modèles Relationnels
```python
Book ← Category (ForeignKey)
Loan → Book (ForeignKey)
Loan → Member (ForeignKey)
Member ← User (Relation optionnelle)
```

### 3. Authentification & Permissions
```python
# Rôles
- admin/librarian: Accès complet
- lecteur/reader: Accès limité

# Décorateurs
@login_required          # Nécessite authentification
@permission_required     # Vérifie les permissions

# Mixins
IsAdminMixin             # Vérifie rôle admin
LoginRequiredMixin       # Mixin DRY
```

### 4. Views Principales

#### library/views.py
```
dashboard()              # / (accueil)
book_list()             # /library/books/ + recherche
book_detail()           # /library/books/<id>/
BookCreateView          # /library/books/create/
BookUpdateView          # /library/books/<id>/update/
BookDeleteView          # /library/books/<id>/delete/
```

#### loans/views.py
```
loan_list()             # /loans/ (admin)
loan_detail()           # /loans/<id>/
loan_return()           # /loans/<id>/return/
my_loans()              # /loans/my-loans/ (lecteur)
loan_history()          # /loans/history/ (admin)
LoanCreateView          # /loans/create/
```

#### members/views.py
```
member_list()           # /members/ (admin)
member_detail()         # /members/<id>/
MemberCreateView        # /members/create/
MemberUpdateView        # /members/<id>/update/
MemberDeleteView        # /members/<id>/delete/
```

## 🧪 Tests et Débogage

### Lancer les tests
```bash
python manage.py test library
python manage.py test --verbosity=2
```

### Utiliser le shell Django
```bash
python manage.py shell

>>> from library.models import Book
>>> Book.objects.all()
>>> from accounts.models import CustomUser
>>> CustomUser.objects.all()
```

### Voir les requêtes SQL
```python
from django.db import connection
print(connection.queries)
```

## 📝 Tâches Courantes

### Ajouter un Livre
1. Aller à `/library/books/create/`
2. Remplir le formulaire
3. Le stock se met à jour automatiquement

### Créer un Emprunt
1. Accéder à `/loans/create/` (Admin)
2. Sélectionner le membre et le livre
3. Le stock du livre diminue automatiquement

### Retourner un Livre
1. Aller à `/loans/<id>/return/`
2. L'amende est calculée si en retard
3. Le stock augmente automatiquement

## 🔧 Personnalisation

### Changer les couleurs du thème
Éditer `templates/base.html`:
```css
:root {
    --primary-color: #2c3e50;      /* Bleu foncé */
    --secondary-color: #3498db;    /* Bleu clair */
    --danger-color: #e74c3c;       /* Rouge */
}
```

### Ajouter un nouveau champ à Book
```python
# 1. models.py
class Book(models.Model):
    pages = models.IntegerField(default=0)  # Nouveau

# 2. Terminal
python manage.py makemigrations
python manage.py migrate

# 3. forms.py
fields = (..., 'pages')

# 4. template
{{ form.pages }}
```

## 📊 Requêtes Utiles

### Tous les livres disponibles
```python
Book.objects.filter(available_copies__gt=0)
```

### Emprunts en retard
```python
Loan.objects.filter(status='EN_RETARD')
```

### Membres actifs
```python
Member.objects.filter(is_active=True, status='active')
```

### Historique d'un membre
```python
member.loans.filter(status='RETOURNÉ')
```

## 🐛 Dépannage Courant

### La base de données ne se synchronise pas
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Les images ne s'affichent pas
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# urls.py
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Erreur de permission
```bash
# Vérifier les groupes
python manage.py shell
>>> from django.contrib.auth.models import Group, Permission
>>> Group.objects.all()
```

## 🚀 Déploiement

### Production Checklist
- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` unique et sécurisé
- [ ] `ALLOWED_HOSTS` configuré
- [ ] Base de données (PostgreSQL recommandé)
- [ ] Variables d'environnement (python-decouple)
- [ ] HTTPS activé
- [ ] Static files collectés
- [ ] Logs configurés

### Serveur WSGI (Gunicorn)
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📚 Ressources

- Django Docs: https://docs.djangoproject.com/
- Bootstrap 5: https://getbootstrap.com/
- Django Models: https://docs.djangoproject.com/en/4.2/topics/db/models/
- Class-Based Views: https://docs.djangoproject.com/en/4.2/topics/class-based-views/

## ✅ Checklist Post-Installation

- [ ] Serveur démarre sans erreur
- [ ] Page d'accueil accessible
- [ ] Connexion admin fonctionne
- [ ] Création d'un livre fonctionne
- [ ] Création d'un emprunt fonctionne
- [ ] Dashboard visible
- [ ] Admin Django accessible

## 📞 Support

Pour les problèmes:
1. Vérifiez les logs: `python manage.py runserver --verbosity=3`
2. Consultez les errors en détail
3. Vérifiez les migrations: `python manage.py showmigrations`
4. Lancez les tests: `python manage.py test`

---
**Bonne utilisation! 🎉**
