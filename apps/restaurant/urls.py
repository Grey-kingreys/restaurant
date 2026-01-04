from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # ==========================================
    # URLs pour les SERVEURS (Rserveur)
    # ==========================================
    
    # Gestion des tables
    path('tables/', views.table_list_serveur, name='table_list_serveur'),
    path('tables/<int:table_id>/', views.table_detail_serveur, name='table_detail_serveur'),
    
    # Gestion des commandes
    path('commandes/', views.commande_list_serveur, name='commande_list_serveur'),
    path('commandes/<int:commande_id>/', views.commande_detail_serveur, name='commande_detail_serveur'),
    
    # Actions sur les commandes
    path('commandes/<int:commande_id>/servie/', views.commande_marquer_servie, name='commande_marquer_servie'),
    path('commandes/<int:commande_id>/payee/', views.commande_marquer_payee, name='commande_marquer_payee'),
]