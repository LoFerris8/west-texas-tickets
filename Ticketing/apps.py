from django.apps import AppConfig

class TicketingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ticketing'
    
    def ready(self):
        import Ticketing.signals