from django.contrib import admin
from .models import League, Team, Player, PlayerType, Faction, Match, Touchdown, PassCompletion, Casualty, Interception, MostValuablePlayer, InjuryType, Injury, LevelUpType, LevelUp, Skill

admin.site.register(League)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(PlayerType)
admin.site.register(Faction)
admin.site.register(Match)
admin.site.register(Touchdown)
admin.site.register(PassCompletion)
admin.site.register(Casualty)
admin.site.register(Interception)
admin.site.register(MostValuablePlayer)
admin.site.register(InjuryType)
admin.site.register(Injury)
admin.site.register(LevelUpType)
admin.site.register(LevelUp)
admin.site.register(Skill)
