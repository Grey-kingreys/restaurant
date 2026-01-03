from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    # Panier
    path('panier/', views.cart_detail, name='cart_detail'),
    path('panier/ajouter/<int:plat_id>/', views.cart_add, name='cart_add'),
    path('panier/modifier/<int:plat_id>/', views.cart_update, name='cart_update'),
    path('panier/retirer/<int:plat_id>/', views.cart_remove, name='cart_remove'),
    
    # Commandes
    path('valider/', views.commande_valider, name='commande_valider'),
    path('mes-commandes/', views.commande_list, name='commande_list'),
    path('commande/<int:commande_id>/', views.commande_detail, name='commande_detail'),
]