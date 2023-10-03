# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DrugAgeBiblio',
            fields=[
                ('id_biblio', models.AutoField(max_length=11, serialize=False, primary_key=True)),
                ('terms', models.CharField(max_length=500, null=True, blank=True)),
                ('title', models.CharField(max_length=500, null=True, blank=True)),
                ('journal', models.CharField(max_length=500, null=True, blank=True)),
                ('author', models.CharField(max_length=500, null=True, blank=True)),
                ('volume', models.CharField(max_length=500, null=True, blank=True)),
                ('authors', models.CharField(max_length=500, null=True, blank=True)),
                ('pubmed', models.IntegerField(unique=True)),
                ('author_initials', models.CharField(max_length=500, null=True, blank=True)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('contact_addresses', models.CharField(max_length=500, null=True, blank=True)),
                ('issue', models.CharField(max_length=500, null=True, blank=True)),
                ('pages', models.CharField(max_length=500, null=True, blank=True)),
                ('editor', models.CharField(max_length=500, null=True, blank=True)),
                ('review', models.CharField(max_length=500, null=True, blank=True)),
                ('publisher', models.CharField(max_length=500, null=True, blank=True)),
                ('url', models.CharField(max_length=500, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'bibliographic reference',
                'db_table': 'biblio',
                'managed': False,
                'verbose_name_plural': 'bibliographic references',
            },
        ),
        migrations.CreateModel(
            name='DrugAgeCompounds',
            fields=[
                ('id', models.AutoField(max_length=11, serialize=False, primary_key=True)),
                ('compound_name', models.CharField(max_length=255, null=True, blank=True)),
                ('cas_number', models.CharField(max_length=25, null=True, blank=True)),
                ('pubchem_cid', models.IntegerField(max_length=10, null=True, blank=True)),
                ('iupac_name', models.CharField(max_length=800, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Compounds',
                'db_table': 'compounds',
                'managed': False,
                'verbose_name_plural': 'Compounds',
            },
        ),
        migrations.CreateModel(
            name='DrugAgeCompoundSynonyms',
            fields=[
                ('id', models.AutoField(max_length=11, serialize=False, primary_key=True)),
                ('synonym', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'Synonyms',
                'db_table': 'compound_synonyms',
                'managed': False,
                'verbose_name_plural': 'Synonyms',
            },
        ),
        migrations.CreateModel(
            name='DrugAgeResults',
            fields=[
                ('id', models.AutoField(max_length=11, serialize=False, primary_key=True)),
                ('species', models.CharField(max_length=255, null=True, blank=True)),
                ('gender', models.CharField(blank=True, max_length=15, null=True, choices=[(b'MALE', b'Male'), (b'FEMALE', b'Female'), (b'BOTH', b'Mixed'), (b'HERMAPHRODITE', b'Hermaphrodite')])),
                ('strain', models.CharField(max_length=255, null=True, blank=True)),
                ('dosage', models.CharField(max_length=100, null=True, blank=True)),
                ('avg_lifespan_change_percent', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('max_lifespan_change_percent', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('significance', models.CharField(blank=True, max_length=255, null=True, choices=[(b'S', b'Significant'), (b'NS', b'Non-significant'), (b'', b'')])),
                ('pubmed_id', models.IntegerField(max_length=11)),
                ('notes', models.CharField(max_length=2000, null=True, blank=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('biblio_id', models.ForeignKey(to='drugage.DrugAgeBiblio', db_column=b'biblio_id')),
                ('compound_id', models.ForeignKey(to='drugage.DrugAgeCompounds', db_column=b'compound_id')),
            ],
            options={
                'verbose_name': 'Results',
                'db_table': 'results',
                'managed': True,
                'verbose_name_plural': 'Results',
            },
        ),
    ]
