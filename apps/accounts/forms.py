# apps/accounts/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import User
import re


class LoginForm(AuthenticationForm):
    # ... (code existant reste inchangé)
    pass


class UserCreationForm(forms.ModelForm):
    """
    Formulaire pour créer un nouvel utilisateur
    Validation conditionnelle : nom_complet, email, telephone obligatoires sauf pour Rtable
    """
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
            'placeholder': 'Minimum 8 caractères',
        }),
        help_text='Minimum 8 caractères avec lettres, chiffres et caractères spéciaux',
    )
    
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
            'placeholder': 'Confirmer le mot de passe',
        }),
        help_text='Entrez le même mot de passe pour vérification',
    )
    
    class Meta:
        model = User
        fields = ['login', 'role', 'nom_complet', 'email', 'telephone', 'actif']
        
        widgets = {
            'login': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
                'placeholder': 'Ex: TABLE005, SERV002',
                'autofocus': True,
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
                'onchange': 'togglePersonalInfoFields(this.value)',
            }),
            'nom_complet': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
                'placeholder': 'Ex: Mamadou Sow',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
                'placeholder': 'Ex: mamadou.sow@restaurant.com',
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
                'placeholder': 'Ex: +224624815998 ou 624815998',
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
            }),
        }
        
        labels = {
            'login': 'Identifiant (Login)',
            'role': 'Rôle de l\'utilisateur',
            'nom_complet': 'Nom complet',
            'email': 'Adresse email',
            'telephone': 'Numéro de téléphone',
            'actif': 'Compte actif',
        }
        
        help_texts = {
            'login': 'Minimum 6 caractères alphanumériques (ex: TABLE001)',
            'role': 'Définit les permissions de l\'utilisateur',
            'nom_complet': '⚠️ Obligatoire pour les serveurs, cuisiniers, comptables et admins',
            'email': '⚠️ Obligatoire pour les serveurs, cuisiniers, comptables et admins',
            'telephone': '⚠️ Obligatoire pour les serveurs, cuisiniers, comptables et admins',
            'actif': 'Si décoché, l\'utilisateur ne pourra pas se connecter',
        }
    
    def clean_login(self):
        """Validation du login"""
        login = self.cleaned_data.get('login')
        
        if not login:
            raise forms.ValidationError("Le login est obligatoire")
        
        if len(login) < 6:
            raise forms.ValidationError("Le login doit contenir au moins 6 caractères")
        
        if not re.match(r'^[a-zA-Z0-9]+$', login):
            raise forms.ValidationError(
                "Le login ne peut contenir que des lettres et des chiffres"
            )
        
        if User.objects.filter(login=login).exists():
            raise forms.ValidationError(f"Le login '{login}' est déjà utilisé")
        
        return login
    
    def clean_password1(self):
        """Validation du mot de passe"""
        password = self.cleaned_data.get('password1')
        
        if not password:
            raise forms.ValidationError("Le mot de passe est obligatoire")
        
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères")
        
        if not re.search(r'[a-zA-Z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre")
        
        if not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial")
        
        return password
    
    def clean_email(self):
        """Validation de l'email"""
        email = self.cleaned_data.get('email')
        role = self.cleaned_data.get('role')
        
        # ✅ Obligatoire sauf pour Rtable
        if role and role != 'Rtable':
            if not email:
                raise forms.ValidationError("L'email est obligatoire pour ce rôle")
        
        # Vérifier l'unicité si fourni
        if email:
            existing = User.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(f"L'email '{email}' est déjà utilisé")
        
        return email
    
    def clean_nom_complet(self):
        """Validation du nom complet"""
        nom_complet = self.cleaned_data.get('nom_complet')
        role = self.cleaned_data.get('role')
        
        # ✅ Obligatoire sauf pour Rtable
        if role and role != 'Rtable':
            if not nom_complet or not nom_complet.strip():
                raise forms.ValidationError("Le nom complet est obligatoire pour ce rôle")
            
            # Minimum 3 caractères
            if len(nom_complet.strip()) < 3:
                raise forms.ValidationError("Le nom complet doit contenir au moins 3 caractères")
        
        return nom_complet.strip() if nom_complet else nom_complet
    
    def clean_telephone(self):
        """Validation du téléphone"""
        telephone = self.cleaned_data.get('telephone')
        role = self.cleaned_data.get('role')
        
        # ✅ Obligatoire sauf pour Rtable
        if role and role != 'Rtable':
            if not telephone:
                raise forms.ValidationError("Le numéro de téléphone est obligatoire pour ce rôle")
        
        # Vérifier l'unicité si fourni
        if telephone:
            existing = User.objects.filter(telephone=telephone)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(f"Le numéro '{telephone}' est déjà utilisé")
        
        return telephone
    
    def clean(self):
        """Vérification de la correspondance des mots de passe"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Enregistrement avec hashage du mot de passe"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier un utilisateur existant
    """
    class Meta:
        model = User
        fields = ['login', 'role', 'nom_complet', 'email', 'telephone', 'actif']
        
        widgets = {
            'login': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
                'onchange': 'togglePersonalInfoFields(this.value)',
            }),
            'nom_complet': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-900',
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
            }),
        }
        
        labels = {
            'login': 'Identifiant (Login)',
            'role': 'Rôle de l\'utilisateur',
            'nom_complet': 'Nom complet',
            'email': 'Adresse email',
            'telephone': 'Numéro de téléphone',
            'actif': 'Compte actif',
        }
        
        help_texts = {
            'login': 'Minimum 6 caractères alphanumériques',
            'role': 'Modifie les permissions de l\'utilisateur',
            'nom_complet': '⚠️ Obligatoire pour les serveurs, cuisiniers, comptables et admins',
            'email': '⚠️ Obligatoire pour les serveurs, cuisiniers, comptables et admins',
            'telephone': '⚠️ Obligatoire pour les serveurs, cuisiniers, comptables et admins',
            'actif': 'Si décoché, l\'utilisateur ne pourra pas se connecter',
        }
    
    # ✅ CORRECTION : Redéfinir clean_login pour UserUpdateForm
    def clean_login(self):
        """Validation du login (en tenant compte de l'instance existante)"""
        login = self.cleaned_data.get('login')
        
        if not login:
            raise forms.ValidationError("Le login est obligatoire")
        
        if len(login) < 6:
            raise forms.ValidationError("Le login doit contenir au moins 6 caractères")
        
        if not re.match(r'^[a-zA-Z0-9]+$', login):
            raise forms.ValidationError(
                "Le login ne peut contenir que des lettres et des chiffres"
            )
        
        # ✅ Exclure l'instance actuelle de la vérification d'unicité
        existing = User.objects.filter(login=login)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError(f"Le login '{login}' est déjà utilisé")
        
        return login
    
    # Réutiliser les autres validations de UserCreationForm
    clean_email = UserCreationForm.clean_email
    clean_nom_complet = UserCreationForm.clean_nom_complet
    clean_telephone = UserCreationForm.clean_telephone