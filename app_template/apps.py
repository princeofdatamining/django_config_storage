from django.apps import AppConfig

from . import constant

class QAppConfig(AppConfig):

    name = 'app_template'
    verbose_name = constant.APP_VERBOSE_NAME

    def ready(self):
        pass
