from django.apps import AppConfig
import threading
from emailclassifier.utils.email_content_extractor import start_email_watcher  # Import function to start the extractor

class EmailclassifierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emailclassifier'

    def ready(self):
        """Run the email watcher on Django startup"""
        threading.Thread(target=start_email_watcher, daemon=True).start()