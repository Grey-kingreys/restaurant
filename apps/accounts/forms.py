from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
import re

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