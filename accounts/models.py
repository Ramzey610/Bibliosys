from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé
    Hérite de AbstractUser avec des champs additionnels si nécessaire
    """
    ROLE_CHOICES = (
        ('admin', 'Bibliothécaire'),
        ('lecteur', 'Lecteur'),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='lecteur',
        verbose_name='Rôle'
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
    is_librarian = models.BooleanField(
        default=False,
        verbose_name='Est bibliothécaire'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    def is_admin_user(self):
        """Vérifie si l'utilisateur est un bibliothécaire"""
        return self.role == 'admin' or self.is_librarian or self.is_staff
