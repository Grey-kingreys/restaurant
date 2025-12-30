# apps/commandes/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class StatutCommande(models.TextChoices):
    """États possibles d'une commande"""
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    SERVIE = 'SERVIE', 'Servie'
    PAYEE = 'PAYEE', 'Payée'


class CommandeManager(models.Manager):
    """Manager personnalisé avec filtres utiles"""
    
    def en_attente(self):
        return self.filter(statut=StatutCommande.EN_ATTENTE)
    
    def servies(self):
        return self.filter(statut=StatutCommande.SERVIE)
    
    def payees(self):
        return self.filter(statut=StatutCommande.PAYEE)
    
    def pour_table(self, table):
        return self.filter(table=table)


class Commande(models.Model):
    """
    Commande validée par une table
    Créée quand le client valide son panier (en session)
    """
    table = models.ForeignKey(
        'restaurant.TableRestaurant',
        on_delete=models.CASCADE,
        related_name='commandes',
        verbose_name="Table"
    )
    
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant total"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=StatutCommande.choices,
        default=StatutCommande.EN_ATTENTE,
        verbose_name="Statut"
    )
    
    date_commande = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    date_modification = models.DateTimeField(auto_now=True)
    
    # Optionnel: traçabilité
    serveur_ayant_servi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'RSERVEUR'},
        related_name='commandes_servies',
        verbose_name="Serveur"
    )
    
    objects = CommandeManager()
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']
    
    def __str__(self):
        return f"Commande #{self.pk} - {self.table} - {self.montant_total} GNF"
    
    def calculer_montant_total(self):
        """Recalcule le montant total basé sur les lignes"""
        total = sum(
            ligne.quantite * ligne.prix_unitaire 
            for ligne in self.lignes.all()
        )
        return total
    
    def peut_etre_servie(self):
        """Vérifie si la commande peut être marquée comme servie"""
        return self.statut == StatutCommande.EN_ATTENTE
    
    def peut_etre_payee(self):
        """Vérifie si la commande peut être payée"""
        return self.statut == StatutCommande.SERVIE
    
    def marquer_servie(self, serveur=None):
        """Marque la commande comme servie"""
        if self.peut_etre_servie():
            self.statut = StatutCommande.SERVIE
            if serveur:
                self.serveur_ayant_servi = serveur
            self.save()
            return True
        return False
    
    def marquer_payee(self):
        """Marque la commande comme payée et crée le paiement"""
        if self.peut_etre_payee():
            self.statut = StatutCommande.PAYEE
            self.save()
            
            # Créer le paiement (importé ici pour éviter import circulaire)
            from apps.paiements.models import Paiement
            paiement = Paiement.objects.create(
                commande=self,
                montant=self.montant_total
            )
            
            # Mettre à jour la caisse
            from apps.paiements.services import CaisseService
            CaisseService.ajouter_paiement(paiement)
            
            return True
        return False


class LigneCommande(models.Model):
    """
    Une ligne de commande = un plat avec sa quantité
    ATTENTION: Nom différent de "CommandeItem" pour éviter confusion
    """
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name="Commande"
    )
    
    plat = models.ForeignKey(
        'menu.Plat',
        on_delete=models.PROTECT,  # Ne pas supprimer si utilisé dans commande
        related_name='lignes_commande',
        verbose_name="Plat"
    )
    
    quantite = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name="Quantité"
    )
    
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix unitaire"
    )
    
    note = models.TextField(blank=True, verbose_name="Note")
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
        unique_together = ['commande', 'plat']  # Un plat une seule fois par commande
    
    def __str__(self):
        return f"{self.quantite}x {self.plat.nom}"
    
    def get_montant_ligne(self):
        """Calcule le montant de cette ligne"""
        return self.quantite * self.prix_unitaire
    
    def save(self, *args, **kwargs):
        """Override save pour capturer le prix au moment de la commande"""
        if not self.prix_unitaire:
            self.prix_unitaire = self.plat.prix_unitaire
        super().save(*args, **kwargs)