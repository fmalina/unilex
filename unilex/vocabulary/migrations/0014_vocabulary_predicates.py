# Generated by Django 4.2 on 2023-07-30 21:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vocabulary", "0013_object_is_predicate"),
    ]

    operations = [
        migrations.AddField(
            model_name="vocabulary",
            name="predicates",
            field=models.ManyToManyField(
                blank=True, related_name="predicates", to="vocabulary.concept"
            ),
        ),
    ]
