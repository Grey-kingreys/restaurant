from django.contrib import admin
from .models import Commande, CommandeItem


class CommandeItemInline(admin.TabularInline):
    """
    Affichage des items de commande directement dans la commande
    """
    model = CommandeItem
    extra = 0
    readonly_fields = ('plat', 'quantite', 'prix_unitaire', 'sous_total')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'montant_total', 'statut','serveur_ayant_servi', 'date_commande')
    list_filter = ('statut', 'date_commande', 'serveur_ayant_servi')
    search_fields = ('table__login', 'id', 'serveur_ayant_servi__login')
    readonly_fields = ('date_commande', 'date_modification')
    inlines = [CommandeItemInline]
    
    fieldsets = (
        ('Informations', {
            'fields': ('table', 'montant_total', 'statut', 'serveur_ayant_servi')
        }),
        ('Dates', {
            'fields': ('date_commande', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Seul l'admin peut supprimer
        return request.user.is_admin() if hasattr(request.user, 'is_admin') else request.user.is_superuser


@admin.register(CommandeItem)
class CommandeItemAdmin(admin.ModelAdmin):
    list_display = ('commande', 'plat', 'quantite', 'prix_unitaire', 'sous_total')
    list_filter = ('commande__date_commande',)
    search_fields = ('plat__nom', 'commande__id')
    readonly_fields = ('sous_total',)
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin() if hasattr(request.user, 'is_admin') else request.user.is_superuser