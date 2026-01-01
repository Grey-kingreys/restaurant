from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Plat(models.Model):
    """
    Modèle représentant un plat du menu
    """
    nom = models.CharField(
        max_length=200,
        verbose_name="Nom du plat",
        help_text="Nom du plat (max 200 caractères)"
    )
    
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True,
        help_text="Description détaillée du plat"
    )
    
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire",
        help_text="Prix en GNF (Francs Guinéens)"
    )
    
    image = models.ImageField(
        upload_to='plats/%Y/%m/',
        verbose_name="Image du plat",
        blank=True,
        null=True,
        help_text="Image du plat (formats acceptés: JPG, PNG)"
    )
    
    disponible = models.BooleanField(
        default=True,
        verbose_name="Disponible",
        help_text="Le plat est-il disponible à la commande ?"
    )
    
    # Catégories possibles
    CATEGORIE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('PLAT', 'Plat principal'),
        ('DESSERT', 'Dessert'),
        ('BOISSON', 'Boisson'),
        ('ACCOMPAGNEMENT', 'Accompagnement'),
    ]
    
    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIE_CHOICES,
        default='PLAT',
        verbose_name="Catégorie"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    # Manager personnalisé pour les plats disponibles
    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"
        ordering = ['categorie', 'nom']
        indexes = [
            models.Index(fields=['disponible', 'categorie']),
            models.Index(fields=['nom']),
        ]
    
    def __str__(self):
        statut = "✅" if self.disponible else "❌"
        return f"{statut} {self.nom} - {self.prix_unitaire} GNF"
    
    @property
    def prix_formate(self):
        """Retourne le prix formaté avec séparateur de milliers"""
        return f"{self.prix_unitaire:,.0f}".replace(',', ' ')
    
    def get_image_url(self):
        """Retourne l'URL de l'image ou une image par défaut"""
        if self.image:
            return self.image.url
        return '/static/images/plat-default.jpg'


# Manager personnalisé pour filtrer facilement les plats disponibles
class PlatDisponibleManager(models.Manager):
    """Manager pour récupérer uniquement les plats disponibles"""
    def get_queryset(self):
        return super().get_queryset().filter(disponible=True)


# Ajouter le manager au modèle
Plat.add_to_class('disponibles', PlatDisponibleManager())