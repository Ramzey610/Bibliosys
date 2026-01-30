from django.contrib import admin
from .models import Category, Book


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin pour les catégories"""
    list_display = ('name', 'get_books_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    
    def get_books_count(self, obj):
        """Nombre de livres dans la catégorie"""
        return obj.books.count()
    get_books_count.short_description = 'Nombre de livres'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin pour les livres"""
    list_display = ('title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'is_active', 'date_added')
    list_filter = ('category', 'is_active', 'date_added', 'language')
    search_fields = ('title', 'author', 'isbn')
    readonly_fields = ('date_added', 'updated_at')
    fieldsets = (
        ('Informations Principales', {
            'fields': ('title', 'author', 'isbn', 'category')
        }),
        ('Exemplaires', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Détails', {
            'fields': ('description', 'publisher', 'language', 'publication_date')
        }),
        ('Statut', {
            'fields': ('is_active', 'date_added', 'updated_at')
        }),
    )
    ordering = ('-date_added',)
    date_hierarchy = 'date_added'
    actions = ['mark_as_active', 'mark_as_inactive']

    def mark_as_active(self, request, queryset):
        """Action pour marquer les livres comme actifs"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} livre(s) marqué(s) comme actif(s).')
    mark_as_active.short_description = 'Marquer comme actif'

    def mark_as_inactive(self, request, queryset):
        """Action pour marquer les livres comme inactifs"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} livre(s) marqué(s) comme inactif(s).')
    mark_as_inactive.short_description = 'Marquer comme inactif'
