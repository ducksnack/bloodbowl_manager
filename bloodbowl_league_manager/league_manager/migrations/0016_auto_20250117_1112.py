# Generated by Django 3.2.5 on 2025-01-17 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league_manager', '0015_remove_player_casualties_remove_player_interceptions_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='InjuryType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('ma_modifier', models.IntegerField(default=0)),
                ('st_modifier', models.IntegerField(default=0)),
                ('ag_modifier', models.IntegerField(default=0)),
                ('av_modifier', models.IntegerField(default=0)),
                ('dead', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='player',
            name='injuries',
            field=models.CharField(default='None', max_length=100),
        ),
        migrations.CreateModel(
            name='Injury',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('injury_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league_manager.injurytype')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='_match_injuries', to='league_manager.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_injuries', to='league_manager.player')),
            ],
        ),
    ]
