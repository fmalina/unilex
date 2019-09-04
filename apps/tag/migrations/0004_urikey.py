# Generated by Django 2.2.3 on 2019-09-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0003_desc_text_url_to_uri'),
    ]

    operations = [
        migrations.RenameField('record', 'uri', 'key'),
        migrations.AlterField(
            model_name='record',
            name='key',
            field=models.CharField(max_length=150, unique=True, verbose_name='Key / URI / Unique Resource ID'),
        ),
    ]
