# apps/restaurant/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from apps.accounts.models import User
from apps.commandes.models import Commande
from apps.accounts.decorators import admin_required
from .models import TableRestaurant
from .forms import TableRestaurantForm, TableSearchForm
from decimal import Decimal


# ==========================================
# CRUD TABLES PHYSIQUES (Admin uniquement)
# ==========================================

@login_required
@admin_required
def table_list_admin(request):
    """
    Liste de toutes les tables physiques (Admin)
    """
    tables = TableRestaurant.objects.select_related('utilisateur').order_by('numero_table')
    
    # Recherche
    search_query = request.GET.get('recherche', '')
    if search_query:
        tables = tables.filter(
            Q(numero_table__icontains=search_query) |
            Q(utilisateur__login__icontains=search_query)
        )
    
    # Formulaire de recherche
    search_form = TableSearchForm(request.GET)
    
    # Statistiques
    stats = {
        'total': TableRestaurant.objects.count(),
        'utilisateurs_disponibles': User.objects.filter(
            role='Rtable'
        ).exclude(
            id__in=TableRestaurant.objects.values_list('utilisateur_id', flat=True)
        ).count(),
    }
    
    context = {
        'tables': tables,
        'search_form': search_form,
        'stats': stats,
        'search_query': search_query,
    }
    
    return render(request, 'restaurant/table_list_admin.html', context)


@login_required
@admin_required
def table_create(request):
    """
    Créer une nouvelle table physique
    """
    if request.method == 'POST':
        form = TableRestaurantForm(request.POST)
        if form.is_valid():
            table = form.save()
            messages.success(
                request, 
                f"✅ Table '{table.numero_table}' créée avec succès ! "
                f"Associée à {table.utilisateur.login}"
            )
            return redirect('restaurant:table_list_admin')
    else:
        form = TableRestaurantForm()
    
    context = {
        'form': form,
        'title': 'Créer une nouvelle table',
        'button_text': 'Créer la table',
        'action': 'create',
    }
    
    return render(request, 'restaurant/table_form.html', context)


@login_required
@admin_required
def table_detail_admin(request, pk):
    """
    Détails d'une table physique (Admin)
    """
    table = get_object_or_404(
        TableRestaurant.objects.select_related('utilisateur'),
        pk=pk
    )
    
    # Statistiques de la table
    commandes = Commande.objects.filter(table=table.utilisateur)
    
    stats = {
        'total_commandes': commandes.count(),
        'commandes_en_attente': commandes.filter(statut='en_attente').count(),
        'commandes_servies': commandes.filter(statut='servie').count(),
        'commandes_payees': commandes.filter(statut='payee').count(),
        'montant_total': commandes.filter(statut='payee').aggregate(
            total=Sum('montant_total')
        )['total'] or Decimal('0.00'),
    }
    
    # Dernières commandes
    dernieres_commandes = commandes.order_by('-date_commande')[:10]
    
    context = {
        'table': table,
        'stats': stats,
        'dernieres_commandes': dernieres_commandes,
    }
    
    return render(request, 'restaurant/table_detail_admin.html', context)


@login_required
@admin_required
def table_update(request, pk):
    """
    Modifier une table existante
    """
    table = get_object_or_404(TableRestaurant, pk=pk)
    
    if request.method == 'POST':
        form = TableRestaurantForm(request.POST, instance=table)
        if form.is_valid():
            table = form.save()
            messages.success(
                request, 
                f"✅ Table '{table.numero_table}' modifiée avec succès !"
            )
            return redirect('restaurant:table_detail_admin', pk=table.pk)
    else:
        form = TableRestaurantForm(instance=table)
    
    context = {
        'form': form,
        'table': table,
        'title': f'Modifier : {table.numero_table}',
        'button_text': 'Enregistrer les modifications',
        'action': 'update',
    }
    
    return render(request, 'restaurant/table_form.html', context)


@login_required
@admin_required
def table_delete(request, pk):
    """
    Supprimer une table physique
    Confirmation requise
    """
    table = get_object_or_404(
        TableRestaurant.objects.select_related('utilisateur'),
        pk=pk
    )
    
    if request.method == 'POST':
        numero = table.numero_table
        utilisateur_login = table.utilisateur.login
        
        # Supprimer la table
        table.delete()
        
        messages.success(
            request, 
            f"✅ Table '{numero}' supprimée avec succès ! "
            f"L'utilisateur {utilisateur_login} peut maintenant être réassocié."
        )
        return redirect('restaurant:table_list_admin')
    
    # Vérifier les dépendances (commandes)
    commandes_count = Commande.objects.filter(table=table.utilisateur).count()
    
    context = {
        'table': table,
        'commandes_count': commandes_count,
    }
    
    return render(request, 'restaurant/table_delete_confirm.html', context)


# ==========================================
# VUES POUR LES SERVEURS (Rserveur)
# ==========================================



@login_required
def table_list_serveur(request):
    """
    Liste de toutes les tables avec leurs statuts
    Accessible uniquement par les serveurs et admins
    """
    if not (request.user.is_serveur() or request.user.is_admin()):
        messages.error(request, "Accès refusé : fonctionnalité réservée aux serveurs")
        return redirect('dashboard:index')
    
    # Récupérer toutes les tables (utilisateurs avec rôle Rtable)
    tables = User.objects.filter(role='Rtable').prefetch_related('commandes')
    
    # Calculer les statistiques pour chaque table
    tables_data = []
    for table in tables:
        # Dernière commande non payée
        derniere_commande = table.commandes.filter(
            statut__in=['en_attente', 'servie']
        ).order_by('-date_commande').first()
        
        # Déterminer le statut
        if not derniere_commande:
            statut = 'libre'
        elif derniere_commande.statut == 'en_attente':
            statut = 'en_attente'
        elif derniere_commande.statut == 'servie':
            statut = 'servie'
        else:
            statut = 'libre'
        
        tables_data.append({
            'table': table,
            'statut': statut,
            'derniere_commande': derniere_commande,
            'total_commandes': table.commandes.count(),
            'commandes_en_attente': table.commandes.filter(statut='en_attente').count(),
        })
    
    # Filtrer par statut si demandé
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        tables_data = [t for t in tables_data if t['statut'] == statut_filter]
    
    # Statistiques globales
    stats = {
        'total_tables': len(tables_data),
        'libres': len([t for t in tables_data if t['statut'] == 'libre']),
        'en_attente': len([t for t in tables_data if t['statut'] == 'en_attente']),
        'servies': len([t for t in tables_data if t['statut'] == 'servie']),
    }
    
    context = {
        'tables_data': tables_data,
        'stats': stats,
        'statut_filter': statut_filter,
    }
    
    return render(request, 'restaurant/table_list_serveur.html', context)


@login_required
def table_detail_serveur(request, table_id):
    """
    Détails d'une table spécifique avec ses commandes
    """
    if not (request.user.is_serveur() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    table = get_object_or_404(User, id=table_id, role='Rtable')
    
    # Récupérer toutes les commandes de cette table
    commandes = table.commandes.select_related().prefetch_related('items__plat').order_by('-date_commande')
    
    # Filtrer par statut
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        commandes = commandes.filter(statut=statut_filter)
    
    # Statistiques de la table
    stats = {
        'total_commandes': table.commandes.count(),
        'en_attente': table.commandes.filter(statut='en_attente').count(),
        'servies': table.commandes.filter(statut='servie').count(),
        'payees': table.commandes.filter(statut='payee').count(),
        'montant_total': table.commandes.filter(statut='payee').aggregate(
            total=Sum('montant_total')
        )['total'] or Decimal('0.00'),
    }
    
    context = {
        'table': table,
        'commandes': commandes,
        'stats': stats,
        'statut_filter': statut_filter,
    }
    
    return render(request, 'restaurant/table_detail_serveur.html', context)


@login_required
def commande_list_serveur(request):
    """
    Liste de toutes les commandes (tous statuts)
    """
    if not (request.user.is_serveur() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    commandes = Commande.objects.select_related('table').prefetch_related('items__plat').order_by('-date_commande')
    
    # Filtres
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        commandes = commandes.filter(statut=statut_filter)
    
    table_filter = request.GET.get('table', '')
    if table_filter:
        commandes = commandes.filter(table__login__icontains=table_filter)
    
    # Statistiques
    stats = {
        'total': Commande.objects.count(),
        'en_attente': Commande.objects.filter(statut='en_attente').count(),
        'servies': Commande.objects.filter(statut='servie').count(),
        'payees': Commande.objects.filter(statut='payee').count(),
    }
    
    context = {
        'commandes': commandes,
        'stats': stats,
        'statut_filter': statut_filter,
        'table_filter': table_filter,
    }
    
    return render(request, 'restaurant/commande_list_serveur.html', context)


@login_required
def commande_detail_serveur(request, commande_id):
    """
    Détail d'une commande pour le serveur
    """
    if not (request.user.is_serveur() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    commande = get_object_or_404(
        Commande.objects.select_related('table').prefetch_related('items__plat'),
        id=commande_id
    )
    
    context = {
        'commande': commande,
    }
    
    return render(request, 'restaurant/commande_detail_serveur.html', context)


@login_required
def commande_marquer_servie(request, commande_id):
    """
    Marque une commande comme servie
    """
    if not (request.user.is_serveur() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if commande.statut != 'en_attente':
        messages.warning(request, f"⚠️ La commande #{commande.id} n'est pas en attente")
        return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)
    
    # Marquer comme servie
    commande.statut = 'servie'
    commande.save()
    
    messages.success(request, f"✅ Commande #{commande.id} marquée comme servie")
    
    # Rediriger selon le paramètre 'next'
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)


@login_required
def commande_marquer_payee(request, commande_id):
    """
    Marque une commande comme payée
    Crée un paiement et met à jour la caisse
    """
    if not (request.user.is_serveur() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if commande.statut != 'servie':
        messages.warning(
            request, 
            f"⚠️ La commande #{commande.id} doit d'abord être servie avant d'être payée"
        )
        return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)
    
    # Vérifier si déjà payée
    if hasattr(commande, 'paiement'):
        messages.warning(request, f"⚠️ La commande #{commande.id} est déjà payée")
        return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)
    
    # Import ici pour éviter les imports circulaires
    from apps.paiements.models import Paiement, Caisse
    from django.db import transaction
    
    try:
        with transaction.atomic():
            # Créer le paiement
            paiement = Paiement.objects.create(
                commande=commande,
                montant=commande.montant_total
            )
            
            # Mettre à jour le statut de la commande
            commande.statut = 'payee'
            commande.save()
            
            # Mettre à jour la caisse
            caisse = Caisse.get_instance()
            caisse.solde_actuel += commande.montant_total
            caisse.save()
            
            messages.success(
                request, 
                f"✅ Commande #{commande.id} payée avec succès ! Montant : {commande.montant_total} GNF"
            )
    
    except Exception as e:
        messages.error(request, f"❌ Erreur lors du paiement : {str(e)}")
        return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)
    
    # Rediriger selon le paramètre 'next'
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)