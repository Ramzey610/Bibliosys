# Gestion de Bibliothèque - Django 4

Système de gestion complet pour une bibliothèque avec authentification, gestion de livres, abonnés et emprunts.

## 📋 Fonctionnalités

### Authentification
- ✅ Inscription / Connexion / Déconnexion
- ✅ Deux rôles : ADMIN (Bibliothécaire) et LECTEUR
- ✅ Profil utilisateur modifiable
- ✅ Protection CSRF intégrée

### Livres
- ✅ CRUD complet (Créer, Lire, Mettre à jour, Supprimer)
- ✅ Catégories de livres
- ✅ Recherche par titre, auteur, ISBN
- ✅ Filtrage par catégorie et disponibilité
- ✅ Pagination (12 livres par page)
- ✅ Gestion du stock d'exemplaires

### Abonnés
- ✅ CRUD complet
- ✅ Numéro d'adhésion unique
- ✅ Suivi du statut (Actif, Inactif, Suspendu)
- ✅ Historique des emprunts par abonné

### Emprunts
- ✅ Créer emprunt si livre disponible
- ✅ Retourner livre avec calcul d'amende
- ✅ Mise à jour automatique du stock
- ✅ Historique des emprunts
- ✅ Statuts : EN_COURS, RETOURNÉ, EN_RETARD
- ✅ Détection des retards automatique

### Tableau de Bord
- ✅ Dashboard Admin avec statistiques
- ✅ Dashboard Lecteur personnalisé
- ✅ Liste des emprunts récents
- ✅ Alertes sur les retards

### Interface Admin Django
- ✅ Admin personnalisé pour tous les modèles
- ✅ Actions en masse (marquer actif/inactif, etc.)
- ✅ Recherche avancée
- ✅ Filtres dynamiques
- ✅ Hiérarchie chronologique

### Design
- ✅ Bootstrap 5 responsif
- ✅ Interface moderne et intuitive
- ✅ Navigation claire
- ✅ Messages de succès/erreur

## 🚀 Installation et Lancement

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. **Cloner/Créer le projet**
```bash
cd /home/ramadane/bibliosys
```

2. **Créer et activer l'environnement virtuel** (si nécessaire)
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\\Scripts\\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Créer les migrations**
```bash
python manage.py makemigrations
```

5. **Appliquer les migrations**
```bash
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
# Entrez le nom d'utilisateur, email, mot de passe
```

7. **Charger les données de test (optionnel)**
```bash
python manage.py loaddata initial_data
```

8. **Lancer le serveur**
```bash
python manage.py runserver
```

Accédez à http://localhost:8000

## 📁 Structure du Projet

```
bibliosys/
├── config/                 # Configuration Django
│   ├── settings.py        # Paramètres Django
│   ├── urls.py            # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── accounts/              # Gestion des utilisateurs
│   ├── models.py          # CustomUser
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
├── library/               # Gestion des livres
│   ├── models.py          # Book, Category
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
├── members/               # Gestion des abonnés
│   ├── models.py          # Member
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
├── loans/                 # Gestion des emprunts
│   ├── models.py          # Loan, LoanHistory
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
├── templates/             # Templates HTML
│   ├── base.html
│   ├── accounts/
│   ├── library/
│   ├── members/
│   └── loans/
├── static/                # Fichiers statiques
│   ├── css/
│   └── js/
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## 🔑 Comptes de Test

Après `createsuperuser`, utilisez ces identifiants:

### Administrateur (Bibliothécaire)
- Accès complet à toutes les fonctionnalités
- Gestion des livres, abonnés, emprunts
- Interface admin

### Lecteur
- Consultation des livres disponibles
- Visualisation de ses emprunts
- Consulter l'historique

## 📊 Modèles de Données

### CustomUser
- username, email, password
- first_name, last_name
- role (admin, lecteur)
- phone, address
- is_librarian, is_active

### Book
- title, author, isbn
- category (ForeignKey)
- total_copies, available_copies
- publication_date, language
- description, publisher
- is_active

### Member
- first_name, last_name, email
- phone, address
- member_number (unique)
- status (active, inactive, suspended)
- registration_date, is_active

### Loan
- book (ForeignKey)
- member (ForeignKey)
- loan_date, due_date, return_date
- status (EN_COURS, RETOURNÉ, EN_RETARD)
- fine (amende en retard)

### LoanHistory
- Archive des emprunts terminés
- Conserve les données même après suppression

## 🎯 URLs Principales

| URL | Fonction |
|-----|----------|
| `/` | Dashboard |
| `/accounts/login/` | Connexion |
| `/accounts/register/` | Inscription |
| `/accounts/profile/` | Profil utilisateur |
| `/library/books/` | Liste des livres |
| `/library/books/<id>/` | Détail livre |
| `/library/books/create/` | Ajouter livre (Admin) |
| `/members/` | Liste abonnés (Admin) |
| `/loans/` | Gestion emprunts (Admin) |
| `/loans/my-loans/` | Mes emprunts (Lecteur) |
| `/admin/` | Interface admin Django (superusers uniquement — préférez le Dashboard Admin interne `/`) |

## 🔐 Sécurité

- ✅ Protection CSRF activée
- ✅ Authentification requise (login_required)
- ✅ Contrôle d'accès par rôle
- ✅ Validation des formulaires
- ✅ Sanitization des entrées

## 🎨 Customisation

### Modifier les couleurs
Éditer `templates/base.html` section CSS:
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --danger-color: #e74c3c;
}
```

### Ajouter des champs
1. Modifier le modèle dans `models.py`
2. Exécuter `python manage.py makemigrations`
3. Exécuter `python manage.py migrate`
4. Mettre à jour les formulaires et templates

## 📝 Migrations

```bash
# Créer les migrations
python manage.py makemigrations

# Voir les migrations
python manage.py showmigrations

# Appliquer les migrations
python manage.py migrate

# Revenir à une migration
python manage.py migrate library 0001
```

## 🐛 Dépannage

### Erreur de connexion à la base de données
```bash
python manage.py migrate
```

### Déploiement
Pour la production, éditez `config/settings.py`:
- Changez `DEBUG = False`
- Configurez `ALLOWED_HOSTS`
- Changez `SECRET_KEY`
- Configurez la base de données appropriée

## 📧 Contact & Support

Pour toute question, consultez la documentation Django: https://docs.djangoproject.com/

## 📄 Licence

Ce projet est fourni à titre d'exemple éducatif.

---
**Version:** 1.0  
**Date:** Janvier 2026  
**Django:** 4.2+
