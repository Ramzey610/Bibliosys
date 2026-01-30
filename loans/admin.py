from django.contrib import admin
from .models import Loan, LoanHistory


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin pour les emprunts (Emprunts = actions validées par le bibliothécaire)"""
    list_display = ('id', 'get_member_name', 'get_book_title', 'loan_date', 'due_date', 
                    'status', 'get_overdue_status', 'fine')
    list_filter = ('status', 'loan_date', 'due_date')
    search_fields = ('member__first_name', 'member__last_name', 'book__title', 'book__author')
    readonly_fields = ('loan_date', 'due_date')
    fieldsets = (
        ('Informations', {
            'fields': ('book', 'member', 'loan_date', 'due_date', 'return_date')
        }),
        ('Statut', {
            'fields': ('status', 'fine', 'notes')
        }),
    )
    ordering = ('-loan_date',)
    date_hierarchy = 'loan_date'
    actions = ['mark_as_returned', 'mark_as_overdue']

    def get_member_name(self, obj):
        """Affiche le nom du membre"""
        return obj.member.get_full_name()
    get_member_name.short_description = 'Membre'

    def get_book_title(self, obj):
        """Affiche le titre du livre"""
        return obj.book.title
    get_book_title.short_description = 'Livre'

    def get_overdue_status(self, obj):
        """Affiche le statut de retard"""
        return '⚠️ En retard' if obj.is_overdue() else 'OK'
    get_overdue_status.short_description = 'Retard'

    def mark_as_returned(self, request, queryset):
        """Action pour marquer comme retourné"""
        updated = queryset.filter(status='EN_COURS').update(status='RETOURNÉ')
        self.message_user(request, f'{updated} emprunt(s) marqué(s) comme retourné(s).')
    mark_as_returned.short_description = 'Marquer comme retourné'

    def mark_as_overdue(self, request, queryset):
        """Action pour marquer comme en retard"""
        updated = queryset.filter(status='EN_COURS').update(status='EN_RETARD')
        self.message_user(request, f'{updated} emprunt(s) marqué(s) comme en retard.')
    mark_as_overdue.short_description = 'Marquer comme en retard'


@admin.register(LoanHistory)
class LoanHistoryAdmin(admin.ModelAdmin):
    """Admin pour l'historique des emprunts"""
    list_display = ('id', 'member', 'book', 'loan_date', 'return_date', 'status', 'fine', 'created_at')
    list_filter = ('status', 'loan_date', 'return_date', 'created_at')
    search_fields = ('member__first_name', 'member__last_name', 'book__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'loan_date'
    ordering = ('-loan_date',)

    def has_add_permission(self, request):
        """Empêcher l'ajout manuel"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permettre la suppression"""
        return True


# Enregistrement des Demandes (actions séparées)
from .models import DemandeEmprunt, DemandeRetour


@admin.register(DemandeEmprunt)
class DemandeEmpruntAdmin(admin.ModelAdmin):
    """Admin pour valider/refuser les demandes d'emprunt"""
    list_display = ('id', 'lecteur', 'livre', 'date_demande', 'statut', 'valide_par', 'date_validation')
    list_filter = ('statut', 'date_demande')
    search_fields = ('lecteur__first_name', 'lecteur__last_name', 'livre__title')
    readonly_fields = ('date_demande', 'date_validation', 'valide_par')


@admin.register(DemandeRetour)
class DemandeRetourAdmin(admin.ModelAdmin):
    """Admin pour valider/refuser les demandes de retour"""
    list_display = ('id', 'lecteur', 'emprunt', 'date_demande', 'statut', 'valide_par', 'date_validation')
    list_filter = ('statut', 'date_demande')
    search_fields = ('lecteur__first_name', 'lecteur__last_name', 'emprunt__book__title')
    readonly_fields = ('date_demande', 'date_validation', 'valide_par')
