from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal

from apps.paiements.models import Paiement, Depense, Caisse
from apps.commandes.models import Commande


@shared_task
def envoyer_rapport_quotidien():
    """
    Tâche Celery exécutée quotidiennement à 18h
    
    Actions :
    1. Calculer les stats de la journée (paiements - dépenses)
    2. Mettre à jour le solde de la caisse (déjà fait automatiquement)
    3. Envoyer le rapport par email à l'admin
    """
    maintenant = timezone.now()
    aujourd_hui = maintenant.date()
    
    # ===== CALCUL DES STATISTIQUES DU JOUR =====
    
    # Paiements de la journée
    paiements_jour = Paiement.objects.filter(
        date_paiement__date=aujourd_hui
    )
    total_paiements = paiements_jour.aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0.00')
    nombre_paiements = paiements_jour.count()
    
    # Dépenses de la journée
    depenses_jour = Depense.objects.filter(
        date_depense=aujourd_hui
    )
    total_depenses = depenses_jour.aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0.00')
    nombre_depenses = depenses_jour.count()
    
    # Bénéfice net du jour
    benefice_net = total_paiements - total_depenses
    
    # Commandes de la journée
    commandes_jour = Commande.objects.filter(
        date_commande__date=aujourd_hui
    )
    nombre_commandes = commandes_jour.count()
    commandes_payees = commandes_jour.filter(statut='payee').count()
    
    # Solde actuel de la caisse
    caisse = Caisse.get_instance()
    solde_caisse = caisse.solde_actuel
    
    # ===== PRÉPARATION DE L'EMAIL =====
    
    subject = f"📊 Rapport Quotidien - {aujourd_hui.strftime('%d/%m/%Y')}"
    
    body = f"""
╔═══════════════════════════════════════════════════════════════╗
║           RAPPORT QUOTIDIEN DES VENTES - RESTAURANT          ║
╚═══════════════════════════════════════════════════════════════╝

📅 Date : {aujourd_hui.strftime('%A %d %B %Y')}
🕐 Généré le : {maintenant.strftime('%d/%m/%Y à %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ DE LA JOURNÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 REVENUS
   • Nombre de paiements : {nombre_paiements}
   • Montant total : {total_paiements:,.0f} GNF

💸 DÉPENSES
   • Nombre de dépenses : {nombre_depenses}
   • Montant total : {total_depenses:,.0f} GNF

📈 BÉNÉFICE NET DU JOUR
   • {benefice_net:,.0f} GNF

📦 ACTIVITÉ COMMANDES
   • Commandes créées : {nombre_commandes}
   • Commandes payées : {commandes_payees}
   • Taux de conversion : {(commandes_payees/nombre_commandes*100) if nombre_commandes > 0 else 0:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 ÉTAT DE LA CAISSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Solde actuel : {solde_caisse:,.0f} GNF
"""

    # Ajouter le détail des dépenses si il y en a
    if nombre_depenses > 0:
        body += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        body += "💸 DÉTAIL DES DÉPENSES\n"
        body += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for depense in depenses_jour:
            body += f"   • {depense.motif[:50]}\n"
            body += f"     Montant : {depense.montant:,.0f} GNF\n"
            body += f"     Par : {depense.enregistree_par.login}\n\n"
    
    body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  Ceci est un envoi automatique quotidien.
   Le solde de la caisse est mis à jour automatiquement à chaque 
   paiement et dépense. Ce rapport est envoyé à 18h00.

🔗 Accédez au dashboard pour plus de détails :
   https://votre-site.com/dashboard/analytics/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Restaurant Manager - Système de Gestion
© 2025 Souleymane Diallo
"""

    # ===== ENVOI DE L'EMAIL =====
    
    to_email = getattr(settings, 'REPORT_EMAIL_TO', None)
    
    if not to_email:
        return "❌ Aucune adresse email configurée (REPORT_EMAIL_TO)"
    
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.send(fail_silently=False)
        
        return f"✅ Rapport quotidien envoyé avec succès à {to_email}"
        
    except Exception as e:
        return f"❌ Erreur lors de l'envoi : {str(e)}"


@shared_task
def test_email():
    """
    Tâche de test pour vérifier que l'envoi d'email fonctionne
    Utilisez : python manage.py shell
    >>> from apps.dashboard.tasks import test_email
    >>> test_email.delay()
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject='🧪 Test Email - Restaurant Manager',
            message='Ceci est un email de test. Si vous recevez ce message, la configuration email fonctionne !',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.REPORT_EMAIL_TO],
            fail_silently=False,
        )
        return "✅ Email de test envoyé avec succès"
    except Exception as e:
        return f"❌ Erreur : {str(e)}"
