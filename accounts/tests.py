from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from io import StringIO
from members.models import Lecteur


class RegistrationRouteTests(TestCase):
    def test_register_url_not_resolvable(self):
        # The named route 'accounts:register' must not be defined when registration is disabled
        with self.assertRaises(NoReverseMatch):
            reverse('accounts:register')

    def test_register_path_returns_404(self):
        # Direct access to the path should return 404 (no route configured)
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 404)


class LecteurCreationPermissionsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()

        self.user = User.objects.create_user(username='user', password='pass')

    def test_non_admin_cannot_access_create(self):
        self.client.login(username='user', password='pass')
        url = reverse('members:member_create')
        response = self.client.get(url)
        # Non-admin should be redirected to book_list
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('library:book_list'), response.url)

    def test_admin_can_create_lecteur(self):
        self.client.login(username='admin', password='pass')
        url = reverse('members:member_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test-lecteur@example.com',
            'phone': '',
            'address': '',
            'numero_abonnement': 'MEM-TEST-001',
            'statut': 'active',
            'is_active': True,
            'remarques': ''
        }
        response = self.client.post(url, data)
        # on success redirect to list
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lecteur.objects.filter(email='test-lecteur@example.com').exists())

    def test_reset_admins_command_dry_run_and_execute(self):
        User = get_user_model()
        # Add an extra admin to be removed
        other = User.objects.create_user(username='otheradmin', password='p')
        other.is_staff = True
        other.is_superuser = True
        other.save()

        out = StringIO()
        call_command('reset_admins', '--dry-run', stdout=out)
        self.assertIn('Dry-run', out.getvalue())

        # Now actually reset (pass args to avoid interactive prompts)
        out2 = StringIO()
        call_command('reset_admins', '--username=resetadmin', '--email=reset@example.com', '--password=secretpass', '--yes', stdout=out2)
        output = out2.getvalue()
        self.assertIn('Admin créé', output)
        # Verify the old admins were removed except the new one
        admins = User.objects.filter(is_staff=True)
        self.assertEqual(admins.count(), 1)
        self.assertTrue(admins.filter(username='resetadmin').exists())
