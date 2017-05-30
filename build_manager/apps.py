"""Extra application configuration options for the build_manager app"""
from django.apps import AppConfig


class BuildManagerConfig(AppConfig):
    """Application configuration for the build_manager"""
    name = 'build_manager'
    verbose_name = 'Build Manager'
