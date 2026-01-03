from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from apps.menu.models import Plat


class Commande(models.Model):
    """
    Représente une commande passée par une table
    """
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('servie', 'Servie'),
        ('payee', 'Payée'),
    ]
    
    table = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='commandes',
        limit_choices_to={'role': 'Rtable'}
    )
    montant_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    statut = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='en_attente'
    )
    date_commande = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_commande']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
    
    def __str__(self):
        return f"Commande #{self.id} - {self.table.login} - {self.get_statut_display()}"
    
    def est_modifiable(self):
        """Une commande ne peut être modifiée que si elle est en attente"""
        return self.statut == 'en_attente'
    
    def peut_etre_servie(self):
        """Une commande peut être marquée comme servie si elle est en attente"""
        return self.statut == 'en_attente'
    
    def peut_etre_payee(self):
        """Une commande peut être payée si elle est servie"""
        return self.statut == 'servie'


class CommandeItem(models.Model):
    """
    Représente une ligne de commande (un plat dans une commande)
    """
    commande = models.ForeignKey(
        Commande, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    plat = models.ForeignKey(
        Plat, 
        on_delete=models.PROTECT,
        related_name='commande_items'
    )
    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    prix_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'
        unique_together = ['commande', 'plat']
    
    def __str__(self):
        return f"{self.plat.nom} x{self.quantite}"
    
    @property
    def sous_total(self):
        """Calcule le sous-total de cette ligne"""
        return self.quantite * self.prix_unitaire
    
    def save(self, *args, **kwargs):
        """Enregistre le prix unitaire actuel du plat"""
        if not self.prix_unitaire:
            self.prix_unitaire = self.plat.prix_unitaire
        super().save(*args, **kwargs)