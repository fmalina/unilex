from django.db import models, migrations
import datetime


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AttributeOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False,
                                        auto_created=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('name', models.SlugField(verbose_name='Attribute name', max_length=100)),
                ('validation', models.CharField(
                    verbose_name='Field Validations', max_length=100,
                    choices=[
                        ('vocabulary.validation_utils.validation_simple', 'One or more characters'),
                        ('vocabulary.validation_utils.validation_integer', 'Integer number'),
                        ('vocabulary.validation_utils.validation_yesno', 'Yes or No'),
                        ('vocabulary.validation_utils.validation_decimal', 'Decimal number')
                    ]
                )),
                ('sort_order', models.IntegerField(default=1, verbose_name='Sort Order')),
                ('error_message', models.CharField(default='Invalid Entry',
                                                   verbose_name='Error Message', max_length=100)),
            ],
            options={
                'db_table': 'concepts_attribute_options',
                'ordering': ('sort_order',),
            },
        ),
        migrations.CreateModel(
            name='Authority',
            fields=[
                ('code', models.CharField(primary_key=True, serialize=False, max_length=5,
                                          help_text='Uppercase shorthand, no spaces, only set once')),
                ('name', models.CharField(max_length=150)),
            ],
            options={'verbose_name_plural': 'Authorities'},
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True,
                                        serialize=False, auto_created=True)),
                ('node_id', models.SlugField(max_length=60, blank=True,
                                             verbose_name='Permalink ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('query', models.TextField(blank=True)),
                ('count', models.IntegerField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('parent', models.ManyToManyField(related_name='children',
                                                  to='vocabulary.Concept', blank=True)),
                ('related', models.ManyToManyField(related_name='related_concepts',
                                                   to='vocabulary.Concept', blank=True)),
            ],
            options={
                'db_table': 'concepts',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ConceptAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True,
                                        serialize=False, auto_created=True)),
                ('value', models.CharField(verbose_name='Value', max_length=255)),
                ('concept', models.ForeignKey(to='vocabulary.Concept',
                                              on_delete=models.CASCADE)),
                ('option', models.ForeignKey(to='vocabulary.AttributeOption',
                                             on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'concepts_attributes',
                'verbose_name_plural': 'Notes: Concept Attributes',
                'verbose_name': 'Note: Concept Attribute',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('iso', models.CharField(verbose_name='ISO code', primary_key=True,
                                         serialize=False, max_length=5)),
                ('name', models.CharField(max_length=60)),
            ],
            options={
                'db_table': 'languages',
            },
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True,
                                        serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('concept', models.ForeignKey(to='vocabulary.Concept', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'concepts_synonyms',
            },
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True,
                                        serialize=False, auto_created=True)),
                ('node_id', models.SlugField(verbose_name='Permalink: /tree/',
                                             max_length=60)),
                ('title', models.CharField(max_length=75)),
                ('description', models.TextField(max_length=200, blank=True)),
                ('queries', models.BooleanField(default=False, verbose_name='Enable queries?')),
                ('updated_at', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('authority', models.ForeignKey(to='vocabulary.Authority', on_delete=models.CASCADE,
                                                blank=True, null=True)),
                ('language', models.ForeignKey(to='vocabulary.Language', on_delete=models.CASCADE,
                                               blank=True, null=True)),
            ],
            options={
                'db_table': 'vocabularies',
                'verbose_name_plural': 'Vocabularies',
            },
        ),
        migrations.AddField(
            model_name='concept',
            name='vocabulary',
            field=models.ForeignKey(to='vocabulary.Vocabulary', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='synonym',
            unique_together=set([('concept', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='concept',
            unique_together=set([('node_id', 'vocabulary')]),
        ),
    ]
