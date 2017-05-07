from django.apps import AppConfig


class UsermanagerConfig(AppConfig):
    name = 'user_manager'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('WorkbenchUser'))
        from django.contrib.auth.models import User
        registry.register(User)

