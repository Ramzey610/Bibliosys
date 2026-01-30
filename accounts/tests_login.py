from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from members.models import Lecteur

User = get_user_model()

class LoginStatusMessageTests(TestCase):
    def setUp(self):
        # create user and lecteur
        self.user_inactive = User.objects.create_user(username='u_inactive', password='pass')
        self.member_inactive = Lecteur.objects.create(first_name='I', last_name='N', email='i@example.com', numero_abonnement='M100', utilisateur=self.user_inactive, statut='inactive')

        self.user_suspended = User.objects.create_user(username='u_sus', password='pass')
        self.member_suspended = Lecteur.objects.create(first_name='S', last_name='P', email='s@example.com', numero_abonnement='M200', utilisateur=self.user_suspended, statut='suspended')

    def test_inactive_user_shows_message(self):
        url = reverse('accounts:login')
        resp = self.client.post(url, {'username': 'u_inactive', 'password': 'pass'})
        self.assertEqual(resp.status_code, 200)
        messages = list(resp.context['messages'])
        self.assertTrue(any('inactif' in m.message.lower() or 'inact' in m.message.lower() for m in messages))

    def test_suspended_user_shows_message(self):
        url = reverse('accounts:login')
        resp = self.client.post(url, {'username': 'u_sus', 'password': 'pass'})
        self.assertEqual(resp.status_code, 200)
        messages = list(resp.context['messages'])
        self.assertTrue(any('suspendu' in m.message.lower() or 'suspend' in m.message.lower() for m in messages))
