from django.apps import AppConfig

class ExpungerConfig(AppConfig):
    name = 'expunger'
    verbose_name = 'Expunger App'

    def ready(self):
        import expunger.signals 

            
        