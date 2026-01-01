from django import forms
from .models import Plat
from decimal import Decimal


class PlatForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier un plat
    """
    class Meta:
        model = Plat
        fields = ['nom', 'description', 'prix_unitaire', 'categorie', 'image', 'disponible']
        
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: Poulet Yassa',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Décrivez le plat...',
                'rows': 4,
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: 50000',
                'step': '0.01',
                'min': '0.01',
            }),
            'categorie': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/jpeg,image/png,image/jpg',
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
            }),
        }
        
        labels = {
            'nom': 'Nom du plat',
            'description': 'Description',
            'prix_unitaire': 'Prix unitaire (GNF)',
            'categorie': 'Catégorie',
            'image': 'Image du plat',
            'disponible': 'Plat disponible à la vente',
        }
        
        help_texts = {
            'nom': 'Donnez un nom clair et appétissant',
            'prix_unitaire': 'Prix en Francs Guinéens (GNF)',
            'image': 'Formats acceptés: JPG, PNG (max 5MB)',
            'disponible': 'Décochez si le plat n\'est plus disponible',
        }
    
    def clean_prix_unitaire(self):
        """Validation du prix"""
        prix = self.cleaned_data.get('prix_unitaire')
        if prix and prix <= Decimal('0'):
            raise forms.ValidationError("Le prix doit être supérieur à 0")
        return prix
    
    def clean_nom(self):
        """Validation du nom (pas de doublons)"""
        nom = self.cleaned_data.get('nom')
        if nom:
            nom = nom.strip()
            # Vérifier les doublons (sauf si on modifie le plat actuel)
            query = Plat.objects.filter(nom__iexact=nom)
            if self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise forms.ValidationError(f"Un plat nommé '{nom}' existe déjà")
        return nom
    
    def clean_image(self):
        """Validation de l'image"""
        image = self.cleaned_data.get('image')
        if image:
            # Vérifier la taille (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne doit pas dépasser 5MB")
            
            # Vérifier le format
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("Format non supporté. Utilisez JPG, JPEG ou PNG")
        
        return image


class PlatSearchForm(forms.Form):
    """
    Formulaire de recherche de plats
    """
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '🔍 Rechercher un plat...',
        }),
        label=''
    )
    
    categorie = forms.ChoiceField(
        required=False,
        choices=[('', 'Toutes les catégories')] + Plat.CATEGORIE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        }),
        label=''
    )
    
    disponible = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Tous les plats'),
            ('1', 'Disponibles uniquement'),
            ('0', 'Non disponibles uniquement'),
        ],
        widget=forms.Select(attrs={
            'class': 'px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        }),
        label=''
    )