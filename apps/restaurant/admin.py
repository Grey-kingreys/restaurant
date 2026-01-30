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



from django.contrib import admin
from .models import TableRestaurant, TableSession


@admin.register(TableSession)
class TableSessionAdmin(admin.ModelAdmin):
    list_display = [
        'table',
        'date_creation',
        'date_paiement',
        'est_active',
        'temps_restant'
    ]
    
    list_filter = ['est_active', 'date_creation', 'date_paiement']
    search_fields = ['table__login', 'session_token']
    readonly_fields = ['session_token', 'django_session_key', 'date_creation', 'date_derniere_activite']
    
    def temps_restant(self, obj):
        """Affiche le temps restant avant expiration"""
        if not obj.date_paiement:
            return "Pas de paiement"
        
        if not obj.est_active:
            return "❌ Expirée"
        
        from django.utils import timezone
        from datetime import timedelta
        
        temps_ecoule = timezone.now() - obj.date_paiement
        temps_restant = timedelta(minutes=1) - temps_ecoule
        
        if temps_restant.total_seconds() <= 0:
            return "⏱️ Devrait expirer"
        
        secondes = int(temps_restant.total_seconds())
        return f"⏱️ {secondes}s restantes"
    
    temps_restant.short_description = "Temps restant"