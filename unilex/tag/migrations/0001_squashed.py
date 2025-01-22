# Generated by Django 4.2.11 on 2025-01-20 20:42

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [
        ("tag", "0001_initial"),
        ("tag", "0002_accountability"),
        ("tag", "0003_desc_text_url_to_uri"),
        ("tag", "0004_urikey"),
    ]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vocabulary", "0007_vocabulary_force_unique_nodeid"),
    ]

    operations = [
        migrations.CreateModel(
            name="Record",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=150)),
                ("desc", models.TextField(blank=True, verbose_name="Description")),
                (
                    "key",
                    models.CharField(
                        max_length=150,
                        unique=True,
                        verbose_name="Key / URI / Unique Resource ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=datetime.datetime.now, editable=False),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=datetime.datetime.now, editable=False),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "concept",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vocabulary.concept",
                    ),
                ),
                (
                    "record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tag.record"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=datetime.datetime.now, editable=False),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=datetime.datetime.now, editable=False),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "weight",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Relevance weight of conceptfor the record that determines order and importance of tags",
                    ),
                ),
            ],
        ),
    ]
