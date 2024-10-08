# Generated by Django 4.2 on 2023-04-30 13:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vocabulary", "0011_onto_relations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vocabulary",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="vocabulary",
            name="private",
            field=models.BooleanField(
                default=False,
                help_text="Private vocabulary can be edited only by the users belonging to its authority.",
                verbose_name="Private vocabulary (paid members only)",
            ),
        ),
    ]
