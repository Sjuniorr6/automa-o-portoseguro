from django.apps import AppConfig


class Formulario2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'formulario2'
    
    def ready(self):
        """Registra os signals quando o app estiver pronto"""
        import formulario2.signals