# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import daa.atlas.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=daa.atlas.models.generate_identifier, max_length=20)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('type', models.CharField(help_text=b'As a hint, changes to a gene (e.g. gene expression, proteomics) are usually molecular, changes that occur whole body, such as hormonal changes, are physiological', max_length=15, db_index=True, choices=[('physiological', 'Physiological'), ('molecular', 'Molecular'), ('pathological', 'Pathological'), ('psychological', 'Psychological')])),
                ('gender', models.CharField(default='male/female', max_length=15, choices=[('male', 'Male'), ('female', 'Female'), ('male/female', 'Male/Female')])),
                ('date_entered', models.DateTimeField(default=django.utils.timezone.now)),
                ('starts_age', models.IntegerField(help_text=b"Use -1 if you don't know the actual start date.")),
                ('ends_age', models.IntegerField(help_text=b"Use -1 if you don't know the end date. If both of the fields contain -1, a message will be displayed that the age this occurs is unknown.")),
                ('time_measure', models.CharField(default=b'years', max_length=10, choices=[('years', 'Years'), ('months', 'Months')])),
                ('description', models.TextField(help_text=b'You can use Markdown formatting in this field. See <a href="http://daringfireball.net/projects/markdown/syntax">here for more details</a>. Basically, paragraphs will be kept, _word_ for italic, **word** for bold, [words here](http://ageing-map.org) for a link.', null=True, blank=True)),
                ('hide', models.BooleanField(default=False, help_text=b'Hides the change from the interface but leaves it present in the database')),
            ],
            options={
                'ordering': ('name', 'type'),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=20, choices=[(b'percentage', b'Percentage Change'), (b'equation', b'Equation'), (b'series', b'Series'), (b'incidence', b'Incidence Series'), (b'morbidity', b'Morbidity Series')])),
                ('plot', models.CharField(default=b'none', max_length=20, choices=[(b'none', b'Do not plot'), (b'linear', b'Linear Line'), (b'exponential', b'Exponential Line'), (b'line', b'Line'), (b'bar', b'Bar'), (b'column', b'Column'), (b'point', b'Point'), (b'pie', b'Pie')])),
                ('sample_size', models.IntegerField(null=True, blank=True)),
                ('measure', models.CharField(max_length=30, null=True, blank=True)),
                ('method_collection', models.CharField(max_length=50, null=True, blank=True)),
                ('data_transforms', models.CharField(max_length=50, null=True, blank=True)),
                ('percentage_change', models.FloatField(null=True, blank=True)),
                ('p_value', models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=20)),
                ('point', models.FloatField()),
            ],
            options={
                'ordering': ['label'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entrez_id', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('symbol', models.CharField(max_length=20, db_index=True)),
                ('alias', models.CharField(db_index=True, max_length=50, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('omim', models.CharField(max_length=20, null=True, blank=True)),
                ('ensembl', models.CharField(db_index=True, max_length=20, null=True, blank=True)),
                ('uniprot', models.CharField(max_length=20, null=True, blank=True)),
                ('unigene', models.CharField(max_length=20, null=True, blank=True)),
                ('in_genage', models.BooleanField(default=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GOTerm',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('term', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=20, choices=[(b'process', b'process'), (b'function', b'function'), (b'component', b'component')])),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Homolog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(max_length=20)),
                ('entrez_id', models.PositiveIntegerField()),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'change_images/')),
                ('caption', models.TextField(help_text=b'An optional caption displayed under the image, supports markdown formatting', null=True, blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('text', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taxonomy_id', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50, null=True, blank=True)),
                ('hasDatabase', models.BooleanField()),
            ],
            options={
                'ordering': ['common_name'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('website', models.URLField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProcessMeasured',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, db_index=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['group'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PropertyGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pubmed', models.CharField(db_index=True, max_length=20, null=True, blank=True)),
                ('title', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('author', models.CharField(db_index=True, max_length=100, null=True, blank=True)),
                ('publisher', models.CharField(max_length=50, null=True, blank=True)),
                ('volume', models.CharField(max_length=20, null=True, blank=True)),
                ('pages', models.CharField(max_length=20, null=True, blank=True)),
                ('year', models.PositiveIntegerField()),
                ('journal', models.CharField(max_length=50, null=True, blank=True)),
                ('editor', models.CharField(max_length=50, null=True, blank=True)),
                ('book_title', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('isbn', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
                'ordering': ['-year'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(blank=True, max_length=20, null=True, help_text=b'This had a purpose at one time, but I no longer know what any of these terms mean. Best ignoring it.', choices=[(b'etiology', b'Etiology'), (b'definition', b'Definition')])),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tissue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('evid', models.PositiveIntegerField(default=daa.atlas.models.generate_evid)),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('synonyms', models.CharField(max_length=100, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('inInterface', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('data_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='atlas.Data')),
            ],
            options={
                'managed': False,
            },
            bases=('atlas.data',),
        ),
        migrations.CreateModel(
            name='Equation',
            fields=[
                ('data_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='atlas.Data')),
                ('coefficiant', models.DecimalField(max_digits=30, decimal_places=25)),
                ('intercept', models.DecimalField(max_digits=30, decimal_places=25)),
                ('is_negative', models.BooleanField()),
                ('p_value_d', models.DecimalField(null=True, max_digits=30, decimal_places=25, blank=True)),
            ],
            options={
                'managed': False,
            },
            bases=('atlas.data',),
        ),
        migrations.CreateModel(
            name='Percentage',
            fields=[
                ('data_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='atlas.Data')),
                ('is_negative', models.BooleanField(verbose_name=b'Is negative or decreases')),
            ],
            options={
                'managed': False,
            },
            bases=('atlas.data',),
        ),
    ]
