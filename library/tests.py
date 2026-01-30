from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from library.models import Book, Category
from members.models import Lecteur
from loans.models import Loan
from accounts.models import CustomUser


class BookModelTest(TestCase):
    """Tests pour le modèle Book"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            category=self.category,
            total_copies=5,
            available_copies=5
        )

    def test_book_creation(self):
        """Test la création d'un livre"""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertTrue(self.book.is_active)

    def test_book_available(self):
        """Test la disponibilité d'un livre"""
        self.assertTrue(self.book.is_available())

    def test_borrow_book(self):
        """Test l'emprunt d'un livre"""
        self.book.borrow_book()
        self.assertEqual(self.book.available_copies, 4)

    def test_return_book(self):
        """Test le retour d'un livre"""
        self.book.borrow_book()
        self.book.return_book()
        self.assertEqual(self.book.available_copies, 5)


class LecteurModelTest(TestCase):
    """Tests pour le modèle Lecteur"""
    
    def setUp(self):
        self.lecteur = Lecteur.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            numero_abonnement='MEM001'
        )

    def test_lecteur_creation(self):
        """Test la création d'un lecteur"""
        self.assertEqual(self.lecteur.get_full_name(), 'John Doe')
        self.assertEqual(self.lecteur.statut, 'active')

    def test_lecteur_active_loans(self):
        """Test le comptage des emprunts actifs"""
        self.assertEqual(self.lecteur.get_active_loans_count(), 0)


class LoanModelTest(TestCase):
    """Tests pour le modèle Loan"""
    
    def setUp(self):
        self.lecteur = Lecteur.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            numero_abonnement='MEM002'
        )
        self.category = Category.objects.create(name='Test')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            category=self.category,
            total_copies=1,
            available_copies=1
        )
        self.loan = Loan.objects.create(
            book=self.book,
            member=self.lecteur
        )

    def test_loan_creation(self):
        """Test la création d'un emprunt"""
        self.assertEqual(self.loan.status, 'EN_COURS')
        self.assertIsNotNone(self.loan.due_date)

    def test_loan_overdue(self):
        """Test la détection de retard"""
        self.loan.due_date = timezone.now() - timedelta(days=1)
        self.loan.save()
        self.assertTrue(self.loan.is_overdue())

    def test_loan_return(self):
        """Test le retour d'un livre"""
        self.loan.return_loan()
        self.assertEqual(self.loan.status, 'RETOURNÉ')
        self.assertIsNotNone(self.loan.return_date)


class TemplateFilterTests(TestCase):
    def test_days_until_filter(self):
        from django.template import Template, Context
        from django.utils import timezone
        from datetime import timedelta
        future = timezone.localdate() + timedelta(days=3)
        t = Template('{% load library_extras %}{{ date|days_until }}')
        rendered = t.render(Context({'date': future}))
        self.assertIn('3 jours', rendered)
        today = timezone.localdate()
        import html as _html
        rendered_today = t.render(Context({'date': today}))
        self.assertIn("Aujourd'hui", _html.unescape(rendered_today))
        past = timezone.localdate() - timedelta(days=2)
        rendered_past = t.render(Context({'date': past}))
        self.assertIn('2 jour', rendered_past)


class DashboardTests(TestCase):
    def setUp(self):
        from accounts.models import CustomUser
        self.admin = CustomUser.objects.create_superuser(username='admin', email='a@a.com', password='pass')

    def test_total_lecteurs_counts_active_status(self):
        # Create two members, one active and one inactive
        from members.models import Lecteur
        user1 = None
        l1 = Lecteur.objects.create(first_name='A', last_name='A', email='a1@example.com', numero_abonnement='M1', statut='active')
        l2 = Lecteur.objects.create(first_name='B', last_name='B', email='b1@example.com', numero_abonnement='M2', statut='inactive')
        self.client.login(username='admin', password='pass')
        from django.urls import reverse
        resp = self.client.get(reverse('library:dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_lecteurs', resp.context)
        self.assertIn('total_lecteurs_total', resp.context)
        self.assertEqual(resp.context['total_lecteurs'], 1)
        self.assertEqual(resp.context['total_lecteurs_total'], 2)
