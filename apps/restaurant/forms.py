# apps/restaurant/forms.py

from django import forms
from .models import TableRestaurant
from apps.accounts.models import User
from django.db.models import Q


class TableRestaurantForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier une table physique
    """
    
    class Meta:
        model = TableRestaurant
        fields = ['numero_table', 'nombre_places', 'utilisateur']
        
        widgets = {
            'numero_table': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
                'placeholder': 'Ex: T001, TABLE01',
                'autofocus': True,
            }),
            'nombre_places': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
                'placeholder': 'Ex: 4',
                'min': '1',
                'max': '20',
            }),
            'utilisateur': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
            }),
        }
        
        labels = {
            'numero_table': 'Numéro de la table',
            'nombre_places': 'Nombre de places',
            'utilisateur': 'Utilisateur associé (compte Table)',
        }
        
        help_texts = {
            'numero_table': 'Identifiant unique de la table (ex: T001, TABLE01)',
            'nombre_places': 'Capacité d\'accueil de la table (1-20 personnes)',
            'utilisateur': 'Compte utilisateur qui sera lié à cette table',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        
        # Filtrer uniquement les utilisateurs avec rôle "Rtable"
        # Et exclure ceux déjà associés à une table (sauf pour l'instance actuelle)
        tables_associees = TableRestaurant.objects.values_list('utilisateur_id', flat=True)
        
        # Si on modifie une table existante, on peut garder son utilisateur actuel
        if self.instance.pk:
            utilisateurs_disponibles = User.objects.filter(
                Q(role='Rtable') & (
                    Q(id=self.instance.utilisateur_id) | 
                    ~Q(id__in=tables_associees)
                )
            ).order_by('login')
        else:
            # Pour une nouvelle table, exclure tous les utilisateurs déjà associés
            utilisateurs_disponibles = User.objects.filter(
                role='Rtable'
            ).exclude(
                id__in=tables_associees
            ).order_by('login')
        
        self.fields['utilisateur'].queryset = utilisateurs_disponibles
        
        # Message si aucun utilisateur disponible
        if not utilisateurs_disponibles.exists():
            self.fields['utilisateur'].help_text = (
                "⚠️ Aucun compte 'Table' disponible. "
                "Créez d'abord un utilisateur avec le rôle 'Rtable'."
            )
            self.fields['utilisateur'].widget.attrs['disabled'] = True
    
    def clean_numero_table(self):
        """Validation du numéro de table"""
        numero = self.cleaned_data.get('numero_table')
        
        if not numero:
            raise forms.ValidationError("Le numéro de table est obligatoire")
        
        numero = numero.strip().upper()
        
        # Vérifier l'unicité (sauf pour l'instance actuelle)
        query = TableRestaurant.objects.filter(numero_table=numero)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError(
                f"Le numéro de table '{numero}' est déjà utilisé"
            )
        
        return numero
    
    def clean_nombre_places(self):
        """Validation du nombre de places"""
        places = self.cleaned_data.get('nombre_places')
        
        if places and (places < 1 or places > 20):
            raise forms.ValidationError(
                "Le nombre de places doit être entre 1 et 20"
            )
        
        return places
    
    def clean_utilisateur(self):
        """Validation de l'utilisateur"""
        utilisateur = self.cleaned_data.get('utilisateur')
        
        if not utilisateur:
            raise forms.ValidationError("Vous devez sélectionner un utilisateur")
        
        # Vérifier que c'est bien un compte Table
        if utilisateur.role != 'Rtable':
            raise forms.ValidationError(
                "L'utilisateur doit avoir le rôle 'Table'"
            )
        
        # Vérifier que l'utilisateur n'est pas déjà associé (sauf si c'est la même table)
        query = TableRestaurant.objects.filter(utilisateur=utilisateur)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError(
                f"L'utilisateur '{utilisateur.login}' est déjà associé à une autre table"
            )
        
        return utilisateur


class TableSearchForm(forms.Form):
    """
    Formulaire de recherche de tables
    """
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all',
            'placeholder': '🔍 Rechercher par numéro ou utilisateur...',
        }),
        label=''
    )