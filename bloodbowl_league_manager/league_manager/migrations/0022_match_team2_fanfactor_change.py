# Generated by Django 3.2.5 on 2025-01-20 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league_manager', '0021_match_team1_fanfactor_change_match_team1_winnings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='team2_fanfactor_change',
            field=models.IntegerField(default=0),
        ),
    ]
