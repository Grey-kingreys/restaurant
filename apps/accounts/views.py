# apps/accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .forms import LoginForm, UserCreationForm, UserUpdateForm
from .models import User
from apps.accounts.decorators import admin_required


# ==========================================
# VUES EXISTANTES (Login/Logout)
# ==========================================

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


# ==========================================
# CRUD UTILISATEURS (Admin uniquement)
# ==========================================

@login_required
@admin_required
def user_list(request):
    """
    Liste de tous les utilisateurs
    Accessible uniquement par les administrateurs
    """
    # Récupérer tous les utilisateurs
    users = User.objects.all().order_by('-date_creation')
    
    # Filtres
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    statut_filter = request.GET.get('statut', '')
    if statut_filter == 'actif':
        users = users.filter(actif=True)
    elif statut_filter == 'inactif':
        users = users.filter(actif=False)
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(login__icontains=search_query)
        )
    
    # Statistiques par rôle
    stats = {
        'total': User.objects.count(),
        'actifs': User.objects.filter(actif=True).count(),
        'inactifs': User.objects.filter(actif=False).count(),
        'tables': User.objects.filter(role='Rtable').count(),
        'serveurs': User.objects.filter(role='Rserveur').count(),
        'cuisiniers': User.objects.filter(role='Rcuisinier').count(),
        'comptables': User.objects.filter(role='Rcomptable').count(),
        'admins': User.objects.filter(role='Radmin').count(),
    }
    
    context = {
        'users': users,
        'stats': stats,
        'role_filter': role_filter,
        'statut_filter': statut_filter,
        'search_query': search_query,
        'role_choices': User.ROLE_CHOICES,
    }
    
    return render(request, 'accounts/user_list.html', context)


@login_required
@admin_required
def user_create(request):
    """
    Créer un nouvel utilisateur
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f"✅ Utilisateur '{user.login}' créé avec succès ! "
                f"Rôle : {user.get_role_display()}"
            )
            return redirect('accounts:user_list')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'title': 'Créer un utilisateur',
        'button_text': 'Créer l\'utilisateur',
        'action': 'create',
    }
    
    return render(request, 'accounts/user_form.html', context)


@login_required
@admin_required
def user_detail(request, user_id):
    """
    Détail d'un utilisateur
    """
    user_obj = get_object_or_404(User, id=user_id)
    
    # Statistiques selon le rôle
    extra_stats = {}
    
    if user_obj.is_table():
        # Stats pour une table
        extra_stats = {
            'total_commandes': user_obj.commandes.count(),
            'commandes_en_attente': user_obj.commandes.filter(statut='en_attente').count(),
            'commandes_payees': user_obj.commandes.filter(statut='payee').count(),
            'montant_total': user_obj.commandes.filter(
                statut='payee'
            ).aggregate(total=Count('montant_total'))['total'] or 0,
        }
    
    elif user_obj.is_comptable():
        # Stats pour un comptable
        from apps.paiements.models import Depense
        extra_stats = {
            'depenses_enregistrees': Depense.objects.filter(
                enregistree_par=user_obj
            ).count(),
        }
    
    context = {
        'user_obj': user_obj,
        'extra_stats': extra_stats,
    }
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
@admin_required
def user_update(request, user_id):
    """
    Modifier un utilisateur existant
    """
    user_obj = get_object_or_404(User, id=user_id)
    
    # Empêcher la modification de son propre compte via cette interface
    if user_obj == request.user:
        messages.warning(
            request, 
            "⚠️ Vous ne pouvez pas modifier votre propre compte via cette interface. "
            "Utilisez la page de profil."
        )
        return redirect('accounts:user_detail', user_id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f"✅ Utilisateur '{user.login}' modifié avec succès !"
            )
            return redirect('accounts:user_detail', user_id=user.id)
    else:
        form = UserUpdateForm(instance=user_obj)
    
    context = {
        'form': form,
        'user_obj': user_obj,
        'title': f'Modifier : {user_obj.login}',
        'button_text': 'Enregistrer les modifications',
        'action': 'update',
    }
    
    return render(request, 'accounts/user_form.html', context)


@login_required
@admin_required
def user_toggle_status(request, user_id):
    """
    Activer/Désactiver un utilisateur
    """
    user_obj = get_object_or_404(User, id=user_id)
    
    # Empêcher la désactivation de son propre compte
    if user_obj == request.user:
        messages.error(
            request, 
            "❌ Vous ne pouvez pas désactiver votre propre compte !"
        )
        return redirect('accounts:user_list')
    
    # Inverser le statut
    user_obj.actif = not user_obj.actif
    user_obj.save()
    
    statut = "activé" if user_obj.actif else "désactivé"
    messages.success(
        request, 
        f"✅ Le compte '{user_obj.login}' a été {statut}"
    )
    
    return redirect('accounts:user_detail', user_id=user_id)


@login_required
@admin_required
def user_delete(request, user_id):
    """
    Supprimer un utilisateur
    Note : Confirmation requise
    """
    user_obj = get_object_or_404(User, id=user_id)
    
    # Empêcher la suppression de son propre compte
    if user_obj == request.user:
        messages.error(
            request, 
            "❌ Vous ne pouvez pas supprimer votre propre compte !"
        )
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        login_to_delete = user_obj.login
        user_obj.delete()
        messages.success(
            request, 
            f"✅ L'utilisateur '{login_to_delete}' a été supprimé définitivement"
        )
        return redirect('accounts:user_list')
    
    # Vérifier les dépendances
    dependencies = []
    
    if user_obj.is_table():
        commandes_count = user_obj.commandes.count()
        if commandes_count > 0:
            dependencies.append(f"{commandes_count} commande(s)")
    
    if user_obj.is_comptable():
        from apps.paiements.models import Depense
        depenses_count = Depense.objects.filter(enregistree_par=user_obj).count()
        if depenses_count > 0:
            dependencies.append(f"{depenses_count} dépense(s) enregistrée(s)")
    
    context = {
        'user_obj': user_obj,
        'dependencies': dependencies,
    }
    
    return render(request, 'accounts/user_delete_confirm.html', context)


@login_required
@admin_required
def user_reset_password(request, user_id):
    """
    Réinitialiser le mot de passe d'un utilisateur
    Génère un mot de passe temporaire
    """
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Générer un mot de passe temporaire
        import random
        import string
        
        # Mot de passe : 8 caractères avec lettres, chiffres et caractères spéciaux
        chars = string.ascii_letters + string.digits + "!@#$%"
        temp_password = ''.join(random.choice(chars) for _ in range(8))
        
        # Définir le nouveau mot de passe
        user_obj.set_password(temp_password)
        user_obj.save()
        
        messages.success(
            request, 
            f"✅ Mot de passe réinitialisé pour '{user_obj.login}'. "
            f"Nouveau mot de passe temporaire : {temp_password}"
        )
        
        return redirect('accounts:user_detail', user_id=user_id)
    
    context = {
        'user_obj': user_obj,
    }
    
    return render(request, 'accounts/user_reset_password_confirm.html', context)