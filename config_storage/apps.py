from django.apps import AppConfig, apps

from . import constant

class QAppConfig(AppConfig):

    name = constant.APP_LABEL
    verbose_name = constant.APP_VERBOSE_NAME

    def ready(self):
        from .models import configurations
        configurations.load(apps)
