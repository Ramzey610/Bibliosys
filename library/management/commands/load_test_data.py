"""
Commandes personnalisées Django pour le projet Bibliothèque
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from accounts.models import CustomUser
from library.models import Book, Category
from members.models import Lecteur
from loans.models import Loan
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Charge les données de test pour la bibliothèque'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Chargement des données de test...')

        # 1. Créer les groupes et permissions
        self.create_groups_and_permissions()

        # 2. Créer les utilisateurs de test
        self.create_test_users()

        # 3. Créer les catégories
        self.create_categories()

        # 4. Créer les livres
        self.create_books()

        # 5. Créer les abonnés
        self.create_members()

        # 6. Créer les emprunts
        self.create_loans()

        self.stdout.write(self.style.SUCCESS('✅ Données de test chargées avec succès!'))

    def create_groups_and_permissions(self):
        """Créer les groupes d'utilisateurs"""
        admin_group, _ = Group.objects.get_or_create(name='Administrateur')
        lecteur_group, _ = Group.objects.get_or_create(name='Lecteur')

        self.stdout.write('✓ Groupes créés')

    def create_test_users(self):
        """Créer les utilisateurs de test"""
        # Admin
        if not CustomUser.objects.filter(username='admin').exists():
            admin = CustomUser.objects.create_superuser(
                username='admin',
                email='admin@bibliotheque.local',
                password='admin123',
                first_name='Admin',
                last_name='Bibliothécaire',
                role='admin',
                is_librarian=True
            )
            self.stdout.write('✓ Admin créé (admin / admin123)')

        # Lecteur
        if not CustomUser.objects.filter(username='lecteur').exists():
            lecteur = CustomUser.objects.create_user(
                username='lecteur',
                email='lecteur@bibliotheque.local',
                password='lecteur123',
                first_name='Jean',
                last_name='Lecteur',
                role='lecteur'
            )
            self.stdout.write('✓ Lecteur créé (lecteur / lecteur123)')

    def create_categories(self):
        """Créer les catégories de livres"""
        categories_data = [
            ('Littérature Générale', 'Romans et fictions'),
            ('Science-Fiction', 'Mondes futuristes et imaginaires'),
            ('Policier', 'Mystère et crime'),
            ('Jeunesse', 'Livres pour enfants et adolescents'),
            ('Biographie', 'Histoires de vies réelles'),
            ('Développement Personnel', 'Améliorer sa vie'),
        ]

        for name, description in categories_data:
            Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )

        self.stdout.write(f'✓ {len(categories_data)} catégories créées')

    def create_books(self):
        """Créer des livres de test"""
        books_data = [
            ('1984', 'George Orwell', '9780451524935', 'Littérature Générale', 5, 3),
            ('Le Seigneur des Anneaux', 'J.R.R. Tolkien', '9780544003415', 'Littérature Générale', 4, 2),
            ('Fondation', 'Isaac Asimov', '9780553293357', 'Science-Fiction', 3, 1),
            ('Dune', 'Frank Herbert', '9780441013593', 'Science-Fiction', 3, 2),
            ('Le Meurtre de Roger Ackroyd', 'Agatha Christie', '9780062693471', 'Policier', 2, 1),
            ('Harry Potter à l\'école des sorciers', 'J.K. Rowling', '9780590353403', 'Jeunesse', 6, 4),
            ('Steve Jobs', 'Walter Isaacson', '9781451648539', 'Biographie', 2, 2),
            ('Atomic Habits', 'James Clear', '9780735211292', 'Développement Personnel', 3, 3),
        ]

        for title, author, isbn, category_name, total, available in books_data:
            if not Book.objects.filter(isbn=isbn).exists():
                category = Category.objects.get(name=category_name)
                Book.objects.create(
                    title=title,
                    author=author,
                    isbn=isbn,
                    category=category,
                    total_copies=total,
                    available_copies=available,
                    language='Français'
                )

        self.stdout.write(f'✓ {len(books_data)} livres créés')

    def create_members(self):
        """Créer des lecteurs de test"""
        members_data = [
            ('Marie', 'Dupont', 'marie@example.com', '0601020304', 'MEM001'),
            ('Pierre', 'Martin', 'pierre@example.com', '0602030405', 'MEM002'),
            ('Sophie', 'Bernard', 'sophie@example.com', '0603040506', 'MEM003'),
            ('Luc', 'Thomas', 'luc@example.com', '0604050607', 'MEM004'),
        ]

        for first_name, last_name, email, phone, numero_abonnement in members_data:
            if not Lecteur.objects.filter(numero_abonnement=numero_abonnement).exists():
                Lecteur.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    numero_abonnement=numero_abonnement,
                    statut='active',
                    is_active=True
                )

        # Lier l'utilisateur de test 'lecteur' s'il existe
        try:
            user_lecteur = CustomUser.objects.get(username='lecteur')
            # Si le Lecteur lié n'existe pas, en créer un à partir des infos de l'utilisateur
            if not hasattr(user_lecteur, 'lecteur'):
                Lecteur.objects.create(
                    utilisateur=user_lecteur,
                    first_name=user_lecteur.first_name or 'Jean',
                    last_name=user_lecteur.last_name or 'Lecteur',
                    email=user_lecteur.email or 'lecteur@bibliotheque.local',
                    numero_abonnement='MEM999',
                    statut='active',
                    is_active=True
                )
        except CustomUser.DoesNotExist:
            pass

        self.stdout.write(f'✓ {len(members_data)} lecteurs créés')

    def create_loans(self):
        """Créer des emprunts de test"""
        lecteurs = Lecteur.objects.all()
        books = Book.objects.all()

        if lecteurs.exists() and books.exists():
            for i, lecteur in enumerate(lecteurs[:2]):
                book = books[i % len(books)]
                if book.available_copies > 0:
                    loan_date = timezone.now() - timedelta(days=random.randint(5, 20))
                    due_date = loan_date + timedelta(days=28)

                    Loan.objects.create(
                        book=book,
                        member=lecteur,
                        loan_date=loan_date,
                        due_date=due_date,
                        status='EN_COURS'
                    )
                    book.borrow_book()

            self.stdout.write('✓ Emprunts de test créés')
