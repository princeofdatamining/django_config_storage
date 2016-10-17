from django.apps import AppConfig, apps

from config_storage import constant

class QAppConfig(AppConfig):

    name = constant.APP_LABEL
    verbose_name = constant.APP_VERBOSE_NAME

    def ready(self):
        pass
