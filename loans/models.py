from django.db import models
from django.utils import timezone
from datetime import timedelta
from library.models import Book
from members.models import Lecteur
from accounts.models import CustomUser


class Loan(models.Model):
    """Modèle interne représentant un Emprunt effectif (table existante).

    IMPORTANT: Ce modèle n'est pas directement créé par le lecteur. Il est créé
    uniquement quand une `DemandeEmprunt` a été VALIDÉE par le bibliothécaire.
    """

    STATUS_CHOICES = (
        ('EN_COURS', 'En cours'),
        ('RETOURNÉ', 'Retourné'),
        ('EN_RETARD', 'En retard'),
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name='Livre',
        related_name='loans'
    )
    member = models.ForeignKey(
        Lecteur,
        on_delete=models.CASCADE,
        verbose_name='Lecteur',
        related_name='loans'
    )
    loan_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'emprunt'
    )
    due_date = models.DateTimeField(
        verbose_name='Date d\'échéance'
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de retour'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_COURS',
        verbose_name='Statut'
    )
    fine = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name='Amende'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Remarques'
    )

    class Meta:
        verbose_name = 'Emprunt'
        verbose_name_plural = 'Emprunts'
        ordering = ['-loan_date']
        indexes = [
            models.Index(fields=['status', 'member']),
            models.Index(fields=['loan_date']),
        ]

    def __str__(self):
        return f"{self.member.get_full_name()} - {self.book.title}"

    def save(self, *args, **kwargs):
        """Définir la date d'échéance si elle n'existe pas"""
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=28)
        super().save(*args, **kwargs)

    def is_overdue(self):
        """Vérifie si l'emprunt est en retard"""
        if self.status == 'EN_COURS' and timezone.now() > self.due_date:
            return True
        return False

    def return_loan(self, return_date=None):
        """Retourner le livre (mise à jour du statut et du stock)"""
        if return_date is None:
            return_date = timezone.now()
        
        self.return_date = return_date
        
        # Calculer l'amende si en retard
        if return_date > self.due_date:
            days_overdue = (return_date.date() - self.due_date.date()).days
            self.fine = days_overdue * 1.00  # 1€ par jour de retard
            self.status = 'EN_RETARD'
        else:
            self.status = 'RETOURNÉ'
        
        # Rendre le livre disponible
        self.book.return_book()
        self.save()

    def get_days_borrowed(self):
        """Nombre de jours empruntés"""
        end_date = self.return_date or timezone.now()
        return (end_date.date() - self.loan_date.date()).days


class LoanHistory(models.Model):
    """Historique des emprunts (archive)"""
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Livre'
    )
    member = models.ForeignKey(
        Lecteur,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Lecteur'
    )
    loan_date = models.DateTimeField(
        verbose_name='Date d\'emprunt'
    )
    due_date = models.DateTimeField(
        verbose_name='Date d\'échéance'
    )
    return_date = models.DateTimeField(
        verbose_name='Date de retour'
    )
    status = models.CharField(
        max_length=20,
        verbose_name='Statut'
    )
    fine = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Amende'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Archivé le'
    )

    class Meta:
        verbose_name = 'Historique d\'emprunt'
        verbose_name_plural = 'Historique des emprunts'
        ordering = ['-loan_date']

    def __str__(self):
        return f"Archive: {self.member} - {self.book}"


# ----- Modèles pour les demandes (UML strict séparant Demande et Action Finale) -----

class DemandeEmprunt(models.Model):
    """Demande d'emprunt créée par un Lecteur (statuts: EN_ATTENTE, VALIDÉE, REFUSÉE)

    - Sur VALIDATION par le bibliothécaire, on crée un `Loan` (Emprunt) et on diminue le stock
    - Sur REFUS, aucune modification de stock
    """

    STATUTS = (
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validée'),
        ('REFUSE', 'Refusée'),
    )

    livre = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Livre')
    lecteur = models.ForeignKey(Lecteur, on_delete=models.CASCADE, verbose_name='Lecteur', related_name='demandes_emprunt')
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name='Date de la demande')
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE', verbose_name='Statut')
    commentaire = models.TextField(blank=True, null=True, verbose_name='Commentaire du lecteur')
    valide_par = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Validé par')
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name='Date de validation')

    class Meta:
        verbose_name = 'Demande d\'emprunt'
        verbose_name_plural = 'Demandes d\'emprunt'
        ordering = ['-date_demande']

    def __str__(self):
        return f"DemandeEmprunt #{self.pk} - {self.lecteur} -> {self.livre} ({self.statut})"

    def valider(self, bibliothecaire_user):
        """Valider la demande : créer un Emprunt et diminuer le stock si possible"""
        if self.statut != 'EN_ATTENTE':
            return False
        # Vérifier disponibilité
        if not self.livre.is_available():
            # On peut marquer comme refusée si plus d'exemplaires
            self.statut = 'REFUSE'
            self.valide_par = bibliothecaire_user
            self.date_validation = timezone.now()
            self.save()
            return False

        # Créer l'emprunt
        emprunt = Loan.objects.create(
            book=self.livre,
            member=self.lecteur,
            # due_date sera calculée automatiquement si non fourni
        )
        # Diminuer le stock
        self.livre.borrow_book()

        self.statut = 'VALIDE'
        self.valide_par = bibliothecaire_user
        self.date_validation = timezone.now()
        self.save()
        return emprunt


class DemandeRetour(models.Model):
    """Demande de retour créée par le Lecteur pour un Emprunt existant"""

    STATUTS = (
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validée'),
        ('REFUSE', 'Refusée'),
    )

    emprunt = models.ForeignKey(Loan, on_delete=models.CASCADE, verbose_name='Emprunt')
    lecteur = models.ForeignKey(Lecteur, on_delete=models.CASCADE, verbose_name='Lecteur', related_name='demandes_retour')
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name='Date de la demande')
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_ATTENTE', verbose_name='Statut')
    commentaire = models.TextField(blank=True, null=True, verbose_name='Commentaire du lecteur')
    valide_par = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Validé par')
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name='Date de validation')

    class Meta:
        verbose_name = 'Demande de retour'
        verbose_name_plural = 'Demandes de retour'
        ordering = ['-date_demande']

    def __str__(self):
        return f"DemandeRetour #{self.pk} - {self.lecteur} -> Emprunt #{self.emprunt.pk} ({self.statut})"

    def valider(self, bibliothecaire_user, return_date=None):
        """Valider le retour : clôturer l'emprunt et incrémenter le stock"""
        if self.statut != 'EN_ATTENTE':
            return False

        self.emprunt.return_loan(return_date=return_date)

        self.statut = 'VALIDE'
        self.valide_par = bibliothecaire_user
        self.date_validation = timezone.now()
        self.save()
        return True
