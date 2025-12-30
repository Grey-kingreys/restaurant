# apps/menu/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Plat(models.Model):
    """
    Représente un plat du menu
    Géré par les cuisiniers
    """
    nom = models.CharField(max_length=200, verbose_name="Nom du plat")
    
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )
    
    image = models.ImageField(
        upload_to='plats/',
        blank=True,
        null=True,
        verbose_name="Image du plat"
    )
    
    description = models.TextField(blank=True, verbose_name="Description")
    
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} - {self.prix_unitaire} GNF"