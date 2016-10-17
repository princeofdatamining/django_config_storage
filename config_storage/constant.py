from django.utils.translation import ugettext_lazy as _, ungettext_lazy, pgettext_lazy, npgettext_lazy

APP_LABEL = 'config_storage'
APP_VERBOSE_NAME = pgettext_lazy('App', APP_LABEL)

MODEL_VERBOSE_CONF = pgettext_lazy("Model", "Configuration")
MODEL_VERBOSE_CONFS = pgettext_lazy("Model", "Configurations")
