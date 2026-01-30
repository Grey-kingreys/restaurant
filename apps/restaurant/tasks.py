# apps/restaurant/tasks.py

from celery import shared_task
from apps.restaurant.models import TableSession

@shared_task
def nettoyer_sessions_expirees():
    """
    Tâche Celery pour nettoyer les sessions expirées
    À exécuter toutes les 30 secondes ou 1 minute
    """
    count = TableSession.nettoyer_sessions_expirees()
    return f"{count} session(s) expirée(s)"