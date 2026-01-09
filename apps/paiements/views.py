# apps/paiements/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Paiement, Caisse, Depense
from apps.commandes.models import Commande
from .forms import DepenseForm

# ==========================================
# DASHBOARD CAISSE (Comptable/Admin)
# ==========================================
@login_required
def caisse_dashboard(request):
    if not (request.user.is_comptable() or request.user.is_admin()):
        messages.error(request, "Accès refusé : fonctionnalité réservée aux comptables")
        return redirect('dashboard:index')
    
    caisse = Caisse.get_instance()
    
    periode = request.GET.get('periode', 'aujourd_hui')
    date_debut = None
    date_fin = timezone.now()
    
    if periode == 'aujourd_hui':
        date_debut = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        titre_periode = "Aujourd'hui"
    elif periode == 'semaine':
        date_debut = timezone.now() - timedelta(days=7)
        titre_periode = "Cette semaine"
    elif periode == 'mois':
        date_debut = timezone.now() - timedelta(days=30)
        titre_periode = "Ce mois"
    elif periode == 'tout':
        date_debut = None
        titre_periode = "Depuis le début"
    else:
        date_debut = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        titre_periode = "Aujourd'hui"
    
    paiements_query = Paiement.objects.all()
    if date_debut:
        paiements_query = paiements_query.filter(date_paiement__gte=date_debut)
    
    total_paiements = paiements_query.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    nombre_paiements = paiements_query.count()
    
    depenses_query = Depense.objects.all()
    if date_debut:
        depenses_query = depenses_query.filter(date_depense__gte=date_debut.date())
    
    total_depenses = depenses_query.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    nombre_depenses = depenses_query.count()
    
    benefice_net = total_paiements - total_depenses
    
    derniers_paiements = Paiement.objects.select_related('commande__table').order_by('-date_paiement')[:10]
    dernieres_depenses = Depense.objects.select_related('enregistree_par').order_by('-date_depense')[:10]
    
    context = {
        'caisse': caisse,
        'total_paiements': total_paiements,
        'nombre_paiements': nombre_paiements,
        'total_depenses': total_depenses,
        'nombre_depenses': nombre_depenses,
        'benefice_net': benefice_net,
        'derniers_paiements': derniers_paiements,
        'dernieres_depenses': dernieres_depenses,
        'periode': periode,
        'titre_periode': titre_periode,
    }
    
    return render(request, 'paiements/caisse_dashboard.html', context)


# ==========================================
# LISTE DES PAIEMENTS
# ==========================================
@login_required
def paiement_list(request):
    if not (request.user.is_comptable() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    paiements = Paiement.objects.select_related('commande__table').order_by('-date_paiement')
    
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    table_filter = request.GET.get('table')
    
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d')
            paiements = paiements.filter(date_paiement__gte=date_debut)
        except ValueError:
            pass
    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d')
            date_fin = date_fin.replace(hour=23, minute=59, second=59)
            paiements = paiements.filter(date_paiement__lte=date_fin)
        except ValueError:
            pass
    if table_filter:
        paiements = paiements.filter(commande__table__login__icontains=table_filter)
    
    stats = {
        'total': paiements.count(),
        'montant_total': paiements.aggregate(Sum('montant'))['montant__sum'] or Decimal('0.00'),
    }
    
    context = {
        'paiements': paiements,
        'stats': stats,
        'date_debut': request.GET.get('date_debut', ''),
        'date_fin': request.GET.get('date_fin', ''),
        'table_filter': table_filter or '',
    }
    
    return render(request, 'paiements/paiement_list.html', context)


# ==========================================
# LISTE DES DÉPENSES
# ==========================================
@login_required
def depense_list(request):
    if not (request.user.is_comptable() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    depenses = Depense.objects.select_related('enregistree_par').order_by('-date_depense')
    
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            depenses = depenses.filter(date_depense__gte=date_debut)
        except ValueError:
            pass
    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            depenses = depenses.filter(date_depense__lte=date_fin)
        except ValueError:
            pass
    
    stats = {
        'total': depenses.count(),
        'montant_total': depenses.aggregate(Sum('montant'))['montant__sum'] or Decimal('0.00'),
    }
    
    context = {
        'depenses': depenses,
        'stats': stats,
        'date_debut': request.GET.get('date_debut', ''),
        'date_fin': request.GET.get('date_fin', ''),
    }
    
    return render(request, 'paiements/depense_list.html', context)


# ==========================================
# CRÉER UNE DÉPENSE
# ==========================================
@login_required
def depense_create(request):
    if not (request.user.is_comptable() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    caisse = Caisse.get_instance()
    
    if request.method == 'POST':
        form = DepenseForm(request.POST)
        if form.is_valid():
            montant = form.cleaned_data['montant']
            if not caisse.peut_effectuer_depense(montant):
                messages.error(
                    request,
                    f"❌ Solde insuffisant ! Solde actuel : {caisse.solde_actuel} GNF, Montant demandé : {montant} GNF"
                )
                return render(request, 'paiements/depense_form.html', {'form': form, 'caisse': caisse})
            try:
                with transaction.atomic():
                    depense = form.save(commit=False)
                    depense.enregistree_par = request.user
                    depense.save()
                    
                    caisse.solde_actuel -= montant
                    caisse.save()
                    
                    messages.success(
                        request,
                        f"✅ Dépense enregistrée avec succès ! Nouveau solde : {caisse.solde_actuel} GNF"
                    )
                    return redirect('paiements:depense_list')
            except Exception as e:
                messages.error(request, f"❌ Erreur lors de l'enregistrement : {str(e)}")
    else:
        form = DepenseForm()
    
    return render(request, 'paiements/depense_form.html', {'form': form, 'caisse': caisse})


# ==========================================
# DÉTAIL D'UNE DÉPENSE
# ==========================================
@login_required
def depense_detail(request, depense_id):
    if not (request.user.is_comptable() or request.user.is_admin()):
        messages.error(request, "Accès refusé")
        return redirect('dashboard:index')
    
    depense = get_object_or_404(Depense.objects.select_related('enregistree_par'), id=depense_id)
    caisse = Caisse.objects.first()

    
    context = {
        'depense': depense,
        'caisse': caisse,
    }
    
    return render(request, 'paiements/depense_detail.html', context)
