# apps/paiements/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db import transaction

class Paiement(models.Model):
    """
    Enregistrement d'un paiement
    Créé automatiquement quand une commande est marquée comme payée
    """
    commande = models.OneToOneField(
        'commandes.Commande',
        on_delete=models.CASCADE,
        related_name='paiement',
        verbose_name="Commande"
    )
    
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )
    
    date_paiement = models.DateTimeField(auto_now_add=True, verbose_name="Date de paiement")
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement #{self.pk} - {self.montant} GNF - {self.date_paiement}"


class Caisse(models.Model):
    """
    Caisse du restaurant
    Il ne doit y avoir qu'une seule instance de ce modèle
    """
    solde_actuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Solde actuel"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Caisse"
        verbose_name_plural = "Caisses"
    
    def __str__(self):
        return f"Caisse - Solde: {self.solde_actuel} GNF"
    
    @classmethod
    def get_instance(cls):
        """Récupère ou crée l'instance unique de la caisse"""
        caisse, created = cls.objects.get_or_create(pk=1)
        return caisse
    
    def peut_effectuer_depense(self, montant):
        """Vérifie si une dépense peut être effectuée"""
        return self.solde_actuel >= montant


class Depense(models.Model):
    """
    Dépense enregistrée par le comptable
    """
    motif = models.CharField(max_length=255, verbose_name="Motif")
    
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )
    
    date_depense = models.DateField(verbose_name="Date de la dépense")
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    
    enregistree_par = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'RCOMPTABLE'},
        related_name='depenses_enregistrees',
        verbose_name="Enregistrée par"
    )
    
    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-date_depense']
    
    def __str__(self):
        return f"{self.motif} - {self.montant} GNF"

