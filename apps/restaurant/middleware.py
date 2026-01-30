# apps/restaurant/middleware.py

from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from apps.restaurant.models import TableSession


class AutoLogoutTableMiddleware:
    """
    Middleware qui déconnecte automatiquement les tables 
    1 minute après le paiement via le token de session
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Nettoyer les sessions expirées (périodiquement)
        TableSession.nettoyer_sessions_expirees()
        
        # Vérifier uniquement pour les utilisateurs connectés avec rôle Table
        if request.user.is_authenticated and request.user.is_table():
            
            # Récupérer le token de session stocké
            session_token = request.session.get('table_session_token')
            
            if session_token:
                try:
                    session_table = TableSession.objects.get(
                        session_token=session_token,
                        table=request.user
                    )
                    
                    # Vérifier si la session doit expirer
                    if session_table.doit_etre_expiree():
                        # Vérifier qu'il n'y a pas de nouvelle commande en cours
                        from apps.commandes.models import Commande
                        
                        a_commande_en_cours = Commande.objects.filter(
                            table=request.user,
                            statut__in=['en_attente', 'servie']
                        ).exists()
                        
                        if not a_commande_en_cours:
                            # Expirer la session
                            session_table.expirer()
                            
                            # Déconnexion automatique
                            messages.info(
                                request,
                                "⏱️ Votre session a expiré (1 minute après le paiement). "
                                "Scannez à nouveau le QR Code pour une nouvelle commande."
                            )
                            logout(request)
                            return redirect('accounts:login')
                    
                    # Session toujours active - vérifier si elle est marquée comme inactive
                    elif not session_table.est_active:
                        messages.info(
                            request,
                            "⏱️ Votre session a expiré. "
                            "Scannez à nouveau le QR Code pour commander."
                        )
                        logout(request)
                        return redirect('accounts:login')
                
                except TableSession.DoesNotExist:
                    # Session invalide ou supprimée
                    pass
        
        response = self.get_response(request)
        return response