# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AverageLifespan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p_value', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('average_lifespan_change_percent', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
            ],
            options={
                'verbose_name': 'Average Lifespan (% Change)',
                'db_table': 'average_lifespan',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MaxLifespan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p_value', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('max_lifespan_change_percent', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
            ],
            options={
                'verbose_name': 'Max Lifespan (% Change)',
                'db_table': 'max_lifespan',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='drugageresults',
            name='age_at_treatment',
            field=models.IntegerField(max_length=3, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='drugageresults',
            name='average_lifespan',
            field=models.ForeignKey(db_column=b'average_lifespan', to='drugage.AverageLifespan', null=True),
        ),
        migrations.AddField(
            model_name='drugageresults',
            name='max_lifespan',
            field=models.ForeignKey(db_column=b'max_lifespan', to='drugage.MaxLifespan', null=True),
        ),
    ]
