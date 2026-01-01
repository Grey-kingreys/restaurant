from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

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
    
    login = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)
    
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