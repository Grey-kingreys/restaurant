# test_connection.py
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant.settings')
django.setup()

from django.db import connection

print("🔍 Test de connexion à PostgreSQL Neon.tech...")
print(f"Host: {connection.settings_dict['HOST']}")
print(f"Database: {connection.settings_dict['NAME']}")
print(f"User: {connection.settings_dict['USER']}")

try:
    with connection.cursor() as cursor:
        # Test 1: Version PostgreSQL
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL Version: {version[0].split(',')[0]}")
        
        # Test 2: Base de données
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"✅ Database connectée: {db_name[0]}")
        
        # Test 3: Heure serveur
        cursor.execute("SELECT NOW();")
        server_time = cursor.fetchone()
        print(f"✅ Heure serveur: {server_time[0]}")
        
        # Test 4: Liste des tables (après migration)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"✅ Tables trouvées: {len(tables)}")
            for table in tables[:5]:  # Affiche les 5 premières
                print(f"   - {table[0]}")
        else:
            print("ℹ️  Aucune table trouvée. Exécutez 'python manage.py migrate'")
            
except Exception as e:
    print(f"❌ Erreur de connexion: {type(e).__name__}")
    print(f"   Détail: {e}")
    sys.exit(1)