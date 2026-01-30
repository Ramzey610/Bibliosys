# INSTRUCTIONS DE LANCEMENT

## 🚀 Avant de Démarrer

Assurez-vous d'avoir:
- Python 3.8+ installé
- pip à jour
- Une terminal (cmd, bash, zsh, etc.)

---

## ⚡ LANCEMENT RAPIDE (5 MINUTES)

### Étape 1: Se Placer dans le Répertoire
```bash
cd /home/ramadane/bibliosys
```

### Étape 2: Créer l'Environnement Virtuel (Premier lancement)
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Étape 3: Installer les Dépendances
```bash
pip install -r requirements.txt
```

### Étape 4: Créer les Tables (Migration)
```bash
python manage.py migrate
```

### Étape 5: Créer un Utilisateur Admin
```bash
python manage.py createsuperuser
```
Remplissez avec:
- Username: `admin`
- Email: `admin@test.local`
- Password: `admin123`

### Étape 6: Charger les Données de Test (Optionnel)
```bash
python manage.py load_test_data
```

### Étape 7: Démarrer le Serveur
```bash
python manage.py runserver
```

Accédez à: **http://localhost:8000**

---

## 🔧 COMMANDES DÉTAILLÉES

### 1️⃣ Installation des Dépendances
```bash
pip install -r requirements.txt
```
Installe Django 4.2 et dépendances.

### 2️⃣ Créer les Migrations
```bash
python manage.py makemigrations
```
Génère les fichiers de migration basés sur les modèles.

### 3️⃣ Appliquer les Migrations
```bash
python manage.py migrate
```
Crée les tables dans la base de données.

### 4️⃣ Créer un Superutilisateur
```bash
python manage.py createsuperuser
```
Crée un compte administrateur.

### 5️⃣ Charger les Données de Test
```bash
python manage.py load_test_data
```
Peuple la base avec:
- 2 utilisateurs (admin + lecteur)
- 6 catégories
- 8 livres
- 4 membres
- Quelques emprunts

### 6️⃣ Démarrer le Serveur
```bash
python manage.py runserver
```
Ou avec un port différent:
```bash
python manage.py runserver 8080
```

### 7️⃣ Lancer les Tests
```bash
python manage.py test
```

---

## 📍 ACCÈS AUX PAGES

Une fois le serveur lancé (`http://localhost:8000`):

### Public (Non authentifié)
- `/accounts/login/` - Connexion
- `/accounts/register/` - Inscription

### Authentifié (Lecteur)
- `/` - Dashboard lecteur
- `/library/books/` - Liste des livres
- `/library/books/<id>/` - Détail livre
- `/accounts/profile/` - Mon profil
- `/loans/my-loans/` - Mes emprunts

### Admin (Bibliothécaire)
- `/` - Dashboard admin
- `/library/books/create/` - Ajouter livre
- `/library/books/<id>/update/` - Modifier livre
- `/library/books/<id>/delete/` - Supprimer livre
- `/members/` - Gestion abonnés
- `/members/create/` - Ajouter abonné
- `/loans/` - Gestion emprunts
- `/loans/create/` - Créer emprunt
- `/loans/<id>/return/` - Retourner livre
- `/admin/` - Interface admin Django (réservée aux superusers ; **préférez** le Dashboard Admin interne `/` pour les tâches quotidiennes du bibliothécaire)

---

## 👤 COMPTES DE TEST

Après `load_test_data`:

### Administrateur
```
Username: admin
Password: admin123
Email: admin@bibliotheque.local
```

### Lecteur
```
Username: lecteur
Password: lecteur123
Email: lecteur@bibliotheque.local
```

### Autres Membres (pour test d'emprunt)
```
Marie Dupont - marie@example.com
Pierre Martin - pierre@example.com
Sophie Bernard - sophie@example.com
Luc Thomas - luc@example.com
```

---

## ✅ VÉRIFICATION

Après le lancement, vérifiez:

1. **Page d'accueil charge**
   - Allez sur http://localhost:8000
   - Vous voyez la navbar avec logo "Bibliothèque"

2. **Connexion fonctionne**
   - Cliquez sur "Connexion"
   - Entrez admin / admin123
   - Vous êtes redirigé au dashboard

3. **Liste des livres affiche**
   - Cliquez sur "Livres"
   - Vous voyez 8 livres (si données test)

4. **Dashboard Admin interne accessible**
   - Allez sur http://localhost:8000
   - Connectez-vous avec admin / admin123
   - Vous êtes redirigé vers le Dashboard Admin interne. (L'interface Django `/admin/` reste disponible pour les superusers si nécessaire.)

---

## 🐛 DÉPANNAGE

### Erreur "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Erreur "No such table"
```bash
python manage.py migrate
```

### Port 8000 déjà utilisé
```bash
python manage.py runserver 8080
```

### Besoin de réinitialiser la base
```bash
# Supprimer db.sqlite3
rm db.sqlite3

# Recommencer
python manage.py migrate
python manage.py createsuperuser
python manage.py load_test_data
```

### Les migrations ne se créent pas
```bash
python manage.py makemigrations library
python manage.py makemigrations accounts
python manage.py makemigrations members
python manage.py makemigrations loans
python manage.py migrate
```

---

## 📚 FICHIERS IMPORTANTS

| Fichier | Description |
|---------|-------------|
| `manage.py` | Utilitaire Django |
| `config/settings.py` | Configuration Django |
| `config/urls.py` | URLs principales |
| `requirements.txt` | Dépendances Python |
| `db.sqlite3` | Base de données (créée) |
| `README.md` | Documentation complète |
| `QUICKSTART.md` | Guide rapide |

---

## 🎯 PROCHAIN ÉTAPES (Après Lancement)

1. Explorez l'interface
2. Créez un livre depuis `/library/books/create/`
3. Créez un emprunt depuis `/loans/create/`
4. Retournez un livre depuis `/loans/<id>/return/`
5. Explorez l'admin Django `/admin/`

---

## 💡 TIPS UTILES

### Lancer en mode debug verbose
```bash
python manage.py runserver --verbosity=3
```

### Utiliser le shell Django pour tester
```bash
python manage.py shell

>>> from library.models import Book
>>> Book.objects.all()
>>> for book in Book.objects.all():
...     print(book.title)
```

### Voir les requêtes SQL
```bash
python manage.py runserver

# Dans le code
from django.db import connection
print(connection.queries)
```

### Créer une nouvelle migration
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🎓 STRUCTURE POUR COMPRENDRE

**Flux d'une Demande Web:**
```
Request → urls.py → views.py → models.py → Database
                        ↓
                     forms.py
                        ↓
                   templates/
                        ↓
Response HTML → Navigateur
```

**Exemple: Créer un Emprunt**
```
1. /loans/create/          → loans/urls.py (routing)
2. LoanCreateView          → loans/views.py (logique)
3. LoanForm                → loans/forms.py (validation)
4. Loan, Book, Member      → loans/models.py (données)
5. loan_form.html          → templates/loans/ (interface)
6. Retour à loan_list.html → Redirection
```

---

## ✨ PRÊT!

Tout est en place pour:
- ✅ Développer
- ✅ Tester
- ✅ Déployer

**Bon développement! 🚀**

---

Questions? Consultez:
- README.md (documentation complète)
- ARCHITECTURE.md (architecture technique)
- QUICKSTART.md (guide rapide)
- Docs Django: https://docs.djangoproject.com/
