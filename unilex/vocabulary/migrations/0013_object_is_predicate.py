from django.db import migrations, models
from unilex.vocabulary.models import Relation


def object_is_predicate(apps, schema_editor):
    Relation.objects.all().update(object=models.F('predicate'))


def predicate_is_empty(apps, schema_editor):
    Relation.objects.all().update(predicate=None)


class Migration(migrations.Migration):
    dependencies = [
        ("vocabulary", "0012_longer_vocab_desc_and_public_by_default"),
    ]

    operations = [
        migrations.RunPython(object_is_predicate),
        migrations.AlterField(
            model_name="relation",
            name="object",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="object",
                to="vocabulary.concept",
            ),
        ),
        migrations.AlterField(
            model_name="relation",
            name="predicate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="predicate",
                to="vocabulary.concept",
            ),
        ),
        migrations.RunPython(predicate_is_empty),
    ]
