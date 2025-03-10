# Generated by Django 5.1.4 on 2025-01-15 10:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("league_manager", "0013_remove_player_pass_completions_passcompletion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passcompletion",
            name="match",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="match_completions",
                to="league_manager.match",
            ),
        ),
        migrations.AlterField(
            model_name="passcompletion",
            name="receiver",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="receiver_completions",
                to="league_manager.player",
            ),
        ),
        migrations.AlterField(
            model_name="passcompletion",
            name="team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="team_completions",
                to="league_manager.team",
            ),
        ),
        migrations.AlterField(
            model_name="passcompletion",
            name="thrower",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="thrower_completions",
                to="league_manager.player",
            ),
        ),
        migrations.CreateModel(
            name="Casualty",
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
                    "causing_player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="caused_casualties",
                        to="league_manager.player",
                    ),
                ),
                (
                    "causing_team",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="casualties_inflicted",
                        to="league_manager.team",
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_casualties",
                        to="league_manager.match",
                    ),
                ),
                (
                    "victim_player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="suffered_casualties",
                        to="league_manager.player",
                    ),
                ),
                (
                    "victim_team",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="casualties_sustained",
                        to="league_manager.team",
                    ),
                ),
            ],
        ),
    ]
