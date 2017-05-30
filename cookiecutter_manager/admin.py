from django.contrib import admin

from .models import CookieCutterLocationToStepMapping, CookieCutterTemplate

admin.site.register(CookieCutterTemplate)
admin.site.register(CookieCutterLocationToStepMapping)
