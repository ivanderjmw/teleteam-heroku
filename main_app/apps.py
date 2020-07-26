from django.apps import AppConfig

class MainAppConfig(AppConfig):
    name = 'main_app'
    
    def ready(self):
        from teleteam_bot.recurring_tasks import setup_recurring_tasks
        setup_recurring_tasks()

        import main_app.post_save_actions
