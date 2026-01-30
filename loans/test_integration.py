from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from library.models import Book, Category
from members.models import Lecteur
from .models import DemandeEmprunt, DemandeRetour, Loan


class IntegrationDemandeFlowTest(TestCase):
    def setUp(self):
        # Administrateur (bibliothécaire)
        self.admin = CustomUser.objects.create_superuser(
            username='admin_flow', email='admin@flow.local', password='adminpass', role='admin', is_librarian=True
        )

        # Lecteur
        self.user_lect = CustomUser.objects.create_user(username='lect_flow', password='lectpass', email='lect@flow.local', role='lecteur')
        self.lecteur = Lecteur.objects.create(utilisateur=self.user_lect, first_name='Test', last_name='Lecteur', email='lect@flow.local', numero_abonnement='LFLOW')

        self.cat = Category.objects.create(name='IntCat', description='Intégration')
        self.book = Book.objects.create(title='Int Livre', author='Auteur', isbn='INT001', category=self.cat, total_copies=1, available_copies=1)

    def test_demande_emprunt_to_emprunt_creation(self):
        # Le lecteur crée une demande d'emprunt
        self.client.login(username='lect_flow', password='lectpass')
        resp = self.client.post(reverse('loans:demande_emprunt'), data={'livre': self.book.pk, 'commentaire': 'Demande intégration'}, follow=True)
        self.assertEqual(DemandeEmprunt.objects.count(), 1)
        demande = DemandeEmprunt.objects.first()
        self.assertEqual(demande.statut, 'EN_ATTENTE')

        # L'administrateur valide la demande
        self.client.logout()
        self.client.login(username='admin_flow', password='adminpass')
        url = reverse('loans:valider_demande_emprunt', args=[demande.pk, 'valider'])
        resp = self.client.get(url, follow=True)

        # Un emprunt a été créé et le stock a diminué
        self.assertEqual(Loan.objects.count(), 1)
        loan = Loan.objects.first()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 0)
        demande.refresh_from_db()
        self.assertEqual(demande.statut, 'VALIDE')
        self.assertEqual(demande.valide_par, self.admin)

    def test_demande_retour_flow(self):
        # Créer un emprunt effectif
        loan = Loan.objects.create(book=self.book, member=self.lecteur)
        self.book.available_copies = 0
        self.book.save()

        # Le lecteur crée une demande de retour
        self.client.login(username='lect_flow', password='lectpass')
        resp = self.client.post(reverse('loans:demande_retour'), data={'emprunt': loan.pk, 'commentaire': 'Retour intégration'}, follow=True)
        self.assertEqual(DemandeRetour.objects.count(), 1)
        demande = DemandeRetour.objects.first()
        self.assertEqual(demande.statut, 'EN_ATTENTE')

        # L'administrateur valide la demande
        self.client.logout()
        self.client.login(username='admin_flow', password='adminpass')
        url = reverse('loans:valider_demande_retour', args=[demande.pk, 'valider'])
        resp = self.client.get(url, follow=True)

        # L'emprunt doit être clôturé et le stock incrémenté
        loan.refresh_from_db()
        self.assertIn(loan.status, ['RETOURNÉ', 'EN_RETARD'])
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)
        demande.refresh_from_db()
        self.assertEqual(demande.statut, 'VALIDE')
        self.assertEqual(demande.valide_par, self.admin)
