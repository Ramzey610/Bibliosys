from django import forms
from .models import Lecteur


class LecteurForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier des lecteurs (géré par le bibliothécaire)

    Le champ `numero_abonnement` est facultatif dans le formulaire : il sera
    automatiquement généré si l'admin le laisse vide.

    Le formulaire expose aussi des champs optionnels que l'administrateur
    peut renseigner pour créer directement le compte utilisateur lié :
    - `user_username` : nom d'utilisateur (optionnel, sinon on utilise l'email)
    - `user_password` / `user_confirm_password` : mot de passe (optionnel)
    """

    user_username = forms.CharField(required=False, label="Nom d'utilisateur (optionnel)")
    user_password = forms.CharField(required=False, label='Mot de passe (optionnel)', widget=forms.PasswordInput)
    user_confirm_password = forms.CharField(required=False, label='Confirmer le mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = Lecteur
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 
                  'numero_abonnement', 'statut', 'is_active', 'remarques')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'numero_abonnement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro d\'adhésion'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarques': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permettre à l'admin de laisser vide `numero_abonnement` et le générer ensuite
        self.fields['numero_abonnement'].required = False

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('user_password')
        cpwd = cleaned.get('user_confirm_password')
        if pwd or cpwd:
            if pwd != cpwd:
                raise forms.ValidationError('Les mots de passe ne correspondent pas.')
            # valider la robustesse du mot de passe selon les validateurs de Django
            from django.contrib.auth import password_validation
            try:
                password_validation.validate_password(pwd)
            except forms.ValidationError as e:
                raise forms.ValidationError({'user_password': e.messages})
        return cleaned
