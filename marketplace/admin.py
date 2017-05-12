from django.contrib import admin
from marketplace.models import Language, Category,  PackageResource

# Register your models here.
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(PackageResource)