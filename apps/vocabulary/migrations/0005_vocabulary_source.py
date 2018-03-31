from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0004_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocabulary',
            name='source',
            field=models.URLField(blank=True),
        ),
    ]
