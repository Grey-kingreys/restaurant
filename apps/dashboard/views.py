# apps/dashboard/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages

from datetime import timedelta, datetime
from decimal import Decimal
import csv
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT

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
                'status': 'Disponible',
                'url': '/dashboard/rapport/email/',
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
    """Génère un rapport PDF structuré des ventes et le renvoie en téléchargement."""

    maintenant = timezone.now()
    aujourd_hui = maintenant.date()
    debut_periode = aujourd_hui - timedelta(days=30)

    pdf = _build_sales_report_pdf(debut_periode, aujourd_hui, maintenant)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_ventes.pdf"'
    return response


def _build_sales_report_pdf(debut_periode, aujourd_hui, maintenant):
    """Construit le PDF de rapport de ventes pour une période donnée et renvoie les bytes."""

    # Paiements et dépenses sur la période
    paiements_qs = Paiement.objects.filter(date_paiement__date__gte=debut_periode)
    total_ventes = paiements_qs.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    nombre_commandes = paiements_qs.count()

    depenses_qs = Depense.objects.filter(date_depense__gte=debut_periode)
    total_depenses = depenses_qs.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

    panier_moyen = Decimal('0.00')
    if nombre_commandes > 0:
        panier_moyen = total_ventes / nombre_commandes

    benefice_net = total_ventes - total_depenses

    # Préparation du buffer et du document
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = TA_LEFT
    normal = styles['Normal']
    heading = styles['Heading2']

    elements = []

    # Titre principal
    elements.append(Paragraph('<font color="#2563eb">RAPPORT DES VENTES</font>', title_style))
    elements.append(Spacer(1, 12))

    # Infos de période et date de génération
    periode_txt = f"Période: {debut_periode.strftime('%d/%m/%Y')} - {aujourd_hui.strftime('%d/%m/%Y')}"
    genere_txt = f"Généré le: {maintenant.strftime('%d/%m/%Y à %H:%M')}"
    elements.append(Paragraph(periode_txt, normal))
    elements.append(Paragraph(genere_txt, normal))
    elements.append(Spacer(1, 24))

    # Section RÉSUMÉ
    elements.append(Paragraph('<b>RÉSUMÉ</b>', heading))
    elements.append(Spacer(1, 8))

    resume_data = [
        ['Indicateur', 'Valeur'],
        ['Total des ventes', f"{total_ventes:.2f} GNF"],
        ['Nombre de commandes', str(nombre_commandes)],
        ['Panier moyen', f"{panier_moyen:.2f} GNF"],
        ['Total des dépenses', f"{total_depenses:.2f} GNF"],
        ['Bénéfice net', f"{benefice_net:.2f} GNF"],
    ]

    resume_table = Table(resume_data, colWidths=[220, 220])
    resume_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(resume_table)
    elements.append(Spacer(1, 24))

    # Section DÉTAIL DES PAIEMENTS
    elements.append(Paragraph('<b>DÉTAIL DES PAIEMENTS</b>', heading))
    elements.append(Spacer(1, 8))

    paiements_liste = paiements_qs.select_related('commande__table').order_by('-date_paiement')

    detail_data = [['Date', 'Commande', 'Table', 'Montant', 'Mode']]
    for p in paiements_liste:
        code_commande = f"CMD-{p.date_paiement.strftime('%Y%m%d')}-{p.commande.id:04d}"
        table_nom = getattr(p.commande.table, 'login', str(p.commande.table_id))
        montant_str = f"{float(p.montant):.2f} GNF"
        mode = 'Espèces'
        detail_data.append([
            p.date_paiement.strftime('%d/%m/%Y'),
            code_commande,
            table_nom,
            montant_str,
            mode,
        ])

    if len(detail_data) == 1:
        elements.append(Paragraph("Aucun paiement sur la période.", normal))
    else:
        detail_table = Table(detail_data, colWidths=[70, 130, 100, 90, 70])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(detail_table)

    # Construction du PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf


@login_required
@admin_required
def send_sales_report_email(request):
    """Génère le rapport de ventes et l'envoie par email à l'adresse configurée."""

    maintenant = timezone.now()
    aujourd_hui = maintenant.date()
    debut_periode = aujourd_hui - timedelta(days=30)

    pdf = _build_sales_report_pdf(debut_periode, aujourd_hui, maintenant)

    subject = "Rapport des ventes - Dashboard Restaurant"
    body = (
        "Bonjour,\n\n"
        "Vous trouverez ci-joint le rapport des ventes du restaurant pour la période "
        f"du {debut_periode.strftime('%d/%m/%Y')} au {aujourd_hui.strftime('%d/%m/%Y')}.\n\n"
        "Ceci est un envoi automatique depuis le Dashboard Analytics.\n"
    )

    to_email = getattr(settings, 'REPORT_EMAIL_TO', None)
    if not to_email:
        messages.error(request, "Aucune adresse email de destination n'est configurée (REPORT_EMAIL_TO).")
        return redirect('dashboard:index')

    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    email.attach('rapport_ventes.pdf', pdf, 'application/pdf')
    email.send(fail_silently=False)

    messages.success(request, f"Rapport envoyé avec succès à {to_email}.")
    return redirect('dashboard:index')