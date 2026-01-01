# 📚 Référence Rapide - Partie 2 : Gestion du Menu

## 🎯 Résumé de ce qui a été créé

### Fonctionnalités implémentées ✅

#### Pour le Cuisinier (Rcuisinier)
- ✅ Liste de tous les plats (disponibles et non disponibles)
- ✅ Ajout d'un nouveau plat
- ✅ Modification d'un plat existant
- ✅ Activation/Désactivation d'un plat
- ✅ Upload d'image (JPG, PNG)
- ✅ Filtres et recherche
- ✅ Statistiques (total, disponibles, non disponibles)

#### Pour la Table (Rtable)
- ✅ Liste des plats disponibles uniquement
- ✅ Détail d'un plat avec sélection de quantité
- ✅ Filtrage par catégorie
- ✅ Recherche de plats
- ✅ Interface optimisée pour tablette

## 🔗 URLs disponibles

### URLs Cuisinier
```
/menu/cuisinier/                     → Liste des plats
/menu/cuisinier/ajouter/             → Ajouter un plat
/menu/cuisinier/<id>/                → Détail d'un plat
/menu/cuisinier/<id>/modifier/       → Modifier un plat
/menu/cuisinier/<id>/toggle/         → Activer/Désactiver
```

### URLs Table
```
/menu/plats/                         → Liste des plats disponibles
/menu/plats/<id>/                    → Détail d'un plat
```

## 📦 Modèle de données

### Table `menu_plat`
```sql
- id                    : INT (PK)
- nom                   : VARCHAR(200)
- description           : TEXT
- prix_unitaire         : DECIMAL(10,2)
- image                 : VARCHAR(100)
- disponible            : BOOLEAN
- categorie             : VARCHAR(20)
- date_creation         : DATETIME
- date_modification     : DATETIME
```

### Catégories disponibles
- `ENTREE` : Entrée
- `PLAT` : Plat principal
- `DESSERT` : Dessert
- `BOISSON` : Boisson
- `ACCOMPAGNEMENT` : Accompagnement

## 🔒 Permissions par rôle

### Cuisinier (Rcuisinier)
```python
# Peut faire :
- Voir tous les plats (disponibles + non disponibles)
- Créer un nouveau plat
- Modifier un plat
- Activer/Désactiver un plat
- Uploader/Modifier une image

# Ne peut PAS faire :
- Supprimer un plat (seulement désactiver)
- Voir la caisse
- Gérer les commandes
```

### Table (Rtable)
```python
# Peut faire :
- Voir les plats disponibles uniquement
- Filtrer par catégorie
- Rechercher un plat
- Voir les détails d'un plat

# Ne peut PAS faire :
- Modifier les plats
- Voir les plats non disponibles
- Accéder à l'interface cuisinier
```

### Admin (Radmin)
```python
# Peut tout faire :
- Toutes les actions du cuisinier
- Supprimer des plats (via l'admin Django)
- Accéder à l'interface d'administration
```

## 🎨 Composants de l'interface

### Cartes de plats (Tables)
- Image du plat (ou icône par défaut)
- Nom du plat
- Description (2 lignes max)
- Prix formaté
- Badge catégorie
- Bouton "Voir détails"
- Bouton panier (préparation Partie 3)

### Tableau de plats (Cuisiniers)
- Miniature de l'image
- Nom et description courte
- Catégorie (badge)
- Prix formaté
- État (disponible/non disponible)
- Actions : Voir, Modifier, Activer/Désactiver

## 💾 Gestion des images

### Configuration
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Emplacement
```
media/
└── plats/
    └── 2025/
        └── 01/
            ├── plat1.jpg
            └── plat2.png
```

### Contraintes
- Formats acceptés : JPG, JPEG, PNG
- Taille maximale : 5MB
- Validation côté formulaire
- Image par défaut si pas d'upload

## 🧪 Commandes de test utiles

### Créer un plat de test
```python
python manage.py shell
```
```python
from apps.menu.models import Plat
from decimal import Decimal

Plat.objects.create(
    nom="Test Plat",
    description="Description du test",
    prix_unitaire=Decimal("25000"),
    categorie="PLAT",
    disponible=True
)
```

### Lister les plats disponibles
```python
from apps.menu.models import Plat
print(Plat.disponibles.all())
```

### Changer la disponibilité
```python
plat = Plat.objects.get(id=1)
plat.disponible = not plat.disponible
plat.save()
```

### Compter les plats par catégorie
```python
from apps.menu.models import Plat
from django.db.models import Count

stats = Plat.objects.values('categorie').annotate(total=Count('id'))
print(stats)
```

## 🐛 Debug rapide

### Les images ne s'affichent pas
1. Vérifier que `MEDIA_URL` et `MEDIA_ROOT` sont dans `settings.py`
2. Vérifier les URLs dans `restaurant/urls.py` :
   ```python
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```
3. Vérifier les permissions du dossier `media/`

### Erreur lors de l'upload
1. Vérifier que Pillow est installé : `pip install Pillow`
2. Vérifier que le dossier `media/` existe
3. Vérifier la taille du fichier (max 5MB)

### Le formulaire ne se soumet pas
1. Vérifier le `{% csrf_token %}`
2. Vérifier que `enctype="multipart/form-data"` est présent
3. Regarder les erreurs dans la console du navigateur

## 📊 Statistiques disponibles

Dans la vue cuisinier, vous avez accès à :
```python
stats = {
    'total': Plat.objects.count(),
    'disponibles': Plat.objects.filter(disponible=True).count(),
    'non_disponibles': Plat.objects.filter(disponible=False).count(),
}
```

Vous pouvez étendre avec :
```python
# Plats par catégorie
par_categorie = {}
for code, label in Plat.CATEGORIE_CHOICES:
    par_categorie[label] = Plat.objects.filter(categorie=code).count()

# Prix moyen
from django.db.models import Avg
prix_moyen = Plat.objects.aggregate(Avg('prix_unitaire'))
```

## 🚀 Prochaines étapes (Partie 3)

La Partie 2 est maintenant complète ! Voici ce qui vient ensuite :

### Partie 3 : Système de Panier et Commandes
- [ ] Panier en session pour les tables
- [ ] Ajout/Modification/Suppression d'articles
- [ ] Validation du panier → Création de commande
- [ ] Historique des commandes par table
- [ ] Calcul automatique du total

### Modèles à créer (Partie 3)
```python
class Commande(models.Model):
    table = models.ForeignKey(TableRestaurant)
    montant_total = models.DecimalField()
    statut = models.CharField()  # en_attente, servie, payee
    date_commande = models.DateTimeField()

class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande)
    plat = models.ForeignKey(Plat)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField()
```

## 📝 Checklist de validation

Avant de passer à la Partie 3, vérifiez :

- [ ] Un cuisinier peut se connecter
- [ ] Un cuisinier peut voir la liste des plats
- [ ] Un cuisinier peut ajouter un plat avec image
- [ ] Un cuisinier peut modifier un plat
- [ ] Un cuisinier peut activer/désactiver un plat
- [ ] Une table peut se connecter
- [ ] Une table voit uniquement les plats disponibles
- [ ] Une table peut filtrer par catégorie
- [ ] Une table peut voir le détail d'un plat
- [ ] Les images s'affichent correctement
- [ ] Les prix sont bien formatés (espaces entre milliers)
- [ ] Le dashboard affiche les bons liens (Partie 2 = 100%)

## 💡 Astuces

### Performance
- Les images sont uploadées dans des sous-dossiers par année/mois
- Index créés sur `disponible` et `categorie` pour des requêtes rapides
- Manager personnalisé `Plat.disponibles.all()` pour filtrer facilement

### Sécurité
- Validation de la taille des images (5MB max)
- Validation du format (JPG, PNG uniquement)
- Vérification des rôles dans chaque vue
- Protection CSRF sur tous les formulaires

### UX
- Messages de succès/erreur après chaque action
- Confirmation avant désactivation
- Prévisualisation des images dans les formulaires
- Responsive design (mobile/tablette)

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez le guide d'installation
2. Consultez les logs Django : `python manage.py runserver`
3. Vérifiez la console du navigateur (F12)
4. Testez avec les données de test fournies

**Partie 2 terminée avec succès ! 🎉**