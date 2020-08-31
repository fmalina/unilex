from django.db import migrations, models
from unilex.vocabulary.models import Vocabulary


def unique_node_id(apps, schema_editor):
    for v in Vocabulary.objects.all():
        count = Vocabulary.objects.filter(node_id=v.node_id).count()
        if count > 1:
            v.node_id = v.make_node_id(v.node_id)
            v.save(update_fields=['node_id'])


class Migration(migrations.Migration):
    dependencies = [
        ('vocabulary', '0006_ondelete_protect'),
    ]

    operations = [
        migrations.RunPython(unique_node_id),
        migrations.AlterField(
            model_name='vocabulary',
            name='node_id',
            field=models.SlugField(max_length=60, unique=True,
                                   verbose_name='Permalink: /vocabularies/'),
        ),
    ]
