from django.apps import AppConfig


class SampleVolumesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sample_volumes'

    def ready(self):
        from dataUpdater import updater
        updater.start()
