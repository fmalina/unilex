from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0002_accountability'),
    ]

    operations = [
        migrations.RenameField('record', 'url', 'uri'),
        migrations.AlterField(
            model_name='record',
            name='desc',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
    ]
