# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0008_auto_20231212_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='drugageresults',
            name='pvalue',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
