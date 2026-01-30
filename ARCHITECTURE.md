# ARCHITECTURE DU PROJET BIBLIOTHÈQUE

## 📊 Diagramme des Modèles

```
┌─────────────────────────────────────────────────────────────┐
│                        CustomUser (accounts)                 │
├─────────────────────────────────────────────────────────────┤
│ - username, email, password                                  │
│ - first_name, last_name                                      │
│ - role: 'admin' | 'lecteur'                                 │
│ - phone, address                                             │
│ - is_librarian, is_active                                   │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────┐      ┌────────────────────────────┐
│    Category (library)    │      │     Book (library)         │
├──────────────────────────┤      ├────────────────────────────┤
│ - name                   │◄─────│ - title, author            │
│ - description            │ FK   │ - isbn                     │
│ - created_at             │      │ - total_copies             │
└──────────────────────────┘      │ - available_copies         │
                                  │ - publication_date         │
                                  │ - language, publisher      │
                                  │ - description, is_active   │
                                  │ - date_added, updated_at   │
                                  └────────────────────────────┘

┌──────────────────────────┐      ┌────────────────────────────┐
│  Member (members)        │      │     Loan (loans)           │
├──────────────────────────┤      ├────────────────────────────┤
│ - first_name, last_name  │◄─────│ - member_id (FK)           │
│ - email, phone           │ FK   │ - book_id (FK)             │
│ - address                │      │ - loan_date                │
│ - member_number (unique) │      │ - due_date                 │
│ - registration_date      │      │ - return_date              │
│ - status: active/...     │      │ - status: EN_COURS/...     │
│ - is_active              │      │ - fine                     │
│ - notes                  │      │ - notes                    │
└──────────────────────────┘      └────────────────────────────┘
           ↑                                ↑
           └────────────────────────────────┘
                  Relations: 1:N
```

## 🗂️ Arborescence Complète

```
bibliosys/
│
├── config/                    # Configuration Django
│   ├── __init__.py
│   ├── settings.py           # Paramètres (DB, APPS, AUTH, etc.)
│   ├── urls.py               # URLs principales (router)
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/                  # Gestion des utilisateurs
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py              # Admin personnalisé
│   ├── apps.py
│   ├── forms.py              # CustomUserCreationForm, etc.
│   ├── models.py             # CustomUser
│   ├── urls.py               # /accounts/*
│   ├── views.py              # register, login, logout, profile
│   └── tests.py
│
├── library/                   # Gestion des livres
│   ├── migrations/
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── load_test_data.py  # Commande pour charger données
│   ├── __init__.py
│   ├── admin.py              # CategoryAdmin, BookAdmin
│   ├── apps.py
│   ├── forms.py              # BookForm, CategoryForm, SearchForm
│   ├── models.py             # Book, Category
│   ├── urls.py               # /library/*, /
│   ├── views.py              # CRUD + Dashboard + Recherche
│   └── tests.py
│
├── members/                   # Gestion des abonnés
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py              # MemberAdmin
│   ├── apps.py
│   ├── forms.py              # MemberForm
│   ├── models.py             # Member
│   ├── urls.py               # /members/*
│   ├── views.py              # CRUD Membres
│   └── tests.py
│
├── loans/                     # Gestion des emprunts
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py              # LoanAdmin, LoanHistoryAdmin
│   ├── apps.py
│   ├── forms.py              # LoanForm, ReturnLoanForm, SearchForm
│   ├── models.py             # Loan, LoanHistory
│   ├── urls.py               # /loans/*
│   ├── views.py              # CRUD + Return + My Loans
│   └── tests.py
│
├── templates/                 # Templates HTML
│   ├── base.html             # Template de base (navbar, footer)
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── library/
│   │   ├── admin_dashboard.html    # Dashboard admin
│   │   ├── reader_dashboard.html   # Dashboard lecteur
│   │   ├── book_list.html          # Liste + Recherche
│   │   ├── book_detail.html
│   │   ├── book_form.html          # Ajouter/Modifier
│   │   ├── book_confirm_delete.html
│   │   ├── category_list.html
│   │   ├── category_form.html
│   │   └── category_confirm_delete.html
│   ├── members/
│   │   ├── member_list.html        # Liste + Filtres
│   │   ├── member_detail.html
│   │   ├── member_form.html        # Ajouter/Modifier
│   │   └── member_confirm_delete.html
│   └── loans/
│       ├── loan_list.html          # Gestion emprunts (admin)
│       ├── loan_detail.html
│       ├── loan_form.html          # Créer emprunt
│       ├── loan_return.html        # Retourner livre
│       ├── my_loans.html           # Mes emprunts (lecteur)
│       └── loan_history.html       # Historique (admin)
│
├── static/                    # Fichiers statiques
│   ├── css/
│   │   └── style.css         # (Optionnel - Bootstrap 5 en CDN)
│   └── js/
│       └── main.js           # (Optionnel)
│
├── manage.py                  # Utilitaire Django
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation complète
├── ARCHITECTURE.md            # Ce fichier
├── .gitignore
└── db.sqlite3                 # Base de données (créée après migration)
```

## 🔄 Flux de Données

### 1. Authentification
```
User Request → accounts/views.py
    ↓
    CustomUser (model) → Django Auth
    ↓
    Session/Token
    ↓
    Redirect Dashboard
```

### 2. Gestion des Livres
```
Admin Dashboard → library/views.py
    ↓
    BookForm → library/models.py (Book)
    ↓
    book_list.html
    ↓
    Search/Filter → Q objects (Django ORM)
```

### 3. Processus d'Emprunt
```
Member clicks "Emprunter"
    ↓
    LoanForm validation
    ↓
    Book.borrow_book() ← Réduit available_copies
    ↓
    Loan.objects.create()
    ↓
    loan_detail.html
```

### 4. Retour de Livre
```
Admin clicks "Retourner"
    ↓
    loan_return view
    ↓
    Loan.return_loan()
        - Calcule fine si en retard
        - Book.return_book() ← Augmente available_copies
    ↓
    Status = RETOURNÉ or EN_RETARD
```

## 📋 Checklist des Fonctionnalités

### Authentification ✓
- [x] Registration (CustomUserCreationForm)
- [x] Login (CustomAuthenticationForm)
- [x] Logout
- [x] Profile Edit (UserProfileForm)
- [x] Roles (admin, lecteur)
- [x] login_required decorators
- [x] Group-based permissions

### Livres ✓
- [x] CRUD complet
- [x] Catégories
- [x] Recherche (titre, auteur, ISBN)
- [x] Filtres (catégorie, disponibilité)
- [x] Pagination
- [x] Stock management (borrow/return)
- [x] Admin actions

### Membres ✓
- [x] CRUD complet
- [x] Numéro d'adhésion unique
- [x] Statuts (actif, inactif, suspendu)
- [x] Suivi des emprunts actifs
- [x] Historique d'emprunts

### Emprunts ✓
- [x] Créer emprunt (si livre disponible)
- [x] Retourner livre
- [x] Calcul automatique d'amende
- [x] Détection de retard
- [x] Historique (LoanHistory)
- [x] Statuts (EN_COURS, RETOURNÉ, EN_RETARD)
- [x] Filtres et recherche

### Dashboard ✓
- [x] Dashboard Admin (statistiques)
- [x] Dashboard Lecteur (mes emprunts)
- [x] Widgets de statut
- [x] Emprunts récents

### Templates ✓
- [x] Bootstrap 5
- [x] Responsive design
- [x] Navigation complète
- [x] Messages (success/error)
- [x] Breadcrumbs
- [x] Pagination

### Admin Django ✓
- [x] CustomUserAdmin
- [x] CategoryAdmin + BookAdmin
- [x] MemberAdmin
- [x] LoanAdmin + LoanHistoryAdmin
- [x] Actions en masse
- [x] Recherche
- [x] Filtres
- [x] Readonly fields

## 🔒 Sécurité

| Mesure | Statut | Implémentation |
|--------|--------|-----------------|
| CSRF Protection | ✓ | settings.py + {% csrf_token %} |
| SQL Injection | ✓ | Django ORM |
| XSS Prevention | ✓ | Template auto-escaping |
| Authentication | ✓ | Django auth + CustomUser |
| Authorization | ✓ | is_staff, roles, decorators |
| Validation | ✓ | Forms + Model validation |
| Input Sanitization | ✓ | Django forms cleaning |

## 🚀 Commandes Utiles

```bash
# Initialiser le projet
python manage.py migrate
python manage.py createsuperuser
python manage.py load_test_data

# Développement
python manage.py runserver
python manage.py shell
python manage.py test

# Maintenance
python manage.py makemigrations
python manage.py sqlmigrate library 0001
python manage.py collectstatic

# Debugging
python manage.py shell_plus
python manage.py dbshell
```

## 📱 Points d'Extension

### Ajouter une Nouvelle App
1. `python manage.py startapp new_app`
2. Ajouter à `INSTALLED_APPS`
3. Créer models.py, views.py, urls.py, forms.py
4. Inclure les URLs dans config/urls.py

### Ajouter des Champs au Modèle
1. Modifier models.py
2. `python manage.py makemigrations`
3. `python manage.py migrate`
4. Mettre à jour forms.py et templates

### Ajouter des Permissions Personnalisées
```python
# Dans models.py
class Meta:
    permissions = [
        ('can_return_book', 'Can return book'),
    ]
```

## 🎯 Diagramme de Navigation

```
┌─────────────────────────────────────────────────────────┐
│                        BASE (navbar)                     │
├─────────────────────────────────────────────────────────┤
│  Logo │ Livres │ [Admin Options] │ [User Menu]          │
└─────────────────────────────────────────────────────────┘
            │
    ┌───────┴───────┬───────────────────────┐
    │               │                       │
  LOGIN         BOOKS             ADMIN ONLY
    │               │                       │
    ├→Register      ├→List                 ├→Members
    ├→Profile       ├→Search               ├→Loans
    │               ├→Detail               ├→Statistics
    │               ├→Categories           └→Admin Site
    │               └→CRUD (Admin)
    │
  Dashboard
    ├→Admin: Stats + Recent
    └→Reader: My Loans + Available
```

## 📊 Statistiques du Projet

- **Apps:** 4 (accounts, library, members, loans)
- **Models:** 7 (CustomUser, Book, Category, Member, Loan, LoanHistory, + Django built-in)
- **Views:** ~25 (CRUD + Dashboard + Custom)
- **Forms:** ~12
- **Templates:** ~25
- **URLs:** ~30
- **Tests:** Classes prêtes

---
**Version:** 1.0
**Django:** 4.2+
**Python:** 3.8+
