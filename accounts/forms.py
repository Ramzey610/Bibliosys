from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Formulaire de création d'utilisateur"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    phone = forms.CharField(
        label='Téléphone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification de profil"""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
