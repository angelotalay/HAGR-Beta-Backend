# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0002_auto_20231003_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drugageresults',
            name='average_lifespan',
            field=models.ForeignKey(db_column=b'average_lifespan', blank=True, to='drugage.AverageLifespan', null=True),
        ),
        migrations.AlterField(
            model_name='drugageresults',
            name='max_lifespan',
            field=models.ForeignKey(db_column=b'max_lifespan', blank=True, to='drugage.MaxLifespan', null=True),
        ),
    ]
