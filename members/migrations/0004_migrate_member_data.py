from django.db import migrations


def forwards(apps, schema_editor):
    Member = apps.get_model('members', 'Member')
    Lecteur = apps.get_model('members', 'Lecteur')

    # Copier chaque Member existant en conservant le même id pour préserver les FK
    for m in Member.objects.all():
        # Utiliser update_or_create pour être idempotent
        Lecteur.objects.update_or_create(
            id=m.id,
            defaults={
                'first_name': m.first_name,
                'last_name': m.last_name,
                'email': m.email,
                'phone': m.phone,
                'address': m.address,
                'numero_abonnement': getattr(m, 'member_number', f'MEM{m.id:04d}'),
                'date_inscription': m.registration_date if hasattr(m, 'registration_date') else None,
                'derniere_activite': m.last_activity if hasattr(m, 'last_activity') else None,
                'statut': getattr(m, 'status', 'active'),
                'is_active': m.is_active if hasattr(m, 'is_active') else True,
                'remarques': getattr(m, 'notes', '') or None,
            }
        )


def reverse(apps, schema_editor):
    Lecteur = apps.get_model('members', 'Lecteur')
    Member = apps.get_model('members', 'Member')

    # Supprimer les Lecteurs créés à partir des anciens Members (si possible)
    try:
        member_ids = list(Member.objects.values_list('id', flat=True))
        Lecteur.objects.filter(id__in=member_ids).delete()
    except Exception:
        # Si Member n'existe pas au reverse, ne rien faire
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_lecteur'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
