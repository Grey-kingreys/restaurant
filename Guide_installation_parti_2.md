# 🚀 Guide d'Installation - Partie 2 : Gestion du Menu

## 📋 Prérequis

- Partie 1 (Authentification) déjà fonctionnelle
- Python 3.x installé
- MySQL/XAMPP configuré
- Pillow installé pour la gestion des images

## 🔧 Installation

### 1. Installer Pillow (pour les images)

```bash
pip install Pillow
```

### 2. Créer l'application `menu`

```bash
python manage.py startapp apps/menu
```

### 3. Structure des fichiers à créer

Créez les fichiers suivants dans `apps/menu/` :

```
apps/menu/
├── __init__.py
├── admin.py          ← À modifier
├── apps.py           ← À modifier
├── models.py         ← À modifier
├── forms.py          ← À créer
├── views.py          ← À modifier
├── urls.py           ← À créer
└── migrations/
```

### 4. Copier le code

#### `models.py`
Copiez le code de l'artifact **menu_models**

#### `forms.py`
Copiez le code de l'artifact **menu_forms**

#### `views.py`
Copiez le code de l'artifact **menu_views**

#### `urls.py`
Copiez le code de l'artifact **menu_urls**

#### `admin.py`
Copiez le code de l'artifact **menu_admin**

#### `apps.py`
Copiez le code de l'artifact **menu_apps**

### 5. Créer les templates

Créez la structure suivante dans `templates/` :

```
templates/
└── menu/
    ├── plat_list_table.html          ← Pour les tables
    ├── plat_list_cuisinier.html      ← Pour les cuisiniers
    ├── plat_form.html                ← Formulaire d'ajout/modification
    ├── plat_detail_table.html        ← Détail pour table (à créer plus tard)
    └── plat_detail_cuisinier.html    ← Détail pour cuisinier (à créer plus tard)
```

Copiez les templates des artifacts correspondants.

### 6. Mettre à jour `settings.py`

Vérifiez que `apps.menu` est dans `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    # ...
    'apps.accounts',
    'apps.restaurant',
    'apps.menu',  # ← Ajouter cette ligne
    # ...
]
```

### 7. Mettre à jour les URLs principales

Dans `restaurant/urls.py`, ajoutez :

```python
urlpatterns = [
    # ...
    path('menu/', include('apps.menu.urls')),
    # ...
]
```

### 8. Créer le dossier media

```bash
mkdir media
mkdir media/plats
```

### 9. Faire les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🧪 Tests

### 1. Créer un compte cuisinier (si pas déjà fait)

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
User.objects.create_user(login='COOK001', password='Test@123', role='Rcuisinier')
exit()
```

### 2. Lancer le serveur

```bash
python manage.py runserver
```

### 3. Se connecter

1. Allez sur http://127.0.0.1:8000/auth/login/
2. Connectez-vous avec : `COOK001` / `Test@123`
3. Vous devriez voir le dashboard cuisinier avec les liens actifs

### 4. Tester les fonctionnalités

#### En tant que Cuisinier :
- ✅ Accéder à `/menu/cuisinier/`
- ✅ Ajouter un plat via `/menu/cuisinier/ajouter/`
- ✅ Modifier un plat
- ✅ Activer/Désactiver un plat

#### En tant que Table :
- ✅ Se connecter avec `TABLE001` / `Test@123`
- ✅ Accéder à `/menu/plats/`
- ✅ Voir uniquement les plats disponibles
- ✅ Filtrer par catégorie

## 📊 Données de test

Vous pouvez créer des plats de test via l'admin Django ou directement :

```python
python manage.py shell
```

```python
from apps.menu.models import Plat
from decimal import Decimal

# Créer des plats de test
Plat.objects.create(
    nom="Poulet Yassa",
    description="Poulet mariné avec oignons et citron",
    prix_unitaire=Decimal("50000"),
    categorie="PLAT",
    disponible=True
)

Plat.objects.create(
    nom="Riz au Gras",
    description="Riz cuisiné à la tomate avec viande",
    prix_unitaire=Decimal("45000"),
    categorie="PLAT",
    disponible=True
)

Plat.objects.create(
    nom="Coca Cola",
    description="Boisson fraîche 33cl",
    prix_unitaire=Decimal("5000"),
    categorie="BOISSON",
    disponible=True
)

Plat.objects.create(
    nom="Salade",
    description="Salade fraîche du jardin",
    prix_unitaire=Decimal("15000"),
    categorie="ENTREE",
    disponible=True
)

exit()
```

## ✅ Vérifications

### Checklist de fonctionnement

- [ ] L'application `menu` est créée
- [ ] Les migrations sont appliquées
- [ ] Le dossier `media/plats/` existe
- [ ] Les templates sont créés
- [ ] Les URLs sont configurées
- [ ] Le dashboard affiche les bons liens
- [ ] Un cuisinier peut :
  - [ ] Voir la liste des plats
  - [ ] Ajouter un plat
  - [ ] Modifier un plat
  - [ ] Activer/Désactiver un plat
  - [ ] Uploader une image
- [ ] Une table peut :
  - [ ] Voir les plats disponibles
  - [ ] Filtrer par catégorie
  - [ ] Rechercher un plat

## 🐛 Problèmes courants

### Erreur : "No module named 'PIL'"
```bash
pip install Pillow
```

### Erreur : "MEDIA_ROOT not configured"
Vérifiez dans `settings.py` :
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Les images ne s'affichent pas
Dans `urls.py` principal, vérifiez :
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Erreur 403 lors de l'upload
Vérifiez les permissions du dossier `media/` :
```bash
# Linux/Mac
chmod -R 755 media/

# Windows : Propriétés → Sécurité → Modifier
```

## 🎯 Prochaines étapes (Partie 3)

La partie 2 est terminée ! Prochainement :
- Système de panier en session
- Validation de commandes
- Interface serveur

## 📝 Notes importantes

- ⚠️ Les cuisiniers ne peuvent PAS supprimer les plats (seulement les désactiver)
- ⚠️ Les tables ne voient QUE les plats disponibles
- ⚠️ Le prix est en Francs Guinéens (GNF)
- ⚠️ Formats d'images acceptés : JPG, PNG (max 5MB)

## 🎨 Personnalisation

Pour personnaliser le style, modifiez `static/css/custom.css` (si créé).

## 📚 Ressources

- Documentation Django : https://docs.djangoproject.com/
- Documentation Pillow : https://pillow.readthedocs.io/
- Tailwind CSS : https://tailwindcss.com/docs