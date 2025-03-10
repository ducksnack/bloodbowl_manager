# Generated by Django 5.1.4 on 2025-01-19 12:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("league_manager", "0019_injurytype_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="team1_fame",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="team2_fame",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="weather",
            field=models.CharField(default="nice", max_length=20),
        ),
    ]
