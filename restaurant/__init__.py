# restaurant/__init__.py
"""
Configuration d'initialisation du projet Restaurant.
Ce fichier est exécuté au démarrage de Django.
"""

import os
import sys

# Ajouter des vérifications ou configurations globales ici
def check_environment():
    """Vérifie que l'environnement est correctement configuré"""
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"⚠️  Variables d'environnement manquantes: {', '.join(missing)}")
        print("Assurez-vous que votre fichier .env est correctement configuré.")
        if os.getenv('DEBUG', '').lower() == 'true':
            print("Mode DEBUG activé - continuer avec des valeurs par défaut...")
        else:
            print("❌ Impossible de démarrer en production sans ces variables.")
            sys.exit(1)

# Exécuter la vérification au chargement
if __name__ != "__main__":
    check_environment()
    
print("✅ Configuration PostgreSQL chargée avec succès")