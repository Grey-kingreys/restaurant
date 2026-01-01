from django.apps import AppConfig


class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.menu'
    verbose_name = 'Gestion du Menu'
    
    def ready(self):
        """
        Méthode appelée quand l'application est prête
        Utilisée pour importer des signaux si nécessaire
        """
        pass