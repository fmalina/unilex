from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('vocabulary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocabulary',
            name='private',
            field=models.BooleanField(
                verbose_name='Private vocabulary', default=False,
                help_text='Private vocabulary can be edited only by the users belonging to its authority.'),
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='description',
            field=models.TextField(null=True, max_length=200, blank=True),
        ),
    ]
