# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0007_auto_20231006_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drugageresults',
            name='avg_lifespan_p_value',
            field=models.CharField(blank=True, max_length=10, null=True, choices=[(b'NS', b'Non-significant'), (b'p<0.05', b'p<0.05'), (b'p<0.01', b'p<0.01'), (b'p<0.001', b'p<0.001'), (b'p<0.0001', b'p<0.0001')]),
        ),
        migrations.AlterField(
            model_name='drugageresults',
            name='max_lifespan_p_value',
            field=models.CharField(blank=True, max_length=10, null=True, choices=[(b'NS', b'Non-significant'), (b'p<0.05', b'p<0.05'), (b'p<0.01', b'p<0.01'), (b'p<0.001', b'p<0.001'), (b'p<0.0001', b'p<0.0001')]),
        ),
    ]
