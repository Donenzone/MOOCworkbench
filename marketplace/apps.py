from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    name = 'marketplace'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('InternalPackage'))
        registry.register(self.get_model('ExternalPackage'))
        registry.register(self.get_model('PackageResource'))
        registry.register(self.get_model('PackageVersion'))

