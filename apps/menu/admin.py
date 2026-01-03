from django.contrib import admin
from .models import Plat


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les plats
    """
    list_display = [
        'nom',
        'categorie',
        'prix_formate_admin',
        'disponible_badge',
        'date_creation',
        'date_modification'
    ]
    
    list_filter = [
        'disponible',
        'categorie',
        'date_creation',
    ]
    
    search_fields = [
        'nom',
        'description',
    ]
    
    readonly_fields = [
        'date_creation',
        'date_modification',
        'image_preview'
    ]
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'description', 'categorie')
        }),
        ('Prix', {
            'fields': ('prix_unitaire',)
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Disponibilité', {
            'fields': ('disponible',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = None
    
    actions = ['activer_plats', 'desactiver_plats']
    
    def prix_formate_admin(self, obj):
        """Affiche le prix formaté dans l'admin"""
        return f"{obj.prix_unitaire:,.0f} GNF".replace(',', ' ')
    prix_formate_admin.short_description = "Prix"
    
    def disponible_badge(self, obj):
        """Affiche un badge pour la disponibilité"""
        if obj.disponible:
            return "✅ Disponible"
        return "❌ Non disponible"
    disponible_badge.short_description = "État"
    
    def image_preview(self, obj):
        """Prévisualisation de l'image dans l'admin"""
        if obj.image:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return "Pas d'image"
    image_preview.short_description = "Prévisualisation"
    
    def activer_plats(self, request, queryset):
        """Action pour activer plusieurs plats"""
        updated = queryset.update(disponible=True)
        self.message_user(request, f"{updated} plat(s) activé(s)")
    activer_plats.short_description = "✅ Activer les plats sélectionnés"
    
    def desactiver_plats(self, request, queryset):
        """Action pour désactiver plusieurs plats"""
        updated = queryset.update(disponible=False)
        self.message_user(request, f"{updated} plat(s) désactivé(s)")
    desactiver_plats.short_description = "❌ Désactiver les plats sélectionnés"