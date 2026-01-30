from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import getpass


class Command(BaseCommand):
    help = 'Supprime les administrateurs existants (optionnel) et crée un nouvel administrateur.'

    def add_arguments(self, parser):
        parser.add_argument('--username', dest='username', help='Nom d\'utilisateur pour le nouvel admin')
        parser.add_argument('--email', dest='email', help='Email pour le nouvel admin')
        parser.add_argument('--password', dest='password', help='Mot de passe pour le nouvel admin')
        parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='Afficher ce qui serait fait sans exécuter')
        parser.add_argument('--yes', dest='yes', action='store_true', help='Accepter automatiquement la suppression des admins existants')

    def handle(self, *args, **options):
        User = get_user_model()
        admins = User.objects.filter(is_staff=True).order_by('id')

        if admins.exists():
            self.stdout.write(self.style.WARNING('Admins existants :'))
            for u in admins:
                self.stdout.write(f' - {u.username} (id={u.pk}, email={u.email}, is_superuser={u.is_superuser})')

            if options.get('dry_run'):
                self.stdout.write(self.style.NOTICE('Dry-run: aucune suppression effectuée.'))
                return

            if not options.get('yes'):
                confirmed = input('Supprimer ces comptes administrateurs? TAPEZ OUI pour confirmer: ')
            else:
                confirmed = 'OUI'

            if confirmed != 'OUI':
                self.stdout.write(self.style.NOTICE('Abandon.'))
            else:
                count = admins.count()
                admins.delete()
                self.stdout.write(self.style.SUCCESS(f'{count} comptes administrateurs supprimés.'))
        else:
            self.stdout.write('Aucun admin existant trouvé.')

        # Création du nouvel admin
        username = options.get('username') or input('Nom d\'utilisateur pour le nouvel admin: ')
        email = options.get('email') or input('Email: ')
        password = options.get('password')
        if not password:
            password = getpass.getpass('Mot de passe (sera masqué lors de la saisie): ')
            confirm = getpass.getpass('Confirmer le mot de passe: ')
            if password != confirm:
                self.stdout.write(self.style.ERROR('Les mots de passe ne correspondent pas. Abandon.'))
                return

        if options.get('dry_run'):
            self.stdout.write(self.style.NOTICE('Dry-run: aucun compte créé.'))
            return

        user = User.objects.create_superuser(username=username, email=email, password=password)
        user.is_staff = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Admin créé: {user.username} (email={user.email})'))
        self.stdout.write(self.style.WARNING('ATTENTION: gardez ces identifiants en lieu sûr.'))
