# Commandes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from apps.menu.models import Plat
from .models import Commande, CommandeItem
from .cart import Cart
from .pdf_utils import generer_recu_pdf


# ========== GESTION DU PANIER (Tables uniquement) ==========

@login_required
def cart_detail(request):
    """
    Affiche le contenu du panier
    Accessible uniquement aux tables
    """
    if not request.user.is_table():
        messages.error(request, "Accès refusé : cette fonctionnalité est réservée aux tables.")
        return redirect('dashboard:index')
    
    cart = Cart(request)
    
    context = {
        'cart': cart,
        'total': cart.get_total_prix(),
        'items_count': cart.get_items_count(),
    }
    
    return render(request, 'commandes/cart_detail.html', context)


@login_required
def cart_add(request, plat_id):
    """
    Ajoute un plat au panier
    """
    if not request.user.is_table():
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')
    
    plat = get_object_or_404(Plat, id=plat_id, disponible=True)
    cart = Cart(request)
    
    quantite = int(request.POST.get('quantite', 1))
    quantite = max(1, min(10, quantite))  # Entre 1 et 10
    
    cart.add(plat=plat, quantite=quantite)
    
    messages.success(
        request, 
        f"✅ {plat.nom} ajouté au panier (x{quantite})"
    )
    
    # Rediriger selon le paramètre 'next' ou vers la liste des plats
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    # Rediriger vers la liste des plats (nom correct: 'table_list')
    return redirect('menu:table_list')


@login_required
def cart_update(request, plat_id):
    """
    Met à jour la quantité d'un plat dans le panier
    """
    if not request.user.is_table():
        return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
    
    plat = get_object_or_404(Plat, id=plat_id)
    cart = Cart(request)
    
    quantite = int(request.POST.get('quantite', 1))
    quantite = max(1, min(10, quantite))
    
    cart.add(plat=plat, quantite=quantite, update_quantite=True)
    
    return JsonResponse({
        'success': True,
        'quantite': quantite,
        'total': str(cart.get_total_prix()),
        'items_count': len(cart)
    })


@login_required
def cart_remove(request, plat_id):
    """
    Supprime un plat du panier
    """
    if not request.user.is_table():
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')
    
    plat = get_object_or_404(Plat, id=plat_id)
    cart = Cart(request)
    cart.remove(plat)
    
    messages.info(request, f"🗑️ {plat.nom} retiré du panier")
    
    return redirect('commandes:cart_detail')


# ========== VALIDATION DE COMMANDE ==========

@login_required
@transaction.atomic
def commande_valider(request):
    """
    Valide le panier et crée une commande
    """
    if not request.user.is_table():
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')
    
    cart = Cart(request)
    
    if cart.is_empty():
        messages.warning(request, "⚠️ Votre panier est vide.")
        return redirect('menu:plat_list_table')
    
    # Créer la commande
    commande = Commande.objects.create(
        table=request.user,
        montant_total=cart.get_total_prix(),
        statut='en_attente'
    )
    
    # Créer les lignes de commande
    for item in cart:
        CommandeItem.objects.create(
            commande=commande,
            plat=item['plat'],
            quantite=item['quantite'],
            prix_unitaire=item['prix_unitaire']
        )
    
    # Vider le panier
    cart.clear()
    
    messages.success(
        request, 
        f"✅ Commande #{commande.id} validée avec succès ! Montant : {commande.montant_total} GNF"
    )
    
    return redirect('commandes:commande_detail', commande_id=commande.id)


# ========== CONSULTATION DES COMMANDES ==========

@login_required
def commande_list(request):
    """
    Liste des commandes de la table connectée
    """
    if not request.user.is_table():
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')
    
    commandes = Commande.objects.filter(table=request.user).prefetch_related('items__plat')
    
    context = {
        'commandes': commandes,
        'total_commandes': commandes.count(),
        'commandes_en_attente': commandes.filter(statut='en_attente').count(),
        'commandes_servies': commandes.filter(statut='servie').count(),
        'commandes_payees': commandes.filter(statut='payee').count(),
    }
    
    return render(request, 'commandes/commande_list.html', context)


@login_required
def commande_detail(request, commande_id):
    """
    Détails d'une commande spécifique
    """
    if not request.user.is_table():
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')
    
    commande = get_object_or_404(
        Commande.objects.prefetch_related('items__plat'),
        id=commande_id,
        table=request.user  # Sécurité : la table ne voit que ses commandes
    )
    
    context = {
        'commande': commande,
    }
    
    return render(request, 'commandes/commande_detail.html', context)


@login_required
def telecharger_recu_pdf(request, commande_id):
    """
    Génère et télécharge le reçu PDF d'une commande
    
    Accessible par:
    - La table qui a passé la commande
    - Les serveurs
    - Les comptables
    - Les admins
    """
    # Récupérer la commande
    commande = get_object_or_404(
        Commande.objects.select_related('table', 'serveur_ayant_servi')
                        .prefetch_related('items__plat'),
        id=commande_id
    )
    
    # Vérification des permissions
    user = request.user
    
    # La table ne peut télécharger que ses propres reçus
    if user.is_table() and commande.table != user:
        from django.contrib import messages
        messages.error(request, "Vous ne pouvez télécharger que vos propres reçus")
        return redirect('dashboard:index')
    
    # Les serveurs, comptables et admins peuvent tout télécharger
    if not (user.is_table() or user.is_serveur() or user.is_comptable() or user.is_admin()):
        from django.contrib import messages
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard:index')
    
    # Générer le PDF
    try:
        pdf_buffer = generer_recu_pdf(commande)
        
        # Nom du fichier
        filename = f'recu_commande_{commande.id}_{commande.date_commande.strftime("%Y%m%d_%H%M")}.pdf'
        
        # Créer la réponse HTTP
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f"Erreur lors de la génération du reçu: {str(e)}")
        
        # Redirection selon le rôle
        if user.is_table():
            return redirect('commandes:commande_detail', commande_id=commande.id)
        else:
            return redirect('restaurant:commande_detail_serveur', commande_id=commande.id)