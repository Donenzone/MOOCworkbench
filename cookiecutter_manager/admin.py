"""Registers the CookieCutterTemplate and CookieCutterLocationToStepMapping to admin"""
from django.contrib import admin

from .models import CookieCutterLocationToStepMapping, CookieCutterTemplate

admin.site.register(CookieCutterTemplate)
admin.site.register(CookieCutterLocationToStepMapping)
