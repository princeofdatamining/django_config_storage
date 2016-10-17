from django.test import TestCase

from core import models
from config_storage.models import Storage

class ConfigTest(TestCase):

    def setUp(self):
        Storage.objects.all().delete()
        self.conf = models.RootSetting()

    def test(self):
        # not set
        self.assertEqual(0, self.conf.rmb_to_coin)
        # test set
        self.conf.rmb_to_coin = v = 100
        self.conf.save()
        # test get
        self.conf = models.RootSetting()
        self.assertEqual(v, self.conf.rmb_to_coin)
