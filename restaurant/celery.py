import os
from celery import Celery
from celery.schedules import crontab

# Définir le module de settings par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant.settings')

# Créer l'application Celery
app = Celery('restaurant')

# Charger la configuration depuis Django settings avec le préfixe CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-découvrir les tâches dans toutes les apps installées
app.autodiscover_tasks()

# ✅ CONFIGURATION DU SCHEDULER - Email quotidien à 18h
app.conf.beat_schedule = {
    'envoi-rapport-quotidien': {
        'task': 'apps.dashboard.tasks.envoyer_rapport_quotidien',
        'schedule': crontab(minute='*/1'),  # Tous les jours à 18h00
        # Pour tester, utilisez : crontab(minute='*/1')  # Toutes les minutes
    },
}

# Timezone
app.conf.timezone = 'Africa/Conakry'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')
