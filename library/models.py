from django.db import models


class Category(models.Model):
    """Catégorie de livres"""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Nom de la catégorie'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Modèle pour les livres"""
    title = models.CharField(
        max_length=300,
        verbose_name='Titre'
    )
    author = models.CharField(
        max_length=200,
        verbose_name='Auteur'
    )
    isbn = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='ISBN'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Catégorie',
        related_name='books'
    )
    total_copies = models.PositiveIntegerField(
        default=1,
        verbose_name='Nombre total d\'exemplaires'
    )
    available_copies = models.PositiveIntegerField(
        default=1,
        verbose_name='Exemplaires disponibles'
    )
    publication_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date de publication'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'ajout'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de mise à jour'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    publisher = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Éditeur'
    )
    language = models.CharField(
        max_length=50,
        default='Français',
        verbose_name='Langue'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Actif'
    )

    class Meta:
        verbose_name = 'Livre'
        verbose_name_plural = 'Livres'
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['isbn']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} - {self.author}"

    def is_available(self):
        """Vérifie si le livre est disponible"""
        return self.available_copies > 0

    def borrow_book(self):
        """Emprunter un exemplaire"""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()
            return True
        return False

    def return_book(self):
        """Retourner un exemplaire"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
            return True
        return False
