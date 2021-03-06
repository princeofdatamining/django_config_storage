# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-21 08:46
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=191, unique=True)),
                ('value', jsonfield.fields.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'config_storage',
                'verbose_name': 'Configuration',
                'verbose_name_plural': 'Configurations',
            },
        ),
    ]
