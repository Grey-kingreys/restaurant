# apps/restaurant/urls.py
from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # ==========================================
    # URLs ADMIN - CRUD Tables Physiques
    # ==========================================
    path('admin/tables/', views.table_list_admin, name='table_list_admin'),
    path('admin/tables/create/', views.table_create, name='table_create'),
    path('admin/tables/<int:pk>/', views.table_detail_admin, name='table_detail_admin'),
    path('admin/tables/<int:pk>/update/', views.table_update, name='table_update'),
    path('admin/tables/<int:pk>/delete/', views.table_delete, name='table_delete'),
    
    # ==========================================
    # 🆕 QR CODE - ADMIN
    # ==========================================
    path('admin/tables/<int:table_id>/qr/', views.afficher_qr_code, name='qr_display'),
    path('admin/tables/<int:table_id>/qr/generate/', views.generer_qr_code, name='qr_generate'),
    
    # ==========================================
    # 🆕 CONNEXION AUTOMATIQUE VIA QR
    # ==========================================
    path('qr/<str:token>/', views.qr_login, name='qr_login'),
    
    # ==========================================
    # URLs pour les SERVEURS (Rserveur)
    # ==========================================
    path('tables/', views.table_list_serveur, name='table_list_serveur'),
    path('tables/<int:table_id>/', views.table_detail_serveur, name='table_detail_serveur'),
    
    # Gestion des commandes
    path('commandes/', views.commande_list_serveur, name='commande_list_serveur'),
    path('commandes/<int:commande_id>/', views.commande_detail_serveur, name='commande_detail_serveur'),
    
    # Actions sur les commandes
    path('commandes/<int:commande_id>/servie/', views.commande_marquer_servie, name='commande_marquer_servie'),
    path('commandes/<int:commande_id>/payee/', views.commande_marquer_payee, name='commande_marquer_payee'),
]