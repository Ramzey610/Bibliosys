from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Lecteur
from .forms import LecteurForm
from library.views import is_admin


class IsAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier si l'utilisateur est bibliothécaire"""
    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')


@login_required
def lecteur_list(request):
    """Liste des lecteurs (accessible uniquement au bibliothécaire)"""
    if not is_admin(request.user):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')
    
    lecteurs = Lecteur.objects.all()
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        lecteurs = lecteurs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(numero_abonnement__icontains=search)
        )
    
    # Filtrer par statut
    status = request.GET.get('status', '')
    if status:
        lecteurs = lecteurs.filter(statut=status)
    
    # Pagination
    paginator = Paginator(lecteurs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'lecteurs': page_obj.object_list,
        'members': page_obj.object_list,  # compatibilité avec les templates utilisant 'members'
        'search': search,
        'status': status,
    }
    
    return render(request, 'members/member_list.html', context)


@login_required
def lecteur_detail(request, pk):
    """Détail d'un lecteur"""
    lecteur = get_object_or_404(Lecteur, pk=pk)
    
    # Vérifier les permissions : un lecteur ne peut voir que son propre profil
    if not is_admin(request.user) and (not hasattr(request.user, 'lecteur') or request.user != lecteur.utilisateur):
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('library:book_list')
    
    # Récupérer les emprunts de ce lecteur
    active_loans = lecteur.loans.filter(status='EN_COURS')
    loan_history = lecteur.loans.filter(status__in=['RETOURNÉ', 'EN_RETARD'])
    
    context = {
        'lecteur': lecteur,
        'member': lecteur,  # compatibilité template (nombreux templates utilisent `member`)
        'active_loans': active_loans,
        'loan_history': loan_history,
    }
    
    return render(request, 'members/member_detail.html', context)


class LecteurCreateView(IsAdminMixin, CreateView):
    """Vue pour créer un lecteur (seulement le bibliothécaire)"""
    model = Lecteur
    form_class = LecteurForm
    template_name = 'members/member_form.html'
    success_url = reverse_lazy('members:member_list')

    def form_valid(self, form):
        # Si l'administrateur n'a pas fourni de numéro d'adhésion, le générer automatiquement
        if not form.instance.numero_abonnement:
            import time
            form.instance.numero_abonnement = f"MEM{int(time.time())}"

        created_user_info = None

        # Créer automatiquement un utilisateur lié (CustomUser) si pas fourni
        if not form.instance.utilisateur:
            from django.contrib.auth import get_user_model
            import secrets
            User = get_user_model()

            # Préférer un username fourni dans le formulaire sinon utiliser l'email
            base_username = form.cleaned_data.get('user_username') or (form.instance.email if form.instance.email else form.instance.numero_abonnement)
            username = base_username

            # Si l'admin a fourni un mot de passe dans le formulaire, l'utiliser après validation
            provided_password = form.cleaned_data.get('user_password')
            if provided_password:
                password = provided_password
            else:
                # Générer un mot de passe sûr (assez long pour passer les validateurs)
                password = secrets.token_urlsafe(12)

            # Essayer de créer l'utilisateur de façon robuste (retries si collision sur la contrainte unique)
            from django.db import IntegrityError
            import secrets as _secrets
            max_attempts = 6
            attempt = 0
            created = False
            user = None
            while not created and attempt < max_attempts:
                candidate = username if attempt == 0 else f"{username}-{_secrets.token_hex(3)}"
                if User.objects.filter(username=candidate).exists():
                    attempt += 1
                    continue
                try:
                    user = User.objects.create_user(
                        username=candidate,
                        email=form.instance.email or '',
                        first_name=form.instance.first_name,
                        last_name=form.instance.last_name,
                    )
                    user.role = 'lecteur'
                    user.set_password(password)
                    user.save()
                    created = True
                    username = candidate
                except IntegrityError:
                    attempt += 1

            if created:
                form.instance.utilisateur = user
                created_user_info = {'username': username, 'password': password}
            else:
                # Ne pas bloquer la création du Lecteur : sauvegarder le Lecteur sans utilisateur lié
                messages.error(self.request, "L'utilisateur lié n'a pas pu être créé après plusieurs tentatives. Le lecteur est enregistré sans compte utilisateur. Veuillez créer manuellement un compte pour lui.")

        # Avant de rediriger, ajouter les messages côté serveur (sauf pour AJAX qui gère sa propre réponse)
        from django.http import JsonResponse
        if not (self.request.headers.get('x-requested-with') == 'XMLHttpRequest'):
            if created_user_info:
                messages.success(self.request, f"Lecteur créé avec succès! Identifiants: {created_user_info['username']} / {created_user_info['password']} (connexion avec l'email)")
            else:
                messages.success(self.request, 'Lecteur créé avec succès!')

        # Sauvegarder le lecteur (redirige vers success_url)
        response = super().form_valid(form)

        # Réponse AJAX: retourner JSON avec identifiants ou message
        from django.http import JsonResponse
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if created_user_info:
                return JsonResponse({
                    'status': 'ok',
                    'username': created_user_info['username'],
                    'password': created_user_info['password'],
                    'member_url': self.object.get_absolute_url(),
                    'statut': self.object.statut,
                }, status=201)
            else:
                return JsonResponse({
                    'status': 'partial',
                    'message': "Lecteur créé sans compte utilisateur. Veuillez créer manuellement un compte pour ce lecteur.",
                    'member_url': self.object.get_absolute_url(),
                    'statut': self.object.statut,
                }, status=201)

        return response

    def form_invalid(self, form):
        # En cas d'erreur, si AJAX on renvoie les erreurs en JSON
        from django.http import JsonResponse
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)


class LecteurUpdateView(IsAdminMixin, UpdateView):
    """Vue pour modifier un lecteur (seulement le bibliothécaire)"""
    model = Lecteur
    form_class = LecteurForm
    template_name = 'members/member_form.html'
    success_url = reverse_lazy('members:member_list')

    def form_valid(self, form):
        """Mettre à jour le modèle Lecteur et gérer la création/mise à jour du compte utilisateur lié."""
        created_user_info = None
        user_username = form.cleaned_data.get('user_username')
        user_password = form.cleaned_data.get('user_password')

        if user_username or user_password:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            utilisateur = form.instance.utilisateur

            if utilisateur:
                # Mise à jour simple de l'utilisateur existant
                if user_username and utilisateur.username != user_username:
                    if User.objects.filter(username=user_username).exclude(pk=utilisateur.pk).exists():
                        form.add_error('user_username', 'Ce nom d\'utilisateur est déjà utilisé.')
                        return self.form_invalid(form)
                    utilisateur.username = user_username
                if user_password:
                    utilisateur.set_password(user_password)

                # Synchroniser quelques champs
                utilisateur.email = form.instance.email or utilisateur.email
                utilisateur.first_name = form.instance.first_name
                utilisateur.last_name = form.instance.last_name
                utilisateur.save()
            else:
                # Créer un utilisateur si aucun lié
                import secrets as _secrets
                from django.db import IntegrityError
                username_base = user_username or (form.instance.email or form.instance.numero_abonnement)
                username = username_base
                password = user_password or _secrets.token_urlsafe(12)

                max_attempts = 6
                attempt = 0
                created = False
                while not created and attempt < max_attempts:
                    candidate = username if attempt == 0 else f"{username}-{_secrets.token_hex(3)}"
                    if User.objects.filter(username=candidate).exists():
                        attempt += 1
                        continue
                    try:
                        utilisateur = User.objects.create_user(
                            username=candidate,
                            email=form.instance.email or '',
                            first_name=form.instance.first_name,
                            last_name=form.instance.last_name,
                        )
                        utilisateur.role = 'lecteur'
                        utilisateur.set_password(password)
                        utilisateur.save()
                        created = True
                        created_user_info = {'username': candidate, 'password': password}
                    except IntegrityError:
                        attempt += 1

                if created:
                    form.instance.utilisateur = utilisateur
                else:
                    messages.warning(self.request, "L'utilisateur lié n'a pas pu être créé automatiquement.")

        # Sauvegarder le lecteur
        response = super().form_valid(form)

        # Réponse AJAX
        from django.http import JsonResponse
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {'status': 'ok', 'member_url': self.object.get_absolute_url()}
            if created_user_info:
                data['created_user'] = created_user_info
            return JsonResponse(data)

        messages.success(self.request, 'Lecteur modifié avec succès!')
        return response


class LecteurDeleteView(IsAdminMixin, DeleteView):
    """Vue pour supprimer un lecteur (seulement le bibliothécaire)"""
    model = Lecteur
    template_name = 'members/member_confirm_delete.html'
    success_url = reverse_lazy('members:member_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lecteur supprimé avec succès!')
        return super().delete(request, *args, **kwargs)
