from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'  # This should match the app name
    app_name = 'blog'  # This sets the app_name attribute
