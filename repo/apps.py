from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "repo"
    verbose_name = "Repo Automator Core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import repo.authentication
