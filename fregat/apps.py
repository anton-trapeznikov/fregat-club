from django.apps import AppConfig


class FregatConfig(AppConfig):
    name = 'fregat'
    verbose_name = "Фрегат"

    def ready(self):
        import fregat.signals