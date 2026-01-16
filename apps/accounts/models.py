# apps/accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator, RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError("Le login est obligatoire")
        
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('role', 'Radmin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Rtable', 'Table'),
        ('Rserveur', 'Serveur/Servante'),
        ('Rcuisinier', 'Cuisinier'),
        ('Rcomptable', 'Comptable'),
        ('Radmin', 'Administrateur'),
    ]
    
    # Champs existants
    login = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)
    
    # ✅ NOUVEAUX CHAMPS (optionnels dans le modèle, obligatoires via le formulaire)
    nom_complet = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nom complet",
        help_text="Obligatoire pour les serveurs, cuisiniers, comptables et admins"
    )
    
    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        validators=[EmailValidator()],
        verbose_name="Adresse email",
        help_text="Obligatoire pour les serveurs, cuisiniers, comptables et admins"
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{9,20}$',
                message="Format valide: +224XXXXXXXXX ou XXXXXXXXX (9-20 chiffres)"
            )
        ],
        verbose_name="Numéro de téléphone",
        help_text="Obligatoire pour les serveurs, cuisiniers, comptables et admins"
    )
    
    # Champs requis par Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['role']
    
    class Meta:
        db_table = 'user'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        if self.nom_complet and not self.is_table():
            return f"{self.nom_complet} ({self.login})"
        return f"{self.login} ({self.get_role_display()})"
    
    # Méthodes helper pour vérifier les rôles
    def is_table(self):
        return self.role == 'Rtable'
    
    def is_serveur(self):
        return self.role == 'Rserveur'
    
    def is_cuisinier(self):
        return self.role == 'Rcuisinier'
    
    def is_comptable(self):
        return self.role == 'Rcomptable'
    
    def is_admin(self):
        return self.role == 'Radmin'
    
    def requires_personal_info(self):
        """
        Retourne True si le rôle nécessite des informations personnelles
        (tous les rôles SAUF Rtable)
        """
        return self.role != 'Rtable'