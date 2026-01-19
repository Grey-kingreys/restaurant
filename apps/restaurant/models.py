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
        limit_choices_to={'role': 'Rtable'},
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


# Token de connexion via QR Code

import secrets
from django.utils import timezone

class TableToken(models.Model):
    """
    Token unique pour la connexion automatique via QR Code
    Invalide automatiquement si le mot de passe de la table change
    """
    table = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Rtable'},
        related_name='auth_token',
        verbose_name="Table associée"
    )
    
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Token d'authentification"
    )
    
    # Hash du mot de passe au moment de la génération du token
    # Permet de détecter si le mot de passe a changé
    password_hash = models.CharField(
        max_length=128,
        verbose_name="Hash du mot de passe"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_utilisation = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Token de table"
        verbose_name_plural = "Tokens de tables"
    
    def __str__(self):
        return f"Token - {self.table.login}"
    
    @classmethod
    def generer_token(cls, table):
        """
        Génère ou régénère un token pour une table
        """
        # Générer un token sécurisé de 64 caractères
        nouveau_token = secrets.token_urlsafe(48)
        
        # Récupérer ou créer le token
        token_obj, created = cls.objects.update_or_create(
            table=table,
            defaults={
                'token': nouveau_token,
                'password_hash': table.password,  # Hash Django du mot de passe
            }
        )
        
        return token_obj
    
    def est_valide(self):
        """
        Vérifie si le token est toujours valide
        (le mot de passe n'a pas changé)
        """
        return self.password_hash == self.table.password
    
    def marquer_utilise(self):
        """
        Marque le token comme utilisé (pour statistiques)
        """
        self.date_derniere_utilisation = timezone.now()
        self.save(update_fields=['date_derniere_utilisation'])
    
    def get_qr_url(self, request):
        """
        Retourne l'URL complète pour le QR code
        """
        from django.urls import reverse
        path = reverse('restaurant:qr_login', kwargs={'token': self.token})
        return request.build_absolute_uri(path)