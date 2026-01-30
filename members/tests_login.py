from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Lecteur

User = get_user_model()

class MemberActiveSyncTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='m1', password='pass')
        self.member = Lecteur.objects.create(
            first_name='A', last_name='B', email='a@example.com', numero_abonnement='M1', utilisateur=self.user
        )

    def test_deactivating_member_disables_user(self):
        self.member.statut = 'inactive'
        self.member.is_active = False
        self.member.save()
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_suspending_member_disables_user(self):
        self.member.statut = 'suspended'
        self.member.save()
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activating_member_enables_user(self):
        # Disable first
        self.member.statut = 'inactive'
        self.member.is_active = False
        self.member.save()
        # Re-enable
        self.member.statut = 'active'
        self.member.is_active = True
        self.member.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
