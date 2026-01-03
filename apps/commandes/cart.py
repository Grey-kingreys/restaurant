from decimal import Decimal
from apps.menu.models import Plat


class Cart:
    """
    Gestion du panier en session pour les tables
    """
    
    def __init__(self, request):
        """
        Initialise le panier à partir de la session
        """
        self.session = request.session
        cart = self.session.get('cart')
        
        if not cart:
            # Créer un nouveau panier vide
            cart = self.session['cart'] = {}
        
        self.cart = cart
    
    def add(self, plat, quantite=1, update_quantite=False):
        """
        Ajoute un plat au panier ou met à jour sa quantité
        
        Args:
            plat: Instance de Plat
            quantite: Quantité à ajouter (1-10)
            update_quantite: Si True, remplace la quantité au lieu de l'additionner
        """
        plat_id = str(plat.id)
        
        if plat_id not in self.cart:
            self.cart[plat_id] = {
                'quantite': 0,
                'prix_unitaire': str(plat.prix_unitaire),
                'nom': plat.nom,
                'image': plat.image.url if plat.image else None
            }
        
        if update_quantite:
            self.cart[plat_id]['quantite'] = quantite
        else:
            self.cart[plat_id]['quantite'] += quantite
        
        # Limiter la quantité entre 1 et 10
        self.cart[plat_id]['quantite'] = max(1, min(10, self.cart[plat_id]['quantite']))
        
        self.save()
    
    def remove(self, plat):
        """
        Supprime un plat du panier
        """
        plat_id = str(plat.id)
        
        if plat_id in self.cart:
            del self.cart[plat_id]
            self.save()
    
    def save(self):
        """
        Marque la session comme modifiée
        """
        self.session.modified = True
    
    def clear(self):
        """
        Vide le panier
        """
        del self.session['cart']
        self.save()
    
    def __iter__(self):
        """
        Itère sur les items du panier et récupère les plats depuis la BDD
        """
        plat_ids = self.cart.keys()
        plats = Plat.objects.filter(id__in=plat_ids)
        cart = self.cart.copy()
        
        for plat in plats:
            cart[str(plat.id)]['plat'] = plat
        
        for item in cart.values():
            item['prix_unitaire'] = Decimal(item['prix_unitaire'])
            item['total'] = item['prix_unitaire'] * item['quantite']
            yield item
    
    def __len__(self):
        """
        Compte le nombre total d'articles dans le panier
        """
        return sum(item['quantite'] for item in self.cart.values())
    
    def get_total_prix(self):
        """
        Calcule le prix total du panier
        """
        return sum(
            Decimal(item['prix_unitaire']) * item['quantite'] 
            for item in self.cart.values()
        )
    
    def get_items_count(self):
        """
        Retourne le nombre de types de plats différents
        """
        return len(self.cart)
    
    def is_empty(self):
        """
        Vérifie si le panier est vide
        """
        return len(self.cart) == 0