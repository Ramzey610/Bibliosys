from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from library.models import Book, Category
from members.models import Lecteur
from .models import Loan


class UIButtonsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='lect1', password='pass', email='lect1@local', role='lecteur')
        self.lecteur = Lecteur.objects.create(utilisateur=self.user, first_name='Lect', last_name='One', email='lect1@local', numero_abonnement='L100')
        self.cat = Category.objects.create(name='UI Test', description='UI')
        self.book = Book.objects.create(title='Livre UI', author='A.', isbn='UIISBN', category=self.cat, total_copies=1, available_copies=1)
        self.loan = Loan.objects.create(book=self.book, member=self.lecteur)

    def test_book_detail_shows_demande_emprunt_for_lecteur(self):
        self.client.login(username='lect1', password='pass')
        url = reverse('library:book_detail', args=[self.book.pk])
        resp = self.client.get(url)
        self.assertContains(resp, "Demande d'emprunt")
        self.assertContains(resp, reverse('loans:demande_emprunt'))

        # Anonymous should not see the button
        self.client.logout()
        resp2 = self.client.get(url)
        self.assertNotContains(resp2, "Demande d'emprunt")

    def test_loan_detail_shows_demande_retour_for_owner(self):
        self.client.login(username='lect1', password='pass')
        url = reverse('loans:loan_detail', args=[self.loan.pk])
        resp = self.client.get(url)
        self.assertContains(resp, 'Demande de retour')
        self.assertContains(resp, reverse('loans:demande_retour'))

        # Another user should not see the demande de retour
        other = CustomUser.objects.create_user(username='other', password='pass', email='other@local', role='lecteur')
        Lecteur.objects.create(utilisateur=other, first_name='O', last_name='O', email='other@local', numero_abonnement='L101')
        self.client.logout()
        self.client.login(username='other', password='pass')
        resp2 = self.client.get(url)
        self.assertNotContains(resp2, 'Demande de retour')
