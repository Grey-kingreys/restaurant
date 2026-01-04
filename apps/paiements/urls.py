from django.urls import path
from . import views

app_name = 'paiements'

urlpatterns = [
    # Dashboard Caisse
    path('caisse/', views.caisse_dashboard, name='caisse_dashboard'),
    
    # Paiements
    path('paiements/', views.paiement_list, name='paiement_list'),
    
    # Dépenses
    path('depenses/', views.depense_list, name='depense_list'),
    path('depenses/ajouter/', views.depense_create, name='depense_create'),
    path('depenses/<int:depense_id>/', views.depense_detail, name='depense_detail'),
]