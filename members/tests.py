from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from members.models import Lecteur


class LecteurUserCreationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()

    def test_admin_create_lecteur_creates_customuser_and_password(self):
        self.client.login(username='admin', password='pass')
        url = reverse('members:member_create')

        data = {
            'first_name': 'Alice',
            'last_name': 'Dupont',
            'email': 'alice@example.com',
            'phone': '',
            'address': '',
            'numero_abonnement': '',  # laisser vide pour auto-géné
            'statut': 'active',
            'is_active': True,
            'remarques': ''
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Le lecteur est créé
        lecteur = Lecteur.objects.filter(email='alice@example.com').first()
        self.assertIsNotNone(lecteur)

        # Un utilisateur lié a été créé et assigné
        self.assertIsNotNone(lecteur.utilisateur)
        User = get_user_model()
        user = User.objects.get(pk=lecteur.utilisateur.pk)
        self.assertEqual(user.email, 'alice@example.com')

        # Le message doit contenir les identifiants (username et password)
        messages = list(response.context['messages'])
        found = None
        for m in messages:
            if 'Identifiants' in str(m):
                found = str(m)
                break
        self.assertIsNotNone(found, msg='Message d\'identifiants non trouvé')

        import re
        match = re.search(r"Identifiants:\s*(\S+)\s*/\s*(\S+)", found)
        self.assertIsNotNone(match, msg='Format du message d\'identifiants invalide')
        username, password = match.group(1), match.group(2)

        # Vérifier qu'on peut se connecter avec ces identifiants
        self.client.logout()
        login_ok = self.client.login(username=username, password=password)
        self.assertTrue(login_ok, msg="La connexion avec les identifiants générés a échoué")

    def test_admin_site_add_creates_user_and_credentials(self):
        # Utilisation de l'interface admin "add" pour créer un lecteur
        admin_login = self.client.login(username='admin', password='pass')
        self.assertTrue(admin_login)
        url = reverse('admin:members_lecteur_add')
        data = {
            'first_name': 'Charles',
            'last_name': 'Petit',
            'email': 'charles.petit@example.com',
            'phone': '',
            'address': '',
            'numero_abonnement': 'MEM-ADM-002',
            'statut': 'active',
            'is_active': 'on',
            'remarques': '',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Lecteur.objects.filter(email='charles.petit@example.com').exists())
        lecteur = Lecteur.objects.get(email='charles.petit@example.com')
        self.assertIsNotNone(lecteur.utilisateur)

        # Messages d'admin contiennent les identifiants
        messages = list(response.context['messages'])
        found = None
        for m in messages:
            if 'Identifiants' in str(m):
                found = str(m)
                break
        self.assertIsNotNone(found)
        import re
        match = re.search(r"Identifiants:\s*(\S+)\s*/\s*(\S+)", found)
        self.assertIsNotNone(match)
        username, password = match.group(1), match.group(2)
        self.client.logout()
        self.assertTrue(self.client.login(username=username, password=password))

    def test_username_uniqueness_handling(self):
        # Créer d'abord un utilisateur qui pourrait clash
        User = get_user_model()
        User.objects.create_user(username='alice', password='p')

        self.client.login(username='admin', password='pass')
        url = reverse('members:member_create')
        data = {
            'first_name': 'Alice',
            'last_name': 'Dupont',
            'email': 'alice@example.com',
            'numero_abonnement': 'MEM999',
            'statut': 'active',
            'is_active': True,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        lecteur = Lecteur.objects.get(email='alice@example.com')
        self.assertIsNotNone(lecteur.utilisateur)
        # Username should not equal the existing 'alice' exactly
        self.assertNotEqual(lecteur.utilisateur.username, 'alice')

    def test_ajax_quick_add_creates_user_and_returns_json(self):
        # Test the Quick Add modal submission via AJAX returns JSON with credentials
        self.client.login(username='admin', password='pass')
        url = reverse('members:member_create')
        data = {
            'first_name': 'Ajax',
            'last_name': 'User',
            'email': 'ajax.user@example.com',
            'phone': '',
            'address': '',
            'numero_abonnement': '',
            'statut': 'active',
            'is_active': True,
            'remarques': ''
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        json_data = response.json()
        self.assertEqual(json_data.get('status'), 'ok')
        username = json_data.get('username')
        password = json_data.get('password')
        self.assertTrue(username and password)

        # Verify login with returned credentials works
        self.client.logout()
        self.assertTrue(self.client.login(username=username, password=password))

    def test_ajax_quick_add_with_password_uses_provided_password(self):
        # If admin provides password via modal, it must be used
        self.client.login(username='admin', password='pass')
        url = reverse('members:member_create')
        data = {
            'first_name': 'Ajax2',
            'last_name': 'User2',
            'email': 'ajax2.user@example.com',
            'user_password': 'Complexp@ss123',
            'user_confirm_password': 'Complexp@ss123',
            'numero_abonnement': '',
            'statut': 'active',
            'is_active': True,
            'remarques': ''
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        json_data = response.json()
        self.assertEqual(json_data.get('status'), 'ok')
        username = json_data.get('username')
        password = json_data.get('password')
        self.assertEqual(password, 'Complexp@ss123')
        # Verify login with returned credentials works
        self.client.logout()
        self.assertTrue(self.client.login(username=username, password=password))

    def test_admin_create_with_password_field_in_form(self):
        # Test classic (non-AJAX) CreateView accepts a provided password
        self.client.login(username='admin', password='pass')
        url = reverse('members:member_create')
        data = {
            'first_name': 'Manual',
            'last_name': 'Pass',
            'email': 'manual.pass@example.com',
            'user_password': 'AnotherC0nsistent!',
            'user_confirm_password': 'AnotherC0nsistent!',
            'numero_abonnement': '',
            'statut': 'active',
            'is_active': True,
            'remarques': ''
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        lecteur = Lecteur.objects.get(email='manual.pass@example.com')
        self.assertIsNotNone(lecteur.utilisateur)
        self.client.logout()
        self.assertTrue(self.client.login(username=lecteur.utilisateur.username, password='AnotherC0nsistent!'))

    def test_purge_lecteurs_dry_run_and_execute(self):
        # Créer des lecteurs à supprimer et un à préserver (lié à superuser)
        User = get_user_model()
        superu = User.objects.create_superuser(username='super', password='s', email='super@example.com')
        preserved = Lecteur.objects.create(first_name='Preserve', last_name='Me', email='preserve@example.com', numero_abonnement='MEMPRES', utilisateur=superu)
        to_remove1 = Lecteur.objects.create(first_name='To', last_name='Remove1', email='r1@example.com', numero_abonnement='MEM1')
        to_remove2 = Lecteur.objects.create(first_name='To', last_name='Remove2', email='r2@example.com', numero_abonnement='MEM2')

        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command('purge_lecteurs', '--dry-run', stdout=out)
        output = out.getvalue()
        self.assertIn('Dry-run complete', output)

        # Now actually purge (simulate confirmation by patching input)
        import builtins
        old_input = builtins.input
        builtins.input = lambda prompt='': 'OUI'
        out2 = StringIO()
        call_command('purge_lecteurs', stdout=out2)
        builtins.input = old_input
        self.assertFalse(Lecteur.objects.filter(pk=to_remove1.pk).exists())
        self.assertFalse(Lecteur.objects.filter(pk=to_remove2.pk).exists())
        self.assertTrue(Lecteur.objects.filter(pk=preserved.pk).exists())
