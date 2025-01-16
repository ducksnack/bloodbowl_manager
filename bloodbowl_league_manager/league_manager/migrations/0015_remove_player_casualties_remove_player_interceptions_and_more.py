# Generated by Django 5.1.4 on 2025-01-15 10:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("league_manager", "0014_alter_passcompletion_match_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="player",
            name="casualties",
        ),
        migrations.RemoveField(
            model_name="player",
            name="interceptions",
        ),
        migrations.RemoveField(
            model_name="player",
            name="mvps",
        ),
        migrations.CreateModel(
            name="Interception",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "intercepting_player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="caught_interceptions",
                        to="league_manager.player",
                    ),
                ),
                (
                    "intercepting_team",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_caught_interceptions",
                        to="league_manager.team",
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_interceptions",
                        to="league_manager.match",
                    ),
                ),
                (
                    "throwing_player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="thrown_interceptions",
                        to="league_manager.player",
                    ),
                ),
                (
                    "throwing_team",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_thrown_interceptions",
                        to="league_manager.team",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MostValuablePlayer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_mvps",
                        to="league_manager.match",
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="player_mvps",
                        to="league_manager.player",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_mvps",
                        to="league_manager.team",
                    ),
                ),
            ],
        ),
    ]
