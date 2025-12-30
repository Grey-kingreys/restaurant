# apps/restaurant/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class TableRestaurant(models.Model):
    """
    Représente une table physique du restaurant
    Liée à un utilisateur de type TABLE
    """
    numero_table = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Numéro de table"
    )
    
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Nombre de places"
    )
    
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'RTABLE'},
        related_name='table_restaurant',
        verbose_name="Utilisateur associé"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Table"
        verbose_name_plural = "Tables"
        ordering = ['numero_table']
    
    def __str__(self):
        return f"Table {self.numero_table}"
    
    def get_current_status(self):
        """
        Retourne le statut actuel de la table
        États: LIBRE, EN_ATTENTE, SERVIE, PAYEE
        """
        from apps.commandes.models import Commande, StatutCommande
        
        derniere_commande = self.commandes.filter(
            statut__in=[StatutCommande.EN_ATTENTE, StatutCommande.SERVIE]
        ).order_by('-date_commande').first()
        
        if not derniere_commande:
            return 'LIBRE'
        
        return derniere_commande.statut
    
    def has_active_commande(self):
        """Vérifie si la table a une commande active"""
        from apps.commandes.models import Commande, StatutCommande
        
        return self.commandes.filter(
            statut__in=[StatutCommande.EN_ATTENTE, StatutCommande.SERVIE]
        ).exists()