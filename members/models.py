from django.db import models
from django.utils import timezone
from django.urls import reverse
from accounts.models import CustomUser


class Lecteur(models.Model):
    """Modèle représentant un Lecteur (lié à un utilisateur)

    - `utilisateur` : lien OneToOne vers `CustomUser` (peut être null pour les données existantes)
    - `numero_abonnement` : numéro d'adhésion pédagogique
    - `statut` : 'active'/'inactive'/'suspended'
    - méthodes pédagogiques: `get_full_name`, `get_active_loans_count`
    """

    STATUS_CHOICES = (
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('suspended', 'Suspendu'),
    )

    utilisateur = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='lecteur',
        null=True,
        blank=True,
        verbose_name="Utilisateur lié"
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name='Prénom'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Nom'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Téléphone'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Adresse'
    )
    numero_abonnement = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro d\'adhésion'
    )
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'inscription'
    )
    derniere_activite = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière activité'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Est actif'
    )
    remarques = models.TextField(
        blank=True,
        null=True,
        verbose_name='Remarques'
    )

    class Meta:
        verbose_name = 'Lecteur'
        verbose_name_plural = 'Lecteurs'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['numero_abonnement']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        """URL du détail du lecteur"""
        return reverse('members:member_detail', kwargs={'pk': self.pk})

    def get_active_loans_count(self):
        """Nombre d'emprunts actifs pour ce lecteur"""
        from loans.models import Loan
        return Loan.objects.filter(member=self, status='EN_COURS').count()

    def save(self, *args, **kwargs):
        """Sauvegarde le Lecteur et synchronise l'état `is_active` de l'utilisateur lié.

        Règle : si `statut` != 'active' ou `is_active` == False alors l'utilisateur lié
        est désactivé (`utilisateur.is_active = False`). Sinon l'utilisateur est activé.
        """
        super().save(*args, **kwargs)
        if self.utilisateur:
            # L'état actif du compte utilisateur dépend uniquement du statut du Lecteur.
            desired = (self.statut == 'active')
            if self.utilisateur.is_active != desired:
                self.utilisateur.is_active = desired
                self.utilisateur.save(update_fields=['is_active'])

    # --- Propriétés de compatibilité (anciennes dénominations françaises pédagogiques)
    @property
    def member_number(self):
        """Compatibilité : ancien nom `member_number` -> `numero_abonnement`"""
        return self.numero_abonnement

    @member_number.setter
    def member_number(self, value):
        self.numero_abonnement = value

    @property
    def registration_date(self):
        """Compatibilité : ancien nom `registration_date` -> `date_inscription`"""
        return self.date_inscription

    @property
    def last_activity(self):
        """Compatibilité : ancien nom `last_activity` -> `derniere_activite`"""
        return self.derniere_activite

    @property
    def status(self):
        """Compatibilité : ancien nom `status` -> `statut`"""
        return self.statut

    @status.setter
    def status(self, value):
        self.statut = value

    @property
    def notes(self):
        """Compatibilité : ancien nom `notes` -> `remarques`"""
        return self.remarques

    @notes.setter
    def notes(self, value):
        self.remarques = value
