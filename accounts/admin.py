from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin personnalisé pour les utilisateurs"""
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_librarian', 'is_active')
    list_filter = ('role', 'is_librarian', 'is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Supplémentaires', {
            'fields': ('role', 'phone', 'address', 'is_librarian')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Supplémentaires', {
            'fields': ('role', 'phone', 'is_librarian')
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
