from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # ==========================================
    # URLs pour les TABLES (Rtable)
    # ==========================================
    path('plats/', views.plat_list_table, name='table_list'),
    path('plats/<int:pk>/', views.plat_detail_table, name='table_detail'),
    
    # ==========================================
    # URLs pour les CUISINIERS (Rcuisinier)
    # ==========================================
    path('cuisinier/', views.plat_list_cuisinier, name='cuisinier_list'),
    path('cuisinier/ajouter/', views.plat_create, name='plat_create'),
    path('cuisinier/<int:pk>/', views.plat_detail_cuisinier, name='cuisinier_detail'),
    path('cuisinier/<int:pk>/modifier/', views.plat_update, name='plat_update'),
    path('cuisinier/<int:pk>/toggle/', views.plat_toggle_disponibilite, name='plat_toggle'),
]