from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Python import path for this app package
    name = 'Route66Store'
    # Keep the Django app label as "store" so existing
    # database tables and migrations continue to work.
    label = 'store'
    verbose_name = 'Route66 Store'
