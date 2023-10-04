# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0003_auto_20231003_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drugageresults',
            name='biblio_id',
            field=models.ForeignKey(db_column=b'biblio_id', blank=True, to='drugage.DrugAgeBiblio', null=True),
        ),
    ]
