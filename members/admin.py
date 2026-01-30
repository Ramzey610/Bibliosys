from django.contrib import admin
from django import forms
from django.contrib import messages
from django.utils.crypto import get_random_string
from .models import Lecteur


class LecteurAdminForm(forms.ModelForm):
    """Formulaire admin pour Lecteur : permet de renseigner un utilisateur (login) et mot de passe."""
    user_username = forms.CharField(required=False, label="Nom d'utilisateur (optionnel)")
    user_password = forms.CharField(required=False, label="Mot de passe (optionnel)", widget=forms.PasswordInput)
    user_confirm_password = forms.CharField(required=False, label="Confirmer le mot de passe", widget=forms.PasswordInput)

    class Meta:
        model = Lecteur
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        up = cleaned.get('user_password')
        cp = cleaned.get('user_confirm_password')
        if up or cp:
            if up != cp:
                raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return cleaned


@admin.register(Lecteur)
class LecteurAdmin(admin.ModelAdmin):
    """Admin pour les Lecteurs"""
    form = LecteurAdminForm
    list_display = ('numero_abonnement', 'get_full_name', 'email', 'phone', 'statut', 'is_active', 'date_inscription', 'utilisateur_link')
    list_filter = ('statut', 'is_active', 'date_inscription')
    search_fields = ('first_name', 'last_name', 'email', 'numero_abonnement')
    readonly_fields = ('date_inscription', 'derniere_activite')
    fieldsets = (
        ('Utilisateur lié', {
            'fields': ('utilisateur', 'user_username', 'user_password', 'user_confirm_password')
        }),
        ('Informations Personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Adhésion', {
            'fields': ('numero_abonnement', 'date_inscription', 'derniere_activite', 'statut', 'is_active')
        }),
        ('Remarques', {
            'fields': ('remarques',)
        }),
    )
    ordering = ('-date_inscription',)
    date_hierarchy = 'date_inscription'
    actions = ['mark_as_active', 'mark_as_inactive', 'suspend_lecteur']

    def get_full_name(self, obj):
        """Affiche le nom complet"""
        return obj.get_full_name()
    get_full_name.short_description = 'Nom Complet'

    def utilisateur_link(self, obj):
        if obj.utilisateur:
            return obj.utilisateur.username
        return ''
    utilisateur_link.short_description = 'Utilisateur (login)'

    def mark_as_active(self, request, queryset):
        """Action pour activer les lecteurs"""
        updated = queryset.update(statut='active', is_active=True)
        self.message_user(request, f'{updated} lecteur(s) activé(s).')
    mark_as_active.short_description = 'Marquer comme actif'

    def mark_as_inactive(self, request, queryset):
        """Action pour désactiver les lecteurs"""
        updated = queryset.update(statut='inactive', is_active=False)
        self.message_user(request, f'{updated} lecteur(s) désactivé(s).')
    mark_as_inactive.short_description = 'Marquer comme inactif'

    def suspend_lecteur(self, request, queryset):
        """Action pour suspendre les lecteurs"""
        updated = queryset.update(statut='suspended', is_active=False)
        self.message_user(request, f'{updated} lecteur(s) suspendu(s).')
    suspend_lecteur.short_description = 'Suspendre le lecteur'

    def save_model(self, request, obj, form, change):
        """Créer un utilisateur lié automatiquement si l'objet Lecteur n'en a pas, ou appliquer le mot de passe fourni"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Si l'admin a fourni explicitement un utilisateur lié via l'id, respecter/mettre à jour
        if form.cleaned_data.get('utilisateur'):
            obj.utilisateur = form.cleaned_data.get('utilisateur')
        # Si pas d'utilisateur lié, tenter de lier par email
        if not obj.utilisateur:
            linked_user = None
            if obj.email:
                linked_user = User.objects.filter(email__iexact=obj.email).first()

            if linked_user:
                obj.utilisateur = linked_user

        # Si toujours pas d'utilisateur lié, créer un compte (ou utiliser username fourni)
        if not obj.utilisateur:
            # Utiliser l'email complet comme nom d'utilisateur si disponible, sinon fallback sur user_username/numero
            base_username = None
            if form.cleaned_data.get('user_username'):
                base_username = form.cleaned_data.get('user_username')
            elif obj.email:
                base_username = obj.email  # on utilise l'email complet comme username pour permettre la connexion par mail
            else:
                base_username = obj.numero_abonnement

            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                # si collision (rare avec email), ajouter un suffixe
                username = f"{base_username}{suffix}"
                suffix += 1

            password = form.cleaned_data.get('user_password') or get_random_string(12)

            # Créer l'utilisateur de façon robuste (retenter si collision unique)
            from django.db import IntegrityError
            max_attempts = 5
            attempt = 0
            created = False
            user = None
            while not created and attempt < max_attempts:
                try:
                    user = User.objects.create(
                        username=username,
                        email=obj.email or '',
                        first_name=obj.first_name,
                        last_name=obj.last_name,
                        is_active=obj.is_active,
                    )
                    user.set_password(password)
                    if hasattr(user, 'role'):
                        user.role = 'lecteur'
                    user.save()
                    created = True
                except IntegrityError:
                    attempt += 1
                    username = f"{base_username}{attempt}"

            if not created:
                self.message_user(request, 'Échec de création de l\'utilisateur lié après plusieurs tentatives.', level=messages.ERROR)
            else:
                obj.utilisateur = user
                # Informer l'admin des identifiants une seule fois (connexion par email possible si l'email est utilisé comme username)
                self.message_user(request, f"Lecteur créé. Identifiants: {username} / {password} (connexion via email possible)")
        else:
            # Si l'admin a fourni un mot de passe pour l'utilisateur lié
            pwd = form.cleaned_data.get('user_password')
            if pwd and obj.utilisateur:
                obj.utilisateur.set_password(pwd)
                obj.utilisateur.save()
                self.message_user(request, "Mot de passe mis à jour pour l'utilisateur lié.")

        super().save_model(request, obj, form, change)
