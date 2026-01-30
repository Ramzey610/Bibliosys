# UML → Django : Explication pédagogique

## Introduction

Ce document relie les concepts UML (classes, cas d'utilisation, séquences, activités) au code réel du projet Django « bibliosys ». Il est conçu pour des étudiants L2/L3 en génie logiciel et s'appuie uniquement sur le code présent dans le workspace.

Fichiers principaux cités:

- [library/models.py](library/models.py#L1-L200)
- [loans/models.py](loans/models.py#L1-L250)
- [members/models.py](members/models.py#L1-L200)
- [accounts/models.py](accounts/models.py#L1-L200)
- [library/views.py](library/views.py#L1-L300)
- [loans/views.py](loans/views.py#L1-L300)
- [config/urls.py](config/urls.py#L1-L80)

---

## Correspondance UML → Django

### A) Diagramme de classes

1. Category
   - Modèle: `Category` ([library/models.py](library/models.py#L1-L60))
   - Champs: `name: CharField(max_length=200, unique=True)`, `description: TextField(blank=True, null=True)`, `created_at: DateTimeField(auto_now_add=True)`
   - Relation: One-to-Many → `Book` via `Book.category` (ForeignKey, `related_name='books'`, `on_delete=SET_NULL`).

2. Book
   - Modèle: `Book` ([library/models.py](library/models.py#L20-L200))
   - Champs importants: `title`, `author`, `isbn (unique)`, `category (FK, null=True)`, `total_copies`, `available_copies`, `is_active`.
   - Contraintes: `isbn.unique=True`; `category` nullable; indexes en Meta pour accélérer recherches.
   - Méthodes: `is_available()`, `borrow_book()`, `return_book()` — logique métier d'inventaire.

3. Member
   - Modèle: `Member` ([members/models.py](members/models.py#L1-L200))
   - Champs: `first_name`, `last_name`, `email (unique)`, `member_number (unique)`, `status` (choices), `is_active`.
   - Méthodes utilitaires: `get_full_name()`, `get_active_loans_count()`.

4. Loan
   - Modèle: `Loan` ([loans/models.py](loans/models.py#L1-L220))
   - Champs: `book (FK -> Book, CASCADE)`, `member (FK -> Member, CASCADE)`, `loan_date`, `due_date` (fixée si vide), `return_date`, `status (choices)`, `fine`.
   - Logique: `save()` calcule `due_date` par défaut; `return_loan()` calcule l'amende et appelle `book.return_book()`.

5. CustomUser
   - Modèle: `CustomUser` ([accounts/models.py](accounts/models.py#L1-L200)), hérite d'`AbstractUser`.
   - Champs: `role` (choices admin/lecteur), `is_librarian` (Boolean), `phone`, `address`.

Tableau synthétique (UML class → Django model):

| UML | Django model | fichier |
|---|---|---|
| Livre | `Book` | [library/models.py](library/models.py#L20-L200) |
| Emprunt | `Loan` | [loans/models.py](loans/models.py#L1-L220) |
| Membre | `Member` | [members/models.py](members/models.py#L1-L200) |


### B) Diagramme de cas d'utilisation (Use Case)

Pour chaque fonctionnalité, associer : vue, URL, template, permissions.

- Consulter les livres
  - Vue: `book_list` ([library/views.py](library/views.py#L1-L120))
  - URL: `library/books/` ([library/urls.py](library/urls.py#L1-L20))
  - Template: `templates/library/book_list.html`
  - Permission: `@login_required`

- Créer/Modifier un livre (admin)
  - Vue: `BookCreateView`, `BookUpdateView` (class-based) ([library/views.py](library/views.py#L120-L200))
  - URL: `library/books/create/`, `.../<pk>/update/` ([library/urls.py](library/urls.py#L1-L20))
  - Permission: `IsAdminMixin` qui appelle `is_admin(user)` (vérifie `user.is_staff`/`user.role=='admin'`).

- Emprunter un livre
  - Vue: `LoanCreateView` ([loans/views.py](loans/views.py#L1-L140))
  - URL: `loans/create/` ([loans/urls.py](loans/urls.py#L1-L20))
  - Template: `templates/loans/loan_form.html`
  - Règles: vérification `book.is_available()` et `member.is_active` dans `form_valid` avant `loan.save()`; appel `book.borrow_book()`.


### C) Diagramme de séquence (exemple: emprunter un livre)

Traduction en code :

1. Client (navigateur) envoie GET pour `/loans/create/` → Django résout l'URL via [config/urls.py](config/urls.py#L1-L40) puis [loans/urls.py](loans/urls.py#L1-L20) → `LoanCreateView` rend `loan_form.html`.
2. L'admin complète le formulaire et fait POST. Dans `LoanCreateView.form_valid` ([loans/views.py](loans/views.py#L1-L140)) :
   - `loan = form.save(commit=False)` (création objet en mémoire)
   - `if not loan.book.is_available():` → contrôle métier (méthode dans [library/models.py](library/models.py#L20-L200)).
   - `if not loan.member.is_active:` → validation du membre ([members/models.py](members/models.py#L1-L200)).
   - `loan.book.borrow_book()` → décrémente `available_copies` et sauvegarde.
   - `loan.save()` → insertion en base (ORM).
   - Redirection avec message.

Ce flux correspond strictement aux interactions d'un diagramme de séquence : acteur → contrôleur → modèle → BD → réponse.


### D) Diagramme d'activités (décisions et validations)

Les décisions UML (conditions, forks) se traduisent en `if/else` dans les vues ou en validations dans `forms.py`/`models.py` :

- Décision « livre disponible ? » → `if not loan.book.is_available():` dans `LoanCreateView.form_valid` ([loans/views.py](loans/views.py#L1-L140)).
- Décision « membre actif ? » → `if not loan.member.is_active:` même endroit.
- Validation des champs (format, required) → gérée par `ModelForm` dans [loans/forms.py] et [library/forms.py] ; contraintes `unique`, `max_length` sont au niveau du modèle.

---

## 2) Fichiers importants du projet et rôle pédagogique

- `models.py` (ex: [library/models.py](library/models.py#L1-L200)) : définition du modèle de domaine — classes, types, contraintes, méthodes métier. Pédagogiquement : montre la transformation directe d'un diagramme de classes en code.
- `views.py` (ex: [library/views.py](library/views.py#L1-L300)) : contrôleurs — logique d'acheminement, autorisations et orchestration des formulaires et modèles. Pédagogiquement : illustre les diagrammes de séquence et d'activités.
- `urls.py` (ex: [config/urls.py](config/urls.py#L1-L80), [library/urls.py](library/urls.py#L1-L40)) : point d'entrée HTTP, associe cas d'utilisation à vues.
- `forms.py` (ex: [library/forms.py](library/forms.py#L1-L200)) : encapsule validation et transformation des données utilisateurs ; utile pour expliquer où placer les validations UML.
- `admin.py` : configuration d'administration Django — utile pour démontrer la persistance et les vues CRUD automatiques.
- `templates/` : représentation (Vue) côté presentation — associer aux rôles d'acteurs dans les use cases.
- `settings.py` : configuration globale (AUTH_USER_MODEL, middleware, templates) — expliquer dépendances non-fonctionnelles.
- `manage.py` : outil d'exécution (démarrage, migrations) — utile pour montrer comment déployer et tester.
- `migrations/` : historique des évolutions du modèle — correspond aux versions successives du diagramme de classes.

---

## 3) Matériel pédagogique généré

1) Structure d'exposé (oral) — plan en 6 minutes (exemple)
   - 00:00–00:30 : Introduction rapide du projet
   - 00:30–01:30 : Diagramme de classes → mapping vers `models.py` (montrez `Book`, `Member`, `Loan`)
   - 01:30–02:30 : Cas d'utilisation clé (emprunter un livre) → vues/urls/templates
   - 02:30–03:30 : Séquence complète (POST emprunt) avec appels DB (montrez `borrow_book()` et `loan.save()`)
   - 03:30–04:30 : Décisions/validations (if/else, forms) et où les placer
   - 04:30–05:30 : Démonstration rapide en local (création d'un livre + création d'un emprunt)
   - 05:30–06:00 : Conclusion et questions

2) Résumé écrit (pour remise)

Le projet traduit un modèle UML classique en modèles Django : `Book`, `Member`, `Loan`. Les use cases s'implantent par des vues et urls ; les séquences montrent l'enchaînement requête→validation→ORM→réponse. Les décisions (conditions UML) sont codées en if/else dans les vues ou en validations de `forms.py`.

3) Exemples concrets (à montrer pendant l'exposé)
   - Extrait `Book.borrow_book()` ([library/models.py](library/models.py#L20-L200)) : montre modification d'état et persistance.
   - Extrait `LoanCreateView.form_valid` ([loans/views.py](loans/views.py#L1-L140)) : montre validations et orchestration.

4) Vocabulaire simple mais académique
   - Entité / Modèle : classe persistée dans la base (`models.Model`).
   - Association / Relation : `ForeignKey`, `ManyToManyField`, `OneToOneField`.
   - Use case : fonctionnalité exposée par une vue et une URL.
   - Séquence : enchaînement temporel d'appels (client → vue → modèle → BD → réponse).
   - Validation / Contrôle : vérifications dans `forms.py` ou `views.py`.

---

## 4) Exemples concrets (extraits commentés)

Extrait : vérification disponibilité et emprunt (simplifié)

```python
# loans/views.py (form_valid)
loan = form.save(commit=False)
if not loan.book.is_available():
    messages.error(self.request, 'Ce livre n\'est pas disponible.')
    return self.form_invalid(form)
if not loan.member.is_active:
    messages.error(self.request, 'Ce membre est inactif.')
    return self.form_invalid(form)
loan.book.borrow_book()  # décrémente available_copies et save()
loan.save()
```

Commentaire pédagogique : chaque ligne correspond à une boîte/transition dans un diagramme d'activités.

---

## Conclusion

Ce projet est un excellent support pédagogique pour montrer la correspondance directe entre modélisation UML et un framework MVC/MTV (Django). Les modèles incarnent le diagramme de classes, les vues + urls incarnent les cas d'utilisation et les séquences, et les `forms.py` / méthodes de modèle gèrent les validations et décisions.

---

## Annexes utiles

- Commandes utiles pour l'exposé :

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```

---

Fichier généré automatiquement : `UML_Django_Explication.md`.
