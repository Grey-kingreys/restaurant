# apps/dashboard/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta, datetime
from decimal import Decimal
import csv
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from apps.accounts.models import User
from apps.menu.models import Plat
from apps.commandes.models import Commande, CommandeItem
from apps.paiements.models import Paiement, Caisse, Depense
from apps.restaurant.models import TableRestaurant
from apps.accounts.decorators import admin_required

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
                'status': 'Disponible',
                'url': '/auth/users/',
                'badge': 'Actif'
            },
            {
                'icon': '🪑',
                'title': 'Gestion des tables',
                'description': 'CRUD Tables physiques',
                'status': 'Disponible',
                'url': '/restaurant/admin/tables/',
                'badge': 'Actif'
            },
            {
                'icon': '📊',
                'title': 'Dashboard Analytics',
                'description': 'Statistiques complètes',
                'status': 'Disponible',
                'url': '/dashboard/analytics/',
                'badge': 'Actif'
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
                'status': 'Disponible',
                'url': '/dashboard/export/excel/',
                'badge': 'Bonus'
            },
            {
                'icon': '📄',
                'title': 'Export PDF',
                'description': 'Générer des rapports',
                'status': 'Disponible',
                'url': '/dashboard/export/pdf/',
                'badge': 'Bonus'
            },
            {
                'icon': '📧',
                'title': 'Email automatique',
                'description': 'Rapport quotidien caisse',
                'status': 'Configuré',
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
            'progress': 100,
            'status': 'completed',
            'part': 'Partie 6'
        },
    ]
    
    return render(request, 'dashboard/index.html', context)


@login_required
@admin_required
def analytics_dashboard(request):
    """
    Dashboard Analytics avancé
    Accessible uniquement par les administrateurs
    """
    # Période de temps
    aujourd_hui = timezone.now().date()
    debut_mois = aujourd_hui.replace(day=1)
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    
    # ===== STATISTIQUES GÉNÉRALES =====
    stats_generales = {
        'total_utilisateurs': User.objects.count(),
        'utilisateurs_actifs': User.objects.filter(actif=True).count(),
        'total_tables': User.objects.filter(role='Rtable').count(),
        'total_plats': Plat.objects.count(),
        'plats_disponibles': Plat.objects.filter(disponible=True).count(),
    }
    
    # ===== COMMANDES =====
    commandes_stats = {
        'total': Commande.objects.count(),
        'aujourd_hui': Commande.objects.filter(date_commande__date=aujourd_hui).count(),
        'cette_semaine': Commande.objects.filter(date_commande__date__gte=debut_semaine).count(),
        'ce_mois': Commande.objects.filter(date_commande__date__gte=debut_mois).count(),
        'en_attente': Commande.objects.filter(statut='en_attente').count(),
        'servies': Commande.objects.filter(statut='servie').count(),
        'payees': Commande.objects.filter(statut='payee').count(),
    }
    
    # ===== FINANCES =====
    caisse = Caisse.get_instance()
    
    # Revenus (paiements)
    revenus_total = Paiement.objects.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    revenus_mois = Paiement.objects.filter(
        date_paiement__date__gte=debut_mois
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    revenus_semaine = Paiement.objects.filter(
        date_paiement__date__gte=debut_semaine
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    revenus_jour = Paiement.objects.filter(
        date_paiement__date=aujourd_hui
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    
    # Dépenses
    depenses_total = Depense.objects.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    depenses_mois = Depense.objects.filter(
        date_depense__gte=debut_mois
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    depenses_semaine = Depense.objects.filter(
        date_depense__gte=debut_semaine
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    depenses_jour = Depense.objects.filter(
        date_depense=aujourd_hui
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    
    finances_stats = {
        'solde_caisse': caisse.solde_actuel,
        'revenus': {
            'total': revenus_total,
            'mois': revenus_mois,
            'semaine': revenus_semaine,
            'jour': revenus_jour,
        },
        'depenses': {
            'total': depenses_total,
            'mois': depenses_mois,
            'semaine': depenses_semaine,
            'jour': depenses_jour,
        },
        'benefice': {
            'total': revenus_total - depenses_total,
            'mois': revenus_mois - depenses_mois,
            'semaine': revenus_semaine - depenses_semaine,
            'jour': revenus_jour - depenses_jour,
        }
    }
    
    # ===== TOP PLATS =====
    top_plats = CommandeItem.objects.values(
        'plat__nom', 'plat__prix_unitaire'
    ).annotate(
        quantite_totale=Sum('quantite'),
        nombre_commandes=Count('commande', distinct=True),
        revenu_total=Sum(F('quantite') * F('prix_unitaire'))
    ).order_by('-quantite_totale')[:10]
    
    # ===== TOP TABLES =====
    top_tables = Commande.objects.values(
        'table__login'
    ).annotate(
        nombre_commandes=Count('id'),
        montant_total=Sum('montant_total', filter=Q(statut='payee'))
    ).order_by('-montant_total')[:10]
    
    # ===== ÉVOLUTION DES COMMANDES (7 derniers jours) =====
    evolution_commandes = []
    for i in range(6, -1, -1):
        jour = aujourd_hui - timedelta(days=i)
        nb_commandes = Commande.objects.filter(date_commande__date=jour).count()
        revenus = Paiement.objects.filter(
            date_paiement__date=jour
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        
        evolution_commandes.append({
            'date': jour.strftime('%d/%m'),
            'commandes': nb_commandes,
            'revenus': float(revenus),
        })
    
    # ===== RÉPARTITION PAR CATÉGORIE =====
    categories_stats = []
    for code, label in Plat.CATEGORIE_CHOICES:
        # Calculer la quantité totale vendue
        quantite_totale = CommandeItem.objects.filter(
            plat__categorie=code
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        # Calculer le revenu total
        revenu_total = CommandeItem.objects.filter(
            plat__categorie=code
        ).aggregate(
            total=Sum(F('quantite') * F('prix_unitaire'))
        )['total'] or Decimal('0.00')
        
        if quantite_totale > 0:
            categories_stats.append({
                'categorie': label,
                'quantite': quantite_totale,
                'revenu': float(revenu_total),
            })
    
    # ===== TAUX DE CONVERSION =====
    commandes_validees = Commande.objects.filter(statut='payee').count()
    taux_conversion = 0
    if commandes_stats['total'] > 0:
        taux_conversion = (commandes_validees / commandes_stats['total']) * 100
    
    # ===== PANIER MOYEN =====
    panier_moyen = Decimal('0.00')
    if commandes_validees > 0:
        panier_moyen = revenus_total / commandes_validees
    
    context = {
        'stats_generales': stats_generales,
        'commandes_stats': commandes_stats,
        'finances_stats': finances_stats,
        'top_plats': top_plats,
        'top_tables': top_tables,
        'evolution_commandes': evolution_commandes,
        'categories_stats': categories_stats,
        'taux_conversion': round(taux_conversion, 2),
        'panier_moyen': panier_moyen,
        'aujourd_hui': aujourd_hui,
        'debut_semaine': debut_semaine,
        'debut_mois': debut_mois,
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required
@admin_required
def export_excel(request):
    """Export simple des statistiques du dashboard au format CSV (compatible Excel)."""
    aujourd_hui = timezone.now().date()
    debut_mois = aujourd_hui.replace(day=1)
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())

    # Statistiques de base proches de celles du dashboard
    total_commandes = Commande.objects.count()
    commandes_payees = Commande.objects.filter(statut='payee').count()

    revenus_total = Paiement.objects.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    depenses_total = Depense.objects.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    benefice_total = revenus_total - depenses_total

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dashboard_analytics.csv"'

    writer = csv.writer(response)
    writer.writerow(['Période', 'Total commandes', 'Commandes payées', 'Revenus (GNF)', 'Dépenses (GNF)', 'Bénéfice (GNF)'])
    writer.writerow([
        f"Du {debut_mois.strftime('%d/%m/%Y')} au {aujourd_hui.strftime('%d/%m/%Y')}",
        total_commandes,
        commandes_payees,
        int(revenus_total),
        int(depenses_total),
        int(benefice_total),
    ])

    return response


@login_required
@admin_required
def export_pdf(request):
    """Génère un vrai PDF de synthèse des statistiques du dashboard."""
    aujourd_hui = timezone.now().date()

    # Données principales (alignées avec le dashboard)
    total_commandes = Commande.objects.count()
    commandes_payees = Commande.objects.filter(statut='payee').count()
    revenus_total = Paiement.objects.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    depenses_total = Depense.objects.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    benefice_total = revenus_total - depenses_total

    # Préparation du buffer mémoire
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marges
    margin_x = 40
    margin_top = height - 50

    # En-tête
    p.setTitle("Dashboard Analytics - Rapport")
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor("#1f2937"))  # gris foncé proche du site
    p.drawString(margin_x, margin_top, "Dashboard Analytics")

    p.setFont("Helvetica", 11)
    p.setFillColor(colors.gray)
    p.drawString(margin_x, margin_top - 20, "Vue d'ensemble complète du restaurant")

    # Date à droite
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#4b5563"))
    date_str = f"Rapport du {aujourd_hui.strftime('%d/%m/%Y')}"
    p.drawRightString(width - margin_x, margin_top - 5, date_str)

    y = margin_top - 60

    # Section Commandes
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#2563eb"))  # bleu type Tailwind
    p.drawString(margin_x, y, "Commandes")
    y -= 18

    p.setFont("Helvetica", 11)
    p.setFillColor(colors.black)
    p.drawString(margin_x, y, f"Total commandes : {total_commandes}")
    y -= 16
    p.drawString(margin_x, y, f"Commandes payées : {commandes_payees}")
    y -= 24

    # Section Finances
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#16a34a"))  # vert Revenus
    p.drawString(margin_x, y, "Finances")
    y -= 18

    p.setFont("Helvetica", 11)
    p.setFillColor(colors.black)
    p.drawString(margin_x, y, f"Revenus totaux : {int(revenus_total)} GNF")
    y -= 16
    p.drawString(margin_x, y, f"Dépenses totales : {int(depenses_total)} GNF")
    y -= 16
    p.drawString(margin_x, y, f"Bénéfice total : {int(benefice_total)} GNF")
    y -= 28

    # Petite note de bas de page
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.HexColor("#9ca3af"))
    p.drawString(margin_x, 40, "Rapport généré automatiquement depuis le Dashboard Analytics du restaurant")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dashboard_analytics.pdf"'
    return response