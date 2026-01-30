from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Loan, DemandeEmprunt, DemandeRetour
from library.models import Book
from members.models import Lecteur


class LoanForm(forms.ModelForm):
    """Formulaire interne pour créer un emprunt (utilisé par le bibliothécaire).

    Note: Selon l'UML, les emprunts effectifs sont créés uniquement après validation
    d'une `DemandeEmprunt`. Ce formulaire reste uniquement pour usages internes si
    nécessaire (restreint aux bibliothécaires).
    """
    class Meta:
        model = Loan
        fields = ('book', 'member', 'due_date')
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'member': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les livres disponibles
        self.fields['book'].queryset = Book.objects.filter(is_active=True, available_copies__gt=0)
        # Filtrer les lecteurs actifs
        self.fields['member'].queryset = Lecteur.objects.filter(is_active=True)
        # Définir la date d'échéance par défaut
        self.fields['due_date'].initial = timezone.now() + timedelta(days=28)

    def clean(self):
        """Validation du formulaire"""
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        
        if book and not book.is_available():
            raise forms.ValidationError("Ce livre n'est pas disponible.")
        
        due_date = cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError("La date d'échéance ne peut pas être dans le passé.")
        
        return cleaned_data


class DemandeEmpruntForm(forms.ModelForm):
    """Formulaire pour que le lecteur crée une demande d'emprunt"""
    class Meta:
        model = DemandeEmprunt
        fields = ('livre', 'commentaire')
        widgets = {
            'livre': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['livre'].queryset = Book.objects.filter(is_active=True)


class DemandeRetourForm(forms.ModelForm):
    """Formulaire pour que le lecteur demande le retour d'un emprunt"""
    class Meta:
        model = DemandeRetour
        fields = ('emprunt', 'commentaire')
        widgets = {
            'emprunt': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, lecteur=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter les emprunts sélectionnables à ceux du lecteur et en cours
        if lecteur is not None:
            self.fields['emprunt'].queryset = Loan.objects.filter(member=lecteur, status='EN_COURS')
        else:
            self.fields['emprunt'].queryset = Loan.objects.none()


class ReturnLoanForm(forms.Form):
    """Formulaire pour retourner un livre"""
    return_date = forms.DateTimeField(
        label='Date de retour',
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    notes = forms.CharField(
        label='Remarques (optionnel)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )


class LoanSearchForm(forms.Form):
    """Formulaire de recherche d'emprunts"""
    STATUS_CHOICES = [
        ('', 'Tous les statuts'),
        ('EN_COURS', 'En cours'),
        ('RETOURNÉ', 'Retourné'),
        ('EN_RETARD', 'En retard'),
    ]
    
    search = forms.CharField(
        label='Chercher par nom de membre ou titre de livre',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, titre...'
        })
    )
    status = forms.ChoiceField(
        label='Statut',
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        label='Trier par',
        choices=[
            ('loan_date', 'Date d\'emprunt'),
            ('due_date', 'Date d\'échéance'),
            ('-fine', 'Amende (plus élevée d\'abord)'),
        ],
        initial='loan_date',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ReturnLoanForm(forms.Form):
    """Formulaire pour retourner un livre"""
    return_date = forms.DateTimeField(
        label='Date de retour',
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    notes = forms.CharField(
        label='Remarques (optionnel)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )


class LoanSearchForm(forms.Form):
    """Formulaire de recherche d'emprunts"""
    STATUS_CHOICES = [
        ('', 'Tous les statuts'),
        ('EN_COURS', 'En cours'),
        ('RETOURNÉ', 'Retourné'),
        ('EN_RETARD', 'En retard'),
    ]
    
    search = forms.CharField(
        label='Chercher par nom de membre ou titre de livre',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, titre...'
        })
    )
    status = forms.ChoiceField(
        label='Statut',
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        label='Trier par',
        choices=[
            ('loan_date', 'Date d\'emprunt'),
            ('due_date', 'Date d\'échéance'),
            ('-fine', 'Amende (plus élevée d\'abord)'),
        ],
        initial='loan_date',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
