from django.contrib import admin

from marketplace.models import Category, Language, PackageResource

# Register your models here.
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(PackageResource)
