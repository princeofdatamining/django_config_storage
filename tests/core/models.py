from django.db import models

from config_storage.models import Configuration

class RootSetting(Configuration):

    class Meta:
        abstract = True
        verbose_name = verbose_name_plural = '全局配置'

    rmb_to_coin = models.IntegerField()
    text_price = models.IntegerField()
    about_us = models.CharField(max_length=191)
