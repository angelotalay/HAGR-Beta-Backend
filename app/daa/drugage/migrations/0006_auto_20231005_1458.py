# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0005_auto_20231004_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drugageresults',
            name='age_at_treatment',
        ),
        migrations.AddField(
            model_name='drugageresults',
            name='age_at_initiation',
            field=models.CharField(max_length=20, null=True, verbose_name=b'age at initiation of treatment', blank=True),
        ),
    ]
