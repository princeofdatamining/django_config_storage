from django.db import models
from django.utils.functional import cached_property

import jsonfield
import inspect

from . import constant

invalid = object()

class Configuration(models.Model):

    class Meta:
        abstract = True

    def __str__(self):
        return self._meta.verbose_name

    @classmethod
    def unique_key(cls):
        return '.'.join((cls._meta.app_label, cls._meta.model_name))

    @cached_property
    def conf_keys(self):
        return {f.name for f in self._meta.fields}

    def get_or_create_storage(self, storages):
        self.storage, _ = storages.get_or_create(
            defaults=dict(value={}), key=self.unique_key(),
        )
        return self.storage

    def __init__(self, *args, **kwargs):
        storage = self.get_or_create_storage(Storages)
        values = {k:v for k,v in storage.value.items() if k in self.conf_keys}
        kwargs.update(values)
        super(Configuration, self).__init__(*args, **kwargs)

    def save(self):
        dirty = False
        for f in self.conf_keys:
            if not hasattr(self, f):
                continue
            value = getattr(self, f)
            if self.storage.value.get(f, invalid) == value:
                continue
            self.storage.value[f] = value
            dirty = True
        dirty and self.storage.save()

#

class Configurations(dict):

    def load(self, apps):
        for appconfig in apps.get_app_configs():
            for _, klass in inspect.getmembers(appconfig.models_module, inspect.isclass):
                if issubclass(klass, Configuration) and klass is not Configuration:
                    self[klass.unique_key()] = klass

configurations = confs = Configurations()

#

class StorageManager(models.Manager):

    pass

Storages = StorageManager()

class Storage(models.Model):

    class Meta:
        verbose_name = constant.CONF_VERBOSE_NAME
        verbose_name_plural = constant.CONF_VERBOSE_PLURAL

    objects = Storages

    key = models.CharField(max_length=191, unique=True)
    value = jsonfield.JSONField()

    def __str__(self):
        model = configurations.get(self.key)
        return model._meta.verbose_name
