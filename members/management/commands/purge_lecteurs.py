from django.core.management.base import BaseCommand, CommandError
from members.models import Lecteur
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Supprime tous les Lecteur sauf ceux liés à des superusers. Utiliser --dry-run pour prévisualiser.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Ne pas supprimer, afficher seulement ce qui serait supprimé')
        parser.add_argument('--preserve-superusers', action='store_true', default=True, help='Préserver les lecteurs liés aux superusers')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        preserve_super = options.get('preserve_superusers')

        User = get_user_model()
        to_delete = []
        for lect in Lecteur.objects.select_related('utilisateur'):
            if preserve_super and lect.utilisateur and getattr(lect.utilisateur, 'is_superuser', False):
                continue
            to_delete.append(lect)

        self.stdout.write(self.style.WARNING(f"{len(to_delete)} lecteur(s) trouvés pour suppression."))
        if dry_run:
            for lect in to_delete[:50]:
                self.stdout.write(f"- {lect.pk} | {lect.get_full_name()} | {lect.email}")
            if len(to_delete) > 50:
                self.stdout.write(f"... et {len(to_delete)-50} de plus")
            self.stdout.write(self.style.SUCCESS('Dry-run complete. Aucun changement effectué.'))
            return

        # demande confirmation interactive
        confirm = input('Confirmer suppression de ces lecteurs? Tapez OUI pour valider: ')
        if confirm != 'OUI':
            self.stdout.write(self.style.ERROR('Abandon: confirmation non fournie.'))
            return

        count = 0
        for lect in to_delete:
            lect.delete()
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Suppression terminée: {count} lecteur(s) supprimé(s).'))