from django.contrib import admin
from .models import TableRestaurant


@admin.register(TableRestaurant)
class TableRestaurantAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les tables physiques
    """
    list_display = [
        'numero_table',
        'nombre_places',
        'utilisateur_login',
        'utilisateur_actif',
        'date_creation',
    ]
    
    list_filter = [
        'nombre_places',
        'date_creation',
        'utilisateur__actif',
    ]
    
    search_fields = [
        'numero_table',
        'utilisateur__login',
    ]
    
    readonly_fields = [
        'date_creation',
        'date_modification',
    ]
    
    fieldsets = (
        ('Informations de la table', {
            'fields': ('numero_table', 'nombre_places')
        }),
        ('Association', {
            'fields': ('utilisateur',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def utilisateur_login(self, obj):
        """Affiche le login de l'utilisateur"""
        return obj.utilisateur.login
    utilisateur_login.short_description = "Utilisateur"
    utilisateur_login.admin_order_field = "utilisateur__login"
    
    def utilisateur_actif(self, obj):
        """Affiche le statut actif de l'utilisateur"""
        if obj.utilisateur.actif:
            return "✅ Actif"
        return "❌ Inactif"
    utilisateur_actif.short_description = "Statut"
    utilisateur_actif.admin_order_field = "utilisateur__actif"
    
    def get_queryset(self, request):
        """Optimisation des requêtes"""
        return super().get_queryset(request).select_related('utilisateur')