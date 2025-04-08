from django.apps import AppConfig

class SearchConfig(AppConfig):
    """
    Application configuration for the search app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        This could include setting up signal handlers for indexing content on save.
        """
        # Import signals to register handlers
        import search.signals
        pass
