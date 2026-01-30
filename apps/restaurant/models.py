# apps/restaurant/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid
from django.utils import timezone
from datetime import timedelta

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




class TableSession(models.Model):
    """
    Représente une session de connexion pour une table
    Expire 1 minute après le paiement de la commande
    """
    table = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Rtable'},
        related_name='sessions',
        verbose_name="Table"
    )
    
    session_token = models.CharField(
        max_length=64,
        unique=True,
        default=uuid.uuid4,
        verbose_name="Token de session"
    )
    
    django_session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Clé de session Django"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_activite = models.DateTimeField(auto_now=True)
    
    # Marqueur de paiement
    commande_payee = models.ForeignKey(
        'commandes.Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='session_associee',
        verbose_name="Commande payée"
    )
    
    date_paiement = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date du paiement"
    )
    
    est_active = models.BooleanField(
        default=True,
        verbose_name="Session active"
    )
    
    class Meta:
        verbose_name = "Session de table"
        verbose_name_plural = "Sessions de tables"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Session {self.table.login} - {self.date_creation}"
    
    def marquer_payement(self, commande):
        """
        Marque qu'une commande a été payée
        Lance le compte à rebours de 1 minute
        """
        self.commande_payee = commande
        self.date_paiement = timezone.now()
        self.save()
    
    def doit_etre_expiree(self):
        """
        Vérifie si la session doit expirer
        (1 minute après le paiement)
        """
        if not self.date_paiement:
            return False
        
        temps_ecoule = timezone.now() - self.date_paiement
        return temps_ecoule > timedelta(minutes=1)
    
    def expirer(self):
        """
        Expire la session
        """
        self.est_active = False
        self.save()
    
    @classmethod
    def nettoyer_sessions_expirees(cls):
        """
        Nettoie les sessions expirées
        À appeler périodiquement ou via le middleware
        """
        sessions_a_expirer = cls.objects.filter(
            est_active=True,
            date_paiement__isnull=False,
            date_paiement__lt=timezone.now() - timedelta(minutes=1)
        )
        
        count = sessions_a_expirer.update(est_active=False)
        return count