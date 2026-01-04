from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    Dashboard principal - Point d'entrée après connexion
    Affiche les fonctionnalités selon le rôle
    """
    user = request.user
    
    context = {
        'user': user,
        'role_display': user.get_role_display(),
    }
    
    # Définir les fonctionnalités selon le rôle
    if user.is_table():
        context['features'] = [
            {
                'icon': '📋',
                'title': 'Consulter le menu',
                'description': 'Voir tous les plats disponibles',
                'status': 'Disponible',
                'url': '/menu/plats/',  # Correspond à menu:table_list
                'badge': 'Actif'
            },
            {
                'icon': '🛒',
                'title': 'Mon panier',
                'description': 'Gérer mes commandes',
                'status': 'Disponible',  # ✅ CHANGÉ
                'url': '/commandes/panier/',  # ✅ CHANGÉ
                'badge': 'Actif'  # ✅ CHANGÉ
            },
            {
                'icon': '📦',
                'title': 'Mes commandes',
                'description': 'Historique des commandes',
                'status': 'Disponible',  # ✅ CHANGÉ
                'url': '/commandes/mes-commandes/',  # ✅ CHANGÉ
                'badge': 'Actif'  # ✅ CHANGÉ
            },
        ]
    
    elif user.is_serveur():
        context['features'] = [
            {
                'icon': '🪑',
                'title': 'Gestion des tables',
                'description': 'Voir l\'état des tables',
                'status': 'Disponible',  # ✅ CHANGÉ
                'url': '/restaurant/tables/',  # ✅ CHANGÉ
                'badge': 'Actif'  # ✅ CHANGÉ
            },
            {
                'icon': '📦',
                'title': 'Toutes les commandes',
                'description': 'Voir toutes les commandes',
                'status': 'Disponible',  # ✅ CHANGÉ
                'url': '/restaurant/commandes/',  # ✅ CHANGÉ
                'badge': 'Actif'  # ✅ CHANGÉ
            },
            {
                'icon': '✅',
                'title': 'Valider paiements',
                'description': 'Confirmer les paiements',
                'status': 'Disponible',  # ✅ CHANGÉ
                'url': '/restaurant/commandes/',  # ✅ CHANGÉ
                'badge': 'Actif'  # ✅ CHANGÉ
            },
        ]
    
    elif user.is_cuisinier():
        context['features'] = [
            {
                'icon': '🳳',
                'title': 'Gérer les plats',
                'description': 'Liste de tous les plats',
                'status': 'Disponible',
                'url': '/menu/cuisinier/',
                'badge': 'Actif'
            },
            {
                'icon': '➕',
                'title': 'Ajouter un plat',
                'description': 'Créer un nouveau plat',
                'status': 'Disponible',
                'url': '/menu/cuisinier/ajouter/',
                'badge': 'Actif'
            },
            {
                'icon': '📸',
                'title': 'Images des plats',
                'description': 'Gérer les photos',
                'status': 'Disponible',
                'url': '/menu/cuisinier/',
                'badge': 'Actif'
            },
        ]
    
    elif user.is_comptable():
        context['features'] = [
            {
                'icon': '💰',
                'title': 'Caisse',
                'description': 'Solde et transactions',
                'status': 'À venir',
                'url': '#',
                'badge': 'Partie 5'
            },
            {
                'icon': '📊',
                'title': 'Gestion dépenses',
                'description': 'Enregistrer les dépenses',
                'status': 'À venir',
                'url': '#',
                'badge': 'Partie 5'
            },
            {
                'icon': '💳',
                'title': 'Historique paiements',
                'description': 'Voir tous les paiements',
                'status': 'À venir',
                'url': '#',
                'badge': 'Partie 5'
            },
        ]
    
    elif user.is_admin():
        context['features'] = [
            {
                'icon': '📊',
                'title': 'Dashboard Analytics',
                'description': 'Statistiques complètes',
                'status': 'À venir',
                'url': '#',
                'badge': 'Bonus'
            },
            {
                'icon': '👥',
                'title': 'Gestion utilisateurs',
                'description': 'Créer/modifier utilisateurs',
                'status': 'À venir',
                'url': '#',
                'badge': 'Partie 6'
            },
            {
                'icon': '⚙️',
                'title': 'Admin Django',
                'description': 'Interface d\'administration',
                'status': 'Disponible',
                'url': '/admin/',
                'badge': 'Actif'
            },
            {
                'icon': '📥',
                'title': 'Export Excel',
                'description': 'Exporter les données',
                'status': 'À venir',
                'url': '#',
                'badge': 'Bonus'
            },
            {
                'icon': '📄',
                'title': 'Export PDF',
                'description': 'Générer des rapports',
                'status': 'À venir',
                'url': '#',
                'badge': 'Bonus'
            },
            {
                'icon': '📧',
                'title': 'Email automatique',
                'description': 'Rapport quotidien caisse',
                'status': 'À venir',
                'url': '#',
                'badge': 'Avancé'
            },
        ]
    
    # Stats de progression du projet
    context['project_stats'] = [
        {
            'name': 'Authentification',
            'progress': 100,
            'status': 'completed',
            'part': 'Partie 1'
        },
        {
            'name': 'Gestion du menu',
            'progress': 100,
            'status': 'completed',
            'part': 'Partie 2'
        },
        {
            'name': 'Commandes & Panier',
            'progress': 100,  # ✅ CHANGÉ
            'status': 'completed',  # ✅ CHANGÉ
            'part': 'Partie 3'
        },
        {
            'name': 'Serveur',
            'progress': 100,  # ✅ CHANGÉ
            'status': 'completed',  # ✅ CHANGÉ
            'part': 'Partie 4'
        },
        {
            'name': 'Paiements & Caisse',
            'progress': 0,
            'status': 'pending',
            'part': 'Partie 5'
        },
        {
            'name': 'Admin & Dashboard',
            'progress': 0,
            'status': 'pending',
            'part': 'Partie 6'
        },
    ]
    
    return render(request, 'dashboard/index.html', context)