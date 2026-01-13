# 🍽️ Restaurant Manager - Système de Gestion Intégré

[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon.tech-blue.svg)](https://neon.tech/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.1-06B6D4.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-Academic-yellow.svg)]()

> Application web complète de gestion de restaurant développée avec Django et Tailwind CSS. Ce projet académique implémente un système complet de prise de commandes via tablettes, gestion du personnel, suivi financier et reporting automatisé.

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités principales](#-fonctionnalités-principales)
- [Architecture du projet](#-architecture-du-projet)
- [Technologies utilisées](#-technologies-utilisées)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Guide d'utilisation](#-guide-dutilisation)
- [Gestion des rôles](#-gestion-des-rôles)
- [Structure de la base de données](#-structure-de-la-base-de-données)
- [Fonctionnalités bonus](#-fonctionnalités-bonus)
- [Difficultés rencontrées](#-difficultés-rencontrées)
- [Tests et validation](#-tests-et-validation)
- [Déploiement](#-déploiement)
- [Roadmap](#-roadmap)
- [Contributions](#-contributions)
- [Auteur](#-auteur)
- [Licence](#-licence)

---

## 🎯 Vue d'ensemble

**Restaurant Manager** est une application Django full-stack conçue pour digitaliser la gestion complète d'un restaurant. Le système permet :

- 📱 **Prise de commande digitale** : Tablettes sur chaque table pour commander directement
- 👨‍🍳 **Gestion du personnel** : 5 rôles distincts avec permissions granulaires
- 💰 **Suivi financier** : Caisse automatisée, gestion des dépenses, reporting
- 📊 **Analytics** : Dashboard avec statistiques en temps réel
- 📧 **Automatisation** : Rapports quotidiens par email via Celery

### Contexte académique

Ce projet a été développé dans le cadre d'un cours de Python/Django niveau L4. L'objectif était de créer une application complète mettant en œuvre :
- L'architecture MTV (Model-Template-View) de Django
- Un système d'authentification personnalisé
- Une gestion de permissions basée sur les rôles (RBAC)
- Des interactions base de données complexes
- Une interface utilisateur moderne et responsive

**Date limite du projet** : 02 janvier 2026  
**Proposé par** : Mr Mamadou Dara Sow

---

## ✨ Fonctionnalités principales

### 🔐 Authentification & Autorisation
- **Authentification personnalisée** : Système de login avec identifiant alphanumérique (min. 6 caractères)
- **5 rôles utilisateurs** : Table, Serveur, Cuisinier, Comptable, Administrateur
- **RBAC complet** : Contrôle d'accès basé sur les rôles avec décorateurs Django
- **Gestion des utilisateurs** : CRUD complet (Admin uniquement)

### 🍽️ Gestion du Menu
- **CRUD des plats** : Création, modification, activation/désactivation
- **Catégorisation** : Entrées, Plats, Desserts, Boissons, Accompagnements
- **Upload d'images** : Gestion des photos de plats (JPG, PNG, max 5MB)
- **Filtrage avancé** : Par catégorie, disponibilité, recherche textuelle
- **Prix dynamiques** : Affichage formaté en Francs Guinéens (GNF)

### 📦 Système de Commandes
- **Panier en session** : Gestion côté serveur sans JavaScript obligatoire
- **Quantités limitées** : 1 à 10 unités par plat
- **Statuts de commande** : En attente → Servie → Payée
- **Timeline visuelle** : Suivi de progression de la commande
- **Historique complet** : Toutes les commandes par table

### 💳 Paiements & Caisse
- **Validation manuelle** : Paiement physique confirmé dans le système
- **Caisse automatisée** : Solde mis à jour automatiquement
- **Gestion des dépenses** : Enregistrement avec validation de solde
- **Contrôle de cohérence** : Impossible d'enregistrer une dépense si solde insuffisant
- **Traçabilité** : Qui a servi, qui a payé, qui a enregistré la dépense

### 👨‍🍳 Interface Serveur
- **Vue d'ensemble des tables** : États en temps réel (Libre, En attente, Servie)
- **Gestion des commandes** : Validation service et paiement
- **Statistiques par table** : Nombre de commandes, montants, historique
- **Traçabilité des actions** : Enregistrement du serveur ayant effectué chaque action

### 📊 Dashboard & Analytics (Bonus)
- **Statistiques en temps réel** : Revenus, dépenses, bénéfices
- **Top produits** : Plats les plus vendus
- **Top tables** : Tables générant le plus de revenus
- **Évolution temporelle** : Graphiques sur 7 jours
- **Export de données** : CSV (Excel) et PDF
- **Rapports automatisés** : Email quotidien à 18h via Celery

---

## 🏗️ Architecture du projet

### Structure des dossiers

```
restaurant_manager/
├── 📁 restaurant/              # Configuration Django principale
│   ├── settings.py            # Configuration (PostgreSQL, Celery, Email)
│   ├── urls.py                # URLs principales
│   ├── celery.py              # Configuration Celery/Beat
│   └── wsgi.py                # Point d'entrée WSGI
│
├── 📁 apps/                    # Applications Django métier
│   ├── 📁 accounts/           # Authentification & Utilisateurs
│   │   ├── models.py          # User personnalisé
│   │   ├── views.py           # Login, Logout, CRUD users
│   │   ├── forms.py           # Formulaires auth
│   │   ├── decorators.py      # @role_required
│   │   └── admin.py
│   │
│   ├── 📁 restaurant/         # Tables physiques du restaurant
│   │   ├── models.py          # TableRestaurant
│   │   ├── views.py           # CRUD tables (Admin)
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── 📁 menu/               # Gestion des plats
│   │   ├── models.py          # Plat (avec catégories)
│   │   ├── views.py           # CRUD plats, listes
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── 📁 commandes/          # Commandes & Panier
│   │   ├── models.py          # Commande, CommandeItem
│   │   ├── views.py           # Panier, validation
│   │   ├── cart.py            # Classe Cart (session)
│   │   └── admin.py
│   │
│   ├── 📁 paiements/          # Paiements, Caisse, Dépenses
│   │   ├── models.py          # Paiement, Caisse, Depense
│   │   ├── views.py           # Dashboard caisse
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   └── 📁 dashboard/          # Analytics & Exports
│       ├── views.py           # Dashboard, exports
│       ├── tasks.py           # Tâches Celery (email)
│       └── urls.py
│
├── 📁 templates/              # Templates HTML
│   ├── base.html              # Template de base
│   ├── partials/              # Navbar, footer
│   ├── accounts/              # Login, user management
│   ├── restaurant/            # Tables (Admin & Serveur)
│   ├── menu/                  # Plats (Table & Cuisinier)
│   ├── commandes/             # Panier, commandes
│   ├── paiements/             # Caisse, dépenses
│   └── dashboard/             # Analytics
│
├── 📁 theme/                  # Tailwind CSS
│   ├── static_src/            # Source Tailwind
│   └── static/css/dist/       # CSS compilé
│
├── 📁 static/                 # Fichiers statiques globaux
│   ├── css/
│   ├── js/
│   └── images/
│
├── 📁 media/                  # Uploads utilisateur
│   └── plats/                 # Images des plats
│
├── 📄 requirements.txt        # Dépendances Python
├── 📄 .env                    # Variables d'environnement
├── 📄 manage.py               # CLI Django
└── 📄 README.md               # Ce fichier
```

### Pattern architectural

Le projet suit le **MTV (Model-Template-View)** de Django avec séparation claire des responsabilités :

- **Models** : Logique métier et accès données
- **Views** : Logique de présentation et contrôle
- **Templates** : Interface utilisateur (HTML + Tailwind)
- **Forms** : Validation et nettoyage des données
- **Managers** : Requêtes personnalisées complexes
- **Decorators** : Contrôle d'accès par rôle
- **Tasks** : Tâches asynchrones (Celery)

---

## 🛠️ Technologies utilisées

### Backend
- **Django 5.1** : Framework web Python
- **Python 3.11+** : Langage de programmation
- **PostgreSQL** : Base de données (Neon.tech)
- **Celery 5.4** : Tâches asynchrones et scheduler
- **Redis** : Broker pour Celery
- **Pillow 10.4** : Traitement d'images

### Frontend
- **Tailwind CSS 4.1** : Framework CSS utility-first
- **DaisyUI 5.3** : Composants Tailwind
- **Alpine.js** (optionnel) : Interactivité légère
- **JavaScript vanilla** : Pour interactions simples

### Outils de développement
- **django-tailwind 3.8** : Intégration Tailwind dans Django
- **django-browser-reload** : Hot reload en développement
- **python-dotenv** : Gestion variables d'environnement
- **WhiteNoise** : Service fichiers statiques en production

### Bonus (Fonctionnalités avancées)
- **reportlab 4.2** : Génération de PDF
- **openpyxl 3.1** : Export Excel
- **django-celery-beat 2.7** : Tâches planifiées
- **gunicorn 21.2** : Serveur WSGI production

---

## 📥 Installation

### Prérequis

- **Python 3.11+** installé
- **Git** installé
- **Node.js & npm** (pour Tailwind CSS)
- **PostgreSQL** ou compte **Neon.tech** (gratuit)
- **Redis** (pour Celery, optionnel en développement)

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/restaurant-manager.git
cd restaurant-manager
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Installer les dépendances Tailwind

```bash
cd theme/static_src
npm install
cd ../..
```

### 5. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Django
SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
DEBUG=True

# PostgreSQL (Neon.tech)
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=votre_mot_de_passe
DB_HOST=ep-aged-dawn-xxxxx.eastus2.azure.neon.tech
DB_PORT=5432

# Redis (pour Celery - optionnel en dev)
REDIS_URL=redis://localhost:6379/0

# Email (pour rapports automatiques)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=votre.email@gmail.com
REPORT_EMAIL_TO=admin@restaurant.com
```

### 6. Créer la base de données

#### Option A : Neon.tech (Recommandé - Gratuit)

1. Créez un compte sur [neon.tech](https://neon.tech)
2. Créez un nouveau projet PostgreSQL
3. Copiez les informations de connexion dans `.env`

#### Option B : PostgreSQL local

```bash
# Installer PostgreSQL puis :
createdb restaurant_db
```

### 7. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Créer un superutilisateur

```bash
python manage.py createsuperuser
# Login : ADMIN001
# Password : Admin@123
```

### 9. Charger les données de test (optionnel)

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.menu.models import Plat
from decimal import Decimal

# Créer des utilisateurs de test
User.objects.create_user(login='TABLE001', password='Test@123', role='Rtable')
User.objects.create_user(login='SERV001', password='Test@123', role='Rserveur')
User.objects.create_user(login='COOK001', password='Test@123', role='Rcuisinier')
User.objects.create_user(login='COMPT001', password='Test@123', role='Rcomptable')

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
    nom="Coca Cola 33cl",
    prix_unitaire=Decimal("5000"),
    categorie="BOISSON",
    disponible=True
)

exit()
```

### 10. Compiler Tailwind CSS

```bash
# Terminal 1 - Tailwind en mode watch
python manage.py tailwind start

# Terminal 2 - Serveur Django
python manage.py runserver
```

### 11. Accéder à l'application

- **Interface principale** : http://127.0.0.1:8000
- **Admin Django** : http://127.0.0.1:8000/admin
- **Dashboard** : http://127.0.0.1:8000/dashboard

---

## ⚙️ Configuration

### Configuration PostgreSQL

Le projet est configuré pour **PostgreSQL via Neon.tech** (gratuit, hébergé). Configuration dans `settings.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
    }
}
```

### Configuration Celery (Tâches asynchrones)

Pour activer les rapports automatiques par email :

#### 1. Installer et démarrer Redis

```bash
# Windows (via Chocolatey)
choco install redis-64

# Linux/Mac
sudo apt-get install redis-server
# ou
brew install redis
```

#### 2. Démarrer les workers Celery

```bash
# Terminal 3 - Worker Celery
celery -A restaurant worker -l info

# Terminal 4 - Beat Scheduler (pour tâches planifiées)
celery -A restaurant beat -l info
```

#### 3. Tester l'envoi d'email

```bash
python manage.py shell
```

```python
from apps.dashboard.tasks import test_email
test_email.delay()
```

### Configuration Email (Gmail)

1. Activez la **validation en 2 étapes** sur votre compte Gmail
2. Générez un **mot de passe d'application** : https://myaccount.google.com/apppasswords
3. Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

---

## 📖 Guide d'utilisation

### 🔐 Connexion

1. Accédez à http://127.0.0.1:8000
2. Vous serez redirigé vers `/auth/login/`
3. Utilisez un des comptes de test :

```
TABLE001 / Test@123    (Client/Table)
SERV001 / Test@123     (Serveur)
COOK001 / Test@123     (Cuisinier)
COMPT001 / Test@123    (Comptable)
ADMIN001 / Admin@123   (Administrateur)
```

### 🪑 Interface Table (Rtable)

**Workflow complet :**

1. **Consulter le menu** : `/menu/plats/`
   - Voir tous les plats disponibles
   - Filtrer par catégorie (Entrées, Plats, Desserts, Boissons)
   - Rechercher un plat

2. **Ajouter au panier** :
   - Cliquer sur un plat
   - Sélectionner la quantité (1-10)
   - Ajouter au panier

3. **Gérer le panier** : `/commandes/panier/`
   - Modifier les quantités
   - Supprimer des plats
   - Voir le montant total

4. **Valider la commande** :
   - Cliquer sur "Valider la commande"
   - Une commande est créée avec statut "En attente"

5. **Suivre la commande** : `/commandes/mes-commandes/`
   - Timeline visuelle (Commandé → Servie → Payée)
   - Détails des plats
   - Montant total

### 👨‍🍳 Interface Serveur (Rserveur)

**Workflow :**

1. **Vue d'ensemble** : `/restaurant/tables/`
   - Voir toutes les tables avec leurs états
   - Filtrer par statut (Libre, En attente, Servie)
   - Statistiques globales

2. **Gérer une table** : `/restaurant/tables/<id>/`
   - Voir toutes les commandes de la table
   - Historique complet
   - Statistiques (revenus, nombre de commandes)

3. **Traiter une commande** :
   - **En attente** → Cliquer "Marquer servie"
   - **Servie** → Cliquer "Marquer payée"
   - Confirmation avant validation

4. **Toutes les commandes** : `/restaurant/commandes/`
   - Vue globale de toutes les commandes
   - Filtres par table et statut
   - Statistiques

### 🍳 Interface Cuisinier (Rcuisinier)

**Workflow :**

1. **Liste des plats** : `/menu/cuisinier/`
   - Voir tous les plats (disponibles + non disponibles)
   - Filtrer par catégorie et disponibilité
   - Rechercher un plat
   - Statistiques (total, disponibles, non disponibles)

2. **Ajouter un plat** : `/menu/cuisinier/ajouter/`
   - Nom (obligatoire)
   - Description (optionnelle)
   - Prix unitaire en GNF (obligatoire)
   - Catégorie (obligatoire)
   - Image (optionnelle, max 5MB)
   - Disponibilité (activé par défaut)

3. **Modifier un plat** : `/menu/cuisinier/<id>/modifier/`
   - Tous les champs modifiables
   - Prévisualisation de l'image actuelle

4. **Activer/Désactiver** :
   - Cliquer sur l'icône 🔴/🟢
   - Confirmation avant changement
   - ⚠️ **Pas de suppression** (seulement désactivation)

### 💰 Interface Comptable (Rcomptable)

**Workflow :**

1. **Dashboard Caisse** : `/paiements/caisse/`
   - Solde actuel de la caisse (grand affichage)
   - Statistiques par période (Aujourd'hui, Semaine, Mois, Tout)
   - Paiements reçus vs Dépenses
   - Bénéfice net
   - Derniers paiements et dépenses

2. **Enregistrer une dépense** : `/paiements/depenses/ajouter/`
   - Motif (obligatoire, min. 5 caractères)
   - Montant en GNF (obligatoire)
   - Date de la dépense (obligatoire)
   - **Validation** : Impossible si solde insuffisant
   - Aperçu du nouveau solde

3. **Consulter les paiements** : `/paiements/paiements/`
   - Liste de tous les paiements
   - Filtres par date et table
   - Montant total reçu

4. **Consulter les dépenses** : `/paiements/depenses/`
   - Liste de toutes les dépenses
   - Filtres par date
   - Montant total dépensé
   - Qui a enregistré chaque dépense

### 👑 Interface Administrateur (Radmin)

**Accès complet à toutes les fonctionnalités :**

1. **Gestion des utilisateurs** : `/auth/users/`
   - CRUD complet
   - Filtres par rôle et statut
   - Statistiques par rôle
   - Activer/Désactiver/Supprimer
   - Réinitialiser mot de passe

2. **Gestion des tables physiques** : `/restaurant/admin/tables/`
   - Créer des tables physiques
   - Associer une table à un utilisateur (rôle Table)
   - Voir les statistiques par table
   - Supprimer des tables

3. **Dashboard Analytics** : `/dashboard/analytics/`
   - Statistiques complètes
   - Top 10 plats
   - Top 10 tables
   - Évolution sur 7 jours
   - Répartition par catégorie
   - KPIs (taux de conversion, panier moyen)

4. **Exports** :
   - **Excel (CSV)** : `/dashboard/export/excel/`
   - **PDF** : `/dashboard/export/pdf/`
   - **Email automatique** : `/dashboard/rapport/email/`

5. **Admin Django** : `/admin/`
   - Interface d'administration complète
   - Accès à toutes les tables
   - Actions en masse

---

## 👥 Gestion des rôles

### Matrice des permissions

| Fonctionnalité | Table | Serveur | Cuisinier | Comptable | Admin |
|---|---|---|---|---|---|
| **Menu** |
| Consulter plats disponibles | ✅ | ❌ | ✅ | ❌ | ✅ |
| Ajouter/Modifier plats | ❌ | ❌ | ✅ | ❌ | ✅ |
| Activer/Désactiver plats | ❌ | ❌ | ✅ | ❌ | ✅ |
| Supprimer plats | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Commandes** |
| Passer commande | ✅ | ❌ | ❌ | ❌ | ✅ |
| Voir ses commandes | ✅ | ❌ | ❌ | ❌ | ✅ |
| Voir toutes commandes | ❌ | ✅ | ❌ | ❌ | ✅ |
| Marquer "Servie" | ❌ | ✅ | ❌ | ❌ | ✅ |
| Marquer "Payée" | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Finances** |
| Voir paiements | ❌ | ❌ | ❌ | ✅ | ✅ |
| Enregistrer dépenses | ❌ | ❌ | ❌ | ✅ | ✅ |
| Dashboard caisse | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Administration** |
| CRUD utilisateurs | ❌ | ❌ | ❌ | ❌ | ✅ |
| CRUD tables physiques | ❌ | ❌ | ❌ | ❌ | ✅ |
| Dashboard analytics | ❌ | ❌ | ❌ | ❌ | ✅ |
| Exports (Excel, PDF) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Admin Django | ❌ | ❌ | ❌ | ❌ | ✅ |

### Implémentation technique

Les permissions sont gérées via des **décorateurs personnalisés** dans `apps/accounts/decorators.py` :

```python
@login_required
@role_required('Rtable')
def ma_vue_table(request):
    # Code accessible uniquement aux tables
    pass
```

Décorateurs disponibles :
- `@role_required('Rtable', 'Rserveur')` : Accepte plusieurs rôles
- `@table_required` : Raccourci pour `@role_required('Rtable')`
- `@serveur_required`
- `@cuisinier_required`
- `@comptable_required`
- `@admin_required`

---

## 🗄️ Structure de la base de données

### Diagramme ERD simplifié

```
┌─────────────┐         ┌──────────────┐
│    User     │◄────────│ TableRestau  │
│             │         │   -rant      │
│ - login     │         │ - numero     │
│ - password  │         │ - places     │
│ - role      │         └──────────────┘
│ - actif     │                ▲
└─────────────┘                │
       ▲                       │
       │                       │
       │         ┌─────────────┴─────────┐
       │         │                       │
       │    ┌────────────┐         ┌──────────┐
       │    │  Commande  │         │   Plat   │
       │    │            │         │          │
       └────│ - table    │         │ - nom    │
            │ - montant  │         │ - prix   │
            │ - statut   │◄────────│ - image  │
            └────────────┘    │    │ - categ  │
                 ▲            │    └──────────┘
                 │            │
            ┌────┴─────┐      │
            │          │      │
       ┌────────┐  ┌────────────┐
       │Paiement│  │CommandeItem│
       │        │  │            │
       │-montant│  │ - quantite │
       └────────┘  │ - prix_unit│
                   └────────────┘
            
       ┌──────────┐  ┌─────────┐
       │  Caisse  │  │ Depense │
       │          │  │         │
       │ - solde  │  │ - motif │
       └──────────┘  │ - montnt│
                     └─────────┘
```

### Tables principales

#### 1. **User** (Utilisateurs)
```python
- id: AutoField (PK)
- login: CharField(50, unique=True)
- password: CharField(128, hashé)
- role: CharField(20)  # Rtable, Rserveur, Rcuisinier, Rcomptable, Radmin
- actif: BooleanField
- date_creation: DateTimeField
```

#### 2. **TableRestaurant** (Tables physiques)
```python
- id: AutoField (PK)
- numero_table: CharField(10, unique=True)
- nombre_places: PositiveIntegerField
- utilisateur: OneToOneField(User)  # FK
```

#### 3. **Plat** (Menu)
```python
- id: AutoField (PK)
- nom: CharField(200)
- description: TextField
- prix_unitaire: DecimalField(10, 2)
- image: ImageField (upload_to='plats/%Y/%m/')
- disponible: BooleanField
- categorie: CharField(20)  # ENTREE, PLAT, DESSERT, BOISSON, ACCOMPAGNEMENT
- date_creation: DateTimeField
- date_modification: DateTimeField
```

#### 4. **Commande** (Commandes)
```python
- id: AutoField (PK)
- table: ForeignKey(User)  # Utilisateur avec rôle Rtable
- montant_total: DecimalField(10, 2)
- statut: CharField(20)  # en_attente, servie, payee
- serveur_ayant_servi: ForeignKey(User, null=True)  # Traçabilité
- date_commande: DateTimeField
- date_modification: DateTimeField
```

#### 5. **CommandeItem** (Lignes de commande)
```python
- id: AutoField (PK)
- commande: ForeignKey(Commande)
- plat: ForeignKey(Plat)
- quantite: PositiveIntegerField (1-10)
- prix_unitaire: DecimalField(10, 2)  # Prix au moment de la commande
```

#### 6. **Paiement** (Paiements)
```python
- id: AutoField (PK)
- commande: OneToOneField(Commande)
- montant: DecimalField(10, 2)
- date_paiement: DateTimeField
```

#### 7. **Caisse** (Caisse du restaurant)
```python
- id: AutoField (PK)  # Singleton, toujours id=1
- solde_actuel: DecimalField(12, 2)
- date_creation: DateTimeField
- date_modification: DateTimeField
```

#### 8. **Depense** (Dépenses)
```python
- id: AutoField (PK)
- motif: CharField(255)
- montant: DecimalField(10, 2)
- date_depense: DateField
- date_enregistrement: DateTimeField
- enregistree_par: ForeignKey(User)  # Comptable
```

### Relations clés

- **User ↔ TableRestaurant** : OneToOne (Un utilisateur Table = Une table physique)
- **User ↔ Commande** : OneToMany (Une table peut avoir plusieurs commandes)
- **Commande ↔ CommandeItem** : OneToMany (Une commande contient plusieurs plats)
- **Plat ↔ CommandeItem** : ManyToMany (via CommandeItem)
- **Commande ↔ Paiement** : OneToOne (Une commande = Un paiement)
- **User ↔ Depense** : OneToMany (Un comptable enregistre plusieurs dépenses)

### Indexes optimisés

```python
# models.py
class Meta:
    indexes = [
        models.Index(fields=['disponible', 'categorie']),  # Plat
        models.Index(fields=['nom']),  # Plat
        models.Index(fields=['statut', 'date_commande']),  # Commande
    ]
```

---

## 🎁 Fonctionnalités bonus

### 1. Dashboard Analytics avancé

**Métriques disponibles :**
- KPIs : Taux de conversion, Panier moyen, Commandes actives
- Évolution temporelle sur 7 jours
- Top 10 plats les plus vendus
- Top 10 tables générant le plus de revenus
- Répartition des ventes par catégorie
- Statistiques financières (Revenus, Dépenses, Bénéfice)

**Accès** : `/dashboard/analytics/` (Admin uniquement)

### 2. Export de données

#### Export Excel (CSV)
- **URL** : `/dashboard/export/excel/`
- **Format** : CSV compatible Excel
- **Contenu** : Statistiques de la période actuelle
- **Usage** : Rapports comptables, analyse dans Excel

#### Export PDF
- **URL** : `/dashboard/export/pdf/`
- **Format** : PDF professionnel avec reportlab
- **Contenu** :
  - Résumé de la période (30 derniers jours)
  - Détail des paiements
  - Statistiques complètes
- **Usage** : Rapports officiels, archivage

### 3. Email automatique quotidien

**Configuration Celery Beat** : Envoi automatique à 18h00 chaque jour

**Contenu de l'email :**
```
╔═══════════════════════════════════════════════════════════════╗
║           RAPPORT QUOTIDIEN DES VENTES - RESTAURANT          ║
╚═══════════════════════════════════════════════════════════════╝

📅 Date : Vendredi 10 Janvier 2025
🕐 Généré le : 10/01/2025 à 18:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ DE LA JOURNÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 REVENUS
   • Nombre de paiements : 15
   • Montant total : 650 000 GNF

💸 DÉPENSES
   • Nombre de dépenses : 3
   • Montant total : 120 000 GNF

📈 BÉNÉFICE NET DU JOUR
   • 530 000 GNF

📦 ACTIVITÉ COMMANDES
   • Commandes créées : 18
   • Commandes payées : 15
   • Taux de conversion : 83.3%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 ÉTAT DE LA CAISSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Solde actuel : 1 230 000 GNF
```

**Activation** :
```bash
# Terminal 1 : Worker
celery -A restaurant worker -l info

# Terminal 2 : Beat Scheduler
celery -A restaurant beat -l info
```

**Test manuel** :
```python
from apps.dashboard.tasks import envoyer_rapport_quotidien
envoyer_rapport_quotidien.delay()
```

### 4. Traçabilité complète

**Qui a fait quoi ?**
- Chaque commande enregistre le **serveur ayant servi**
- Chaque dépense enregistre le **comptable l'ayant créée**
- Chaque paiement est lié à une commande traçable
- Timestamps automatiques sur toutes les opérations

**Exemple** :
```python
commande.serveur_ayant_servi  # User instance
depense.enregistree_par        # User instance
```

### 5. Responsive Design

- **Mobile-first** : Interface optimisée pour tablettes (tables)
- **Breakpoints Tailwind** : sm, md, lg, xl, 2xl
- **Menu hamburger** : Navigation mobile fluide
- **Touch-friendly** : Boutons larges, pas de hover obligatoire

### 6. Messages flash élégants

```python
messages.success(request, "✅ Commande validée avec succès !")
messages.error(request, "❌ Solde insuffisant")
messages.warning(request, "⚠️ Accès non autorisé")
messages.info(request, "ℹ️ Votre panier est vide")
```

Affichage automatique dans `base.html` avec Tailwind CSS.

---

## 🐛 Difficultés rencontrées

### 1. Migration MySQL → PostgreSQL

**Problème** : Le projet était initialement conçu pour MySQL, mais PostgreSQL (Neon.tech) a été choisi pour le déploiement gratuit.

**Solution** :
```python
# Avant (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

# Après (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {'sslmode': 'require'},
    }
}
```

**Impact** :
- Migration des données nécessaire
- Ajustement des requêtes spécifiques à MySQL
- Installation de `psycopg` au lieu de `pymysql`

### 2. Gestion du panier en session

**Problème** : Choix entre panier en BDD vs panier en session pour les tables.

**Solution adoptée** : **Panier en session** (`apps/commandes/cart.py`)

**Avantages** :
- Pas de pollution de la BDD avec des paniers non validés
- Performance accrue (pas de requêtes BDD à chaque ajout)
- Nettoyage automatique (session expirée = panier vidé)

**Inconvénients** :
- Perdu si la session expire
- Pas de persistance entre appareils

**Implémentation** :
```python
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
```

### 3. Traçabilité du serveur

**Problème** : Le cahier des charges ne spécifiait pas qui valide les commandes.

**Solution** : Ajout d'un champ `serveur_ayant_servi` dans le modèle `Commande`.

**Bénéfices** :
- Accountability : savoir qui a servi
- Analytics : performance par serveur
- Audit trail : traçabilité complète

**Migration** :
```python
# Migration ajoutée après coup
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='commande',
            name='serveur_ayant_servi',
            field=models.ForeignKey(...)
        ),
    ]
```

### 4. Gestion du solde de caisse

**Problème** : Comment garantir la cohérence du solde avec les paiements/dépenses ?

**Solution** : **Transactions atomiques Django**

```python
from django.db import transaction

@transaction.atomic
def commande_marquer_payee(request, commande_id):
    # 1. Créer le paiement
    paiement = Paiement.objects.create(...)
    
    # 2. Mettre à jour la commande
    commande.statut = 'payee'
    commande.save()
    
    # 3. Mettre à jour la caisse
    caisse = Caisse.get_instance()
    caisse.solde_actuel += montant
    caisse.save()
    
    # Si erreur à n'importe quelle étape → ROLLBACK complet
```

**Bénéfice** : Aucun risque d'incohérence entre paiements et caisse.

### 5. Validation des dépenses

**Problème** : Empêcher l'enregistrement d'une dépense si le solde est insuffisant.

**Solution** : **Validation côté modèle + vue**

```python
# Modèle
class Caisse(models.Model):
    def peut_effectuer_depense(self, montant):
        return self.solde_actuel >= montant

# Vue
if not caisse.peut_effectuer_depense(montant):
    messages.error(request, "❌ Solde insuffisant !")
    return render(...)
```

### 6. Upload d'images avec Pillow

**Problème** : Erreurs lors de l'upload d'images si Pillow mal configuré.

**Solution** :
```bash
pip install Pillow
```

Configuration `settings.py` :
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Configuration `urls.py` :
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 7. Tailwind CSS avec Django

**Problème** : Intégration Tailwind dans un projet Django (compilation, hot reload).

**Solution** : Package `django-tailwind`

```bash
pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind start  # Mode watch
```

**Défi** : Node.js/npm requis, chemin npm.cmd sur Windows.

```python
# settings.py
if os.name == 'nt':
    NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
```

### 8. Celery Beat sous Windows

**Problème** : `celery beat` ne fonctionne pas nativement sous Windows.

**Solution** : Utiliser `eventlet` ou déployer sur Linux.

```bash
pip install eventlet
celery -A restaurant worker -l info -P eventlet
celery -A restaurant beat -l info
```

Ou déployer sur **Render/Heroku** (Linux) en production.

### 9. Configuration Email Gmail

**Problème** : Erreur "Authentication failed" avec Gmail.

**Solution** :
1. Activer la validation en 2 étapes
2. Générer un **mot de passe d'application**
3. Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # Mot de passe app (16 caractères)
EMAIL_USE_TLS=True
```

### 10. Déploiement sur Render

**Problèmes rencontrés** :
- Port dynamique (`$PORT`)
- Collecte des fichiers statiques
- Variables d'environnement

**Solutions** :

`settings.py` :
```python
if 'RENDER' in os.environ:
    PORT = os.getenv('PORT', '8000')
    ALLOWED_HOSTS.append(os.getenv('RENDER_EXTERNAL_HOSTNAME', ''))
```

`build.sh` :
```bash
#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

---

## 🧪 Tests et validation

### Tests manuels effectués

#### ✅ Authentification
- [x] Login avec identifiant valide
- [x] Login avec mot de passe incorrect → erreur
- [x] Login avec compte inactif → erreur
- [x] Logout → redirection vers login
- [x] Accès sans authentification → redirection

#### ✅ Permissions par rôle
- [x] Table ne peut pas accéder à `/menu/cuisinier/`
- [x] Serveur ne peut pas accéder à `/paiements/caisse/`
- [x] Cuisinier ne peut pas accéder à `/restaurant/tables/`
- [x] Comptable ne peut pas marquer une commande comme payée
- [x] Admin peut tout faire

#### ✅ Workflow Table
- [x] Voir les plats disponibles uniquement
- [x] Filtrer par catégorie
- [x] Ajouter un plat au panier (quantité 1-10)
- [x] Modifier la quantité dans le panier
- [x] Supprimer un plat du panier
- [x] Calcul automatique du total
- [x] Validation du panier → création de commande
- [x] Panier vidé après validation
- [x] Voir l'historique des commandes

#### ✅ Workflow Serveur
- [x] Voir la liste des tables avec états
- [x] Filtrer par statut (Libre, En attente, Servie)
- [x] Voir les détails d'une table
- [x] Marquer une commande "Servie" → statut mis à jour
- [x] Marquer une commande "Payée" → paiement créé + caisse mise à jour
- [x] Traçabilité : serveur enregistré dans `serveur_ayant_servi`

#### ✅ Workflow Cuisinier
- [x] Voir tous les plats (disponibles + non disponibles)
- [x] Filtrer par catégorie et disponibilité
- [x] Ajouter un plat avec image
- [x] Modifier un plat existant
- [x] Activer/Désactiver un plat
- [x] Pas de bouton de suppression (seulement désactivation)

#### ✅ Workflow Comptable
- [x] Dashboard caisse : solde affiché
- [x] Filtrer par période (Aujourd'hui, Semaine, Mois, Tout)
- [x] Voir les derniers paiements
- [x] Enregistrer une dépense valide → solde diminué
- [x] Tenter une dépense avec solde insuffisant → erreur
- [x] Voir l'historique des dépenses

#### ✅ Workflow Admin
- [x] CRUD utilisateurs complet
- [x] CRUD tables physiques
- [x] Dashboard analytics affiché
- [x] Export Excel téléchargé
- [x] Export PDF généré
- [x] Email de test envoyé

#### ✅ Intégrité des données
- [x] Solde de la caisse cohérent (paiements - dépenses)
- [x] Transactions atomiques fonctionnelles
- [x] Pas de commandes orphelines
- [x] Images uploadées correctement
- [x] Prix historiques conservés dans CommandeItem

### Tests automatisés (à ajouter)

```python
# tests.py (exemple)
from django.test import TestCase, Client
from apps.accounts.models import User
from apps.menu.models import Plat
from decimal import Decimal

class MenuTestCase(TestCase):
    def setUp(self):
        self.cuisinier = User.objects.create_user(
            login='COOK001',
            password='Test@123',
            role='Rcuisinier'
        )
        
    def test_create_plat(self):
        plat = Plat.objects.create(
            nom="Test Plat",
            prix_unitaire=Decimal("10000"),
            categorie="PLAT"
        )
        self.assertEqual(plat.nom, "Test Plat")
        self.assertTrue(plat.disponible)
        
    def test_cuisinier_can_access_menu(self):
        self.client.login(login='COOK001', password='Test@123')
        response = self.client.get('/menu/cuisinier/')
        self.assertEqual(response.status_code, 200)
```

**Lancer les tests** :
```bash
python manage.py test
```

---

## 🚀 Déploiement

### Option 1 : Render (Recommandé - Gratuit)

**Étapes** :

1. **Créer un compte sur** [Render.com](https://render.com)

2. **Créer un fichier `build.sh`** :
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

3. **Créer un nouveau Web Service** :
   - Repository : GitHub/GitLab
   - Build Command : `./build.sh`
   - Start Command : `gunicorn restaurant.wsgi:application`
   - Environment : Python 3

4. **Ajouter les variables d'environnement** :
```
SECRET_KEY=...
DEBUG=False
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

5. **Ajouter un Redis service** (pour Celery) :
   - Type : Redis
   - Plan : Free

6. **Ajouter un Background Worker** (pour Celery) :
   - Command : `celery -A restaurant worker -l info`

7. **Ajouter un Cron Job** (pour Celery Beat) :
   - Command : `python manage.py shell -c "from apps.dashboard.tasks import envoyer_rapport_quotidien; envoyer_rapport_quotidien()"`
   - Schedule : `0 18 * * *` (18h chaque jour)

### Option 2 : Heroku

**Étapes** :

1. **Créer un `Procfile`** :
```
web: gunicorn restaurant.wsgi
worker: celery -A restaurant worker -l info
beat: celery -A restaurant beat -l info
```

2. **Créer un `runtime.txt`** :
```
python-3.11.6
```

3. **Déployer** :
```bash
heroku create mon-restaurant
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:mini
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 3 : VPS (DigitalOcean, Linode)

**Stack complète** :
- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- PostgreSQL (base de données)
- Redis (Celery broker)
- Supervisor (gestion des processus)

**Guide complet** : https://docs.djangoproject.com/en/5.1/howto/deployment/

---

## 🗺️ Roadmap

### Fonctionnalités futures

#### Court terme (v2.0)
- [ ] **Notifications en temps réel** (WebSockets) : Alertes cuisine quand nouvelle commande
- [ ] **Mode hors ligne** (PWA) : Fonctionnement sans connexion internet
- [ ] **Scan QR Code** : Menu accessible via QR code sur la table
- [ ] **Multi-langues** : Français, Anglais, Soussou, Poular
- [ ] **Photos multiples** : Plusieurs photos par plat
- [ ] **Catégories personnalisables** : Administrateur peut créer ses propres catégories

#### Moyen terme (v3.0)
- [ ] **Application mobile native** (React Native/Flutter)
- [ ] **Paiement électronique** : Intégration Orange Money, MTN Mobile Money
- [ ] **Système de réservation** : Réserver une table en ligne
- [ ] **Programme de fidélité** : Points de fidélité pour clients réguliers
- [ ] **Gestion des stocks** : Ingrédients, alertes de rupture
- [ ] **Multi-restaurants** : Support de plusieurs établissements

#### Long terme (v4.0)
- [ ] **IA prédictive** : Prédiction des ventes, recommandations automatiques
- [ ] **Intégration comptable** : Export vers logiciels comptables (Sage, QuickBooks)
- [ ] **API publique** : Permettre l'intégration avec d'autres services
- [ ] **White label** : Personnalisation complète pour d'autres restaurants

### Améliorations techniques

- [ ] **Tests unitaires** : Couverture 80%+
- [ ] **Tests d'intégration** : Selenium/Playwright
- [ ] **CI/CD** : GitHub Actions pour déploiement automatique
- [ ] **Monitoring** : Sentry pour erreurs, New Relic pour performance
- [ ] **Logs structurés** : ELK stack (Elasticsearch, Logstash, Kibana)
- [ ] **Cache** : Redis pour requêtes fréquentes
- [ ] **CDN** : Cloudflare pour fichiers statiques/images

---

## 🤝 Contributions

Ce projet est un projet académique personnel, mais les contributions sont bienvenues !

### Comment contribuer

1. **Forker le repository**
2. **Créer une branche** : `git checkout -b feature/ma-fonctionnalite`
3. **Committer** : `git commit -m "Ajout de ma fonctionnalité"`
4. **Pusher** : `git push origin feature/ma-fonctionnalite`
5. **Ouvrir une Pull Request**

### Conventions de code

- **PEP 8** pour Python
- **Commentaires en français** dans le code
- **Docstrings** pour toutes les fonctions/classes
- **Tests** pour toutes les nouvelles fonctionnalités

### Rapporter un bug

Ouvrez une **issue** sur GitHub avec :
- Description du problème
- Étapes pour reproduire
- Comportement attendu vs observé
- Screenshots si pertinent

---

## 👨‍💻 Auteur

**Souleymane Diallo**  
Étudiant en développement logiciel - L4 Cours Python

### Contact
- 📧 Email : soulmamoudou0@gmail.com
- 📱 Téléphone : +224 624 81 59 98
- 💼 LinkedIn : [Souleymane Diallo](https://www.linkedin.com/in/souleymane-diallo-1b6424229/)
- 🐙 GitHub : [Grey-kingreys](https://github.com/Grey-kingreys)

### Remerciements

- **Mr Mamadou Dara Sow** : Pour le cahier des charges et l'encadrement
- **Anthropic** : Pour Claude AI (assistance au développement)
- **Communauté Django** : Pour la documentation exceptionnelle
- **Tailwind Labs** : Pour Tailwind CSS

---

## 📜 Licence

Ce projet est développé dans un **cadre académique**. 

**Utilisation** :
- ✅ Libre pour usage éducatif et personnel
- ✅ Peut servir de référence pour d'autres projets académiques
- ❌ Pas d'utilisation commerciale sans permission
- ❌ Pas de redistribution sans attribution

**Copyright © 2025 Souleymane Diallo - Tous droits réservés**

---

## 📚 Ressources et références

### Documentation officielle
- [Django 5.1](https://docs.djangoproject.com/en/5.1/)
- [Tailwind CSS 4.1](https://tailwindcss.com/docs)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Celery](https://docs.celeryq.dev/)
- [Pillow](https://pillow.readthedocs.io/)

### Tutoriels utilisés
- Django for Beginners - William S. Vincent
- Two Scoops of Django - Audrey & Daniel Roy Greenfeld
- Test-Driven Development with Django - Harry J.W. Percival

### Outils
- [Neon.tech](https://neon.tech) : PostgreSQL hébergé gratuit
- [Render.com](https://render.com) : Déploiement gratuit
- [Tailwind UI](https://tailwindui.com) : Composants Tailwind

---

## 🎓 Contexte académique

### Compétences développées

Ce projet a permis de mettre en pratique :

#### Backend Python/Django
- Architecture MTV (Model-Template-View)
- ORM Django : modèles, relations, migrations
- Authentification personnalisée (AbstractBaseUser)
- Permissions et décorateurs personnalisés
- Gestion de sessions (panier)
- Transactions atomiques
- Signaux Django
- Tâches asynchrones (Celery)
- Management commands
- Tests unitaires

#### Frontend
- HTML5 sémantique
- Tailwind CSS (utility-first)
- Responsive design (mobile-first)
- JavaScript vanilla
- Formulaires Django
- Messages flash
- Template inheritance

#### Base de données
- Modélisation relationnelle
- PostgreSQL
- Migrations
- Indexes et optimisation
- Transactions ACID

#### Déploiement & DevOps
- Git & GitHub
- Variables d'environnement (.env)
- Fichiers statiques (collectstatic, WhiteNoise)
- Serveur WSGI (Gunicorn)
- Déploiement cloud (Render)
- Configuration Celery/Redis

#### Gestion de projet
- Cahier des charges
- Découpage en sprints (6 parties)
- Tests et validation
- Documentation technique
- Versioning (Git)

---

## 📊 Statistiques du projet

- **Lignes de code Python** : ~5,000+
- **Templates HTML** : 40+
- **Modèles Django** : 8 principaux
- **Vues** : 50+
- **Fichiers CSS** : Tailwind (compilé)
- **Durée de développement** : 4 semaines
- **Commits Git** : 100+
- **Technologies utilisées** : 15+

---

## ❓ FAQ

### Q: Puis-je utiliser ce projet pour mon propre restaurant ?
**R:** Oui, mais le projet est académique et nécessiterait des améliorations pour une utilisation en production (tests complets, sécurité renforcée, monitoring, etc.).

### Q: Pourquoi PostgreSQL et pas MySQL ?
**R:** PostgreSQL offre un hébergement gratuit via Neon.tech, ce qui facilite le déploiement. MySQL fonctionne aussi, il suffit de changer le driver dans `requirements.txt` et `settings.py`.

### Q: Le paiement électronique est-il supporté ?
**R:** Non, actuellement seul le paiement physique est géré (validation manuelle dans le système). C'était une contrainte du cahier des charges.

### Q: Comment ajouter un nouveau rôle utilisateur ?
**R:** 
1. Ajouter le rôle dans `User.ROLE_CHOICES`
2. Créer un décorateur dans `decorators.py`
3. Créer les vues spécifiques
4. Mettre à jour les templates

### Q: Les images sont-elles optimisées ?
**R:** Pillow effectue une validation de base (format, taille max 5MB). Pour une optimisation poussée, utilisez `django-imagekit` ou `easy-thumbnails`.

### Q: Puis-je désactiver Celery en développement ?
**R:** Oui, les tâches Celery sont optionnelles. Sans Celery, l'envoi d'email automatique ne fonctionnera pas, mais le reste de l'application fonctionne normalement.

### Q: Comment changer le fuseau horaire ?
**R:** Dans `settings.py`, modifiez `TIME_ZONE = 'Africa/Conakry'` vers votre fuseau.

---

## 🆘 Support

### Problèmes courants

#### Erreur "