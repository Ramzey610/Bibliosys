from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from library.models import Book, Category
from members.models import Lecteur
from .models import DemandeEmprunt, DemandeRetour, Loan


class DemandeEmpruntTest(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin_test', email='admin@test.local', password='admin123', role='admin', is_librarian=True
        )
        self.lecteur = Lecteur.objects.create(
            first_name='Test', last_name='User', email='test@local', numero_abonnement='T001'
        )
        self.cat = Category.objects.create(name='Test', description='Test')
        self.book = Book.objects.create(title='Livre A', author='Auteur', isbn='ISBN001', category=self.cat, total_copies=2, available_copies=2)

    def test_demande_emprunt_validee_cree_emprunt_et_diminue_stock(self):
        demande = DemandeEmprunt.objects.create(livre=self.book, lecteur=self.lecteur)
        self.assertEqual(demande.statut, 'EN_ATTENTE')

        # Valider la demande
        emprunt = demande.valider(self.admin)

        # Un emprunt doit avoir été créé et le stock diminué
        self.assertIsInstance(emprunt, Loan)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)
        demande.refresh_from_db()
        self.assertEqual(demande.statut, 'VALIDE')
        self.assertEqual(demande.valide_par, self.admin)

    def test_demande_emprunt_refuse_si_indisponible(self):
        # rendre le livre indisponible
        self.book.available_copies = 0
        self.book.save()

        demande = DemandeEmprunt.objects.create(livre=self.book, lecteur=self.lecteur)
        result = demande.valider(self.admin)

        # Devrait renvoyer False et statut REFUSE
        self.assertFalse(result)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 0)
        demande.refresh_from_db()
        self.assertEqual(demande.statut, 'REFUSE')
        self.assertEqual(demande.valide_par, self.admin)


class DemandeRetourTest(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin2', email='admin2@test.local', password='admin123', role='admin', is_librarian=True
        )
        self.lecteur = Lecteur.objects.create(
            first_name='Retour', last_name='User', email='retour@local', numero_abonnement='T002'
        )
        self.cat = Category.objects.create(name='Test2', description='Test2')
        self.book = Book.objects.create(title='Livre B', author='Auteur', isbn='ISBN002', category=self.cat, total_copies=1, available_copies=0)
        self.loan = Loan.objects.create(book=self.book, member=self.lecteur)

    def test_demande_retour_validee_cloture_emprunt_et_incremente_stock(self):
        demande = DemandeRetour.objects.create(emprunt=self.loan, lecteur=self.lecteur)
        self.assertEqual(demande.statut, 'EN_ATTENTE')

        # Valider la demande
        result = demande.valider(self.admin, return_date=timezone.now())
        self.assertTrue(result)

        # L'emprunt doit être clôturé et le stock incrémenté
        self.loan.refresh_from_db()
        self.assertIn(self.loan.status, ['RETOURNÉ', 'EN_RETARD'])
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

        demande.refresh_from_db()
        self.assertEqual(demande.statut, 'VALIDE')
        self.assertEqual(demande.valide_par, self.admin)
