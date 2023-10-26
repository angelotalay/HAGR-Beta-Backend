# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0006_auto_20231005_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drugageresults',
            name='compound_id',
            field=models.ForeignKey(db_column=b'compound_id', verbose_name=b'compound', to='drugage.DrugAgeCompounds'),
        ),
    ]
