from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Loan, LoanHistory, DemandeEmprunt, DemandeRetour
from .forms import LoanForm, ReturnLoanForm, LoanSearchForm, DemandeEmpruntForm, DemandeRetourForm
from library.models import Book
from members.models import Lecteur
from library.views import is_admin
from django.utils import timezone


class IsAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier si l'utilisateur est bibliothécaire"""
    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')


@login_required
def loan_list(request):
    """Liste des emprunts (accessible uniquement au bibliothécaire)"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')
    
    loans = Loan.objects.select_related('book', 'member').all()
    
    form = LoanSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        sort_by = form.cleaned_data.get('sort_by') or 'loan_date'
        
        if search:
            loans = loans.filter(
                Q(member__first_name__icontains=search) |
                Q(member__last_name__icontains=search) |
                Q(book__title__icontains=search) |
                Q(book__author__icontains=search)
            )
        
        if status:
            loans = loans.filter(status=status)
        
        if sort_by:
            loans = loans.order_by(sort_by)
    else:
        loans = loans.order_by('-loan_date')
    
    # Pagination
    paginator = Paginator(loans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'loans': page_obj.object_list,
        'form': form,
    }
    
    return render(request, 'loans/loan_list.html', context)


@login_required
def loan_detail(request, pk):
    """Détail d'un emprunt (visible par tout utilisateur authentifié; actions conditionnelles)"""
    loan = get_object_or_404(Loan, pk=pk)

    # Définir un flag indiquant si l'utilisateur peut créer une demande de retour
    can_request_return = False
    if request.user.is_authenticated and hasattr(request.user, 'lecteur') and request.user == loan.member.utilisateur:
        can_request_return = True

    context = {
        'loan': loan,
        'can_request_return': can_request_return,
    }

    return render(request, 'loans/loan_detail.html', context)


# Selon l'UML, les emprunts ne doivent pas être créés directement par le lecteur.
# Ils ne sont créés que lorsque le bibliothécaire valide une DemandeEmprunt.
# La vue de création d'emprunt par formulaire a été volontairement retirée pour éviter
# tout raccourci logique.


@login_required
def demande_emprunt(request):
    """Le lecteur crée une demande d'emprunt (EN_ATTENTE). Peut être pré-remplie depuis la page livre."""
    if not hasattr(request.user, 'lecteur'):
        messages.error(request, 'Vous devez être enregistré en tant que lecteur pour faire une demande.')
        return redirect('library:book_list')

    lecteur = request.user.lecteur

    # Si on reçoit un paramètre livre pour préselection
    livre_id = request.GET.get('livre') or request.GET.get('livre_id')
    initial = {}
    if livre_id:
        try:
            livre_obj = Book.objects.get(pk=livre_id)
            initial['livre'] = livre_obj
        except Book.DoesNotExist:
            livre_obj = None
            initial = {}

    if request.method == 'POST':
        form = DemandeEmpruntForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.lecteur = lecteur

            # Empêcher les doublons : une même demande EN_ATTENTE pour le même livre
            existe = DemandeEmprunt.objects.filter(lecteur=lecteur, livre=demande.livre, statut='EN_ATTENTE').exists()
            if existe:
                # Support AJAX: retourner une réponse JSON appropriée
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'exists', 'message': 'Vous avez déjà une demande en attente pour ce livre.'}, status=400)
                messages.warning(request, 'Vous avez déjà une demande en attente pour ce livre.')
                return redirect('library:book_detail', pk=demande.livre.pk)

            demande.save()
            # Support AJAX: retourner une réponse JSON plutôt que rediriger
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'status': 'ok', 'message': "Demande d'emprunt créée. Elle est en attente de validation."}, status=201)

            messages.success(request, 'Demande d\'emprunt créée. Elle est en attente de validation.')
            return redirect('loans:my_loans')
    else:
        form = DemandeEmpruntForm(initial=initial)

    context = {'form': form, 'livre': initial.get('livre')}
    return render(request, 'loans/demande_emprunt_form.html', context)


@login_required
def liste_demandes_emprunt(request):
    """Liste des demandes d'emprunt (bibliothécaire)"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')

    demandes = DemandeEmprunt.objects.select_related('livre', 'lecteur').all()

    # Filtrage
    status = request.GET.get('status', '')
    if status:
        demandes = demandes.filter(statut=status)

    paginator = Paginator(demandes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'demandes': page_obj.object_list}
    return render(request, 'loans/demandes_emprunt_list.html', context)


@login_required
def valider_demande_emprunt(request, pk, decision):
    """Valider ou refuser une demande d'emprunt (bibliothécaire)"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour effectuer cette action.')
        return redirect('library:book_list')

    demande = get_object_or_404(DemandeEmprunt, pk=pk)

    if decision == 'valider':
        result = demande.valider(request.user)
        if not result:
            messages.error(request, 'La demande ne peut pas être validée (livre indisponible).')
        else:
            messages.success(request, 'Demande validée et emprunt créé.')
    else:
        demande.statut = 'REFUSE'
        demande.valide_par = request.user
        demande.date_validation = timezone.now()
        demande.save()
        messages.success(request, 'Demande refusée.')

    return redirect('loans:liste_demandes_emprunt')


@login_required
def demande_retour(request):
    """Le lecteur crée une demande de retour pour un emprunt en cours. Peut être pré-remplie depuis la page emprunt."""
    if not hasattr(request.user, 'lecteur'):
        messages.error(request, 'Vous devez être enregistré en tant que lecteur pour faire une demande.')
        return redirect('library:book_list')

    lecteur = request.user.lecteur

    emprunt_id = request.GET.get('emprunt') or request.GET.get('loan')

    if request.method == 'POST':
        form = DemandeRetourForm(lecteur=lecteur, data=request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.lecteur = lecteur

            # Empêcher doublon de demande de retour pour le même emprunt
            existe = DemandeRetour.objects.filter(lecteur=lecteur, emprunt=demande.emprunt, statut='EN_ATTENTE').exists()
            if existe:
                messages.warning(request, 'Vous avez déjà une demande de retour en attente pour cet emprunt.')
                return redirect('loans:loan_detail', pk=demande.emprunt.pk)

            demande.save()
            messages.success(request, 'Demande de retour créée. Elle est en attente de validation.')
            return redirect('loans:my_loans')
    else:
        emprunt = None
        if emprunt_id:
            try:
                emprunt = Loan.objects.get(pk=emprunt_id, member=lecteur, status='EN_COURS')
                form = DemandeRetourForm(lecteur=lecteur, initial={'emprunt': emprunt})
            except Loan.DoesNotExist:
                emprunt = None
                form = DemandeRetourForm(lecteur=lecteur)
        else:
            form = DemandeRetourForm(lecteur=lecteur)

    context = {'form': form, 'emprunt': emprunt}
    return render(request, 'loans/demande_retour_form.html', context)


@login_required
def liste_demandes_retour(request):
    """Liste des demandes de retour (bibliothécaire)"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')

    demandes = DemandeRetour.objects.select_related('emprunt', 'lecteur').all()

    # Filtrage
    status = request.GET.get('status', '')
    if status:
        demandes = demandes.filter(statut=status)

    paginator = Paginator(demandes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'demandes': page_obj.object_list}
    return render(request, 'loans/demandes_retour_list.html', context)


@login_required
def valider_demande_retour(request, pk, decision):
    """Valider ou refuser une demande de retour (bibliothécaire)"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour effectuer cette action.')
        return redirect('library:book_list')

    demande = get_object_or_404(DemandeRetour, pk=pk)

    if decision == 'valider':
        demande.valider(request.user)
        messages.success(request, 'Demande de retour validée et emprunt clôturé.')
    else:
        demande.statut = 'REFUSE'
        demande.valide_par = request.user
        demande.date_validation = timezone.now()
        demande.save()
        messages.success(request, 'Demande de retour refusée.')

    return redirect('loans:liste_demandes_retour')


@login_required
def my_loans(request):
    """Mes emprunts (pour lecteur)"""
    try:
        lecteur = request.user.lecteur
    except:
        messages.error(request, 'Vous n\'êtes pas enregistré en tant que lecteur.')
        return redirect('library:book_list')
    
    active_loans = lecteur.loans.filter(status='EN_COURS')
    returned_loans = lecteur.loans.filter(status__in=['RETOURNÉ', 'EN_RETARD'])
    
    context = {
        'active_loans': active_loans,
        'returned_loans': returned_loans,
    }
    
    return render(request, 'loans/my_loans.html', context)


@login_required
def loan_history(request):
    """Historique des emprunts"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')
    
    history = LoanHistory.objects.select_related('book', 'member').all()
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        history = history.filter(
            Q(member__first_name__icontains=search) |
            Q(member__last_name__icontains=search) |
            Q(book__title__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(history, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'history': page_obj.object_list,
        'search': search,
    }
    
    return render(request, 'loans/loan_history.html', context)
