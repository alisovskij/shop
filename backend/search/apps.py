from django.apps import AppConfig
from elasticsearch_dsl.connections import connections


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'

    def ready(self):
        from .signals import CustomSignalProcessor
        es_connections = connections
        signal_processor = CustomSignalProcessor(connections=es_connections)
        signal_processor.setup()

