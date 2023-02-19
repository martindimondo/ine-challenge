"""
    Django app config
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    App User config
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
