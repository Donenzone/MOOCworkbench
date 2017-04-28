from django.contrib import admin

from .models import CookieCutterTemplate, CookieCutterLocationToStepMapping


admin.site.register(CookieCutterTemplate)
admin.site.register(CookieCutterLocationToStepMapping)
