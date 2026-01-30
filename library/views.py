from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Book, Category
from .forms import BookForm, CategoryForm, BookSearchForm
from loans.models import Loan


def is_admin(user):
    """Vérifie si l'utilisateur est bibliothécaire"""
    return user.is_staff or user.is_superuser or user.role == 'admin'


def is_lecteur(user):
    """Vérifie si l'utilisateur est lecteur"""
    return hasattr(user, 'lecteur') and user.role == 'lecteur'


class IsAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier si l'utilisateur est admin"""
    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')


@login_required
def dashboard(request):
    """Tableau de bord principal"""
    context = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(available_copies__gt=0).count(),
        'unavailable_books': Book.objects.filter(available_copies=0).count(),
        'active_loans': Loan.objects.filter(status='EN_COURS').count(),
        'overdue_loans': Loan.objects.filter(status='EN_RETARD').count(),
    }
    
    if is_admin(request.user):
        # Dashboard admin (accessible uniquement au bibliothécaire)
        from members.models import Lecteur
        context.update({
            'total_lecteurs': Lecteur.objects.filter(statut='active').count(),
            'total_lecteurs_total': Lecteur.objects.count(),
            'recent_loans': Loan.objects.select_related('book', 'member')[:10],
            'categories_count': Category.objects.count(),
            'active_categories': Category.objects.filter(books__is_active=True).distinct().count(),
        })
        return render(request, 'library/admin_dashboard.html', context)
    else:
        # Pas de dashboard administrateur pour le lecteur, on affiche son espace de lecture
        user_loans = request.user.lecteur.loans.filter(status='EN_COURS') if hasattr(request.user, 'lecteur') else Loan.objects.none()
        context['user_loans'] = user_loans
        return render(request, 'library/reader_dashboard.html', context)


@login_required
def book_list(request):
    """Liste des livres avec recherche et filtrage"""
    books = Book.objects.filter(is_active=True)
    
    form = BookSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        availability = form.cleaned_data.get('availability')
        
        if search:
            books = books.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(isbn__icontains=search)
            )
        
        if category:
            books = books.filter(category=category)
        
        if availability == 'available':
            books = books.filter(available_copies__gt=0)
        elif availability == 'unavailable':
            books = books.filter(available_copies=0)
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'books': page_obj.object_list,
        'form': form,
        'total_books': books.count(),
    }
    
    return render(request, 'library/book_list.html', context)


def book_detail(request, pk):
    """Détail d'un livre (publique)"""
    book = get_object_or_404(Book, pk=pk)
    
    # Récupérer les emprunts de ce livre
    loans = book.loans.all()[:5]
    
    context = {
        'book': book,
        'recent_loans': loans,
    }
    
    return render(request, 'library/book_detail.html', context)


class BookCreateView(IsAdminMixin, CreateView):
    """Vue pour créer un livre"""
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        messages.success(self.request, 'Livre créé avec succès!')
        return super().form_valid(form)


class BookUpdateView(IsAdminMixin, UpdateView):
    """Vue pour modifier un livre"""
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        messages.success(self.request, 'Livre modifié avec succès!')
        return super().form_valid(form)


class BookDeleteView(IsAdminMixin, DeleteView):
    """Vue pour supprimer un livre"""
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:book_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Livre supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


class CategoryCreateView(IsAdminMixin, CreateView):
    """Vue pour créer une catégorie"""
    model = Category
    form_class = CategoryForm
    template_name = 'library/category_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie créée avec succès!')
        return super().form_valid(form)


class CategoryUpdateView(IsAdminMixin, UpdateView):
    """Vue pour modifier une catégorie"""
    model = Category
    form_class = CategoryForm
    template_name = 'library/category_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie modifiée avec succès!')
        return super().form_valid(form)


class CategoryDeleteView(IsAdminMixin, DeleteView):
    """Vue pour supprimer une catégorie"""
    model = Category
    template_name = 'library/category_confirm_delete.html'
    success_url = reverse_lazy('library:book_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Catégorie supprimée avec succès!')
        return super().delete(request, *args, **kwargs)


@login_required
def category_list(request):
    """Liste des catégories"""
    categories = Category.objects.all()
    
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': page_obj.object_list,
    }
    
    return render(request, 'library/category_list.html', context)
