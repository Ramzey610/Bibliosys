from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Lecteur

User = get_user_model()

class MemberUITests(TestCase):
    def setUp(self):
        # Create admin user and login
        self.admin = User.objects.create_superuser(username='admin', email='a@a.com', password='pass')
        self.client.login(username='admin', password='pass')

    def test_detail_shows_deactivation_alert(self):
        user = User.objects.create_user(username='u1', password='pass')
        member = Lecteur.objects.create(first_name='A', last_name='B', email='a@example.com', numero_abonnement='M1', utilisateur=user, statut='inactive')
        url = reverse('members:member_detail', kwargs={'pk': member.pk})
        resp = self.client.get(url)
        self.assertContains(resp, 'Compte désactivé')

    def test_form_shows_deactivation_alert(self):
        user = User.objects.create_user(username='u2', password='pass')
        member = Lecteur.objects.create(first_name='C', last_name='D', email='c@example.com', numero_abonnement='M2', utilisateur=user, statut='suspended')
        url = reverse('members:member_update', kwargs={'pk': member.pk})
        resp = self.client.get(url)
        self.assertContains(resp, 'Le statut actuel')