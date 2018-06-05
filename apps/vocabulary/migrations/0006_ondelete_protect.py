from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0005_vocabulary_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vocabulary',
            name='authority',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=models.PROTECT,
                                    to='vocabulary.Authority'),
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='language',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=models.PROTECT,
                                    to='vocabulary.Language'),
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='user',
            field=models.ForeignKey(on_delete=models.PROTECT,
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
