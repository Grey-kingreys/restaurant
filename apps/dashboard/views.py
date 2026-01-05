# apps/dashboard/views.py

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
                'url': '/menu/plats/',
                'badge': 'Actif'
            },
            {
                'icon': '🛒',
                'title': 'Mon panier',
                'description': 'Gérer mes commandes',
                'status': 'Disponible',
                'url': '/commandes/panier/',
                'badge': 'Actif'
            },
            {
                'icon': '📦',
                'title': 'Mes commandes',
                'description': 'Historique des commandes',
                'status': 'Disponible',
                'url': '/commandes/mes-commandes/',
                'badge': 'Actif'
            },
        ]
    
    elif user.is_serveur():
        context['features'] = [
            {
                'icon': '🪑',
                'title': 'Gestion des tables',
                'description': 'Voir l\'état des tables',
                'status': 'Disponible',
                'url': '/restaurant/tables/',
                'badge': 'Actif'
            },
            {
                'icon': '📦',
                'title': 'Toutes les commandes',
                'description': 'Voir toutes les commandes',
                'status': 'Disponible',
                'url': '/restaurant/commandes/',
                'badge': 'Actif'
            },
            {
                'icon': '✅',
                'title': 'Valider paiements',
                'description': 'Confirmer les paiements',
                'status': 'Disponible',
                'url': '/restaurant/commandes/',
                'badge': 'Actif'
            },
        ]
    
    elif user.is_cuisinier():
        context['features'] = [
            {
                'icon': '🍳',
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
                'title': 'Dashboard Caisse',
                'description': 'Solde et statistiques',
                'status': 'Disponible',
                'url': '/paiements/caisse/',
                'badge': 'Actif'
            },
            {
                'icon': '💳',
                'title': 'Historique paiements',
                'description': 'Voir tous les paiements',
                'status': 'Disponible',
                'url': '/paiements/paiements/',
                'badge': 'Actif'
            },
            {
                'icon': '💸',
                'title': 'Gestion dépenses',
                'description': 'Consulter les dépenses',
                'status': 'Disponible',
                'url': '/paiements/depenses/',
                'badge': 'Actif'
            },
            {
                'icon': '➕',
                'title': 'Ajouter une dépense',
                'description': 'Enregistrer une nouvelle dépense',
                'status': 'Disponible',
                'url': '/paiements/depenses/ajouter/',
                'badge': 'Actif'
            },
        ]
    
    elif user.is_admin():
        context['features'] = [
            {
                'icon': '👥',
                'title': 'Gestion des utilisateurs',
                'description': 'Créer/modifier/supprimer utilisateurs',
                'status': 'Disponible',  # ✅ CHANGÉ
                'url': '/auth/users/',    # ✅ CHANGÉ
                'badge': 'Actif'          # ✅ CHANGÉ
            },
            {
                'icon': '📊',
                'title': 'Dashboard Analytics',
                'description': 'Statistiques complètes',
                'status': 'À venir',
                'url': '#',
                'badge': 'Partie 6'
            },
            {
                'icon': '🪑',
                'title': 'Gestion des tables',
                'description': 'CRUD Tables physiques',
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
            'progress': 100,
            'status': 'completed',
            'part': 'Partie 3'
        },
        {
            'name': 'Serveur',
            'progress': 100,
            'status': 'completed',
            'part': 'Partie 4'
        },
        {
            'name': 'Paiements & Caisse',
            'progress': 100,
            'status': 'completed',
            'part': 'Partie 5'
        },
        {
            'name': 'Admin & Dashboard',
            'progress': 35,
            'status': 'in_progress',
            'part': 'Partie 6'
        },
    ]
    
    return render(request, 'dashboard/index.html', context)