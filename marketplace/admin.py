from django.contrib import admin
from marketplace.models import PackageLanguage, PackageCategory

# Register your models here.
admin.site.register(PackageLanguage)
admin.site.register(PackageCategory)