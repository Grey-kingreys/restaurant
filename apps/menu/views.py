from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Plat
from .forms import PlatForm, PlatSearchForm


# ==========================================
# VUES POUR LES TABLES (Rtable)
# ==========================================

@login_required
def plat_list_table(request):
    """
    Liste des plats disponibles pour les tables
    Accessible uniquement par les utilisateurs avec rôle Rtable
    """
    if not request.user.is_table():
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    # Récupérer uniquement les plats disponibles
    plats = Plat.disponibles.all()
    
    # Filtre par catégorie
    categorie_filter = request.GET.get('categorie', '')
    if categorie_filter:
        plats = plats.filter(categorie=categorie_filter)
    
    # Recherche
    search_query = request.GET.get('recherche', '')
    if search_query:
        plats = plats.filter(
            Q(nom__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Formulaire de recherche
    search_form = PlatSearchForm(request.GET)
    
    context = {
        'plats': plats,
        'search_form': search_form,
        'total_plats': plats.count(),
        'categories': Plat.CATEGORIE_CHOICES,
        'categorie_active': categorie_filter,
    }
    
    return render(request, 'menu/plat_list_table.html', context)


@login_required
def plat_detail_table(request, pk):
    """
    Détail d'un plat pour les tables
    """
    if not request.user.is_table():
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    plat = get_object_or_404(Plat, pk=pk, disponible=True)
    
    context = {
        'plat': plat,
    }
    
    return render(request, 'menu/plat_detail_table.html', context)


# ==========================================
# VUES POUR LES CUISINIERS (Rcuisinier)
# ==========================================

@login_required
def plat_list_cuisinier(request):
    """
    Liste de tous les plats pour le cuisinier
    Accessible uniquement par les utilisateurs avec rôle Rcuisinier ou Radmin
    """
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    # Récupérer tous les plats (disponibles et non disponibles)
    plats = Plat.objects.all()
    
    # Filtre par catégorie
    categorie_filter = request.GET.get('categorie', '')
    if categorie_filter:
        plats = plats.filter(categorie=categorie_filter)
    
    # Filtre par disponibilité
    disponible_filter = request.GET.get('disponible', '')
    if disponible_filter == '1':
        plats = plats.filter(disponible=True)
    elif disponible_filter == '0':
        plats = plats.filter(disponible=False)
    
    # Recherche
    search_query = request.GET.get('recherche', '')
    if search_query:
        plats = plats.filter(
            Q(nom__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Formulaire de recherche
    search_form = PlatSearchForm(request.GET)
    
    # Statistiques
    stats = {
        'total': Plat.objects.count(),
        'disponibles': Plat.objects.filter(disponible=True).count(),
        'non_disponibles': Plat.objects.filter(disponible=False).count(),
    }
    
    context = {
        'plats': plats,
        'search_form': search_form,
        'stats': stats,
        'categories': Plat.CATEGORIE_CHOICES,
    }
    
    return render(request, 'menu/plat_list_cuisinier.html', context)


@login_required
def plat_create(request):
    """
    Créer un nouveau plat
    """
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES)
        if form.is_valid():
            plat = form.save()
            messages.success(request, f"✅ Le plat '{plat.nom}' a été créé avec succès!")
            return redirect('menu:cuisinier_list')
    else:
        form = PlatForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un nouveau plat',
        'button_text': 'Créer le plat',
    }
    
    return render(request, 'menu/plat_form.html', context)


@login_required
def plat_update(request, pk):
    """
    Modifier un plat existant
    """
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    plat = get_object_or_404(Plat, pk=pk)
    
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            plat = form.save()
            messages.success(request, f"✅ Le plat '{plat.nom}' a été modifié avec succès!")
            return redirect('menu:cuisinier_list')
    else:
        form = PlatForm(instance=plat)
    
    context = {
        'form': form,
        'plat': plat,
        'title': f'Modifier: {plat.nom}',
        'button_text': 'Enregistrer les modifications',
    }
    
    return render(request, 'menu/plat_form.html', context)


@login_required
def plat_toggle_disponibilite(request, pk):
    """
    Activer/Désactiver un plat
    Note: Pas de suppression selon le cahier des charges
    """
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    plat = get_object_or_404(Plat, pk=pk)
    
    # Inverser la disponibilité
    plat.disponible = not plat.disponible
    plat.save()
    
    statut = "disponible" if plat.disponible else "non disponible"
    messages.success(request, f"✅ Le plat '{plat.nom}' est maintenant {statut}")
    
    return redirect('menu:cuisinier_list')


@login_required
def plat_detail_cuisinier(request, pk):
    """
    Détail d'un plat pour le cuisinier
    """
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.warning(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    plat = get_object_or_404(Plat, pk=pk)
    
    context = {
        'plat': plat,
    }
    
    return render(request, 'menu/plat_detail_cuisinier.html', context)