# apps/accounts/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import User
import re


# ==========================================
# FORMULAIRE DE CONNEXION (Existant)
# ==========================================

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Login',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 text-gray-900 bg-gray-50 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-gray-400 transition duration-150',
            'placeholder': 'TABLE001 ou SERV123',
            'autofocus': True
        }),
        error_messages={
            'required': 'Le login est obligatoire',
        }
    )
    
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 text-gray-900 bg-gray-50 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-gray-400 transition duration-150',
            'placeholder': '••••••••'
        }),
        error_messages={
            'required': 'Le mot de passe est obligatoire',
        }
    )
    
    error_messages = {
        'invalid_login': 'Login ou mot de passe incorrect. Veuillez réessayer.',
        'inactive': 'Ce compte est inactif.',
    }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not username:
            raise forms.ValidationError("Le login est obligatoire")
        
        # Vérification longueur minimum
        if len(username) < 6:
            raise forms.ValidationError("Le login doit contenir au moins 6 caractères")
        
        # Vérification alphanumérique
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise forms.ValidationError("Le login ne peut contenir que des lettres et des chiffres")
        
        return username
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Login ou mot de passe incorrect. Veuillez réessayer.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


# ==========================================
# FORMULAIRE DE CRÉATION D'UTILISATEUR
# ==========================================

class UserCreationForm(forms.ModelForm):
    """
    Formulaire pour créer un nouvel utilisateur
    """
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
            'placeholder': 'Minimum 8 caractères',
        }),
        help_text='Minimum 8 caractères avec lettres, chiffres et caractères spéciaux',
    )
    
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
            'placeholder': 'Confirmer le mot de passe',
        }),
        help_text='Entrez le même mot de passe pour vérification',
    )
    
    class Meta:
        model = User
        fields = ['login', 'role', 'actif']
        
        widgets = {
            'login': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
                'placeholder': 'Ex: TABLE005, SERV002',
                'autofocus': True,
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
            }),
        }
        
        labels = {
            'login': 'Identifiant (Login)',
            'role': 'Rôle de l\'utilisateur',
            'actif': 'Compte actif',
        }
        
        help_texts = {
            'login': 'Minimum 6 caractères alphanumériques (ex: TABLE001)',
            'role': 'Définit les permissions de l\'utilisateur',
            'actif': 'Si décoché, l\'utilisateur ne pourra pas se connecter',
        }
    
    def clean_login(self):
        """Validation du login"""
        login = self.cleaned_data.get('login')
        
        if not login:
            raise forms.ValidationError("Le login est obligatoire")
        
        # Vérification longueur minimum
        if len(login) < 6:
            raise forms.ValidationError("Le login doit contenir au moins 6 caractères")
        
        # Vérification alphanumérique
        if not re.match(r'^[a-zA-Z0-9]+$', login):
            raise forms.ValidationError(
                "Le login ne peut contenir que des lettres et des chiffres (sans espaces ni caractères spéciaux)"
            )
        
        # Vérifier l'unicité
        if User.objects.filter(login=login).exists():
            raise forms.ValidationError(f"Le login '{login}' est déjà utilisé")
        
        return login
    
    def clean_password1(self):
        """Validation du mot de passe"""
        password = self.cleaned_data.get('password1')
        
        if not password:
            raise forms.ValidationError("Le mot de passe est obligatoire")
        
        # Minimum 8 caractères
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères")
        
        # Au moins une lettre
        if not re.search(r'[a-zA-Z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre")
        
        # Au moins un chiffre
        if not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre")
        
        # Au moins un caractère spécial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial")
        
        return password
    
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


# ==========================================
# FORMULAIRE DE MODIFICATION D'UTILISATEUR
# ==========================================

class UserUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier un utilisateur existant
    Note : Le mot de passe n'est pas modifiable via ce formulaire
    """
    class Meta:
        model = User
        fields = ['login', 'role', 'actif']
        
        widgets = {
            'login': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
                'placeholder': 'Ex: TABLE005, SERV002',
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
            }),
        }
        
        labels = {
            'login': 'Identifiant (Login)',
            'role': 'Rôle de l\'utilisateur',
            'actif': 'Compte actif',
        }
        
        help_texts = {
            'login': 'Minimum 6 caractères alphanumériques',
            'role': 'Modifie les permissions de l\'utilisateur',
            'actif': 'Si décoché, l\'utilisateur ne pourra pas se connecter',
        }
    
    def clean_login(self):
        """Validation du login (vérifier l'unicité sauf pour l'instance actuelle)"""
        login = self.cleaned_data.get('login')
        
        if not login:
            raise forms.ValidationError("Le login est obligatoire")
        
        # Vérification longueur minimum
        if len(login) < 6:
            raise forms.ValidationError("Le login doit contenir au moins 6 caractères")
        
        # Vérification alphanumérique
        if not re.match(r'^[a-zA-Z0-9]+$', login):
            raise forms.ValidationError(
                "Le login ne peut contenir que des lettres et des chiffres"
            )
        
        # Vérifier l'unicité (exclure l'instance actuelle)
        query = User.objects.filter(login=login)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError(f"Le login '{login}' est déjà utilisé")
        
        return login