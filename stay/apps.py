from django.apps import AppConfig

class StayConfig(AppConfig):
    name = 'stay'

    def ready(self):
        import stay.signals
