from django import forms
from .models import Book, Category


class CategoryForm(forms.ModelForm):
    """Formulaire de catégorie"""
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BookForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier des livres"""
    class Meta:
        model = Book
        fields = ('title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 
                  'publication_date', 'description', 'publisher', 'language', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du livre'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auteur'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Éditeur'}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Langue'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BookSearchForm(forms.Form):
    """Formulaire de recherche de livres"""
    search = forms.CharField(
        label='Rechercher',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Titre, auteur, ISBN...'
        })
    )
    category = forms.ModelChoiceField(
        label='Catégorie',
        queryset=Category.objects.all(),
        required=False,
        empty_label='Toutes les catégories',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    availability = forms.ChoiceField(
        label='Disponibilité',
        choices=[
            ('', 'Tous'),
            ('available', 'Disponibles'),
            ('unavailable', 'Indisponibles'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
