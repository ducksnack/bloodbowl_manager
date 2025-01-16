# Generated by Django 5.1.4 on 2025-01-07 12:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("league_manager", "0005_playertype_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="playertype",
            name="number",
        ),
        migrations.AddField(
            model_name="player",
            name="number",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
