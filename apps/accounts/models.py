# apps/accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator

class UserRole(models.TextChoices):
    """Énumération des rôles utilisateurs"""
    TABLE = 'RTABLE', 'Table'
    SERVEUR = 'RSERVEUR', 'Serveur'
    CUISINIER = 'RCUISINIER', 'Cuisinier'
    COMPTABLE = 'RCOMPTABLE', 'Comptable'
    ADMIN = 'RADMIN', 'Administrateur'


class CustomUserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, login, password=None, role=UserRole.TABLE, **extra_fields):
        """Crée et sauvegarde un utilisateur"""
        if not login:
            raise ValueError('Le login est obligatoire')
        
        user = self.model(login=login, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, password=None, **extra_fields):
        """Crée un super utilisateur (admin)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(login, password, role=UserRole.ADMIN, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur personnalisé
    Tous les acteurs du système (tables, serveurs, etc.) sont des utilisateurs
    """
    login = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(6, "Le login doit contenir au moins 6 caractères"),
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='Le login doit être alphanumérique'
            )
        ],
        verbose_name="Identifiant"
    )
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.TABLE,
        verbose_name="Rôle"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_staff = models.BooleanField(default=False, verbose_name="Staff")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.login} ({self.get_role_display()})"
    
    def is_table(self):
        return self.role == UserRole.TABLE
    
    def is_serveur(self):
        return self.role == UserRole.SERVEUR
    
    def is_cuisinier(self):
        return self.role == UserRole.CUISINIER
    
    def is_comptable(self):
        return self.role == UserRole.COMPTABLE
    
    def is_admin(self):
        return self.role == UserRole.ADMIN