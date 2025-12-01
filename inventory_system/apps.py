from django.apps import AppConfig


class InventorySystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_system'
    
    def ready(self):
        import inventory_system.signals
        
        # Clear all sessions on server start (logs out all users from previous session)
        # This runs when the server starts, ensuring no stale sessions persist
        import sys
        import os
        
        # Only clear sessions on actual server run, not during migrations or other commands
        # Also check RUN_MAIN to only run once (not on reloader process)
        is_server_run = 'runserver' in sys.argv or 'uvicorn' in sys.argv or ('gunicorn' in sys.argv[0] if sys.argv else False)
        is_main_process = os.environ.get('RUN_MAIN') == 'true'
        
        if is_server_run and is_main_process:
            try:
                from django.contrib.sessions.models import Session
                # Delete all sessions - this logs out everyone
                deleted_count = Session.objects.all().delete()[0]
                if deleted_count > 0:
                    print(f"[Auth] Cleared {deleted_count} session(s) from previous server run.")
            except Exception as e:
                # Silently fail if sessions table doesn't exist yet (e.g., fresh install)
                pass