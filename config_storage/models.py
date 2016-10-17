from django.db import models
from django.utils.functional import cached_property
from django.conf import settings
from django.core import cache

import jsonfield
import inspect

# Create your models here.

from config_storage import constant


class Storage(models.Model):

    VERBOSE_NAEMS = {}

    class Meta:
        verbose_name = constant.MODEL_VERBOSE_CONF
        verbose_name_plural = constant.MODEL_VERBOSE_CONFS
        db_table = 'config_storage'

    key = models.CharField(max_length=191, unique=True)
    value = jsonfield.JSONField()
    is_active = models.BooleanField(default=True)

    @cached_property
    def conf_model(self):
        return confs[self.key]()

    # 显示对应 Configuration 的 verbose_name
    def __str__(self):
        if self.key in self.__class__.VERBOSE_NAEMS:
            return self.__class__.VERBOSE_NAEMS[self.key]
        s = str(self.conf_model._meta.verbose_name)
        return self.__class__.VERBOSE_NAEMS.setdefault(self.key, s)

    # 单独保存 Storage 的时候，也要更新 缓存、对应Configuration单例的属性
    # 主要用于 Admin 中的 save()
    def save(self, **kwargs):
        super(Storage, self).save(**kwargs)
        confs.cache and confs.cache.set(self.key, self.value)
        self.conf_model.update_attrs(self.value)


class Configuration(models.Model):

    class Meta:
        # 所有继承自 Configuration 的类也都要显式声明 abstract=True, 因为我们不需要创建该Model
        abstract = True

    @classmethod
    def unique_key(cls):
        return '{}.{}'.format(cls._meta.app_label, cls._meta.model_name)

    # 单例模式
    INSTANCES = {}

    def __new__(cls):
        if cls in Configuration.INSTANCES:
            return Configuration.INSTANCES[cls]
        confs.load()
        instance = super(Configuration, cls).__new__(cls)
        return Configuration.INSTANCES.setdefault(cls, instance)

    def __init__(self):
        super(Configuration, self).__init__()
        # 从 缓存、数据库 中获取初始值
        self.update_attrs()

    # 重置各项value
    def update_attrs(self, values=None):
        if values is None:
            values = self.get_or_create_storage()
        for f in self._meta.fields:
            if f.name in values:
                setattr(self, f.name, values.get(f.name))

    @classmethod
    def get_or_create_storage(cls):
        uk = cls.unique_key()
        # 从缓存读取
        values = confs.cache and confs.cache.get(uk)
        if values:
            return values
        try:
            # 从数据库读取
            values = Storage.objects.get(key=uk).value
        except Storage.DoesNotExist:
            # 初始化
            values = {
                f.name: cls.default_value(f)
                for f in cls._meta.fields
            }
            Storage.objects.create(key=uk, value=values)
        # 更新缓存
        confs.cache and confs.cache.set(uk, values)
        return values

    # 根据 Field 获取默认 value
    DEFAULT_VALUES = {
        models.BooleanField: False,
        models.DecimalField: .0,
        models.FloatField: .0,
        models.IntegerField: 0,
    }

    @classmethod
    def default_value(cls, f):
        if f.default is not models.NOT_PROVIDED:
            return f.default
        if f.null:
            return None
        return cls.DEFAULT_VALUES.get(type(f), '')

    def __str__(self):
        return str(self._meta.verbose_name)

    # 保存：更新 Storage 及 缓存
    def save(self, **kwargs):
        uk = self.unique_key()
        values = {
            f.name: getattr(self, f.name)
            for f in self._meta.fields
        }
        confs.cache and confs.cache.set(uk, values)
        Storage.objects.update_or_create(defaults=dict(value=values), key=uk)

    # 不用删除
    def delete(self):
        pass

#

class Configurations(dict):

    # 从 INSTALLED_APPS 中加载所有的 Configuration
    def load(self):
        if getattr(self, 'loaded', None):
            return
        self.loaded = True
        from django.apps import apps
        # 读取所有可见的 配置项
        keys, activated = [], []
        for row in Storage.objects.all():
            keys.append(row.key)
            row.is_active and activated.append(row.key)
        for appconfig in apps.get_app_configs():
            for _, klass in inspect.getmembers(appconfig.models_module, inspect.isclass):
                if issubclass(klass, Configuration) and klass is not Configuration:
                    uk = klass.unique_key()
                    self[uk] = klass
                    # 保持可见
                    if uk in activated:
                        activated.remove(uk)
                    elif uk in keys:
                        Storage.objects.filter(key=uk, is_active=False).update(is_active=True)
                    else:
                        klass.get_or_create_storage()
        # 未被加载的置为不可见
        for uk in activated:
            Storage.objects.filter(key=uk).update(is_active=False)

    # 缓存
    @cached_property
    def cache(self):
        alias = getattr(settings, 'CONFIGURATION_CACHE_NAME', 'configuration')
        try:
            return cache.caches[alias]
        except:
            pass
        try:
            return cache.caches[cache.DEFAULT_CACHE_ALIAS]
        except:
            pass

confs = Configurations()
