from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm


def register(request):
    """Désactivation de l'inscription publique

    Selon les règles fonctionnelles, un lecteur ne peut pas s'inscrire seul.
    Seul le bibliothécaire peut créer des comptes lecteurs. Cette vue redirige
    et affiche un message informatif.
    """
    messages.error(request, "L'inscription publique est désactivée. Contactez un bibliothécaire.")
    return redirect('accounts:login')


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('library:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'library:dashboard')
                return redirect(next_url)
        else:
            # Si le formulaire est invalide, vérifier si le nom d'utilisateur existe et si le
            # compte est désactivé via le champ `is_active` ou le statut du Lecteur lié.
            username = request.POST.get('username', '').strip()
            if username:
                try:
                    user_obj = CustomUser.objects.filter(username=username).first()
                except Exception:
                    user_obj = None

                if user_obj and not user_obj.is_active:
                    # Préférer afficher le statut du Lecteur s'il existe
                    statut = None
                    try:
                        statut = getattr(user_obj.lecteur, 'statut', None)
                    except Exception:
                        statut = None
                    if statut:
                        # Messages plus conviviaux selon le statut
                        if statut == 'suspended':
                            messages.error(request, "Votre compte est actuellement suspendu. Contactez un administrateur pour plus d'informations.")
                        elif statut == 'inactive':
                            messages.error(request, "Votre compte est temporairement inactif. Contactez un administrateur pour le réactiver.")
                        else:
                            messages.error(request, "Votre compte est désactivé. Contactez un administrateur pour assistance.")
                    else:
                        messages.error(request, "Votre compte est désactivé. Contactez un administrateur pour assistance.")
                else:
                    # Si le compte est actif ou l'utilisateur inexistant, ne rien divulguer (les erreurs
                    # du formulaire seront affichées normalement) -- pas d'action requise
                    pass
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous êtes déconnecté.')
    return redirect('accounts:login')


@login_required
def profile(request):
    """Vue du profil utilisateur"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})
