# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vocabulary', '0002_auto_20150511_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocabulary',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
