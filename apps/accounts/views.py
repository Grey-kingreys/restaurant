from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm

def login_view(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.actif:
                    login(request, user)
                    messages.success(request, f"Bienvenue {user.login} !")
                    return redirect('dashboard:index')
                else:
                    messages.error(request, "Votre compte est désactivé. Contactez l'administrateur.")
            else:
                messages.error(request, "Login ou mot de passe incorrect. Veuillez réessayer.")
        else:
            # Si le formulaire n'est pas valide (erreurs de validation)
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """
    Redirection vers le dashboard principal
    Cette vue existe pour compatibilité mais redirige vers dashboard:index
    """
    return redirect('dashboard:index')