# apps/paiements/forms.py

from django import forms
from .models import Depense
from decimal import Decimal


class DepenseForm(forms.ModelForm):
    """
    Formulaire pour enregistrer une dépense
    """
    class Meta:
        model = Depense
        fields = ['motif', 'montant', 'date_depense']
        
        widgets = {
            'motif': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all',
                'placeholder': 'Ex: Achat de matières premières',
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all',
                'placeholder': 'Ex: 150000',
                'step': '0.01',
                'min': '0.01',
            }),
            'date_depense': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all',
                'type': 'date',
            }),
        }
        
        labels = {
            'motif': 'Motif de la dépense',
            'montant': 'Montant (GNF)',
            'date_depense': 'Date de la dépense',
        }
        
        help_texts = {
            'motif': 'Décrivez la raison de cette dépense',
            'montant': 'Montant en Francs Guinéens (GNF)',
            'date_depense': 'Date à laquelle la dépense a été effectuée',
        }
    
    def clean_montant(self):
        """Validation du montant"""
        montant = self.cleaned_data.get('montant')
        
        if montant and montant <= Decimal('0'):
            raise forms.ValidationError("Le montant doit être supérieur à 0")
        
        return montant
    
    def clean_motif(self):
        """Validation du motif"""
        motif = self.cleaned_data.get('motif')
        
        if motif:
            motif = motif.strip()
            if len(motif) < 5:
                raise forms.ValidationError("Le motif doit contenir au moins 5 caractères")
        
        return motif